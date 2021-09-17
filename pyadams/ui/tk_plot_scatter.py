"""
    数据读取
    散点图
"""
import os
import logging
import tkinter as tk
from pyadams.file import result, file_edit
from pyadams.ui import tkui, tk_figure_show

DataModel = result.DataModel
DataModelScatter = result.DataModelScatter
ResultUi = tkui.ResultUi
dm_obj = DataModel('plot_scatter')


PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


class PlotScatterRsp(tkui.TkUi):

    def __init__(self, title, frame=None):
        super().__init__(title, frame=frame)

        res_frame = tk.LabelFrame(self.window, text='数据读取')
        res_loads = ['res_path', 'reqs', 'comps', 'nrange', 'nchannel']
        res_texts = {
                'res_path'   : '后处理文件',
                'reqs'       : 'reqs',
                'comps'      : 'comps',
                'nrange'     : '数据截取范围\n(起始,结束)',
                'nchannel'   : '通道截取\nNone或n1,n2,...',
                'label_text' : '备注: 计数起始值为0',
        }

        res_obj = ResultUi('ResultUi', res_frame, res_loads, res_texts)
        res_frame.pack()

        set_frame = tk.LabelFrame(self.window, text='配置')
        self.frame_savepath({
            'frame' : 'docx_path', 'var_name':'docx_path', 'path_name' : 'docx file',
            'path_type' : '.docx', 'button_name' : 'docx路径',
            'button_width' : 15, 'entry_width' : 30,
            }, frame=set_frame)

        self.frame_entry({
            'frame':'xchannels', 'var_name':'xchannels', 'label_text':'x通道选择',
            'label_width':20, 'entry_width':40,
            }, frame=set_frame)
        self.frame_entry({
            'frame':'ychannels', 'var_name':'ychannels', 'label_text':'y通道选择',
            'label_width':20, 'entry_width':40,
            }, frame=set_frame)

        self.frame_entry({
            'frame':'nums', 'var_name':'nums', 'label_text':'图片排列',
            'label_width':20, 'entry_width':40,
            }, frame=set_frame)

        set_frame.pack()

        self.frame_buttons_RWR({
            'frame'             : 'rrw',
            'button_run_name'   : '运行',
            'button_write_name' : '保存',
            'button_read_name'  : '读取',
            'button_width'      : 15,
            'func_run'          : self.fun_run,
            })

        self.frame_button({
            'frame':'call_fig',
            'button_name':'图像查看',
            'button_width':15,
            'func':self.fun_call_fig,
            }, frame=None)

        self.frame_note()
        self.sub_frames['res_obj'] = res_obj
        self.sub_frames['res_obj'].vars['nrange'].set(None)
        self.sub_frames['res_obj'].vars['nchannel'].set(None)
        self.vars['nums'].set('3,2')
        self.vars['ychannels'].set('None')

    def fun_call_fig(self):
        res_param = self.sub_frames['res_obj'].get_vars_and_texts()
        res_path  = res_param['res_path']
        nrange    = res_param['nrange']
        nchannel  = res_param['nchannel']
        reqs      = res_param['reqs']
        comps     = res_param['comps']

        name = 'res'
        dm_obj.new_file(res_path, name)
        dm_obj[name].set_reqs_comps(reqs, comps)
        dm_obj[name].set_line_ranges(nrange)
        dm_obj[name].set_select_channels(nchannel)
        dm_obj[name].read_file()

        data = dm_obj[name].get_data()
        titles = dm_obj[name].get_titles()

        data_dic = {}
        for title, line in zip(titles, data):
            data_dic[title] = line

        data_obj = tk_figure_show.TkFigureShowData(data_dic)
        tk_figure_show.TkFigureShow('TkFigureShow', data_obj).run()

        self.print('\n计算完成\n')

        return None


    def fun_run(self):

        self.print('\n开始计算\n')
        params = self.get_vars_and_texts()
        docx_path = params['docx_path']
        docx_path = os.path.abspath(docx_path)
        xchannels = params['xchannels']
        ychannels = params['ychannels']
        nums      = params['nums']

        res_param = self.sub_frames['res_obj'].get_vars_and_texts()
        res_path  = res_param['res_path']
        nrange    = res_param['nrange']
        nchannel  = res_param['nchannel']
        reqs      = res_param['reqs']
        comps     = res_param['comps']

        name = 'res'
        dm_obj.new_file(res_path, name)
        dm_obj[name].set_reqs_comps(reqs, comps)
        dm_obj[name].set_line_ranges(nrange)
        dm_obj[name].set_select_channels(nchannel)
        dm_obj[name].read_file()
        data = dm_obj[name].get_data()

        if xchannels==None:
            xchannels = [n for n in range(len(data))]

        if isinstance(xchannels, int): xchannels = [xchannels]

        params = {
            'docx_path': docx_path,
            'fig_path' : docx_path[:-5],
            'xchannels': xchannels,
            'ychannels': ychannels,
            'nums'     : nums,
        }

        dms_obj = DataModelScatter(dm_obj)
        pdf_paths = dms_obj.run('res', params)
        # for pdf_path in pdf_paths: os.popen(pdf_path)
        str_out = '\n'.join(pdf_paths)
        print(str_out)

        for pdf_path in pdf_paths:
            self.remove_png_file(pdf_path)

        self.print('\n计算完成\n')

        return None

    def remove_png_file(self, pdf_path):

        values     = self.get_vars_and_texts()
        path, name = os.path.split(pdf_path)
        file_edit.file_remove_pt(path, prefix=name[:-4], file_type='png')

        return None

if __name__=='__main__':

    PlotScatterRsp('PlotScatterRsp').run()
