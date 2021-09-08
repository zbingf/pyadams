"""
    作图设置
"""

# import matplotlib
# matplotlib.use('Agg')

from pyadams.datacal import tscal, freqcal

import os
import os.path
import math
import logging
import matplotlib.pyplot as plt
import numpy as np


plt.rcParams.update({'figure.max_open_warning': 0})

def array_range(arr1, nrange): # 数值范围截取
    """
        arr1    numpy.array
        nrange  [lower,upper] 截取范围
    """
    arr2 = arr1 >= nrange[0]
    arr3 = arr1 <= nrange[1]
    arr4 = arr2 * arr3

    return arr4 # 目标范围输出


# # 图像保存、清空、显示设置
# # def plot_end_set(figs, figpath, isShow):
#     """
#         figs : {1: <Figure size 960x540 with 1 Axes>, 
#                 2: <Figure size 960x540 with 1 Axes>, 
#                 3: <Figure size 960x540 with 1 Axes>}
        
#         figpath : 图像路径及前缀,如:
#             D:\\github\\pycae\\test

#         isShow : True or False 是否显示图片

#         输出:
#             fig_paths: ['current_1.png', 'current_2.png', 'current_3.png']
    
#     """
#     logger = logging.getLogger('datacal.plot.scatter_ts_single')

#     # 结尾
#     fig_paths = []
#     for name in figs:
#         if figpath==None:
#             # 默认当前路径输出
#             # figs[name].savefig('current_'+str(name)+'.png')
#             fig_path = 'current_'+str(name)+'.png'
#         else:
#             # figs[name].savefig(figpath+'_'+str(name)+'.png')
#             fig_path = figpath+'_'+str(name)+'.png'

#         logger.info(f'figure save : {fig_path}')

#         figs[name].savefig(fig_path)
#         fig_paths.append(fig_path)

#     if isShow:
#         plt.show()

#     for key in figs:
#         figs[key].clf()

#     return fig_paths


# ======================================================================
# 数据对比-时域&频域
# ======================================================================
# def plot_ts_hz(res_data, target_data, samplerate=None, block_size=None,
#     res_x=None, target_x=None, ylabels=None, xlabel=None,
#     nums=None, figpath=None, isShow=None, isHzPlot=True, isTsPlot=True, 
#     hz_range=None, legend=None, size_gain=0.6): 
#     """
#         用于数据对比
#         res_data        后处理数据   二维数组
#         target_data     目标数据
#         samplerate      采样频率，用于PSD计算 [res, target]
#         block_size      块尺寸 [res, target]
#         res_x           指定res 横坐标数据输入
#         target_x        指定target 横坐标数输入

#         ylabels         Y坐标标签 list
#         nums            图片布局  [行, 列]
#         figpath         文件保存路径
#         isShow          是否输出图片
#         isHzPlot        是否输出频域图片
#         hz_range        频域截取范围

#     """ 
#     logger = logging.getLogger('datacal.plot.plot_ts_hz')

#     plt.rcParams['savefig.dpi'] = 500
#     plt.rcParams['font.sans-serif'] = ['SimHei']
#     plt.rcParams['axes.unicode_minus'] = False
#     # size_gain = 0.6
#     linewidth = 1
#     plt.rcParams['figure.figsize'] = [16*size_gain, 9*size_gain]    # 尺寸

#     if nums == None:
#         nums = [4,3]
    
#     if res_x == None:
#         res_x = [ [n/samplerate[0] for n in range(len(res_data[0]))] ]*len(res_data)

#     if target_x == None:
#         target_x = [ [n/samplerate[1] for n in range(len(target_data[0]))] ]*len(target_data)


#     if block_size == None:
#         block_size = [None,None]

#     if legend == None:
#         # legend = ['对比目标', '当前']
#         legend = ['当前', '对比目标']

#     if xlabel == None:
#         xlabel = 'Time (s)'

#     figs = {}
#     num_plot = nums[0] * nums[1]
#     len_rpc = len(target_data)
#     num_fig = math.ceil(len_rpc/num_plot) # figure 个数
    
#     # res_time = [n/samplerate[0] for n in range(len(res_data[0]))]
#     # target_time = [n/samplerate[1] for n in range(len(target_data[0]))]

