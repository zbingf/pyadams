"""

    提载程序计算
    合力计算
"""

from pyadams.ui import tkui, tk_reqcomp
from pyadams.car import post_force_load

import pysnooper
import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)

class ForceCalUi(tkui.TkUi):

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

        self.frame_entry({
            'frame':'n_start', 'var_name':'n_start', 'label_text':'res起始位置\nv or v1,v2,...',
            'label_width':20, 'entry_width':30,
            })

        self.frame_entry({
            'frame':'n_end', 'var_name':'n_end', 'label_text':'res终止位置\nNone or v or v1,v2,...',
            'label_width':20, 'entry_width':30,
            })

        self.frame_button({
            'frame':'reqcomp_ui',
            'button_name':'reqs comps 辅助生成',
            'button_width':30,
            'func':self.fun_reqcomp_ui,
            })

        self.frame_savepath({
            'frame' : 'csv_path', 'var_name':'csv_path', 'path_name' : 'csv file',
            'path_type' : '.csv', 'button_name' : 'csv save',
            'button_width' : 15, 'entry_width' : 30,
            })

        self.frame_radiobuttons({
            'frame':'cal_type',
            'var_name':'cal_type',
            'texts':['合力计算-客车', '分力计算-卡车'],
            })

        self.frame_radiobuttons({
            'frame':'force_type',
            'var_name':'force_type',
            'texts':['request包含力矩数据-6分力', '不包含力矩数据-3分力'],
            })

        self.frame_checkbutton({
            'frame':'isShow',
            'var_name':'isShow',
            'check_text':'是否显示力值图片',
            })
        
        self.frame_check_entry({
            'frame':'isStatic', 'check_text':'静载-位置截取', 
            'check_var':'isStatic', 'entry_var':'locs',
            'entry_width':30,
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

        self.vars['isShow'].set(True)
        self.vars['locs'].set('-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1')
        self.vars['n_start'].set(5)
        self.vars['n_end'].set(None)
        #self.run()

    # @pysnooper.snoop()
    def fun_run(self):
        params = self.get_vars_and_texts()

        file_paths = params['res_files']
        reqs       = params['reqs']
        comps      = params['comps']
        csv_path   = params['csv_path']
        isShow     = params['isShow']
        n_start    = params['n_start']
        n_end      = params['n_end']
        # print(params['cal_type'])

        if params['cal_type'] == 1:
            # 合力计算
            isComponent = False
        else:
            # 分力计算
            isComponent = True

        if params['force_type'] == 1:
            # 六分力 
            force_type = 6
        else:
            # 三分力
            force_type = 3

        if isinstance(file_paths,str):
            file_paths = [file_paths]
        else:
            file_paths = [file_path for file_path in file_paths if file_path]

        # --------------------------
        # 输入数据
        # force_type = 6
        # file_paths = [r'..\code_test\post_force_ori_load\GB_T_crc.res',
        #   r'..\code_test\post_force_ori_load\GB_T_s.res']
        # reqs = ['bkl_lca_front_force']*6 + ['bkr_lca_front_force']*6 +\
        #   ['bkl_lca_front_force']*6 + ['bkr_lca_front_force']*6
        # comps = [
        #   'fx_front','fy_front','fz_front','tx_front','ty_front','tz_front',
        #   'fx_front','fy_front','fz_front','tx_front','ty_front','tz_front',
        #   'fx_rear','fy_rear','fz_rear','tx_rear','ty_rear','tz_rear',
        #   'fx_rear','fy_rear','fz_rear','tx_rear','ty_rear','tz_rear',
        # ]
        # csv_path = r'..\code_test\post_force_ori_load\multi_cal.csv'
        # isComponent = True
        # isShow = True
        isStatic    = params['isStatic']
        locs        = params['locs']

        if isStatic: # 静态计算
            post_force_load.post_force_load(file_paths, reqs, comps, force_type, csv_path, 
                isShow=isShow, isComponent=isComponent, locs=locs, n_start=n_start, n_end=n_end)          
        else:
            post_force_load.post_force_load(file_paths, reqs, comps, force_type, csv_path, 
                isShow=isShow, isComponent=isComponent , n_start=n_start, n_end=n_end)

        self.print('计算完成')

    def fun_reqcomp_ui(self):
        tk_reqcomp.ReqComTxtUi('ReqsComps').run()


if __name__=='__main__':
    
    logging.basicConfig(level=logging.INFO)
    logger.info('start')
    ForceCalUi('载荷分解').run()