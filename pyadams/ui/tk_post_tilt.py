"""

    提载程序计算
    合力计算
"""

from pyadams.ui import tkui
from pyadams.car import post_tilt
from pyadams import datacal

TkUi = tkui.TkUi

import tkinter as tk
import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)

class PostTiltUi(TkUi):

    def __init__(self, title, frame=None):
        super().__init__(title, frame=frame)

        self.frame_loadpaths({
            'frame':'res_paths', 'var_name':'res_paths', 'path_name':'res files',
            'path_type':'.res', 'button_name':'res files',
            'button_width':15, 'entry_width':40,
            })

        self.frame_entry({
            'frame':'target_angles', 'var_name':'target_angles', 'label_text':'监测侧翻角度 deg',
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

        # self.frame_ui_runs()
        self.frame_note()

        self.vars['target_angles'].set('14,28,35')


    def fun_run(self):
        params = self.get_vars_and_texts()

        res_paths     = params['res_paths']
        target_angles = params['target_angles']

        if not res_paths:
            self.print('\n\n无res文件,取消计算\n\n')
            return None

        res_paths = res_paths if isinstance(res_paths, list) else [res_paths]
        target_angles = target_angles if isinstance(target_angles, list) else [target_angles]

        for res_path in res_paths:
            output_data = post_tilt.cal_tilt(res_path, target_angles)
            print(datacal.str_view_data_type(output_data))  # 数据结构
            docx_path = res_path[:-4]+'.docx'
            pdf_path = post_tilt.pdf_create(docx_path, output_data)

            os.popen(pdf_path)

        self.print('\n计算完成\n')
        
        return None
    

if __name__=='__main__':
    
    logging.basicConfig(level=logging.INFO)
    logger.info('start')
    PostTiltUi('数据处理-静侧翻角').run()