#     # 时域
#     if isTsPlot:
#         for n in range(num_fig):
#             figs[n+1] = plt.figure(n+1)
#             for loc in range(num_plot):
#                 nloc = loc+n*num_plot
#                 if nloc >= len_rpc:
#                     break
#                 ax1 = figs[n+1].add_subplot(nums[0], nums[1], loc+1)
#                 ax1.plot(res_x[nloc], res_data[nloc], 'r--', linewidth=linewidth)   # 当前
#                 ax1.plot(target_x[nloc], target_data[nloc], 'b', linewidth=linewidth)   # 对比目标
#                 ax1.legend(legend)
#                 if ylabels != None:
#                     plt.ylabel(ylabels[nloc])
#                 plt.xlabel(xlabel)
#             plt.tight_layout()

#     # 频域
#     if isHzPlot: # 频域图像
#         f_start = num_fig
#         f_end = num_fig*2
#         for n in range(f_start, f_end):
#             figs[n+1] = plt.figure(n+1)
#             for loc in range(num_plot):
#                 nloc = loc+(n-f_start)*num_plot
#                 if nloc >= len_rpc:
#                     break

#                 ax1 = figs[n+1].add_subplot(nums[0], nums[1], loc+1)
#                 # PSD计算
#                 psd_hz_res,psd_y_res = freqcal.psd(res_data[nloc], samplerate[0], nperseg=block_size[0])            # 当前
#                 psd_hz_target,psd_y_target = freqcal.psd(target_data[nloc], samplerate[1], nperseg=block_size[1])   # 对比目标

#                 if hz_range != None:
#                     # 截取范围
#                     psd_hz_target, psd_y_target = np.array(psd_hz_target), np.array(psd_y_target)
#                     psd_hz_res, psd_y_res = np.array(psd_hz_res), np.array(psd_y_res)

#                     arr_loc_target = array_range(np.array(psd_hz_target), hz_range)
#                     arr_loc_res = array_range(np.array(psd_hz_res), hz_range)

#                     psd_hz_target, psd_y_target = psd_hz_target[arr_loc_target], psd_y_target[arr_loc_target]
#                     psd_hz_res, psd_y_res = psd_hz_res[arr_loc_res], psd_y_res[arr_loc_res]

#                 ax1.plot(psd_hz_target,psd_y_target,'b', linewidth=linewidth)               # 对比目标
#                 ax1.plot(psd_hz_res,psd_y_res,'r--', linewidth=linewidth, alpha=1)          # 当前
#                 ax1.legend(legend)
#                 if ylabels != None:
#                     plt.ylabel(ylabels[nloc])
#                 plt.xlabel('Hz')
#             plt.tight_layout()

#     fig_paths = plot_end_set(figs, figpath, isShow)
#     logger.info(f'figs: {figs}')
#     logger.info(f'figpath: {figpath}')
#     logger.info(f'fig_paths: {fig_paths}')

#     return fig_paths


# ======================================================================
# 单数据作图-时域&频域
# ======================================================================

