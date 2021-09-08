"""
    车辆行驶路径检查

    
    主要参数
        res文件路径
        req
        comp
    
    主要用途：
        显示指定位置车辆行驶路径 图像

"""

from pyadams.file import result
from pyadams.datacal import plot
from pyadams.ui import tkui
TkUi = tkui.TkUi
DataModel = result.DataModel



import os
import os.path
import logging
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


class CarPathCheckUi(TkUi):
    """
    """
    def __init__(self, title, frame=None):
        super().__init__(title, frame=frame)

        self.frame_loadpaths({
            'frame':'res_files', 'var_name':'res_files', 'path_name':'res files',
            'path_type':'.res', 'button_name':'res files',
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


        self.vars['reqs'].set('chassis_displacements,chassis_displacements')
        self.vars['comps'].set('longitudinal,lateral')

        self.frame_savepath({
            'frame' : 'fig_path', 'var_name':'fig_path', 'path_name' : 'fig file',
            'path_type' : '.png', 'button_name' : '保存图片路径',
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

        self.frame_note()

    def fun_run(self):
        params = self.get_vars_and_texts()
        file_paths, reqs, comps, fig_path = params['res_files'], params['reqs'], params['comps'], params['fig_path']
        if isinstance(file_paths, str) : file_paths = [file_paths]
        xs, ys, xlabels = [], [], []
        for path in file_paths:
            name = os.path.basename(path)
            dataobj = DataModel('tk_carpath_check')
            dataobj.new_file(path, name)
            dataobj[name].set_reqs_comps(reqs, comps)
            dataobj[name].set_line_ranges([10,None])
            dataobj[name].read_file_faster()
            data = dataobj[name].get_data()

            xs.append(data[0])
            ys.append(data[1])
            xlabels.append(name+'\n纵向位移 mm')

        # 作图
        figobj = plot.FigPlot()
        figobj.set_figure(nums=[3, 4], size_gain=0.8)
        figobj.plot_ts(ys, xs)
        figobj.set_ylabel(['侧向位移mm']*len(xlabels), 'ts')
        figobj.set_xlabel(xlabels, 'ts')
        figobj.updata('ts')
        figobj.save(fig_path[:-4])
        figobj.show()


        self.print('计算完成')

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    logger.info('start')
    CarPathCheckUi('Car路径检测').run()