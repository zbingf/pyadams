"""
    tk_result_compare
"""
import tkinter.filedialog
import tkinter.messagebox
import tkinter as tk
import json
import os

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

        self.frame_radiobuttons({
            'frame':'pdfType', 'var_name':'pdfType',
            'texts':['pdf-详细', 'pdf-简化']
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

        data_obj['a_result'].set_line_ranges(values['a_result']['nrange'])
        data_obj['b_result'].set_line_ranges(values['b_result']['nrange'])

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

        dmc_obj = DataModelCompare(data_obj)

        params = {
            'block_size': {'u':block_size[0], 'l':block_size[1]},
            'hz_range'  : hz_range,
            'docx_path' : values['current']['docx_path'],
            'fig_path'  : values['current']['docx_path'][:-5],
            'nums'      : [3,2],
        }

        self.print('开始对比-创建pdf文件')
        pdf_path = dmc_obj.run('a_result', 'b_result', params, pdfType=values['current']['pdfType'])
        
        os.popen(pdf_path)
        # print(pdf_path)
        dmc_obj.remove_figure_files(dmc_obj.set_key('a_result', 'b_result'))
        str_pdfpath = '\n'.join(os.path.split(pdf_path))
        self.print(f'计算完成\n pdf路径:\n{str_pdfpath}')
        
        return None

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    # logger.info('start')
    
    # ResultUi('ResultUi').run()

    ResultCompareUi('ResultCompareUi').run()

