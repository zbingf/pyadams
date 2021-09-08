"""
	根据adm文件检测request是否合理

	用于载荷分解查错

	主要检测:	request force (具备参考marker)

	2021/04/13
"""

from pyadams.file import admfile
from pyadams.car import request_check
from pyadams.ui import tkui
TkUi = tkui.TkUi

ReferenceMarkCHeck = request_check.ReferenceMarkCHeck

import re
import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


class RMCheckUi(TkUi):

    def __init__(self, title, frame=None):

        super().__init__(title, frame=frame)

        self.frame_loadpath({
            'frame':'adm_path', 'var_name':'adm_path', 'path_name':'adm file',
            'path_type':'.adm', 'button_name':'adm load',
            'button_width':15, 'entry_width':30,
            })

        self.frame_entry({
            'frame':'target_str','var_name':'target_str','label_text':'目标request包含的文字',
            'label_width':30,'entry_width':10,
            })

        self.frame_entry({
            'frame':'target_part_name','var_name':'target_part_name','label_text':'参考坐标所属部件全称',
            'label_width':30,'entry_width':10,
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

        self.frame_text_lines({
            'frame':'strs',
            'text_name':'strs',
            'text_width':100, 'text_height':40,
            })

        self.vars['target_str'].set('to_frame_force')
        self.vars['target_part_name'].set('ground')

    def fun_run(self):
        
        params = self.get_vars_and_texts()
        obj = ReferenceMarkCHeck(params['adm_path'])
        strs = obj.reference_mark_check(target_str=params['target_str'],
            target_part_name=params['target_part_name'])

        self.set_text('strs', strs)



if __name__=='__main__':
	pass
	
	RMCheckUi('request 参考坐标系查错').run()


