"""
    https://www.w3cschool.cn/doc_tcl_tk/tcl_tk-tkcmd-bind-htm.html
"""

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

    def plot(self, x2s, y2s, legend=None, xlabel=None, ylabel=None):
        """
            x2s: 二维数据
            y2s: 二维数据

        """
        for xs, ys in zip(x2s, y2s):
            self.axes.plot(xs, ys)

        if legend!=None:
            self.axes.legend(legend)
        if xlabel!=None:
            self.axes.set_xlabel(xlabel)
        if ylabel!=None:
            self.axes.set_ylabel(ylabel)

    def scatter(self, x2s, y2s, legend=None, xlabel=None, ylabel=None):
        """
            x2s: 二维数据
            y2s: 二维数据

        """
        for xs, ys in zip(x2s, y2s):
            self.axes.scatter(xs, ys)

        if legend!=None:
            self.axes.legend(legend)

        if xlabel!=None:
            self.axes.set_xlabel(xlabel)

        if ylabel!=None:
            self.axes.set_ylabel(ylabel)

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

    def main_ui(self):
        """程序框体搭建"""

        app = self.app

        # 0.0
        app.addLabelDirectoryEntry(self.obj_name("result_dir"), label="result_dir", row=0, column=0, rowspan=0, colspan=0)
        # 0.1
        app.addNamedButton("result_search", self.obj_name("result_search"), func=self.func_result_search, row=0, column=1, rowspan=0, colspan=1)

        # 1.0
        lob_file_type = app.addLabelOptionBox(self.obj_name("file_type"), ["None"], label="file_type", row=1, column=0, rowspan=0, colspan=0)
        lob_file_type.configure(width=20)
        # 1.1
        app.addButton(self.obj_name("file_type_update"), func=self.func_update_file_type, row=1, column=1, rowspan=0, colspan=0)
        app.setButton(self.obj_name("file_type_update"), "update")
        # 1.2
        lb_main = app.addListBox(self.obj_name("lb_main"), row=1, column=2, rowspan=0, colspan=0)
        app.setListBoxMulti(self.obj_name("lb_main"))
        lb_main.configure(width=30, height=5, exportselection=False)

        # 3.0
        lb_x = app.addListBox(self.obj_name("lb_x"), row=3, column=0, rowspan=0, colspan=1)
        lb_x.configure(width=30, height=20, exportselection=False)
        # 3.2
        lb_y = app.addListBox(self.obj_name("lb_y"), row=3, column=2, rowspan=0, colspan=0)
        lb_y.configure(width=30, height=20, exportselection=False)

        self.obj_plot = AjPlotOne(app, self.obj_name("plot"), row=0, column=3, colspan=0, rowspan=4)

        # 4.0
        grid = app.addGrid(self.obj_name("value_grid"), [["None"], ["None"]], row=4, column=0, colspan=4, rowspan=0)
        grid.configure(width=1200, height=400)


    def bind_link(self):
        """事件关联"""
        app = self.app
        
        lb_main = app.widgetManager.get(app.Widgets.ListBox, self.names['lb_main'])
        lb_main.bind("<<ListboxSelect>>", self.func_lb_main_select)
        
        lb_y = app.widgetManager.get(app.Widgets.ListBox, self.names['lb_y'])
        lb_y.bind("<<ListboxSelect>>", self.func_lb_y_select)
        
        lb_x = app.widgetManager.get(app.Widgets.ListBox, self.names['lb_x'])
        lb_x.bind("<<ListboxSelect>>", self.func_lb_x_select)


    def func_lb_main_select(self, btn):
        # print('call func_lb_main_select')
        names = self.app.getListBox(self.names['lb_main'])
        if not names: return None
        # print(names)
        name_type = self.app.getOptionBox(self.names['file_type'])
        datas = {}
        for name in names:
            file_path = self.obj_DirResultSearch.get_file_path_by_name_and_type(name, name_type)
            datas[name] = read_var(file_path) 
            # 数据格式 {'value':{...}, 'samplerate', 'list':{...}}

        # print(name)
        self.datas = datas
        # updata
        self.set_lb_y(list(datas[name]['list'].keys()))
        self.set_lb_x(['time']+list(datas[name]['list'].keys()))
        self.set_value_grid(datas)

    def func_lb_x_select(self, btn):
        # print('call func_lb_x_select')
        self.select_x_names = self.app.getListBox(self.names['lb_x'])

    def func_lb_y_select(self, btn):
        # print('call func_lb_y_select')

        self.select_y_names = self.app.getListBox(self.names['lb_y'])
        datas = self.datas

        y_name = self.select_y_names[0]
        x_name = self.select_x_names[0]
        # print(x_name)
        xs, ys = [], []
        names = []
        for name in datas:
            y = datas[name]['list'][y_name]
            if x_name=='time':
                x = [n/datas[name]['samplerate'] for n in range(len(y))]
            else:
                x = datas[name]['list'][x_name]
            xs.append(x)
            ys.append(y)
            names.append(name)
        # print(len(xs))

        self.plot(xs, ys, names, xlabel=x_name, ylabel=y_name)
        # help(self.obj_plot.axes)
        

    def func_result_search(self, btn):
        """
            结果数据检索
        """
        result_dir = self.app.getEntry(self.names["result_dir"])
        drs = DirResultSearch(result_dir)
        self.app.changeOptionBox(self.names['file_type'], drs.get_types(), callFunction=True)
        self.obj_DirResultSearch = drs

    def func_update_file_type(self, btn):
        """ 文档数据更新 """

        file_type = self.app.getOptionBox(self.names['file_type'])
        if file_type == "None": return None
        names = self.obj_DirResultSearch.get_names_by_type(file_type)
        self.set_lb_main(names)


    def set_lb_main(self, list1):
        """更新main列表"""
        self.app.updateListBox(self.names['lb_main'], list1, callFunction=False)

    def set_lb_y(self, list1):
        """更新sub列表"""
        self.app.updateListBox(self.names['lb_y'], list1, callFunction=False)

    def set_lb_x(self, list1):
        self.app.updateListBox(self.names['lb_x'], list1, callFunction=False) 


    def set_value_grid(self, datas):
        """
            参数表格设置
        """
        headers = ['-']
        for name in datas: headers.append(name)
        list2d = [headers]

        for key in datas[headers[1]]['value']:
            list1d = []
            for name in datas:
                value = datas[name]['value'][key]
                if isinstance(value, float): value = round(value, 2)
                if not list1d: list1d.append(key)
                list1d.append(value)
            list2d.append(list1d)

        self.app.replaceAllGridRows(self.names['value_grid'], list2d)

    def plot(self, *args, **kwargs):
        # 作图
        self.obj_plot.clear()
        self.obj_plot.plot(*args, **kwargs)
        self.app.refreshPlot(self.names['plot'])

    def scatter(self,):
        # 作散点图
        self.obj_plot.clear()
        self.obj_plot.scatter(*args, **kwargs)
        self.app.refreshPlot(self.names['plot'])


if __name__ == '__main__':

    app=gui()
    app.setFont(10)
    app.setFont('仿宋')
    
    ajpc = AjPlotCompareLabelFrame(app, "A", label="Plot Compare Time")

    app.go() # 运行UI