# def plot_ts_hz_single(res_data, samplerate=None, block_size=None,
    # res_x=None, ylabels=None, xlabels=None,
    # nums=None, figpath=None, isShow=False, isHzPlot=True, isTsPlot=True,
    # hz_range=None, isGrid=False, size_gain=0.6): 
    """
        用于数据对比
        res_data        后处理数据   二维数组
        samplerate      采样频率
        block_size      块尺寸 
        res_x           指定res 横坐标数据输入
        ylabels         Y坐标标签 list
        nums            图片布局  [行, 列]
        figpath         文件保存路径
        isShow          是否显示图片
        isHzPlot        是否输出频域图片
        isTsPlot        是否输出时域图片
        hz_range        频域截取范围

    # """ 
    # logger = logging.getLogger('datacal.plot.plot_ts_hz_single')

    # plt.rcParams['savefig.dpi'] = 500
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_minus'] = False
    # # size_gain = 0.6
    # linewidth = 1
    # plt.rcParams['figure.figsize'] = [16*size_gain, 9*size_gain]    # 尺寸

    # if nums == None:
    #     nums = [4,3]
    
    # if res_x == None:
    #     # print(len(res_data[0]))
    #     res_x = [ [n/samplerate for n in range(len(res_data[0]))] ]*len(res_data)
    
    # if xlabels == None:
    #     xlabels = ['Time (s)']*len(res_data)


    # if block_size == None:
    #     block_size = [None,None]

    # figs = {}
    # num_plot = nums[0] * nums[1]
    # len_rpc = len(res_data)
    # num_fig = math.ceil(len_rpc/num_plot) # figure 个数
    
    # if isTsPlot:
    #     # 时域
    #     for n in range(num_fig):
    #         figs[n+1] = plt.figure(n+1)
    #         for loc in range(num_plot):
    #             nloc = loc+n*num_plot
    #             if nloc >= len_rpc:
    #                 break
    #             ax1 = figs[n+1].add_subplot(nums[0], nums[1], loc+1)
    #             ax1.plot(res_x[nloc], res_data[nloc], 'r', linewidth=linewidth)
    #             # ax1.legend(['对比目标', '当前'])
    #             ax1.axes.set_ylim(auto=True)
    #             if ylabels != None:
    #                 plt.ylabel(ylabels[nloc])
    #             plt.xlabel(xlabels[nloc])
    #             plt.grid(isGrid)
    #         plt.tight_layout()

    # # 频域
    # if isHzPlot: # 频域图像
    #     f_start = num_fig
    #     f_end = num_fig*2
    #     for n in range(f_start, f_end):
    #         figs[n+1] = plt.figure(n+1)
    #         for loc in range(num_plot):
    #             nloc = loc+(n-f_start)*num_plot
    #             if nloc >= len_rpc:
    #                 break

    #             ax1 = figs[n+1].add_subplot(nums[0], nums[1], loc+1)
    #             # PSD计算
    #             psd_hz_res,psd_y_res = freqcal.psd(res_data[nloc], samplerate, nperseg=block_size) 

    #             if hz_range != None:
    #                 # 截取范围
    #                 psd_hz_res, psd_y_res = np.array(psd_hz_res), np.array(psd_y_res)
    #                 arr_loc_res = array_range(np.array(psd_hz_res), hz_range)
    #                 psd_hz_res, psd_y_res = psd_hz_res[arr_loc_res], psd_y_res[arr_loc_res]

    #             ax1.plot(psd_hz_res, psd_y_res, 'r', linewidth=linewidth, alpha=1)          # 当前
    #             # ax1.legend(['对比目标', '当前'])
    #             if ylabels != None:
    #                 plt.ylabel(ylabels[nloc])
    #             plt.xlabel('Hz')
    #             plt.grid(isGrid)
    #         plt.tight_layout()

    # fig_paths = plot_end_set(figs, figpath, isShow)
    # logger.info(f'figs: {figs}')
    # logger.info(f'figpath: {figpath}')
    # logger.info(f'fig_paths: {fig_paths}')

    # return fig_paths


# ======================================================================
# 散点图作图
# ======================================================================
# def scatter_ts_single(xs, ys, xlabels, ylabels, figpath=None, nums=None,
    # isShow=False, size_gain=0.6, isGrid=False, linewidths=0.1, scatter_s=10):
    
    # logger = logging.getLogger('datacal.plot.scatter_ts_single')

    # plt.rcParams['savefig.dpi'] = 500
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_minus'] = False
    # plt.rcParams['figure.figsize'] = [16*size_gain, 9*size_gain]    # 尺寸

    # if nums == None:
    #     nums = [4,3]

    # figs = {}
    # num_plot = nums[0] * nums[1]
    # len_x = len(xs)
    # num_fig = math.ceil(len_x/num_plot) # figure 个数

    # # 时域
    # for n in range(num_fig):
    #     figs[n+1] = plt.figure(n+1)
    #     for loc in range(num_plot):
    #         nloc = loc+n*num_plot
    #         if nloc >= len_x:
    #             break
    #         ax1 = figs[n+1].add_subplot(nums[0], nums[1], loc+1)

    #         ax1.scatter(xs[nloc], ys[nloc], color='r', linewidths=linewidths,
    #             marker='.', s=scatter_s)

    #         ax1.axes.set_ylim(auto=True)

    #         if ylabels != None:
    #             plt.ylabel(ylabels[nloc])
    #         plt.xlabel(xlabels[nloc])
    #         plt.grid(isGrid)
    #     plt.tight_layout()

    # fig_paths = plot_end_set(figs, figpath, isShow)

    # logger.info(f'figs: {figs}')
    # logger.info(f'figpath: {figpath}')
    # logger.info(f'fig_paths: {fig_paths}')

    # return fig_paths


