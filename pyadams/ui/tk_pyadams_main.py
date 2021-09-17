"""
    tkinter UI界面
    主目录，调用各UI子程序
    
    包含：
        tk_adm_sim          仿真对比
        tk_force_cal        合力计算，工况集成，客车
        tk_force_cal_ori    分力计算，工况集成，卡车
        tk_reqcomp          注释
        tk_sus_ite          台架迭代
        
"""

from pyadams.ui import tkui
from pyadams.ui import tk_force_cal
from pyadams.ui import tk_reqcomp,          tk_sus_ites_threading
from pyadams.ui import tk_carpath_check,    tk_drv2cmd,             tk_adm_reqcheck
from pyadams.ui import tk_res_samplerate,   tk_res2csv,             tk_bdf_transient_modal
from pyadams.ui import tk_result_compare
from pyadams.ui import tk_post_handle_s,    tk_post_handle_crc,     tk_adm_sim
from pyadams.ui import tk_post_tilt,        tk_plot_scatter,        tk_adm_sim_car_post
from pyadams.ui import tk_adm_multirun_femfat_lab
import re
import tkinter as tk
from tkinter import ttk
import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


STR_UI = '''
tk_force_cal,           ForceCalUi,             计算-载荷分解
tk_sus_ites_threading,  SusIteSThreadingUi,     多线程文件迭代-悬架-拉线位移

tk_carpath_check,       CarPathCheckUi,         检测-Res-Car路径检测
tk_adm_reqcheck,        RMCheckUi,              检测-Adm-Request
tk_res_samplerate,      ResSamplerateUi,        检测-Res-采样频率

tk_reqcomp,             ReqComTxtUi,            数据转化-ReqsComps
tk_drv2cmd,             Drv2CmdUi,              数据转化-Drv转Cmd
tk_res2csv,             Res2CsvUi,              数据转化-Res转Csv

tk_result_compare,      ResultCompareUi,        数据对比-result-A/B
tk_plot_scatter,        PlotScatterRsp,         数据对比-散点图scatter

tk_bdf_transient_modal, BdfTransientModalPreUi, 模态叠加-BDF生成

tk_post_handle_s,       PostHandleSUi,          数据处理-蛇行试验
tk_post_handle_crc,     PostHandleCrcUi,        数据处理-稳态回转
tk_post_tilt,           PostTiltUi,             数据处理-静侧翻角


tk_adm_sim,             AdmSimCalUi,            AdmSimCal
tk_adm_sim_car_post,    AdmSimCalCarPostUi,     AdmSimCal-CarPos
tk_adm_multirun_femfat_lab, AdmFemfatLabNosieUi , Femfat-Lab白噪声
'''

tk_names, tk_uis, tk_titles = [], [], []
for line in STR_UI.split('\n'):
    line = re.sub(r'\s','',line)
    if line:
        name, ui, title = re.sub(r'\s','',line).split(',')
        tk_names.append(name)
        tk_uis.append(ui)
        tk_titles.append(title) # .ljust(40)
        # print(title.ljust(40)+'>')

# 函数生成
for tk_name, tk_title, tk_ui in zip(tk_names, tk_titles, tk_uis):
    # print(f"def {tk_name}_run(): {tk_name}.{tk_ui}('{tk_title}').run()")
    exec(f"def {tk_name}_run(): {tk_name}.{tk_ui}('{tk_title}').run()")



# 汇总UI界面
class TkMainUi(tkui.TkUi):
    """
        UI程序运行示例
    """
    def __init__(self, title ,tk_names , tk_titles):
        """
            title 标题
            tk_names
            tk_titles
        """
        super().__init__(title)
        # self.window.attributes("-alpha", 0.95) # 透明度
        self.window.geometry('500x700+200+200')
        self.window.resizable(False, False)   # 不可更改尺寸
        self.window.overrideredirect(True)    # 不显示标题栏
        self.window.configure(bg='white')
        self.window.wm_attributes('-transparentcolor', '#FFFFFF') # FFFFFF色设为透明

        self.left_click_mouse_X = tk.IntVar(self.window, value=0)
        self.left_click_mouse_Y = tk.IntVar(self.window, value=0)
        self.left_can_move      = tk.IntVar(self.window, value=0)

        frame_first  = tk.Frame(self.window, width='500', height='500', bg='#FFFFFF')
        frame_first.pack(expand=tk.NO)

        global_photo_1 = tk.PhotoImage(file=r'./README/test2.png').zoom(1)
        label_fig = tk.Label(frame_first, image=global_photo_1, width='500', height='500', bg='#FFFFFF')
        label_fig.image = global_photo_1
        label_fig.pack(expand=tk.NO)
        label_fig.place(relx=0, rely=0)# ,anchor="center"
        

        label_fig.bind('<Button-1>', self.onLeftButtonDown)
        label_fig.bind('<B1-Motion>', self.onLeftBUttonMove)
        label_fig.bind('<ButtonRelease-1>', self.onLeftButtonUp)
        label_fig.bind('<ButtonRelease-3>', self.onRightButtonUp)

        frame_second = tk.Frame(self.window, bg='#FFFFFF')
        frame_second.pack(expand=tk.YES, fill=tk.Y)
        frame_second.place(relx=0, rely=0.57) # ,anchor="center"
        

        row, col = 0, 0
        num = 2
        for tk_name, tk_title in zip(tk_names, tk_titles):
            if divmod(col, 2)[-1] == 0:
                row += 1
            col += 1
            frame_name = str(row)
            self.frame_button({
                    'frame':frame_name,
                    'button_name':tk_title,
                    'button_width':35,
                    'func':eval(f'{tk_name}_run')}, 
                    frame=frame_second)


    def onLeftButtonDown(self, event):
        self.left_click_mouse_X.set(event.x)
        self.left_click_mouse_Y.set(event.y)
        self.left_can_move.set(1)

    def onLeftButtonUp(self, event):
        self.left_can_move.set(0)

    def onLeftBUttonMove(self, event):
        if self.left_can_move.get() == 0:
            return

        newX = self.window.winfo_x() + (event.x-self.left_click_mouse_X.get())
        newY = self.window.winfo_y() + (event.y-self.left_click_mouse_Y.get())
        g  = f'500x700+{newX}+{newY}'
        self.window.geometry(g)

    def onRightButtonUp(self, event):

        self.window.destroy()

            

def main_run():

    logging.basicConfig(level=logging.INFO, filename=LOG_PATH, filemode='w')
    logger.info('Start')

    # 运行程序
    TkMainUi('汇总UI', tk_names, tk_titles).run()


if __name__=='__main__':
    

    main_run()

