
# ===================================================================
# 选择性删除数据

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets  import RectangleSelector

class LocSelect: # 数据选择区域
    x1 = None
    x2 = None
    y1 = None
    y2 = None

    @classmethod
    def set_init(clf):
        clf.x1 = None
        clf.x2 = None
        clf.y1 = None
        clf.y2 = None


class Objs: # 对象存储

    ax_obj = None
    xy_obj = None
    xy_temp_plot_obj = None
    xy_del_plot_obj = None

    @classmethod
    def set_init(clf):
        clf.ax_obj = None
        clf.xy_obj = None
        clf.xy_temp_plot_obj = None # 临时点
        clf.xy_del_plot_obj = None  # 目标删除点


class PlotXYData: # xy数据存储及操作
    
    def __init__(self, xs, ys):

        self.xs = xs
        self.ys = ys
        self.xs_del = []
        self.ys_del = []
        self.loc_del = []
        self.loc_temp = []

    def xy_del(self, LocSelectObj): # 临时转删除区域, 增加

        self.loc_del.extend(self.loc_temp)
        self.loc_del = list(set(self.loc_del))
        return None

    def xy_temp(self, LocSelectObj): # 临时存放

        self.loc_temp = []
        xs = self.xs
        ys = self.ys
        for n in range(len(xs)):
            if xs[n]>= LocSelectObj.x1 and xs[n]<= LocSelectObj.x2:
                if ys[n]>= LocSelectObj.y1 and ys[n]<= LocSelectObj.y2:
                    self.loc_temp.append(n)

        self.loc_temp = list(set(self.loc_temp))
        return None

    def get_temp(self): # 获取临时数据
        loc_temp = self.loc_temp
        return self.get_data(loc_temp)

    def get_del(self): # 获取目标删除数据
        loc_del = self.loc_del
        return self.get_data(loc_del)

    def get_data(self, locs): # 获取指定数据
        xs = self.xs
        ys = self.ys
        xs_temp = [xs[n] for n in locs]
        ys_temp = [ys[n] for n in locs]
        return xs_temp, ys_temp

    def get_current_data(self):
        xs = self.xs
        ys = self.ys
        loc_del = self.loc_del

        xs_temp = [x for n, x in enumerate(xs) if n not in loc_del]
        ys_temp = [y for n, y in enumerate(ys) if n not in loc_del]

        return xs_temp, ys_temp


def line_select_callback(eclick, erelease): # 左键区域选择事件

    xy_obj = Objs.xy_obj
    ax_obj = Objs.ax_obj

    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata

    rect = plt.Rectangle( (min(x1,x2),min(y1,y2)), np.abs(x1-x2), np.abs(y1-y2) )

    LocSelect.x1, LocSelect.x2, LocSelect.y1, LocSelect.y2 = min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2)
    xy_obj.xy_temp(LocSelect)

    if Objs.xy_temp_plot_obj == None:
        lines, = ax_obj.plot(*xy_obj.get_temp(), 'o', color='y')
        Objs.xy_temp_plot_obj = lines
    else:
        lines = Objs.xy_temp_plot_obj
        lines.set_data(*xy_obj.get_temp())


def RightClick(event): # 鼠标右击事件
    # 确认所选数据
    
    xy_obj = Objs.xy_obj
    ax_obj = Objs.ax_obj

    if event.button == 3:
        
        xy_obj.xy_del(LocSelect)
        xy_obj.get_del()

        if Objs.xy_del_plot_obj == None: 
            lines, = ax_obj.plot(*xy_obj.get_del(), 'o', color='r')
            Objs.xy_del_plot_obj = lines
        else:
            lines = Objs.xy_del_plot_obj
            lines.set_data(*xy_obj.get_del())


def plot_select(xdata, ydata): # 

    Objs.xy_obj = PlotXYData(xdata, ydata)

    fig, ax = plt.subplots()
    line, = ax.plot(xdata, ydata)

    Objs.ax_obj = ax

    # 右键连接
    fig.canvas.mpl_connect('button_press_event', RightClick)
    rs = RectangleSelector(ax, line_select_callback,
                           drawtype='box', useblit=False, button=[1], 
                           minspanx=5, minspany=5, spancoords='pixels', 
                           interactive=True)

    plt.show()
    xs_new, ys_new = Objs.xy_obj.get_current_data()
    
    return xs_new, ys_new


# ------------------------------------------

def test_plot_select():

    xdata = np.linspace(0,9*np.pi, num=301)
    ydata = np.sin(xdata)
    print( plot_select(xdata, ydata) )


if __name__ == '__main__':
    pass
    
    test_plot_select()
    

