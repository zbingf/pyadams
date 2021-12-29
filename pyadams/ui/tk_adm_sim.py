"""
    Adm编辑计算
    Car模块
"""
from pyadams.ui import tkui
from pyadams.car import adm_sim
from pyadams.call import admrun, threadingrun
from pyadams.file import result, file_edit

DataModel = result.DataModel

import re
import time
import pprint
import logging
import os.path
import tkinter as tk
TkUi            = tkui.TkUi
TextUi          = tkui.TextUi
TextEditUi      = tkui.TextEditUi
StrValuesEditUi = tkui.StrValuesEditUi
ResultUi        = tkui.ResultUi
AdmSimUi        = tkui.AdmSimUi

PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


class AdmSimCalUi(TkUi):

    def __init__(self, title, frame=None):
        super().__init__(title, frame=frame)

        # ===============================================
        adm_sim_frame = tk.LabelFrame(self.window, text='ADM仿真模块')
        adm_sim_frame.pack()

        admsim_obj = AdmSimUi('ADM仿真', adm_sim_frame)

        load_frame = tk.LabelFrame(adm_sim_frame, text='Spline 加载')
        load_loads = ['res_path', 'reqs', 'comps', 'nrange', 'nchannel']
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
        adm_edit_frame = tk.LabelFrame(self.window, text='ADM编辑')
        adm_edit_frame.pack()

        a_loads = ['value', 'select', 'gain', 'label_text']
        a_texts = {
                'value'      : '各变量数值',
                'select'     : '灵敏计算-通道选取',
                'gain'       : '灵敏计算-增益\n不填则不计算',
                'label_text' : '数值变量',
            }

        b_loads = ['value', 'select', 'gain', 'label_text']
        b_texts = {
                'value'      : '变量选取',
                'select'     : '灵敏计算-通道选取',
                'gain'       : '灵敏计算-设置\n1计算|0不计算',
                'label_text' : '数值变量',
            }

        a_frame = tk.LabelFrame(adm_edit_frame, text='数值变量')
        a_obj   = StrValuesEditUi('数值变量编辑', 'values_cmd', a_frame, a_loads, a_texts)
        a_frame.pack(side='left')

        b_frame = tk.LabelFrame(adm_edit_frame, text='字符变量')
        b_obj   = StrValuesEditUi('字符变量编辑', 'strs_cmd', b_frame, b_loads, b_texts)
        b_frame.pack(side='right')

        # ===============================================
        result_frame = tk.LabelFrame(self.window, text='后处理')
        u_frame      = tk.LabelFrame(result_frame, text='A 分子 Result')
        l_frame      = tk.LabelFrame(result_frame, text='A 分母 Result')

        upper_loads = ['reqs', 'comps', 'nrange', 'nchannel']
        upper_texts = {
                'reqs'       : 'reqs',
                'comps'      : 'comps',
                'nrange'     : '数据截取范围\n(起始,结束)',
                'nchannel'   : '通道截取\nNone或n1,n2,...',
            }

        lower_loads = ['res_path', 'reqs', 'comps', 'nrange', 'nchannel']
        lower_texts = {
                'res_path'   : '后处理文件',
                'reqs'       : 'reqs',
                'comps'      : 'comps',
                'nrange'     : '数据截取范围\n(起始,结束)',
                'nchannel'   : '通道截取\nNone或n1,n2,...',
            }

        upper_obj    = ResultUi('upper', u_frame, upper_loads, upper_texts)
        lower_obj    = ResultUi('lower', l_frame, lower_loads, lower_texts)
        u_frame.pack(side='left')
        l_frame.pack(side='right')
        result_frame.pack()

        # ===============================================
        self.frame_entry({
            'frame':'plot1', 'var_name':'block_size', 'label_text':'|block_size|',
            'label_width':9, 'entry_width':10,
            })

        self.frame_entry({
            'frame':'plot1', 'var_name':'hz_range', 'label_text':'|Hz_range|',
            'label_width':9, 'entry_width':10,
            })
        
        self.frame_savepath({
            'frame' : 'docx_path', 'var_name':'docx_path', 'path_name' : 'docx file',
            'path_type' : '.docx', 'button_name' : 'docx路径',
            'button_width' : 15, 'entry_width' : 30,
            })

        self.frame_radiobuttons({
            'frame':'pdfType', 'var_name':'pdfType',
            'texts':['pdf-详细', 'pdf-简化'],
            })

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

        self.sub_frames['values_cmd'] = a_obj
        self.sub_frames['strs_cmd']   = b_obj
        self.sub_frames['adm_sim']    = admsim_obj
        self.sub_frames['load']       = load_obj
        self.sub_frames['upper']      = upper_obj
        self.sub_frames['lower']      = lower_obj

        # ========================= 默认值设置
        a_obj.vars['value'].set('None')
        b_obj.vars['value'].set('None')
        a_obj.vars['select'].set('all')
        b_obj.vars['select'].set('all')
        a_obj.vars['gain'].set('')
        b_obj.vars['gain'].set('0')
        upper_obj.vars['nrange'].set('None')
        upper_obj.vars['nchannel'].set('None')
        lower_obj.vars['nrange'].set('None')
        lower_obj.vars['nchannel'].set('None')

        self.vars['pdfType'].set(2)
        # print(TkUi.count)

    def fun_run(self):

        self.print('开始计算')

        # ========================= 参数读取
        values = {}
        for key in self.sub_frames:
            values[key] = self.sub_frames[key].get_vars_and_texts()
        values['current'] = self.get_vars_and_texts()
        # pprint.pprint(values)

        # ========================= 参数解析
        adams_version = values['adm_sim']['adams_version']  # adams_version
        adm_path      = values['adm_sim']['adm_path']  
        isLoad        = values['adm_sim']['isLoad']         # spline load
        sim_type      = values['adm_sim']['sim_type']  
        spline_id     = values['adm_sim']['spline_id']  
        sim_samplerate= values['adm_sim']['samplerate']
        simtime       = values['adm_sim']['simtime']

        block_size    = values['current']['block_size']  
        docx_path     = values['current']['docx_path']  
        hz_range      = values['current']['hz_range']  
        pdfType       = values['current']['pdfType']  

        adams_version = '2017.2' if adams_version==1 else '2019'
        # run_type      = 'single' if run_type==1 else 'multi'
        
        if sim_type == 1:
            sim_type = adm_sim.VIEW
        elif sim_type == 2:
            sim_type = adm_sim.VIEW
        elif sim_type == 3:
            sim_type = adm_sim.CAR

        # ========================= 默认设置
        data_model_name = 'multi_adm_result'
        max_threading   = 4
        simlimit        = 300      # 计算时常监测, 300分钟
        # =========================
        
        # spline 加载
        if isLoad:
            obj = self.read_result(values['load'], 'load', data_model_name)
            load_data  = obj.get_data()
            load_samplerate = obj.get_samplerate()
            load_time  = len(load_data[0]) / load_samplerate
            load_edit = {'spline_ids': spline_id, 'list2d': load_data, 'samplerate': load_samplerate}

        else:
            load_edit = {'spline_ids': None, 'list2d': None, 'samplerate': None}

        # 仿真类型
        if sim_type == adm_sim.CAR:
            # car event仿真
            sim_param = {'simtype':sim_type, 'samplerate':None, 'simtime':None, 'step':None, 
                'version':adams_version, 'simlimit':simlimit}
        
        elif sim_type == adm_sim.VIEW:
            # view仿真
            if not sim_samplerate: 
                # 未设置采样频率
                if isLoad:
                    sim_param = {'simtype':sim_type, 'samplerate':load_samplerate, 'simtime':load_time, 'step':None, 
                        'version':adams_version, 'simlimit':simlimit}
                else:
                    raise '未输入仿真时长-请输入simetime'
            else:
                # 已定义采样频率
                sim_param = {'simtype':sim_type, 'samplerate':sim_samplerate, 'simtime':simtime, 'step':None, 
                    'version':adams_version, 'simlimit':simlimit}
        
        value_cmd       = values['values_cmd']['values_cmd']
        list1d_value    = values['values_cmd']['value']
        values_selects  = values['values_cmd']['select']
        values_gain     = values['values_cmd']['gain']

        str_cmd         = values['strs_cmd']['strs_cmd']
        list1d_str      = values['strs_cmd']['value']
        strs_selects    = values['strs_cmd']['select']
        isCal           = values['strs_cmd']['gain']

        edit_param = {
            'value_edit': {'value_cmd': value_cmd, 'list1d_value':list1d_value},
            'str_edit'  : {'str_cmd':str_cmd, 'list1d_str':list1d_str},
            'load_edit' : load_edit,
        }

        params = {
            'block_size': {'u':block_size[0], 'l':block_size[1]},
            'hz_range'  : hz_range,
            'docx_path' : docx_path,
        }

        csv_path   = docx_path[:-4]+'csv'
        req_params = values['upper']
        
        # lower read 目标数据读取
        target_obj = self.read_result(values['lower'], 'target', data_model_name)
        lower_name = 'm' if target_obj == None else 'target'

        # pprint.pprint(edit_param)
        # pprint.pprint(params)
        # pprint.pprint(csv_path)
        # pprint.pprint(target_obj)
        # pprint.pprint(lower_name)

        # =========================修改
        self.print('\n修改adm文件\n')
        admparam_obj = adm_sim.AdmParam(edit_param)
        # admparam_obj.set_values_gain_2(values_selects, values_gain)
        admparam_obj.set_value_orthogonal(values_selects, values_gain)
        admparam_obj.set_strs_n(strs_selects, isCal)
        edit_params = admparam_obj.create_edit_params(base_name='m')

        # =========================计算
        self.print('\n计算中\n')
        adm_sim.AdmSimControl.model_names = [] # 提前清空
        admsim_obj = adm_sim.AdmSimControl(adm_path)
        for sub_name in edit_params:
            admsim_obj.set_sub_dir(sub_name)
            admsim_obj.set_adm_edit(sub_name, edit_params[sub_name])
            admsim_obj.set_sim_param(sub_name, sim_param)
        # return None
        admsim_obj.amd_sim_threading(max_threading)
        res_paths = admsim_obj.res_paths

        logger.info('res_paths:'+pprint.pformat(res_paths))
        # =========================res读取
        self.print('\n后处理读取\n')
        admres_obj = adm_sim.AdmResult(data_model_name)
        admres_obj.read_res_paths(res_paths, req_params)
        result_compare = admres_obj.create_pdf(edit_params, params, 
            lower_name=lower_name, pdfType=pdfType)

        str_input = pprint.pformat(values)
        str_input = str_input.replace("\\n", '')
        str_input = str_input.replace("'", '')
        str_input = re.sub('\n\s+\n', '\n', str_input)
        admres_obj.parse_result_compare(csv_path, str_input)

        time.sleep(0.5)
        self.remove_png_file(docx_path)

        self.print('计算完成')
        return None

    def read_result(self, params, sub_name, data_model_name):
        
        res_path = params['res_path']
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

    def remove_png_file(self, docx_path):

        values     = self.get_vars_and_texts()
        path, name = os.path.split(docx_path)
        file_edit.file_remove_pt(path, prefix=name[:-5], file_type='png')

        return None


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    AdmSimCalUi('AdmSimUi').run()