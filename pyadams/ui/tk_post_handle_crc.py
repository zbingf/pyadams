"""

    提载程序计算
    合力计算
"""
from pyadams.ui import tkui
from pyadams.car import post_handle_crc
TkUi = tkui.TkUi

import tkinter as tk
import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)

class PostHandleCrcUi(TkUi):

    def __init__(self, title, frame=None):
        super().__init__(title, frame=frame)

        self.frame_loadpath({
            'frame':'res_path', 'var_name':'res_path', 'path_name':'res file',
            'path_type':'.res', 'button_name':'res file',
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

        self.frame_entry({
            'frame':'L', 'var_name':'L', 'label_text':'轴距 m',
            'label_width':15, 'entry_width':40,
            })

        self.frame_entry({
            'frame':'spline_s', 'var_name':'spline_s', 'label_text':'侧偏角拟合程度设置S',
            'label_width':20, 'entry_width':40,
            })

        self.frame_savepath({
            'frame' : 'docx_path', 'var_name':'docx_path', 'path_name' : 'docx file',
            'path_type' : '.docx', 'button_name' : 'docx save',
            'button_width' : 15, 'entry_width' : 30,
            })
        
        self.frame_buttons_RWR({
            'frame' : 'rrw',
            'button_run_name' : '运行',
            'button_write_name' : '保存',
            'button_read_name' : '读取',
            'button_width' : 15,
            'func_run' : self.fun_run,
            })
        
        new_frame = tk.LabelFrame(self.window, text='模板调用及替换数据(非必要)')
        new_frame.pack()

        self.frame_loadpath({
            'frame':'template_path', 'var_name':'template_path', 'path_name':'docx file',
            'path_type':'.docx', 'button_name':'docx模板',
            'button_width':15, 'entry_width':40,
            }, frame=new_frame)

        self.frame_savepath({
            'frame' : 'new_docx_path', 'var_name':'new_docx_path', 'path_name' : 'docx file',
            'path_type' : '.docx', 'button_name' : '基于模板生成的docx',
            'button_width' : 20, 'entry_width' : 30,
            }, frame=new_frame)

        self.frame_ui_runs()

        self.frame_note()

        self.vars['reqs'].set('chassis_accelerations,chassis_velocities,chassis_velocities,chassis_displacements,jms_steering_wheel_angle_data,chassis_displacements,chassis_displacements')
        self.vars['comps'].set('lateral,yaw,longitudinal,roll,displacement,lateral,longitudinal')
        self.vars['spline_s'].set(0.1)

    def fun_run(self):
        params = self.get_vars_and_texts()

        res_path = params['res_path']
        docx_path = params['docx_path']
        L = params['L']
        reqs = params['reqs']
        comps = params['comps']
        spline_s = params['spline_s']

        template_path = params['template_path']
        new_docx_path = params['new_docx_path']

        crc_data, score_data, data_plot = post_handle_crc.handle_crc(res_path, docx_path, L, reqs, comps, spline_s)


        if template_path and new_docx_path:
            post_handle_crc.handle_crc_docx_template(template_path, new_docx_path, crc_data, score_data)

        
        self.print('计算完成')
        
        return None
        

if __name__=='__main__':
    
    logging.basicConfig(level=logging.INFO)
    logger.info('start')
    PostHandleCrcUi('数据处理-稳态回转').run()