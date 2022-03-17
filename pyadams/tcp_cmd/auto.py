"""
    AUTO
    
"""

from pyadams.tcp_cmd import \
    tcp_car, \
    tcp_car_brake, \
    tcp_car_static_only, \
    tcp_car_spring_preload, \
    post_brake, \
    post_static_only

from pyadams.file import office_docx
WordEdit = office_docx.WordEdit

import os
import tkinter.messagebox

json_read = tcp_car.json_read
AUTO_SET = json_read('auto.json')


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

    # static仿真
    def sim_static(self):
        # 静态计算
        self.result_static = tcp_car_static_only.main_cur_static_only()

    # brake仿真
    def sim_brake(self):

        self.result_brake = tcp_car_brake.sim_cur_brake()

    # static_preload
    def sim_spring_preload(self):
        
        self.result_spring_preload = tcp_car_spring_preload.main_cur_static_preload()
        res_path = self.result_spring_preload['res_path']
        
        self.result_static = tcp_car_static_only.main_cur_static_only(res_path)

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
    def record_static(self):

        post_static_only.csv_post_static_only_print(self.result_static)

    # 提问是否-csv数据记录
    def ask_record_static(self):
        if tkinter.messagebox.askyesno('提问', '是否上传整车静态数据?'):
            self.record_static()


def auto_brake():

    word_path = AUTO_SET['auto_brake']['word_path']
    new_word_path = set_new_path(AUTO_SET['auto_brake']['new_word_path'])

    obj = AutoCur()
    obj.sim_static()
    obj.sim_brake()
    obj.post_static_list()
    obj.post_brake_list()
    obj.word_edit(word_path, new_word_path)
    obj.ask_record_static()
    obj.remove_figs()


def auto_static_only():
    obj = AutoCur()
    obj.sim_static()
    obj.ask_record_static()


def auto_spring_preload():
    obj = AutoCur()
    obj.sim_spring_preload()
    obj.post_spring_preload()
    obj.ask_record_static()



# auto_brake()
# auto_static_only()
auto_spring_preload()