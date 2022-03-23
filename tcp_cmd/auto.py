"""
    AUTO
    
"""
# 标准库
import os
import tkinter.messagebox
import logging

# 自建库
import tcp_car
import tcp_car_brake
import tcp_car_static_only
import tcp_car_spring_preload
import post_brake
import post_static_only

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

# ----------
log_format = '%(levelname)s : %(module)s : %(funcName)s : %(lineno)s : %(message)s'
# logging.basicConfig(filename='mylog.log', level=logging.DEBUG, filemode='w', format=log_format)
# logging.basicConfig(level=logging.DEBUG, format=log_format)
logging.basicConfig(format=log_format)

# 若文件存在则家后缀
def set_new_path(path):
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


# 当前model的控制类
class AutoCur:

    def __init__(self):
        pass
        self.word_edits = [] # 存放word编辑数据

    # static 仿真
    def sim_static(self, **params_replace):
        # 静态计算
        self.result_static = tcp_car_static_only.main_cur_static_only(**params_replace)

    # brake仿真
    def sim_brake(self):

        self.result_brake = tcp_car_brake.sim_cur_brake()

    # static 仿真 spring preload
    def sim_spring_preload(self, **params_replace):
        
        self.result_spring_preload = tcp_car_spring_preload.main_cur_static_preload(**params_replace)
        res_path = self.result_spring_preload['res_path']
        
        self.result_static = tcp_car_static_only.main_cur_static_only(res_path, **params_replace)

    # static数据编辑目标
    def post_static_list(self):

        r_strs = post_static_only.post_static_only(self.result_static)    
        self.word_edits.append(r_strs)

    # brake数据编辑目标
    def post_brake_list(self):

        r_figs, r_strs = post_brake.post_brake(self.result_brake)
        self.word_edits.append(r_figs)
        self.word_edits.append(r_strs)

    # spring preload 
    def post_spring_preload(self):

        cmd_path = AUTO_SET['auto_spring_preload']['cmd_path']
        with open(cmd_path, 'w') as f:
            f.write(self.result_spring_preload['cmd'])


    # 文档编辑
    def word_edit(self, word_path, new_word_path):
        # self.word_path = word_path
        # self.new_word_path = new_word_path

        word_obj = WordEdit(word_path)
        for edit in self.word_edits:
            word_obj.replace_edit(*edit)    

        word_obj.save(new_word_path)
        word_obj.close()

    # 删除图片
    def remove_figs(self):
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

    # csv数据记录
    def record_static(self, record_state=1):
        if record_state==0: # 不记录
            return None
        elif record_state==1: # 记录
            pass
        elif record_state==2: # 询问
            if not tkinter.messagebox.askyesno('提问', '是否上传整车静态数据?'):
                return None

        post_static_only.csv_post_static_only_print(self.result_static)
        return True

    # # 提问是否-csv数据记录
    # def ask_record_static(self):
    #     if tkinter.messagebox.askyesno('提问', '是否上传整车静态数据?'):
    #         self.record_static()


def auto_brake(record_state=1, params_static_replace=None):
    """
        制动稳定性分析
    """
    if is_debug: logging.debug("Call auto_brake")
    word_path = AUTO_SET['auto_brake']['word_path']
    new_word_path = set_new_path(AUTO_SET['auto_brake']['new_word_path'])

    obj = AutoCur()
    if params_static_replace==None:
        obj.sim_static()
    else:
        obj.sim_static(**params_static_replace)
    obj.sim_brake()
    obj.post_static_list()
    obj.post_brake_list()
    if is_debug: logging.debug("word_edit")
    obj.word_edit(word_path, new_word_path)
    obj.record_static(record_state)
    obj.remove_figs()
    if is_debug: logging.debug("End auto_brake")


def auto_static_only(record_state=1, **params_replace):
    """
        自动
        静态分析
    """
    if is_debug: logging.debug("Call auto_static_only")
    obj = AutoCur()
    obj.sim_static(**params_replace)
    obj.record_static(record_state)
    if is_debug: logging.debug("End auto_static_only")


def auto_spring_preload(record_state=1, **params_replace):
    """
        自动
        静态分析-弹簧预载设置
    """
    if is_debug: logging.debug("Call auto_spring_preload")
    obj = AutoCur()
    obj.sim_spring_preload(**params_replace)
    obj.post_spring_preload()
    obj.record_static(record_state)
    if is_debug: logging.debug("End auto_spring_preload")


# import coverage
# cov = coverage.coverage()
# cov.start()

auto_brake(1, {'sim_type':'normal'})
auto_static_only(1, sim_type='normal')
auto_spring_preload(1, sim_type='normal')

# cov.stop()
# cov.save()

# import sys
# calc_type = sys.argv[1].strip().lower()
# params = sys.argv[2].strip().lower()

# if calc_type == 'auto_brake':
#     auto_brake(1, {'sim_type':params})

# if calc_type == 'auto_static_only':
#     auto_static_only(1, sim_type=params)

# if calc_type == 'auto_spring_preload':
#     auto_spring_preload(1, sim_type=params)

logging.shutdown()