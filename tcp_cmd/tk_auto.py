
# 标准库
import json
from pprint import pprint, pformat
import tkinter.messagebox

# 自建库
from tcp_car import json_read
from tkui import TkUi
from auto import (
    auto_brake,
    auto_static_only,
    auto_spring_preload
    )

def json_save(json_path, data):
    with open(json_path, 'w') as f:
        json.dump(data, f)
    return None


def test_json_file():
    """json文件读写测试"""
    json_path_template = './00_set/example_acar_full_brake_set.json'
    json_path_new = './00_set/acar_full_brake_set.json'
    data = json_read(json_path_template)
    print(data)
    json_save(json_path_new, data)


class TkAuto(TkUi):


    def __init__(self, title, frame=None):
        super().__init__(title, frame=frame)
        self.frame_label_only({
                'frame':'t0',
                'label_text': 'ADAMS command控制\n' \
                              '开启: command_server start\n' \
                              '关闭: command_server stop\n' \
                              '查看: command_server show',
                'label_width':15,
            })

        self.frame_label_only({
                'frame':'t1',
                'label_text':'-'*30+'准静态计算设置'+'-'*30,
                'label_width':15,
            })

        self.frame_label_only({
                'frame':'static_sim_type',
                'label_text':'静态仿真-选择',
                'label_width':15,
            })

        self.frame_radiobuttons({
            'frame':'static_sim_type',
            'var_name':'static_sim_type',
            'texts':['normal', 'settle'],
            })
        self.static_sim_type = {1:'normal', 2:'settle'}

        self.frame_label_only({
                'frame':'static_record_type',
                'label_text':'静态数据记录选择',
                'label_width':15,
            })

        self.frame_radiobuttons({
            'frame':'static_record_type',
            'var_name':'static_record_type',
            'texts':['不记录', '自动记录', '询问'],
            })
        self.static_record_type = {1:0, 2:1, 3:2,}


        # ---------------------
        self.frame_label_only({
                'frame':'t2',
                'label_text':'-'*30+'制动'+'-'*30,
                'label_width':15,
            })
        self.frame_button({
            'frame':'fun_auto_brake',
            'button_name':'制动-自动计算',
            'button_width':20,
            'func':self.fun_auto_brake, # 回调函数
            }, frame=None)

        # ---------------------
        self.frame_label_only({
                'frame':'t3',
                'label_text':'-'*30+'静态计算'+'-'*30,
                'label_width':15,
            })
        self.frame_button({
            'frame':'fun_auto_static_only',
            'button_name':'整车-static静态-计算',
            'button_width':20,
            'func':self.fun_auto_static_only, # 回调函数
            }, frame=None)

        # ---------------------
        self.frame_label_only({
                'frame':'t4',
                'label_text':'-'*30+'整车-spring预载'+'-'*30,
                'label_width':15,
            })
        self.frame_button({
            'frame':'fun_auto_spring_preload',
            'button_name':'整车-spring预载-计算',
            'button_width':20,
            'func':self.fun_auto_spring_preload, # 回调函数
            }, frame=None)

        # ---------------------
        self.frame_label_only({
                'frame':'t5',
                'label_text':'-'*70,
                'label_width':15,
            })

        self.frame_note()

        self.frame_buttons_RWR({
            'frame' : 'rrw',
            'button_run_name' : '运行',
            'button_write_name' : '保存',
            'button_read_name' : '读取',
            'button_width' : 15,
            'func_run' : self.fun_run,
            })
        
        self.vars['static_sim_type'].set(1)
        self.vars['static_record_type'].set(2)

    def fun_run(self):
        pass
        self.print('\n按钮无效\n')

    def fun_auto_brake(self):

        if tkinter.messagebox.askyesnocancel('计算前询问', '是否计算')!=True: 
            self.print('\n不进行计算\n')
            return None
        
        static_sim_type = self.static_sim_type[self.vars['static_sim_type'].get()]
        static_record_type = self.static_record_type[self.vars['static_record_type'].get()]
        self.print('\n制动-自动计算中\n')
        auto_brake(static_record_type, {'sim_type':static_sim_type}, )
        self.print('\n制动-自动计算完成!!\n')

    def fun_auto_static_only(self):

        if tkinter.messagebox.askyesnocancel('计算前询问', '是否计算')!=True: 
            self.print('\n不进行计算\n')
            return None
        static_sim_type = self.static_sim_type[self.vars['static_sim_type'].get()]
        static_record_type = self.static_record_type[self.vars['static_record_type'].get()]
        self.print('\n整车-static静态-计算中\n')
        auto_static_only(static_record_type, sim_type=static_sim_type, )
        self.print('\n整车-static静态-计算-计算完成!!\n')

    def fun_auto_spring_preload(self):

        if tkinter.messagebox.askyesnocancel('计算前询问', '是否计算')!=True: 
            self.print('\n不进行计算\n')
            return None
        static_sim_type = self.static_sim_type[self.vars['static_sim_type'].get()]
        static_record_type = self.static_record_type[self.vars['static_record_type'].get()]
        self.print('\n整车-spring预载-自动计算中\n')
        auto_spring_preload(static_record_type, sim_type=static_sim_type, )
        self.print('\n整车-spring预载-自动计算完成!!\n')


if __name__=='__main__':

    TkAuto('TCP-连接ADAMS计算').run()
    