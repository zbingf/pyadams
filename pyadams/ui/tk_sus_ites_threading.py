"""
    悬架迭代
    多文件、多线程迭代
"""

from pyadams.car import sus_ite
from pyadams.ui import tkui
TkUi = tkui.TkUi

import time

import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)

class SusIteSThreadingUi(TkUi):
    """
        AdmSim 主程序
    """
    def __init__(self, title, frame=None):
        
        logger.info('start SusIteSThreadingUi')

        super().__init__(title, frame=frame)
        str_label = '-'*50

        self.frame_label_only({'label_text':f'{str_label}悬架迭代{str_label}','label_width':50})
        
        # self.frame_loadpath({
        #   'frame':'rsp_path', 'var_name':'rsp_path', 'path_name':'rsp file',
        #   'path_type':'.rsp', 'button_name':'rsp load',
        #   'button_width':15, 'entry_width':30,
        #   })

        self.frame_loadpaths({
            'frame':'rsp_files', 'var_name':'rsp_files', 'path_name':'rsp files',
            'path_type':'.rsp', 'button_name':'rsp files',
            'button_width':15, 'entry_width':40,
            })

        # self.frame_loadpath({
        #   'frame':'lcf_path', 'var_name':'lcf_path', 'path_name':'lcf file',
        #   'path_type':'.lcf', 'button_name':'lcf load',
        #   'button_width':15, 'entry_width':30,
        #   })

        self.frame_loadpath({
            'frame':'adm_path', 'var_name':'adm_path', 'path_name':'adm file',
            'path_type':'.adm', 'button_name':'adm load',
            'button_width':15, 'entry_width':30,
            })

        self.frame_entry({
            'frame':'requests', 'var_name':'requests', 'label_text':'requests',
            'label_width':15, 'entry_width':10,
            })
        self.frame_entry({
            'frame':'components', 'var_name':'components', 'label_text':'components',
            'label_width':15, 'entry_width':10,
            })
        self.frame_entry({
            'frame':'gain_set', 'var_name':'k', 'label_text':'k迭代比例',
            'label_width':15, 'entry_width':10,
            })
        
        self.frame_entry({
            'frame':'gain_set', 'var_name':'maxit', 'label_text':'最大迭代次数',
            'label_width':15, 'entry_width':10,
            })

        self.frame_entry({
            'frame':'init_dis', 'var_name':'init_dis', 'label_text':'仿真位移初始值',
            'label_width':15, 'entry_width':10,
            })

        self.frame_entry({
            'frame':'loc_offset', 'var_name':'loc_offset', 'label_text':'仿真值偏置-起始位置',
            'label_width':18, 'entry_width':10,
            })

        self.frame_entry({
            'frame':'channels_set', 'var_name':'channels', 'label_text':'通道截取',
            'label_width':18, 'entry_width':10,
            })

        self.frame_entry({
            'frame':'channels_set', 'var_name':'res_channels', 'label_text':'res通道截取',
            'label_width':18, 'entry_width':10,
            })

        self.frame_radiobuttons({
            'frame':'version',
            'var_name':'version',
            'texts':['ADAMS 2019', 'ADAMS 2017.2'],
            })

        self.frame_checkbuttons({
            'frame' : 'iteration_set',
            'vars' : ['isStartLcf', 'isPlot'],
            'check_texts' : ['是否读取已有lcf数据', '是否作图'],
            })

        # self.frame_entry({
        #     'frame':'iteration_set', 'var_name':'target_pdi_delta', 'label_text':'相对伪损伤偏差',
        #     'label_width':15, 'entry_width':10,
        #     })
        
        self.frame_entry({
            'frame':'max_threading', 'var_name':'max_threading', 'label_text':'计算线程数',
            'label_width':15, 'entry_width':10,
            })

        self.frame_buttons_RWR({
            'frame' : 'rrw',
            'button_run_name' : '运行',
            'button_write_name' : '保存',
            'button_read_name' : '读取',
            'button_width' : 15,
            'func_run' : self.fun_run,
            })

        self.frame_note()

        self.vars['loc_offset'].set(2)
        self.vars['k'].set(0.8)
        self.vars['maxit'].set(6)
        # self.vars['target_pdi_delta'].set(0.05)
        self.vars['channels'].set('0,1')
        self.vars['res_channels'].set('0,1')
        self.vars['max_threading'].set(3)
        #self.run()

    def fun_run(self):
        """
            运行按钮调用函数
            主程序
        """
        # 获取界面数据
        params = self.get_vars_and_texts()
        logger.info(f'params数据:\n{params}\n')
        if params['version'] == 1:
            params['version'] = '2019'
        elif params['version'] == 2:
            params['version'] = '2017.2'

        # 线程数
        max_threading = int(params['max_threading'])
        max_threading = 0 if max_threading <= 0 else max_threading-1

        params['rsp_files'] = [os.path.abspath(path) for path in params['rsp_files']]
        params['adm_path']  = os.path.abspath(params['adm_path'])

        fun_params = {
            'max_threading' : max_threading, # 最大线程数
            'rsp_paths'     : params['rsp_files'],
            'adm_path'      : params['adm_path'],
            'requests'      : params['requests'],
            'components'    : params['components'],
            'k'             : params['k'],
            'isStartLcf'    : params['isStartLcf'],
            'init_dis'      : params['init_dis'],
            'loc_offset'    : params['loc_offset'],
            'version'       : params['version'],
            'channels'      : params['channels'],
            'isPlot'        : params['isPlot'],
            'res_channels'  : params['res_channels'],
            'maxit'         : int(params['maxit']), # 最大迭代数
        }
        # print(fun_params)
        output_data = sus_ite.sus_ite_threading(fun_params)
        # sus_ite.test_sus_ite_threading()
        logger.info(f'output_data:{output_data}')

        return True

if __name__ == '__main__':

    # Ui测试
    # import importlib
    # importlib.reload(logging)
    # log_path = r'tk_sus_ites_threading.log'
    # logging.basicConfig(level=logging.INFO, filename=log_path, filemode='w')
    logging.basicConfig(level=logging.INFO)
    obj = SusIteSThreadingUi('SusIteSThreadingUi').run()
    logging.shutdown()


