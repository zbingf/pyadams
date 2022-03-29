

# 标准库
from pprint import pprint, pformat
import json
import os.path
import os
import pickle


# 调用库
from appJar import gui

# # 自建库
# from ajui import *

def read_var(path):
    """
        读取变量存储数据
        path 目标数据路径
    """

    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data


class DirResultSearch:

    def __init__(self, path):

        self.directory_search(path)

    def directory_search(self, path):

        file_paths = {}
        file_names = {}
        file_types = {}

        type2name = {}
        for file_name in os.listdir(path):
            abs_path = os.path.join(path, file_name)
            if not os.path.isdir(abs_path):
                name = '.'.join(file_name.split('.')[:-1])
                name_type = file_name.split('.')[-1]
                file_paths[file_name] = abs_path
                file_types[file_name] = name_type
                file_names[file_name] = name

                if name_type not in type2name: type2name[name_type] = []
                type2name[name_type].append(file_name)

        self.file_paths = file_paths
        self.file_types = file_types
        self.file_names = file_names
        self.type2name = type2name
        return None

    def get_types(self):

        return list(self.type2name.keys())

    def get_names_by_type(self, name_type):
        
        names = []
        for file_name in self.type2name[name_type]:
            names.append(self.file_names[file_name])

        return names

    def get_file_path_by_name_and_type(self, name, name_type):

        return self.file_paths[name+'.'+name_type]



# -------------------

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


class AjPlotCompareLabelFrame:

    def __init__(self, app, suffix=None, **kwargs):
        self.app = app
        self.suffix = suffix
        self.prefix = 'AjPlotCompare'
        self.names = {}

        app.startLabelFrame(self.obj_name('LabelFrame'), **kwargs)
        self.main_ui()
        self.bind_link()
        app.stopLabelFrame()

    def obj_name(self, name):
        new_name = self.prefix + "_" + name + "_" + self.suffix
        self.names[name] = new_name
        return new_name

    def func_lb_sub_button1(self, btn):
        # print(btn)
        datas = self.datas
        # print(datas)
        list_name = self.app.getListBox(self.names['lb_sub'])[0]
        print(list_name)
        xs, ys = [], []
        names = []
        for name in datas:
            y = datas[name]['list'][list_name]
            x = [n/datas[name]['samplerate'] for n in range(len(y))]
            xs.append(x)
            ys.append(y)
            names.append(name)
        # print(len(xs))
        self.plot(xs, ys, names)

    def func_lb_main_button1(self, btn):
        # print(btn)
        names = self.app.getListBox(self.names['lb_main'])
        name_type = self.app.getOptionBox(self.names['file_type'])
        datas = {}
        for name in names:
            file_path = self.obj_DirResultSearch.get_file_path_by_name_and_type(name, name_type)
            datas[name] = read_var(file_path) 
        self.set_lb_sub(list(datas[name]['list'].keys()))
        self.datas = datas

    def func_result_search(self, btn):
        """
            结果数据检索
        """
        result_dir = self.app.getEntry(self.names["result_dir"])
        print(result_dir)
        drs = DirResultSearch(result_dir)

        self.app.changeOptionBox(self.names['file_type'], drs.get_types(), callFunction=True)

        self.obj_DirResultSearch = drs
        # self.set_lb_main([1,2,3,4,5,5,6,7]*2)

    def func_update_file_type(self, btn):

        file_type = self.app.getOptionBox(self.names['file_type'])
        if file_type == "None": return None
        names = self.obj_DirResultSearch.get_names_by_type(file_type)
        self.set_lb_main(names)

    def main_ui(self):
        app = self.app

        app.addLabelDirectoryEntry(self.obj_name("result_dir"), label="result_dir", row=0, column=0, colspan=0, rowspan=0)
        app.addNamedButton("result_search", self.obj_name("result_search"), func=self.func_result_search, row=0, column=1)

        app.addLabelOptionBox(self.obj_name("file_type"), ["None"], label="file_type", row=1, column=0, colspan=0)
        app.addButton(self.obj_name("file_type_update"), func=self.func_update_file_type, row=1, column=1)
        app.setButton(self.obj_name("file_type_update"), "update")

        app.addListBox(self.obj_name("lb_main"), row=2, column=0, colspan=0, rowspan=0)
        app.setListBoxMulti(self.obj_name("lb_main"))

        app.addListBox(self.obj_name("lb_sub"), row=2, column=1, colspan=0, rowspan=0)
        
        self.obj_plot = AjPlotOne(app, self.obj_name("plot"), row=0, column=2, colspan=0, rowspan=3)


    def bind_link(self):
        app = self.app
        
        lb_main = app.widgetManager.get(app.Widgets.ListBox, self.names['lb_main'])
        lb_main.bind("<Button-1>", self.func_lb_main_button1)

        lb_sub = app.widgetManager.get(app.Widgets.ListBox, self.names['lb_sub'])
        lb_sub.bind("<Button-1>", self.func_lb_sub_button1)

        # app.setListBoxFunction("colours", btnPress)
        # app.setListBoxFunction(self.names['lb_main'], self.func_lb_main_button1)
        # app.setListBoxFunction(self.names['lb_sub'], self.func_lb_sub_button1)
        # app.setListBoxChangeFunction(self.names['lb_main'], self.func_lb_main_button1)
        # app.setListBoxChangeFunction(self.names['lb_sub'], self.func_lb_sub_button1)

        # ob_file_type = app.widgetManager.get(app.Widgets.OptionBox, self.names['file_type'])
        # ob_file_type.bind("<Button-1>", self.func_result_search)

    def set_lb_main(self, list1):
        self.app.updateListBox(self.names['lb_main'], list1, callFunction=False)

    def set_lb_sub(self, list1):
        self.app.updateListBox(self.names['lb_sub'], list1, callFunction=False)

    def plot(self, *args, **kwargs):
        # print(kwargs)
        self.obj_plot.clear()
        self.obj_plot.plot(*args, **kwargs)
        self.app.refreshPlot(self.names['plot'])

    def scatter(self,):
        self.obj_plot.scatter(*args, **kwargs)



if __name__ == '__main__':

    app=gui()
    app.setFont(12)
    app.setFont('仿宋')
    # create_frame_ui(app, SET_MENU_SAVE_AND_LOAD)
    # aj_plot_compare(app)

    ajpc = AjPlotCompareLabelFrame(app, "A", label="Plot Compare A")
    print(ajpc.names)
    # app.updateListBox('l_list_box_main', [1,2,3,4,5,5,6,7]*2)
    # app.updateListBox('l_list_box_sub', [1,2,3,4,5,5,6,7]*2)

    

    app.go() # 运行UI
