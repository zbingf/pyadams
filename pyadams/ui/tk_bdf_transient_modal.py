"""
    模态叠加-数据前处理 UI
    
"""

from pyadams.datacal import plot
from pyadams.file import bdf_transient_modal
from pyadams.ui import tkui

import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)

# UI模块
class BdfTransientModalPreUi(tkui.TkUi):
    """
        模态叠加 bdf文件生成
        六分力
    """
    def __init__(self, title, frame=None):
        super().__init__(title, frame=frame)
        str_label = '-'*40

        # 删除采样频率设置 2021.8.28
        # self.frame_entry({
        #     'frame':'var_range','var_name':'samplerate','label_text':'采样频率 Hz',
        #     'label_width':15,'entry_width':30,
        #     })

        self.frame_loadpath({
            'frame':'rsp_path', 'var_name':'rsp_path', 'path_name':'rsp file',
            'path_type':'.rsp', 'button_name':'rsp文件',
            'button_width':15, 'entry_width':30,
            })

        self.frame_loadpath({
            'frame':'csv_path', 'var_name':'csv_path', 'path_name':'csv file',
            'path_type':'.csv', 'button_name':'csv硬点数据',
            'button_width':15, 'entry_width':30,
            })

        self.frame_savepath({
            'frame' : 'bdf_path', 'var_name':'bdf_path', 'path_name' : 'bdf file',
            'path_type' : '.bdf', 'button_name' : 'bdf文件',
            'button_width' : 15, 'entry_width' : 30,
            })


        self.frame_entry({
            'frame':'channel_set', 'var_name':'a_channel', 'label_text':'A-通道截取',
            'label_width':15, 'entry_width':30,
            })


        self.frame_entry({
            'frame':'ranges', 'var_name':'a_range', 'label_text':'A-数据截取(点)',
            'label_width':15, 'entry_width':30,
            })
        
        self.frame_checkbuttons({
            'frame' : 'plot1',
            'vars' : ['isShow', 'isTsPlot','isHzPlot'],
            'check_texts' : ['是否显示', '是否作时域图','是否作频域图'],
            })

        self.frame_entry({
            'frame':'plot1', 'var_name':'nums_plot', 'label_text':'|nums_plot|',
            'label_width':9, 'entry_width':10,
            })

        self.frame_entry({
            'frame':'plot1', 'var_name':'block_size', 'label_text':'|block_size|',
            'label_width':9, 'entry_width':10,
            })

        self.frame_entry({
            'frame':'plot1', 'var_name':'hz_range', 'label_text':'|Hz_range|',
            'label_width':9, 'entry_width':10,
            })
        
        self.frame_entry({
            'frame':'plot3', 'var_name':'ylabels', 'label_text':'ylabels',
            'label_width':15, 'entry_width':20,     
            })

        self.frame_savepath({
            'frame' : 'fig_path', 'var_name':'fig_path', 'path_name' : 'fig file',
            'path_type' : '.png', 'button_name' : '图片路径',
            'button_width' : 15, 'entry_width' : 30,
            })

        self.frame_entry({
            'frame':'fig_path', 'var_name':'size_gain', 'label_text':'图片尺寸比例',
            'label_width':15, 'entry_width':10,     
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

        # 初始化设置
        self.vars['a_channel'].set('None')
        self.vars['block_size'].set('1024')
        self.vars['nums_plot'].set('2,3')
        self.vars['hz_range'].set('0,50')
        self.vars['a_range'].set('None,None')
        # self.vars['samplerate'].set('256')
        self.vars['ylabels'].set('None')
        self.vars['size_gain'].set('0.8')

    def fun_run(self):
        """
            运行按钮调用函数
            主程序
        """
        # 获取界面数据
        params = self.get_vars_and_texts()
        logger.info(f'params数据:\n{params}\n')

        obj = bdf_transient_modal.BdfTransientModalPre(params['bdf_path'], params['csv_path'], 
            params['rsp_path'], 
            nranges=params['a_range'], channels=params['a_channel'])
        
        data_a = obj.data

        if params['ylabels'] == None:
            y_labels = obj.rsp_names

        samplerate = obj.samplerate

        # 作图
        figobj = plot.FigPlot()
        figobj.set_figure(nums=params['nums_plot'], size_gain=params['size_gain'])
        if params['isTsPlot']:
            figobj.plot_ts(data_a)
            figobj.set_ylabel(y_labels, 'ts')
            figobj.set_xlabel(['loc']*len(y_labels), 'ts')
            figobj.updata('ts')
        if params['isHzPlot']:
            figobj.plot_hz(data_a, samplerate, params['block_size'], params['hz_range'])
            figobj.set_ylabel(y_labels, 'hz')
            figobj.set_xlabel(['loc']*len(y_labels), 'hz')
            figobj.updata('hz')

        figobj.save(params['fig_path'][:-4])
        if params['isShow']:
            figobj.show()


        self.print('计算完成\n生成bdf 及 fem格式文件')
        
        return True

if __name__ == '__main__':
    
    logging.basicConfig(level=logging.INFO)
    logger.info('start')
    
    # Ui测试
    BdfTransientModalPreUi('Bdf').run()