# ======================================================================
# ======================================================================
# 图像
class FigPlot:

    def __init__(self, fig_dic=None):
        """
            {
            'tx': {
                'figobj': {fig_n1: figobj_1, fig_n2: figobj_2},
                'axobj' : {fig_n1: [axobj1, axobj2], fig_n2: [axobj1, axobj2]},
                },
            'hz': {
                'figobj': {fig_n1: figobj_1, fig_n2: figobj_2},
                'axobj' : {fig_n1: [axobj1, axobj2], fig_n2: [axobj1, axobj2]},
                },
            }
        """
        if fig_dic==None:
            self.fig_dic = {'ts':{'figobj':{}, 'axobj':{}}, 'hz':{'figobj':{}, 'axobj':{}}, }
        else:
            self.fig_dic = fig_dic


    def set_figure(self, size_gain=0.6, nums=None, dpi=500, figsize='16:9'):

        plt.rcParams['savefig.dpi'] = dpi
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        # plt.rcParams['figure.figsize'] = [16*size_gain, 9*size_gain]    # 尺寸

        self.nums = [4,3] if nums==None else nums

        figsize = [float(n) for n in figsize.split(':')]
        plt.rcParams['figure.figsize'] = [figsize[0]*size_gain, figsize[1]*size_gain]    # 尺寸  

        return None

    def set_legend(self, legend=None, figtype='ts'):
        if legend==None : return None
        assert isinstance(legend, list)

        axobjs = self.fig_dic[figtype]['axobj']
        for n_fig in axobjs:
            for n_ax in axobjs[n_fig]:
                axobjs[n_fig][n_ax].legend(legend)

        return None

    def set_ylabel(self, ylabels=None, figtype='ts'):
        if ylabels==None: return None
        assert isinstance(ylabels, list)
        n = 0
        axobjs = self.fig_dic[figtype]['axobj']
        for n_fig in axobjs:
            for n_ax in axobjs[n_fig]:
                axobjs[n_fig][n_ax].set_ylabel(ylabels[n])
                n += 1
        
        return None

    def set_xlabel(self, xlabels=None, figtype='ts'):
        if xlabels==None: return None
        n = 0
        axobjs = self.fig_dic[figtype]['axobj']
        for n_fig in axobjs:
            for n_ax in axobjs[n_fig]:
                if isinstance(xlabels, list):
                    axobjs[n_fig][n_ax].set_xlabel(xlabels[n])
                else:
                    axobjs[n_fig][n_ax].set_xlabel(xlabels)
                n += 1

        return None

    def plot_ts(self, list2d_y, list2d_x=None, linetype='b', linewidth=1, plottype='plot'):

        # ==============================
        nums    = self.nums
        fig_dic = self.fig_dic['ts']
        # ==============================
        if list2d_x == None:
            list2d_x = [[n for n in range(len(list2d_y[0]))]] * len(list2d_y)
        elif not isinstance(list2d_x[0], list):
            list2d_x = [list2d_x] * len(list2d_y)

        figs = {}
        num_plot = nums[0] * nums[1]
        len_rpc = len(list2d_y)
        num_fig = math.ceil(len_rpc/num_plot) # figure 个数

        for n in range(num_fig):

            if n in fig_dic['figobj']:
                figs[n] = fig_dic['figobj'][n]
            else:
                figs[n] = plt.figure()
                fig_dic['figobj'][n] = figs[n]
                fig_dic['axobj'][n]  = {}

            for loc in range(num_plot):
                nloc = loc + n*num_plot
                if nloc >= len_rpc:
                    break

                if loc in fig_dic['axobj'][n]:
                    ax1 = fig_dic['axobj'][n][loc]
                else:
                    ax1 = figs[n].add_subplot(nums[0], nums[1], loc+1)
                    fig_dic['axobj'][n][loc] = ax1

                if plottype == 'plot':
                    ax1.plot(list2d_x[nloc], list2d_y[nloc], linetype, linewidth=linewidth)
                elif plottype == 'scatter':
                    ax1.scatter(list2d_x[nloc], list2d_y[nloc], color=linetype, linewidths=linewidth,
                        marker='.', s=10)

        self.fig_dic['ts'] = fig_dic
        return fig_dic

    def plot_hz(self, list2d_y, samplerate, block_size, hz_range=None, linetype='b', linewidth=1):

        nums = self.nums
        fig_dic = self.fig_dic['hz']

        figs = {}
        num_plot = nums[0] * nums[1]
        len_rpc = len(list2d_y)
        num_fig = math.ceil(len_rpc/num_plot) # figure 个数

        for n in range(num_fig):

            if n in fig_dic['figobj']:
                figs[n] = fig_dic['figobj'][n]
            else:
                figs[n] = plt.figure()
                fig_dic['figobj'][n] = figs[n]
                fig_dic['axobj'][n]  = {}

            for loc in range(num_plot):
                nloc = loc + n*num_plot
                if nloc >= len_rpc:
                    break

                if loc in fig_dic['axobj'][n]:
                    ax1 = fig_dic['axobj'][n][loc]
                else:
                    ax1 = figs[n].add_subplot(nums[0], nums[1], loc+1)
                    fig_dic['axobj'][n][loc] = ax1

                psd_hz, psd_y = freqcal.psd(list2d_y[nloc], samplerate, nperseg=block_size)
                
                if hz_range != None:
                    psd_hz, psd_y = np.array(psd_hz), np.array(psd_y)
                    arr_loc = array_range(psd_hz, hz_range)
                    psd_hz, psd_y = psd_hz[arr_loc], psd_y[arr_loc]

                ax1.plot(psd_hz, psd_y, linetype, linewidth=linewidth, alpha=1)

        self.fig_dic['hz'] = fig_dic
        return None

    def save(self, fig_path):

        fig_dic = self.fig_dic
        fig_paths = {'ts':[], 'hz':[]}
        n = 0
        for key in fig_dic:
            for fig_key in fig_dic[key]['figobj']:
                path = fig_path + f'_{key}_{fig_key}.png'
                fig_dic[key]['figobj'][fig_key].savefig(path)
                n += 1
                fig_paths[key].append(path)

        self.fig_paths = fig_paths
        return fig_paths

    def updata(self, figtype='ts'):

        fig1 = self.fig_dic[figtype]['figobj']
        for n_fig in fig1:
            fig1[n_fig].tight_layout()

        return None

    def show(self):
        plt.show()
        return None


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
        self.fig_paths = {'ts':[], 'hz':[]}

    def set_figure(self, size_gain=0.6, nums=None, dpi=500, figsize='16:9'):

        plt.rcParams['savefig.dpi'] = dpi
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        # plt.rcParams['figure.figsize'] = [16*size_gain, 9*size_gain]    # 尺寸

        self.nums = [4,3] if nums==None else nums

        figsize = [float(n) for n in figsize.split(':')]
        plt.rcParams['figure.figsize'] = [figsize[0]*size_gain, figsize[1]*size_gain]    # 尺寸

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
            fig_obj = plt.figure()

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
            plt.close()

        return None

    def plot_hz(self, list3d_y, samplerates, block_sizes, hz_range=None, linetypes=None, linewidth=1):
        """
            频域图 - PSD
            list3d_y    : [list2d_y, list2d_y, ...]
            samplerates : 采样频率 [512, 512,...]
            block_sizes : 块尺寸大小 [1024, 1024, ...]
            hz_range    : 频域显示范围 [0, 50]
            linetypes   : 线段类型 ['b', 'r--']
        """
        # ==============================
        nums = self.nums
        if linetypes == None:
            linetypes = ['b', 'r--']

        num_plot = nums[0] * nums[1]
        len_rpc = len(list3d_y[0])
        num_fig = math.ceil(len_rpc/num_plot) # figure 个数

        fig_loc = 0
        for n in range(num_fig):
            path = self.fig_path + f'_hz_{n}.png'
            self.fig_paths['hz'].append(path)
            fig_obj = plt.figure()

            for loc in range(num_plot):
                nloc = loc + n*num_plot
                if nloc >= len_rpc:
                    break

                ax1 = fig_obj.add_subplot(nums[0], nums[1], loc+1)

                for list2d_y, samplerate, block_size, linetype in zip(list3d_y, samplerates, block_sizes, linetypes):

                    psd_hz, psd_y = freqcal.psd(list2d_y[nloc], samplerate, nperseg=block_size)
                    
                    if hz_range != None:
                        psd_hz, psd_y = np.array(psd_hz), np.array(psd_y)
                        arr_loc = array_range(psd_hz, hz_range)
                        psd_hz, psd_y = psd_hz[arr_loc], psd_y[arr_loc]

                    ax1.plot(psd_hz, psd_y, linetype, linewidth=linewidth, alpha=1)
                
                ax1.legend(self.legends['hz'])
                ax1.set_ylabel(self.ylabels['hz'][fig_loc])
                if isinstance(self.xlabels['hz'], list):
                    ax1.set_xlabel(self.xlabels['hz'][fig_loc])
                else:
                    ax1.set_xlabel(self.xlabels['hz'])
                fig_loc += 1

            fig_obj.tight_layout()
            fig_obj.savefig(path)
            # 关闭图像-减少内存占用
            plt.close()

        return None


