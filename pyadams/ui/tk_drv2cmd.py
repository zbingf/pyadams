"""
    未完成

    将drv数据转化为cmd数据用于adams加载
    
"""

from pyadams.ui import tkui
from pyadams.view import drv2cmd
import os

import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)

class Drv2CmdUi(tkui.TkUi):
    """

    """

    def __init__(self, title, frame=None):
        super().__init__(title, frame=frame)

        self.frame_loadpaths({
            'frame':'drv_path','var_name':'drv_path', 
            'path_name':'drv file', 'path_type':['*.drv', '*.rsp', '*.res', '*.req', '*.csv'],
            'button_name':'加载文件',
            'button_width':15, 'entry_width':30,
            })
        
        self.frame_entry({
            'frame':'reqs', 'var_name':'reqs', 'label_text':'reqs',
            'label_width':15, 'entry_width':30,
            })

        self.frame_entry({
            'frame':'comps', 'var_name':'comps', 'label_text':'comps',
            'label_width':15, 'entry_width':30,
            })

        self.frame_entry({
            'frame':'nrange', 'var_name':'nrange', 'label_text':'nrange',
            'label_width':15, 'entry_width':30,
            })

        self.frame_savepath({
            'frame' : 'cmd_path', 'var_name':'cmd_path', 'path_name' : 'cmd file',
            'path_type' : '.cmd', 'button_name' : 'cmd文件',
            'button_width' : 15, 'entry_width' : 30,
            })

        self.frame_entry({
            'frame':'model_name', 'var_name':'model_name', 'label_text':'主模型名称',
            'label_width':15, 'entry_width':30,
            })

        self.frame_entry({
            'frame':'spline_names', 'var_name':'spline_names', 'label_text':'spline名称',
            'label_width':15, 'entry_width':30,
            })


        self.frame_radiobuttons({
            'frame':'isEdit',
            'var_name':'isEdit',
            'texts':['编辑曲线', '创建曲线'],
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

        self.vars['nrange'].set('None')


    def fun_run(self):

        params = self.get_vars_and_texts()

        reqs        = params['reqs']
        comps       = params['comps']
        drv_path    = params['drv_path']
        nrange      = params['nrange']
        cmdpath     = params['cmd_path']
        model_name  = params['model_name']
        spline_names= params['spline_names']
        isEdit      = True if params['isEdit']==1 else False
        print(nrange)
        if isinstance(spline_names, str) : spline_names = [spline_names]

        if isinstance(reqs, list):
            reqs = [value for value in reqs if value]
            comps = [value for value in comps if value]

        if isinstance(drv_path, str):
            drv2cmd.drv2cmd(cmdpath, model_name, drv_path, 
                spline_names, reqs=reqs, comps=comps, nrange=nrange, isEdit=isEdit)
        else:
            for path in drv_path:
                drv2cmd.drv2cmd(path[:-3]+'cmd', model_name, path, 
                    spline_names, reqs=reqs, comps=comps, nrange=nrange, isEdit=isEdit)
        
        self.print('计算完成')

        return None

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    logger.info('start')
    Drv2CmdUi('Drv2Cmd').run()