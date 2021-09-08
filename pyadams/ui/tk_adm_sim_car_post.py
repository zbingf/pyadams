"""
    Adm编辑计算
    Car模块
    立柱加载
"""
from pyadams.ui import tkui
from pyadams.car import adm_sim
from pyadams.call import admrun, threadingrun
from pyadams.file import result, file_edit, adm_post_edit


DataModel = result.DataModel

import re
import time
import pprint
import logging
import os.path
import tkinter as tk
TkUi            = tkui.TkUi
ResultUi        = tkui.ResultUi
AdmSimUi        = tkui.AdmSimUi

PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


class AdmSimCalCarPostUi(TkUi):

    def __init__(self, title, frame=None):
        super().__init__(title, frame=frame)

        # ===============================================
        # sim模块-模块
        adm_sim_frame = tk.LabelFrame(self.window, text='ADM仿真模块')
        adm_sim_frame.pack()

        loads = ['adm_path', 'drv_path', 'adams_version', 'label']
        texts = {
            'adm_path'      : 'adm file',
            'drv_path'      : 'spline ID',
            'samplerate'    : '采样频率',
            'simtime'       : '仿真时长s',
            'label'         : 'Car-多立柱垂向加载',
        }
        admsim_obj = AdmSimUi('ADM仿真', frame=adm_sim_frame, loads=loads, texts=texts)

        # ===============================================
        # spline加载-模块
        load_frame = tk.LabelFrame(adm_sim_frame, text='Spline 加载')
        load_loads = ['res_paths', 'reqs', 'comps', 'nrange', 'nchannel']
        load_texts = {
                'res_path'   : '后处理文件',
                'reqs'       : 'reqs',
                'comps'      : 'comps',
                'nrange'     : '数据截取范围\n(起始,结束)',
                'nchannel'   : '通道截取\nNone或n1,n2,...',
                'label_text' : '备注: 计数起始值为0',
            }
        load_obj   = ResultUi('ResultUi', load_frame, load_loads, load_texts)
        admsim_obj.cur_frame.pack(side='left')
        load_frame.pack(side='right')

        # ===============================================
        self.frame_note()
        self.frame_buttons_RWR({
            'frame'             : 'rrw',
            'button_run_name'   : '运行',
            'button_write_name' : '保存',
            'button_read_name'  : '读取',
            'button_width'      : 15,
            'func_run'          : self.fun_run,
            })

        self.sub_frames['adm_sim']    = admsim_obj
        self.sub_frames['load']       = load_obj

        # =========================
        # 多设置计算
        self.frame_ui_runs()


    def fun_run(self):

        self.print('开始计算')

        # ========================= 参数读取
        values = {}
        for key in self.sub_frames:
            values[key] = self.sub_frames[key].get_vars_and_texts()
        values['current'] = self.get_vars_and_texts()

        # ========================= 参数解析
        adams_version = values['adm_sim']['adams_version']    # adams_version
        adm_path      = values['adm_sim']['adm_path']  
        spline_id     = values['adm_sim']['spline_id']  

        adams_version = '2017.2' if adams_version == 1 else '2019'

        # ========================= 默认设置
        data_model_name = 'multi_adm_result'
        max_threading   = 4
        simlimit        = 60
        # =========================
        
        # spline 加载
        load_paths = values['load']['res_path']
        if isinstance(load_paths, str): load_paths = [load_paths]
        
        load_dic = {}
        sim_dic  = {}
        for load_path in load_paths:
            # 子名称 key
            sub_name = os.path.basename(load_path)
            sub_name = '.'.join(sub_name.split('.')[:-1])

            # 读取数据
            obj = self.read_result(load_path, values['load'], sub_name, data_model_name)
            load_data  = obj.get_data()
            load_samplerate = obj.get_samplerate()
            load_time  = len(load_data[0]) / load_samplerate
            load_edit = {'spline_ids': spline_id, 'list2d': load_data, 'samplerate': load_samplerate}

            sim_param = {'simtype':1, 'samplerate':load_samplerate, 'simtime':load_time, 'step':None, 
                'version':adams_version, 'simlimit':simlimit}
            
            load_dic[sub_name] = load_edit
            sim_dic[sub_name]  = sim_param

        # =========================
        # 修改
        self.print('\n修改adm文件\n')

        edit_param = {
            'value_edit': {'value_cmd': None, 'list1d_value':None},
            'str_edit'  : {'str_cmd':None, 'list1d_str':None},
            'load_edit' : None,
        }

        admparam_obj = adm_sim.AdmParam(edit_param)
        edit_params = admparam_obj.create_load_multi_params(load_dic)

        # =========================
        # 计算
        self.print('\n计算中\n')

        # adm 提前编辑
        self.print('\nAdm预编辑\n')
        adm_path = adm_post_edit.adm_car_post_edit(adm_path)

        adm_sim.AdmSimControl.model_names = [] # 提前清空
        admsim_obj = adm_sim.AdmSimControl(adm_path)
        for sub_name in edit_params:
            admsim_obj.set_sub_dir(sub_name)
            admsim_obj.set_adm_edit(sub_name, edit_params[sub_name])
            admsim_obj.set_sim_param(sub_name, sim_dic[sub_name])
        # return None
        admsim_obj.amd_sim_threading(max_threading)
        res_paths = admsim_obj.res_paths

        # =========================
        # 后处理重命名
        adm_dir = os.path.dirname(adm_path)
        new_res_paths = {}
        for sub_name in edit_params:
            new_res_path = os.path.join(adm_dir, sub_name+'.res')
            res_path     = res_paths[sub_name]
            new_res_paths[sub_name] = new_res_path
            if os.path.exists(new_res_path):
                os.remove(new_res_path)
            os.rename(res_path, new_res_path)       # 重命名

        # =========================
        logger.info('new_res_paths:'+pprint.pformat(new_res_paths))
        self.print('计算完成')

        return None

    def read_result(self, res_path, params, sub_name, data_model_name):
        
        # res_path = params['res_path']
        if not res_path: return None

        reqs     = params['reqs']
        comps    = params['comps']
        nrange   = params['nrange']
        nchannel = params['nchannel']

        if not nrange:   nrange   = None
        if not nchannel: nchannel = None

        data_obj = DataModel(data_model_name)
        data_obj.new_file(res_path, sub_name)
        data_obj[sub_name].set_reqs_comps(reqs, comps)
        data_obj[sub_name].set_select_channels(nchannel)
        data_obj[sub_name].set_line_ranges(nrange)

        if res_path[-3:].lower() == 'res':
            data_obj[sub_name].read_file_faster()
        else:
            data_obj[sub_name].read_file()

        return data_obj[sub_name]

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    AdmSimCalCarPostUi('AdmSimCal-CarPost').run()
