"""
    作图设置
"""

# import matplotlib
# matplotlib.use('Agg')

import os
import math
# import matplotlib.pyplot as plt
# from matplotlib import pyplot as plt

from matplotlib.pyplot import figure, rcParams, close
plt_close = close
rcParams.update({'figure.max_open_warning': 0})

def array_range(arr1, nrange): # 数值范围截取
    """
        arr1    numpy.array
        nrange  [lower,upper] 截取范围
    """
    arr2 = arr1 >= nrange[0]
    arr3 = arr1 <= nrange[1]
    arr4 = arr2 * arr3

    return arr4 # 目标范围输出


# ======================================================================
# ======================================================================
# 图像
class FigPlotRealTime:
    """
        实时生成,大量图片的生成
        相比FigPlot内存占用少
    """
    def __init__(self, fig_path):
        """
        """

        self.fig_path  = fig_path
        self.legends   = {'ts':None, 'hz':None}
        self.ylabels   = {'ts':None, 'hz':None}
        self.xlabels   = {'ts':None, 'hz':None}
        self.fig_paths = {'ts':[], 'hz':[], 'ts_Hz':[]}

    def set_figure(self, size_gain=0.6, nums=None, dpi=500, figsize='16:9'):

        rcParams['savefig.dpi'] = dpi
        rcParams['font.sans-serif'] = ['SimHei']
        rcParams['axes.unicode_minus'] = False
        # rcParams['figure.figsize'] = [16*size_gain, 9*size_gain]    # 尺寸

        self.nums = [4,3] if nums==None else nums

        figsize = [float(n) for n in figsize.split(':')]
        rcParams['figure.figsize'] = [figsize[0]*size_gain, figsize[1]*size_gain]    # 尺寸

        return None

    def set_legend(self, legend=None, figtype='ts'):
        """  """
        if legend==None : return None
        assert isinstance(legend, list)
        self.legends[figtype] = legend
        
        return None

    def set_ylabel(self, ylabels=None, figtype='ts'):
        """  """
        if ylabels==None: return None
        assert isinstance(ylabels, list)
        self.ylabels[figtype] = ylabels

        return None

    def set_xlabel(self, xlabels=None, figtype='ts'):

        if xlabels==None: return None
        self.xlabels[figtype] = xlabels

        return None

    def plot_ts(self, list3d_y, list3d_x, linetypes=None, linewidth=1, plottype='plot'):
        """
            多曲线同时作图
            list3d_y    : [list2d_y, list2d_y, ...]
            list3d_x    : [list2d_x, list2d_x, ...]
            linetypes   : 线段类型 ['b', 'r--']
            plottype    : 作图类型 'plot' or 'scatter' 散点图
        """
        # ==============================
        nums    = self.nums
        if linetypes == None:
            linetypes = ['b', 'r--']
        # ==============================

        num_plot = nums[0] * nums[1]
        len_rpc = len(list3d_y[0])
        num_fig = math.ceil(len_rpc/num_plot) # figure 个数

        fig_loc = 0
        for n in range(num_fig):
            path = self.fig_path + f'_ts_{n}.png'
            self.fig_paths['ts'].append(path)
            fig_obj = figure()

            for loc in range(num_plot):
                nloc = loc + n*num_plot
                if nloc >= len_rpc:
                    break

                ax1 = fig_obj.add_subplot(nums[0], nums[1], loc+1)

                for list2d_y, list2d_x, linetype in zip(list3d_y, list3d_x, linetypes):
                    if plottype == 'plot':
                        ax1.plot(list2d_x[nloc], list2d_y[nloc], linetype, linewidth=linewidth)
                    elif plottype == 'scatter':
                        ax1.scatter(list2d_x[nloc], list2d_y[nloc], color=linetype, linewidths=linewidth,
                            marker='.', s=10)

                ax1.legend(self.legends['ts'])
                ax1.set_ylabel(self.ylabels['ts'][fig_loc])
                if isinstance(self.xlabels['ts'], list):
                    ax1.set_xlabel(self.xlabels['ts'][fig_loc])
                else:
                    ax1.set_xlabel(self.xlabels['ts'])
                fig_loc += 1

            fig_obj.tight_layout()
            fig_obj.savefig(path)
            # plt.close()
            plt_close()

        return None


