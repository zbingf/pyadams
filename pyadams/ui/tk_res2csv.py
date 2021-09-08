""" 
    res数据读取并将指定数据专成csv格式

    2021/04/14
"""

from pyadams.ui import tkui, tk_reqcomp
from pyadams.car import post_force_load
TkUi = tkui.TkUi

import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)

class Res2CsvUi(TkUi):

    def __init__(self, title, frame=None):
        super().__init__(title, frame=frame)

        self.frame_loadpaths({
            'frame':'res_files', 'var_name':'res_files', 'path_name':'res files',
            'path_type':'.res', 'button_name':'res files',
            'button_width':15, 'entry_width':40,
            })

        self.frame_entry({
            'frame':'reqs', 'var_name':'reqs', 'label_text':'reqs',
            'label_width':15, 'entry_width':40,
            })

        self.frame_entry({
            'frame':'comps', 'var_name':'comps', 'label_text':'comps',
            'label_width':15, 'entry_width':30,
            })

        self.frame_button({
            'frame':'reqcomp_ui',
            'button_name':'reqs comps 辅助生成',
            'button_width':30,
            'func':self.fun_reqcomp_ui,
            })

        self.frame_entry({
            'frame':'n_start', 'var_name':'n_start', 'label_text':'读取-起始位置',
            'label_width':15, 'entry_width':40,
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

        self.vars['n_start'].set('5')


    def fun_run(self):
        params = self.get_vars_and_texts()

        file_paths = params['res_files']
        reqs = params['reqs']
        comps = params['comps']
        n_start = params['n_start']

        if isinstance(file_paths,str):
            file_paths = [file_paths]
        else:
            file_paths = [file_path for file_path in file_paths if file_path]


        force_data_list, event_names, samplerates = post_force_load.get_res_paths(file_paths, reqs, comps, n_start=n_start)

        post_force_load.csv_force_datas(file_paths, force_data_list, reqs, comps, samplerates)

        self.print('计算完成')

    def fun_reqcomp_ui(self):
        tk_reqcomp.ReqComTxtUi('ReqsComps').run()


if __name__=='__main__':
    
    Res2CsvUi('数据处理:Res转Csv').run()