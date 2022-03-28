
# 标准库
from pprint import pprint, pformat
import json
import os.path

# 调用库
from appJar import gui



SET_RESULT = """
f_result;            label_frame;       result;
e_res_file_path;     label_entry_file;  result_file;
e_res_req;           label_entry;       reqs                  :;
e_res_comp;          label_entry;       comps               :;
e_res_note;          label_entry;       nots                   :;
e_res_channel_range; label_entry;       channel_range :;
e_res_data_range;    label_entry;  data_range      :;          4,None; None,None;
c_res_test;          check_box;         check;
"""

# UI设置保存和读取
SET_MENU_SAVE_AND_LOAD = """
None;         None_frame;        菜单;
配置; menu_item; ---save---; fun_save_params;
配置; menu_item; ---load---; fun_load_params;
"""


# ----------------
# plot model

class AjPlotOne:
    models = {} # 实例数据存储
    """作图"""
    def __init__(self, app, title, **kwargs):
        if title in AjPlotOne.models.keys():
            pass
        else:
            AjPlotOne.models[title] = self
            
            self.app = app
            self.fig = app.addPlotFig(title, **kwargs)
            self.axes = self.fig.add_subplot(1,1,1)

    def clear(self):
        self.axes.clear()

    def plot(self, x2s, y2s, legend=None):
        """
            x2s: 二维数据
            y2s: 二维数据

        """
        for xs, ys in zip(x2s, y2s):
            self.axes.plot(xs, ys)

        if legend!=None:
            self.axes.legend(legend)

    def scatter(self, x2s, y2s, legend=None):
        """
            x2s: 二维数据
            y2s: 二维数据

        """
        for xs, ys in zip(x2s, y2s):
            self.axes.scatter(xs, ys)

        if legend!=None:
            self.axes.legend(legend)


# ----------------
# create 

def parase_set_to_list(set_str, suffix=None):
    """
        解析 set_str 数据
        输出 lines = [[], [], ...]
    """
    lines = [[v.strip() for v in line.split(';') if v] 
            for line in set_str.split('\n') if line]
    
    new_lines = []
    for line in lines:
        if 'frame' in line[1]:
            frame_line = line
            continue
        new_lines.append(line)

    new_lines = [frame_line]+new_lines

    if suffix==None: 
        return new_lines
    else:
        for line in new_lines:
            line[0] = line[0]+'_'+suffix
        return new_lines


def edit_lines_entry_label(lines):
    """
        entry label edit
        编辑label的字符宽度
    """
    n_max = 0
    for n in range(2):
        for line in lines:
            if 'entry' in line[1]:
                label = line[2]
                if n==0:
                    if len(label) > n_max:
                        n_max = len(label)
                elif n==1:
                    line[2] = label.ljust(n_max)
    # print(n_max)
    return lines    


def create_line_ui(app, line):
    """
        单行创建UI
    """
    ui_name = line[0]
    ui_type = line[1].lower()
    if ui_type == 'label_entry': 
        app.addLabelEntry(ui_name, label=line[2])

    elif ui_type == 'label_entry_auto':
        app.addLabelAutoEntry(ui_name, label=line[2], words=line[3:])

    elif ui_type == 'label_entry_file':
        app.addLabelFileEntry(ui_name, label=line[2])

    elif ui_type == 'label_entry_dir':
        row, column, rowspan, colspan = line[3:7]
        row = None if row=='None' else int(row)
        column = 0 if column=='None' else int(column)
        colspan = 0 if colspan=='None' else int(colspan) 
        rowspan = 0 if rowspan=='None' else int(rowspan)
        app.addLabelDirectoryEntry(ui_name, label=line[2], row=row, column=column, colspan=colspan, rowspan=rowspan)

    elif ui_type == 'name_button':
        row, column = line[4:6]
        row = None if row=='None' else int(row)
        column = 0 if column=='None' else int(column)
        app.addNamedButton(line[2], ui_name, func=eval(line[3]), row=row, column=column)

    elif ui_type == 'check_box':
        app.addCheckBox(ui_name, name=line[2])

    elif ui_type == 'menu_item': # 菜单
        app.addMenuItem(ui_name, line[2], func=eval(line[3]))

    elif ui_type == 'aj_plot_one':
        row, column, rowspan, colspan = line[2:6]
        row = None if row=='None' else int(row)
        column = 0 if column=='None' else int(column)
        colspan = 0 if colspan=='None' else int(colspan) 
        rowspan = 0 if rowspan=='None' else int(rowspan)
        AjPlotOne(app, ui_name, row=row, column=column, colspan=colspan, rowspan=rowspan)

    elif ui_type == 'list_box':
        row, column, rowspan, colspan = line[2:6]
        row = None if row=='None' else int(row)
        column = 0 if column=='None' else int(column)
        colspan = 0 if colspan=='None' else int(colspan) 
        rowspan = 0 if rowspan=='None' else int(rowspan)
        app.addListBox(ui_name, row=row, column=column, colspan=colspan, rowspan=rowspan)


