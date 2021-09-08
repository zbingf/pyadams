"""

    提载程序计算
    合力计算
"""

from pyadams.ui import tkui
from pyadams.car import post_handle_s
from pyadams.file import result
from pyadams.datacal import plot
TkUi = tkui.TkUi
DataModel = result.DataModel

import tkinter as tk
import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)

class PostHandleSUi(TkUi):

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
            'frame':'xdistance', 'var_name':'xdistance', 'label_text':'峰值截取大致间距 m',
            'label_width':20, 'entry_width':40,
            })
        
        self.frame_entry({
            'frame':'xdis_start', 'var_name':'xdis_start', 'label_text':'计算起始-X向位置 m',
            'label_width':20, 'entry_width':40,
            })

        self.frame_entry({
            'frame':'xdis_end', 'var_name':'xdis_end', 'label_text':'计算结尾-X向位置 m',
            'label_width':20, 'entry_width':40,
            })

        self.frame_button({
            'frame':'fun_get_xrange',
            'button_name':'查看图像 - 确认截取范围\n左键起始点 - 右键结束点',
            'button_width':20,
            'func':self.fun_get_xrange, # 回调函数
            }, frame=None)

        self.frame_savepath({
            'frame' : 'docx_path', 'var_name':'docx_path', 'path_name' : 'docx file',
            'path_type' : '.docx', 'button_name' : 'docx save',
            'button_width' : 15, 'entry_width' : 30,
            })

        self.frame_radiobuttons({
            'frame':'isBus',
            'var_name':'isBus',
            'texts':['客车', '卡车'],
            })

        self.frame_checkbutton({
            'frame':'isArticulated',
            'var_name':'isArticulated',
            'check_text':'客车铰接车',
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
            }, frame=new_frame )

        
        # self.frame_ui_runs()

        self.frame_note()

        self.vars['reqs'].set('chassis_accelerations,chassis_velocities,chassis_velocities,chassis_displacements,jms_steering_wheel_angle_data,chassis_displacements,chassis_displacements')
        self.vars['comps'].set('lateral,yaw,longitudinal,roll,displacement,lateral,longitudinal')

        self.vars['xdistance'].set(70)
        self.vars['xdis_start'].set(95)
        self.vars['xdis_end'].set(300)
        

    def fun_run(self):
        params = self.get_vars_and_texts()

        res_path = params['res_path']
        docx_path = params['docx_path']
        xdistance = params['xdistance']
        xdis_start = params['xdis_start']
        xdis_end = params['xdis_end']
        isBus = True if params['isBus']==1 else False
        
        # print(params['isBus'])
        # print(isBus)

        isArticulated = params['isArticulated']
        reqs = params['reqs']
        comps = params['comps']
        template_path = params['template_path']
        new_docx_path = params['new_docx_path']

        mean_data, score_data = post_handle_s.handle_s(res_path, docx_path, xdistance, xdis_start, xdis_end, isBus, isArticulated,
            reqs, comps)
        
        if template_path and new_docx_path:
            post_handle_s.handle_s_docx_template(template_path, new_docx_path, mean_data, score_data)


        self.print('\n计算完成\n')
        
        return None
    
    def fun_get_xrange(self): # 获取截取范围

        params = self.get_vars_and_texts()
        res_path = params['res_path']
        reqs = params['reqs']
        comps = params['comps']
        if reqs==None:
            reqs=["chassis_accelerations","chassis_velocities",
                "chassis_velocities","chassis_displacements",
                "jms_steering_wheel_angle_data","chassis_displacements",
                "chassis_displacements"]
        if comps==None:
            comps=["lateral","yaw",
                "longitudinal","roll",
                "displacement","lateral",
                "longitudinal"]


        dataobj = DataModel('post_handle_s')
        dataobj.new_file(res_path, 'handle_s')
        dataobj['handle_s'].set_reqs_comps(reqs, comps)
        dataobj['handle_s'].set_line_ranges([4,None])
        dataobj['handle_s'].set_select_channels(None)
        dataobj['handle_s'].read_file()
        data = dataobj['handle_s'].get_data()
        xline = [value/1000 for value in data[-1]]
        yline = [value/1000 for value in data[-2]]
        v_yaw, d_steer = data[1], data[-3]

        x_start,x_end = plot.plot_get_x_range(xline, [yline, v_yaw, d_steer], 
            xlabel='x:longitudinal m', ylabel='y:lateral m', title='state',
            legend=['lateral m','yaw rad/s', 'steer rad'])

        self.vars['xdis_start'].set(x_start)
        self.vars['xdis_end'].set(x_end)
        self.print('\n截取完成\n')


if __name__=='__main__':
    
    logging.basicConfig(level=logging.INFO)
    logger.info('start')
    PostHandleSUi('数据处理-蛇行试验').run()