# ======================================================================
# 测试

# ======================================================================
# 鼠标交互, 截取图像X范围
# 左键定义开始, 右键定义结束, 中键确认结束
# ======================================================================

def plot_get_x_range(xs, ys, xlabel=None, ylabel=None, title=None, legend=None):

    # 图像交互, 通过鼠标左/右截取X范围
    class PlotDataMousePress2: # 数据存储
        mouse_left  = None
        mouse_right = None
        mouse_left_pointx  = None
        mouse_right_pointx = None
        mouse_x2 = [None, None]
        mouse_y2 = [None, None]

    def mouse_on_key_press(event): # 鼠标按键回调函数
        # 按键
        x, y = event.xdata, event.ydata

        if x==None or y==None: return None

        axes_obj = event.inaxes

        if event.button == 1:
            # 左
            if PlotDataMousePress2.mouse_left != None:
                PlotDataMousePress2.mouse_left.remove()
                # PlotDataMousePress2.mouse_left_pointx.remove()
            PlotDataMousePress2.mouse_x2[0] = x
            PlotDataMousePress2.mouse_y2[0] = y
            PlotDataMousePress2.mouse_left = axes_obj.axvline(x=x, color='green', linestyle='--')
        elif event.button == 3:
            # 右
            if PlotDataMousePress2.mouse_right != None:
                PlotDataMousePress2.mouse_right.remove()
                # PlotDataMousePress2.mouse_right_pointx.remove()
            PlotDataMousePress2.mouse_x2[1] = x
            PlotDataMousePress2.mouse_y2[1] = y
            PlotDataMousePress2.mouse_right = axes_obj.axvline(x=x, color='blue', linestyle='--')
            # PlotDataMousePress2.mouse_right = axes_obj.axvline(x=x, color='blue', linestyle='--')

        x_start,x_end = PlotDataMousePress2.mouse_x2
        if x_start != None:
            str1 = f'Start: {x_start:0.2f}\n'
        else:
            str1 = f'Start: None\n'
        if x_end != None:
            str2 = f'End: {x_end:0.2f}'
        else:
            str2 = 'End: None'
        
        plt.title(title + '\n' + str1 + str2)
        plt.close() if event.button==2 else plt.draw()

        return None

    
    # 图像设置
    fig = plt.figure()

    if isinstance(ys[0], list):
        for yline in ys:
            plt.plot(xs, yline)        
            plt.xlabel(xlabel)
        plt.legend(legend)
        print(111)
    else:
        plt.plot(xs, ys)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
    
    plt.title(title)
    fig.canvas.mpl_connect('button_press_event', mouse_on_key_press)
    plt.show()

    return PlotDataMousePress2.mouse_x2

