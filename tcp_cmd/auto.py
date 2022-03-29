"""
    AUTO
    
"""
# 标准库
import os
import time
import tkinter.messagebox
import logging


# 自建库
import tcp_cmd_fun as tcmdf
import tcp_car
import tcp_car_brake
import tcp_car_static
import tcp_car_spring_preload
import post_car_brake
import post_car_static

import office_docx
WordEdit = office_docx.WordEdit


# ----------
logger = logging.getLogger('auto')
logger.setLevel(logging.DEBUG)
is_debug = True

# ----------
FILEDIR = os.path.dirname(os.path.abspath(__file__))
AUTO_SET_PATH = os.path.abspath(os.path.join(FILEDIR, '00_set/auto_set.json'))

json_read = tcp_car.json_read
AUTO_SET = json_read(AUTO_SET_PATH)


get_cur_time = lambda: time.strftime('%Y%m%d_%H_%M', time.localtime(time.time()))


def parse_path(path):
    """
        路径处理
            #model_name# : 模型名称
            #time# : 当前时间
    """
    new_path = path
    keys = ['#model_name#', '#time#']
    for key in keys:
        if key not in new_path: continue

        if '#model_name#'==key: new_str = tcmdf.get_current_model()
        if '#time#'==key: new_str = get_cur_time()
        new_path = new_path.replace(key, new_str)

    return new_path


def set_new_path(path):
    """
        若文件存在则加后缀
    """
    n = 0
    cur_path = path
    while True:
        if os.path.exists(cur_path):
            n += 1
            file_type = path.split('.')[-1]
            cur_path = '.'.join(path.split('.')[:-1]) + f'_{n}.{file_type}'
        else:
            break

    return cur_path


def get_file_type(path):
    return path.split('.')[-1]


def remove_figs(figs):
    for fig_path in figs:
        os.remove(fig_path)


class AutoCur:
    """
        当前model的控制类      
    """
    def __init__(self):
        pass
        self.word_edits = [] # 存放word编辑数据

    def sim_static(self, **params_replace):
        """
            static 静态 仿真
        """
        self.result_static = tcp_car_static.main_cur_static(**params_replace)

    def sim_brake(self, **params_replace):
        """
            brake仿真
        """
        self.result_brake = tcp_car_brake.main_cur_brake(**params_replace)

    def sim_spring_preload(self, **params_replace):
        """
            弹簧预载调整
            static 仿真
                + spring preload edit
        """
        self.result_spring_preload = tcp_car_spring_preload.main_cur_static_preload(**params_replace)
        res_path = self.result_spring_preload['res_path']
        # 直接调用现成后处理文件
        self.result_static = tcp_car_static.main_cur_static(res_path, **params_replace)

    def post_static_list(self):
        """
            后处理
            static数据编辑目标
        """
        r_strs = post_car_static.post_car_static(self.result_static)    
        self.word_edits.append(r_strs)

    def post_brake_list(self):
        """ 
            后处理
            brake数据编辑目标
        """
        r_figs, r_strs = post_car_brake.post_car_brake(self.result_brake)
        self.word_edits.append(r_figs)
        self.word_edits.append(r_strs)

    def post_spring_preload(self):
        """
            后处理
            spring preload
        """
        cmd_path = AUTO_SET['auto_spring_preload']['cmd_path']
        with open(cmd_path, 'w') as f:
            f.write(self.result_spring_preload['cmd'])

    def word_edit(self, word_path, new_word_path):
        """
            文档编辑
        """
        # self.word_path = word_path
        # self.new_word_path = new_word_path

        word_obj = WordEdit(word_path)
        for edit in self.word_edits:
            word_obj.replace_edit(*edit)    

        word_obj.save(new_word_path)
        word_obj.close()

    def remove_figs(self):
        """
            删除图片
        """
        fig_types = AUTO_SET['figure_types']
        fig_types = [v.strip().lower() for v in fig_types]

        target_paths = []
        for edit in self.word_edits:
            for line in edit[1]:
                if os.path.exists(line):
                    # 文件存在
                    file_type = get_file_type(line)
                    if file_type.lower() in fig_types:
                        target_paths.append(line)

        remove_figs(target_paths)

    def record_static(self, record_path, record_state=1):
        """
            csv数据记录
        """
        if record_state==0: # 不记录
            return None
        elif record_state==1: # 记录
            pass
        elif record_state==2: # 询问
            if not tkinter.messagebox.askyesno('提问', '是否上传整车静态数据?'):
                return None

        post_car_static.csv_post_static_print(record_path, self.result_static)
        return True