def create_frame_ui(app, set_str, suffix=None, row=None, column=0):
    """
        创建 frame
    """
    lines = parase_set_to_list(set_str, suffix)
    # lines = edit_lines_entry_label(lines)
    # print(lines)
    frame_name, frame_type, frame_label = lines[0]
    if suffix!=None: frame_label = frame_label+'_'+suffix

    # Start
    if frame_type=='frame': app.startFrame(frame_name)
    elif frame_type=='label_frame': app.startLabelFrame(frame_name, row=row, column=column, label=frame_label)
    elif frame_type=='None_frame' : pass

    # 
    for line in lines[1:]:
        create_line_ui(app, line)

    # End
    if frame_type=='frame': app.stopFrame()
    elif frame_type=='label_frame': app.stopLabelFrame()
    elif frame_type=='None_frame' : pass


# ----------------
# button callback

def fun_save_params(btn):
    """
        配置数据保存
    """
    params = {
        'entry': app.getAllEntries(),
        'check_box': app.getAllCheckBoxes(),
    }

    json_path = app.saveBox('数据保存', fileTypes=[('json files', '.json'),])
    if not json_path: return None

    with open(json_path, 'w') as f:
        json.dump(params, f)


def fun_load_params(btn):
    """
        配置加载
    """
    json_path = app.openBox('数据保存', fileTypes=[('json files', '.json'),])
    if not os.path.exists(json_path): 
        return None

    with open(json_path, 'r') as f:
        params = json.load(f)

    for key in params['entry']:
        try:
            app.setEntry(key, params['entry'][key])
        except:
            print(f'error: {key}')

    for key in params['check_box']:
        try:
            app.setCheckBox(key, params['check_box'][key])
        except:
            print(f'error: {key}')            



# -------------------

SET_PARAM_PLOT_COMPARE = """
f_param_plot_compare;  label_frame;        Plot Compare;
e_res_dir;              label_entry_dir;   result_dir;          0;0;0;2;
b_save_param;           name_button;       ---update---;        update_plot_compare;   None;None;
l_list_box_main;        list_box;          3;0;0;0;
l_list_box_sub;         list_box;          3;1;0;0;
aj_plot_one_1;          aj_plot_one;       0;2;4;0;
"""

def update_plot_compare(btn):
    print(btn)



if __name__ == '__main__':

    app=gui()
    app.setFont(12)
    # app.setFont('黑体')
    app.setFont('仿宋')
    create_frame_ui(app, SET_MENU_SAVE_AND_LOAD)

    app.startTabbedFrame("tab_frame")
    app.startTab('tab_01')
    create_frame_ui(app, SET_RESULT, suffix='A', row=0, column=0)
    create_frame_ui(app, SET_PARAM_PLOT_COMPARE, suffix=None, row=1, column=0)
    app.stopTab()

    app.startTab('tab_02')
    create_frame_ui(app, SET_RESULT, suffix='B', row=0, column=0)
    # create_frame_ui(app, SET_RESULT, suffix='C', row=0, column=1)
    app.stopTab()


    app.stopTabbedFrame()

    app.updateListBox('l_list_box_main', [1,2,3,4,5,5,6,7]*2)
    app.updateListBox('l_list_box_sub', [1,2,3,4,5,5,6,7]*2)

    app.go() # 运行UI