# ===========================================================
# 测试函数

def test_plot_get_x_range(): # 测试
    
    x_list, y_list = [1,2,3,4,5,6,7],[1,2,3,4,5,6,7]
    y_list2 = [value*2 for value in y_list]
    print(plot_get_x_range(x_list, [y_list,y_list2], 'x', 'y', title = 's', legend=['a', 'b']))
    # print(plot_get_x_range(x_list, y_list, 'x', 'y'))

def test_FigPlot():

    fig_path = r'..\tests\datacal_plot\test'
    figobj = FigPlot()
    figobj.set_figure()

    figobj.plot_ts(
        [[1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8]],
        [1,2,3,4,5,6,7,8],
        linetype='b',
        )

    figobj.plot_ts(
        [[3,2,3,4,5,6,7,8],[3,2,3,4,5,6,7,8],[4,2,3,4,5,6,7,8],[5,2,3,4,5,6,7,8],[4,2,3,4,5,6,7,8],[3,2,3,4,5,6,7,8]],
        [1,2,3,4,5,6,7,8],
        linetype='r',
        plottype='scatter'
        )

    figobj.set_ylabel(['1','2','3','4','5','6'], 'ts')
    figobj.set_xlabel('time(s)', 'ts')
    figobj.set_legend(['a', 'b'], 'ts')
    figobj.updata('ts')
    
    

    t1 = np.sin(np.arange(1000)/512).tolist()
    t2 = (2*np.sin(np.arange(1000)/512)).tolist()

    figobj.plot_hz([t1,t2,t1,t2,t1], samplerate=512, block_size=512, hz_range=[0,20], linetype='r')
    figobj.plot_hz([t2,t1,t2,t1,t2], samplerate=512, block_size=512, hz_range=[0,20], linetype='b')
    figobj.set_ylabel(['1','2','3','4','5'], 'hz')
    figobj.set_xlabel('Hz', 'hz')
    figobj.set_legend(['a', 'b'], 'hz')
    figobj.updata('hz')

    figobj.save(fig_path)
    figobj.show()
    return None