def auto_brake(record_state=1, params_static_replace=None):
    """
        制动稳定性分析
    """
    if is_debug: logger.debug("Call auto_brake")

    if not tcmdf.set_current_asy_with_event_class('__MDI_SDI_TESTRIG'): 
        raise "current model not asy SDI"

    # ---------
    word_path = AUTO_SET['auto_brake']['word_path']
    if is_debug: logger.debug("word_path: {word_path}")

    new_word_path = parse_path(AUTO_SET['auto_brake']['new_word_path'])
    new_word_path = set_new_path(new_word_path)
    if is_debug: logger.debug("new_word_path: {new_word_path}")

    result_path = parse_path(AUTO_SET['auto_brake']['result_path'])
    result_path = set_new_path(result_path)
    result_data_path = parse_path(AUTO_SET['auto_brake']['result_data_path'])
    result_data_path = set_new_path(result_data_path)
    if is_debug: logger.debug("result_path: {result_path}")
    if is_debug: logger.debug("result_data_path: {result_data_path}")

    static_record_path = parse_path(AUTO_SET['auto_static']['record_path'])
    if is_debug: logger.debug("static_record_path: {static_record_path}")

    obj = AutoCur()
    if params_static_replace==None:
        obj.sim_static()
    else:
        obj.sim_static(**params_static_replace)
    obj.sim_brake()
    obj.post_static_list()
    obj.post_brake_list()

    if is_debug: logger.debug("word_edit")
    obj.word_edit(word_path, new_word_path)
    obj.record_static(static_record_path, record_state)
    obj.remove_figs()

    if tkinter.messagebox.askyesno('提问', '是否保存brake result?'):
        tcp_car.save_var(result_path, obj.result_brake)
        tcp_car.save_var(result_data_path, tcp_car_brake.parse_brake_result(obj.result_brake))

    if is_debug: logger.debug("End auto_brake")


def auto_static_only(record_state=1, **params_static_replace):
    """ 
    params_static
        自动
        静态分析
    """
    if is_debug: logger.debug("Call auto_static_only")

    if not tcmdf.set_current_asy_with_event_class('__MDI_SDI_TESTRIG'): 
        raise "current model not asy SDI"

    # ---------
    static_record_path = parse_path(AUTO_SET['auto_static']['record_path'])
    if is_debug: logger.debug(f"static_record_path: {static_record_path}")

    obj = AutoCur()
    obj.sim_static(**params_static_replace)
    obj.record_static(static_record_path, record_state)
    if is_debug: logger.debug("End auto_static_only")


def auto_spring_preload(record_state=1, **params_static_replace):
    """
        自动
        静态分析-弹簧预载设置
    """
    if is_debug: logger.debug("Call auto_spring_preload")

    if not tcmdf.set_current_asy_with_event_class('__MDI_SDI_TESTRIG'): 
        raise "current model not asy SDI"

    # ---------
    static_record_path = parse_path(AUTO_SET['auto_static']['record_path'])
    if is_debug: logger.debug(f"static_record_path: {static_record_path}")

    obj = AutoCur()
    obj.sim_spring_preload(**params_static_replace)
    obj.post_spring_preload()
    obj.record_static(static_record_path, record_state)
    if is_debug: logger.debug("End auto_spring_preload")




if __name__=='__main__':
    pass

    log_format = '%(levelname)s : %(module)s : %(funcName)s : %(lineno)s : %(message)s'
    logging.basicConfig(format=log_format)
    help(logging)
    # auto_brake(1)
    # auto_static_only(1)
    # auto_spring_preload(1)

    # auto_brake(1, {'sim_type':'normal'})
    # auto_static_only(1, sim_type='normal')
    # auto_spring_preload(1, sim_type='normal')

    # result = tcp_car.read_var(r'D:\github\pyadams\tcp_cmd\02_result\auto_brake\result_MDI_Demo_Vehicle_20220326_15_37.brake')

    logging.shutdown()
    