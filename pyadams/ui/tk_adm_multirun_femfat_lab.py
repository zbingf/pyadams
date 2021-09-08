"""
    adm文件 批量计算
    多线程计算
    用于FEMFAT-LAB白噪声
"""

from pyadams.ui import tkui
from pyadams.view import adm_multirun_femfat_lab
import tkinter as tk
ResultUi = tkui.ResultUi

class AdmFemfatLabNosieUi(tkui.TkUi):

    def __init__(self, title, frame=None):

        super().__init__(title, frame=frame)

        self.frame_loadpath({
            'frame':'adm_path', 'var_name':'adm_path', 'path_name':'adm file',
            'path_type':'.adm', 'button_name':'adm load',
            'button_width':15, 'entry_width':30,
            })

        self.frame_savepath({
            'frame' : 'csv_path', 'var_name':'csv_path', 'path_name' : 'csv file',
            'path_type' : '.csv', 'button_name' : 'csv save',
            'button_width' : 15, 'entry_width' : 30,
            })

        self.frame_entry({
            'frame':'suffix', 'var_name':'suffix', 'label_text':'adm后缀配置',
            'label_width':15, 'entry_width':30,
            })

        self.frame_entry({
            'frame':'simtime', 'var_name':'simtime', 'label_text':'仿真时长s',
            'label_width':15, 'entry_width':30,
            })

        self.frame_entry({
            'frame':'samplerate', 'var_name':'samplerate', 'label_text':'采样频率Hz',
            'label_width':15, 'entry_width':30,
            })

        self.frame_entry({
            'frame':'n_load', 'var_name':'n_load', 'label_text':'白噪声-adm数量',
            'label_width':15, 'entry_width':30,
            })

        self.frame_entry({
            'frame':'max_threading', 'var_name':'max_threading', 'label_text':'最大允许线程数',
            'label_width':15, 'entry_width':30,
            })

        self.frame_entry({
            'frame':'simlimit', 'var_name':'simlimit', 'label_text':'允许计算时长min',
            'label_width':15, 'entry_width':30,
            })

        self.frame_checkbuttons({
            'frame':'check_1',
            'vars':['isRead'],
            'check_texts':['读取-生成-CSV'],
            })

        self.frame_radiobuttons({
            'frame':'version',
            'var_name':'version',
            'texts':['2017.2', '2019'],
            })

        result_frame = tk.LabelFrame(self.window, text='后处理')
        result_loads = ['reqs', 'comps', 'nrange', 'nchannel']
        result_texts = {
            'reqs'      : 'reqs',
            'comps'     : 'comps',
            'nrange'    : '数据截取范围\n(起始,结束)',
            'nchannel'  : '通道截取\nNone或n1,n2,...',
        }

        result_obj = ResultUi('result', result_frame, result_loads, result_texts)
        result_frame.pack()
        self.sub_frames['result'] = result_obj

        self.frame_buttons_RWR({
            'frame' : 'rrw',
            'button_run_name' : '运行',
            'button_write_name' : '保存',
            'button_read_name' : '读取',
            'button_width' : 15,
            'func_run' : self.fun_run,
            })

        self.frame_note()

        # =====================================
        self.vars['suffix'].set('_noise_ch{}.adm')
        self.vars['simlimit'].set(60)
        self.vars['max_threading'].set(5)
        self.vars['version'].set(1)

    def fun_run(self):

        self.print('\n\n计算中...\n\n')
        values = self.get_vars_and_texts()
        values.update(self.sub_frames['result'].get_vars_and_texts())

        values['version'] = '2017.2' if values['version'] == 1 else '2019'

        adm_multirun_femfat_lab.multirun_femfat_lab(values, values['isRead'])

        self.print('\n\n计算结束\n\n')

        return None

if __name__ == '__main__':
    AdmFemfatLabNosieUi('AdmFemfatLabNosieUi').run()