if __name__ == '__main__':
    pass
    # import pyadams.file.file_edit as file_edit
    # dic1 = file_edit.var_read(r'..\code_test\temp_var')

    # res_data = dic1['res_data']
    # target_data = dic1['target_data']
    
    test_plot_get_x_range()
    # test_FigPlot()

    # plot_ts_hz(res_data, target_data, samplerate=[512, 512], block_size=[1024, 1024],
    #   res_x=None, target_x=None, ylabels=['test']*len(res_data), 
    #   nums=[2,2], figpath=r'..\code_test\fig_test', isShow=True, isHzPlot=True, 
    #   hz_range=[0.5, 50])

    # plot_ts_hz_single(res_data, samplerate=512, block_size=1024,
    #   res_x=None, ylabels=['test']*len(res_data), 
    #   nums=[2,2], figpath=r'..\code_test\fig_test1', isShow=True, isHzPlot=False, 
    #   hz_range=[0.5, 50], size_gain=0.5)

    # plot_ts_hz_single(res_data, samplerate=512, block_size=1024,
    #   res_x=None, ylabels=['test']*len(res_data), 
    #   nums=[2,2], figpath=r'..\code_test\fig_test2', isShow=True, isHzPlot=False, 
    #   hz_range=[0.5, 50], size_gain=1)

    # 散点图
    # xs, ys = [], []
    # for x_line,y_line in zip(res_data, target_data):
    #   new_x_line, new_y_line = [], []
    #   for x,y in zip(x_line, y_line):
    #       new_x_line.append(x)
    #       new_y_line.append(y)
    #   xs.append(new_x_line)
    #   ys.append(new_y_line)

    # scatter_ts_single(xs, ys, ['x']*len(res_data), ['y']*len(res_data), figpath=None, nums=[1,1],
    #   isShow=False, size_gain=0.6, isGrid=False, linewidths=0.1, scatter_s=10)
    # os.remove('current_1.png')
    # os.remove('current_2.png')
    # os.remove('current_3.png')
