"""
    tk_result_compare
    后处理数据对比评估
"""
import tkinter.filedialog
import tkinter.messagebox
import tkinter as tk
import json
import os
import matplotlib.pyplot as plt

from pyadams.datacal import plot
from pyadams.file import result
from pyadams.ui import tkui
DataModel = result.DataModel
DataModelCompare = result.DataModelCompare

import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)

# UI模块
class ResultCompareUi(tkui.TkUi):
    """
        AdmSim 主程序
    """
    def __init__(self, title, frame=None):
        super().__init__(title, frame=frame)

        result_frame = tk.Frame(self.window)
        
        a_frame = tk.LabelFrame(result_frame, text='A 分子 Result')
        b_frame = tk.LabelFrame(result_frame, text='B 分母 Result')
        a_obj = tkui.ResultUi('a_obj', a_frame)
        b_obj = tkui.ResultUi('a_obj', b_frame)
        a_frame.pack(side='left')
        b_frame.pack(side='right')
        result_frame.pack()

        result_frame2 = tk.LabelFrame(self.window, text='A')
        result_frame2.pack(side='bottom')

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

        self.frame_button({'frame':'set_type', 'button_name':'读取确认截取范围', 'button_width':15, 'func':self.fun_get_xrange, }, frame=None)

        self.frame_radiobuttons({
            'frame':'set_type', 'var_name':'pdfType',
            'texts':['pdf-详细', 'pdf-简化', 'pdf-详细-2', 'pdf-简化-2']
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

        self.frame_ui_runs()


        self.sub_frames = {'a_result':a_obj, 'b_result':b_obj}

        self.vars['hz_range'].set('0,50')
        self.vars['block_size'].set('1024,1024')

        self.sub_frames['a_result'].vars['nrange'].set('None')
        self.sub_frames['a_result'].vars['nchannel'].set('None')
        self.sub_frames['b_result'].vars['nrange'].set('None')
        self.sub_frames['b_result'].vars['nchannel'].set('None')


    def fun_run(self):

        self.print('开始计算')

        values, block_size, hz_range = self.fun_data_read()
        data_obj = self.data_obj
        dmc_obj = DataModelCompare(data_obj)

        params = {
            'block_size': {'u':block_size[0], 'l':block_size[1]},
            'hz_range'  : hz_range,
            'docx_path' : values['current']['docx_path'],
            'fig_path'  : values['current']['docx_path'][:-5],
            'nums'      : [3,2],
        }
        # print(values['current']['pdfType'])
        self.print('开始对比-创建pdf文件')
        pdf_path = dmc_obj.run('a_result', 'b_result', params, pdfType=values['current']['pdfType'])
        
        os.popen(pdf_path)
        # print(pdf_path)
        dmc_obj.remove_figure_files(dmc_obj.set_key('a_result', 'b_result'))
        str_pdfpath = '\n'.join(os.path.split(pdf_path))
        self.print(f'计算完成\n pdf路径:\n{str_pdfpath}')
        
        return None

    def fun_data_read(self, read_type=0):
        """
            read_type ： 计算读取用

        """
        # 数据读取

        values = {}
        for key in self.sub_frames:
            values[key] = self.sub_frames[key].get_vars_and_texts()
        values['current'] = self.get_vars_and_texts()
        block_size = values['current']['block_size']
        hz_range   = values['current']['hz_range']

        data_obj = DataModel('tk_result_compare')
        data_obj.new_file(values['a_result']['res_path'], 'a_result')
        data_obj.new_file(values['b_result']['res_path'], 'b_result')

        data_obj['a_result'].set_reqs_comps(values['a_result']['reqs'], values['a_result']['comps'])
        data_obj['b_result'].set_reqs_comps(values['b_result']['reqs'], values['b_result']['comps'])

        data_obj['a_result'].set_select_channels(values['a_result']['nchannel'])
        data_obj['b_result'].set_select_channels(values['b_result']['nchannel'])

        if read_type == 0:
            data_obj['a_result'].set_line_ranges(values['a_result']['nrange'])
            data_obj['b_result'].set_line_ranges(values['b_result']['nrange'])
        else:
            data_obj['a_result'].set_line_ranges(None)
            data_obj['b_result'].set_line_ranges(None)

        if data_obj.file_types['a_result'] in ['req','res']:
            data_obj['a_result'].read_file_faster()
        else:
            data_obj['a_result'].read_file()

        if data_obj.file_types['b_result'] in ['req','res']:
            data_obj['b_result'].read_file_faster()
        else:
            data_obj['b_result'].read_file()

        data_a = data_obj['a_result'].get_data()
        data_b = data_obj['b_result'].get_data()

        self.data_a = data_a
        self.data_b = data_b
        self.data_obj = data_obj

        return values, block_size, hz_range

    def fun_get_xrange(self):

        values, block_size, hz_range = self.fun_data_read(1)
        data_a = self.data_a
        data_b = self.data_b

        x_a = [value for value in range(len(data_a[0]))]
        x_b = [value for value in range(len(data_b[0]))]

        a_nrange = values['a_result']['nrange']
        b_nrange = values['b_result']['nrange']
        if isinstance(a_nrange, list):
            x_start_a, x_end_a = a_nrange          
        else:
            x_start_a, x_end_a = None, None

        if isinstance(b_nrange, list):
            x_start_b, x_end_b = b_nrange
        else:
            x_start_b, x_end_b = None, None
        
        while True:
            x_start_a, x_end_a = plot.plot_get_x_range(x_a, [data_a[0]], 
                xlabel='x:n', ylabel='y select 1', title='Data A',
                legend=['Data-A select 0'], x_start_init=x_start_a, x_end_init=x_end_a)
            if x_start_a == None: x_start_a = 0
            if x_end_a == None: x_end_a = len(x_a)-1
            x_start_a, x_end_a = int(round(x_start_a)), int(round(x_end_a))

            x_start_b, x_end_b = plot.plot_get_x_range(x_b, [data_b[0]], 
                xlabel='x:n', ylabel='y select 1', title='Data B',
                legend=['Data-B select 0'], x_start_init=x_start_b, x_end_init=x_end_b)
            if x_start_b == None: x_start_b = 0
            if x_end_b == None: x_end_b = len(x_b)-1
            x_start_b, x_end_b = int(round(x_start_b)), int(round(x_end_b))


            fig_obj = plt.figure('tk_result_compare_get_range', clear=True)
            ax1 = fig_obj.add_subplot(1,1,1)
            ax1.plot(range(len(x_a[x_start_a:x_end_a])), data_a[0][x_start_a:x_end_a], 'r')
            ax1.plot(range(len(x_b[x_start_b:x_end_b])), data_b[0][x_start_b:x_end_b], 'b')
            plt.show()

            if tkinter.messagebox.askyesno('提示', '是否确认截取范围'):
                break

        # print(x_start_a, x_end_a)
        # print(x_start_b, x_end_b)
        self.sub_frames['a_result'].vars['nrange'].set(f'{x_start_a},{x_end_a}')
        self.sub_frames['b_result'].vars['nrange'].set(f'{x_start_b},{x_end_b}')



if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    # logger.info('start')
    
    # ResultUi('ResultUi').run()

    ResultCompareUi('ResultCompareUi').run()

