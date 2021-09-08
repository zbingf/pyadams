"""
    ADAMS-悬架台架迭代
    迭代目标:
        左右拉线位移
    迭代目标:
        轮胎垂向位移
"""

import os
import re
import sys
import subprocess
import json
import time
import shutil
import threading

from pyadams.call import threadingrun
from pyadams.file import result, admfile, file_edit
from pyadams.datacal import tscal
from pyadams.call import admrun

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

import pysnooper

import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


DataModel = result.DataModel


mpl.rcParams['font.sans-serif'] = [u'SimHei']
mpl.rcParams['axes.unicode_minus'] = False

LOADCASE_TITLE = """$---------------------------------------------------------------------MDI_HEADER
[MDI_HEADER]
 FILE_TYPE     =  'lcf'
 FILE_VERSION  =  6.0
 FILE_FORMAT   =  'ascii'
(COMMENTS)
{comment_string}
'Loadcase type -- Static Load'
$--------------------------------------------------------------------------UNITS
[UNITS]
 LENGTH  =  'mm'
 FORCE   =  'newton'
 ANGLE   =  'deg'
 MASS    =  'kg'
 TIME    =  'sec'
$
$Generation Parameters: (Do Not Modify!)
$ loadcase = 5
$ nsteps   = 100
$ steering_input  = angle
$ vertical_input  = wheel_center_height
$ steer_upper =     0.00    steer_lower =     0.00
$ align_upr_l =     0.00   align_upr_r =     0.00   align_lwr_l =     0.00   align_lwr_r =     0.00
$ otmom_upr_l =     0.00   otmom_upr_r =     0.00   otmom_lwr_l =     0.00   otmom_lwr_r =     0.00
$ r_res_upr_l =     0.00   r_res_upr_r =     0.00   r_res_lwr_l =     0.00   r_res_lwr_r =     0.00
$ verti_upr_l =    50.00   verti_upr_r =   -50.00   verti_lwr_l =   -50.00   verti_lwr_r =    50.00
$ later_upr_l =     0.00   later_upr_r =     0.00   later_lwr_l =     0.00   later_lwr_r =     0.00
$ dmrad_upr_l =     0.00   dmrad_upr_r =     0.00   dmrad_lwr_l =     0.00   dmrad_lwr_r =     0.00
$ damfr_upr_l =     0.00   damfr_upr_r =     0.00   damfr_lwr_l =     0.00   damfr_lwr_r =     0.00
$ brake_upr_l =     0.00   brake_upr_r =     0.00   brake_lwr_l =     0.00   brake_lwr_r =     0.00
$ drivn_upr_l =     0.00   drivn_upr_r =     0.00   drivn_lwr_l =     0.00   drivn_lwr_r =     0.00
$ drivn_upr_l =     0.00   drivn_upr_r =     0.00   drivn_lwr_l =     0.00   drivn_lwr_r =     0.00
$
$---------------------------------------------------------------------------MODE
[MODE]
 STEERING_MODE  =  'angle'
 VERTICAL_MODE_FOR_SETUP  =  'wheel_center_height'
 VERTICAL_MODE  =  'wheel_center_height'
 VERTICAL_TYPE  =  'absolute'
 COORDINATE_SYSTEM  =  'vehicle'
$---------------------------------------------------------------------------DATA
[DATA]
$COLUMN:  input type:  type of input data:                    side:
$ (c1)     wheel z         disp / force                          left
$ (c2)     wheel z         disp / force                          right
$ (c3)     lateral         force (y)                             left
$ (c4)     lateral         force (y)                             right
$ (c5)     damage_radius   disp                                  left
$ (c6)     damage_radius   disp                                  right
$ (c7)     damage_force    force                                 left
$ (c8)     damage_force    force                                 right
$ (c9)     aligning        torque (z-axis)                       left
$ (c10)    aligning        torque (z-axis)                       right
$ (c11)    brake           force (y)                             left
$ (c12)    brake           force (y)                             right
$ (c13)    driving         force (y)                             left
$ (c14)    driving         force (y)                             right
$ (c15)    otm             torque (z-axis)                       left
$ (c16)    otm             torque (z-axis)                       right
$ (c17)    roll res        torque (z-axis)                       left
$ (c18)    roll res        torque (z-axis)                       right
$ (c19)    steering        force / steer angle / rack travel
{ whl_z_l      whl_z_r        lat_l        lat_r      dam_rad_l      dam_rad_r      dam_for_l      dam_for_r      align_l      align_r      brake_l      brake_r      drive_l      drive_r      otm_l      otm_r      rollres_l      rollres_r        steer}
"""

class LoadcaseCal: #loadcase文件编辑及迭代
    
    # loadcase 文件读取/生成/迭代
    def __init__(self, rsp_path=None, lcf_path=None, channels=None):
        self.rsp_path = rsp_path
        self.lcf_path = lcf_path
        self.channels = channels

    def read_rsp(self, path=None, channels=None):
        """
            rsp数据读取源目标
            目标rsp共2个通道:左位移/右位移
            self.data 为 numpy.array 格式
        """
        if path==None:
            path = self.rsp_path
        if channels==None:
            channels = self.channels

        dataobj = DataModel('sus_ite')
        dataobj.new_file(path, 'rsp')
        dataobj['rsp'].set_select_channels(channels)
        dataobj['rsp'].read_file()
        self.data_list = dataobj['rsp'].get_data()

        # DataModel('rsp', path, isReload=True)
        # DataModel.channels['rsp'] = channels
        # self.data_list = DataModel.get_data('rsp')

        # self.data_list,_,_ = result.rsp_read(path)
        self.data = np.array(self.data_list)

    def get_data(self, start_n=None, end_n=None, dn=1):
        """
            截取源目标数据
            start_n 起始位置
            end_n   终点位置
            dn      截取间隔
        """
        if start_n==None or end_n==None:
            self.target_data = self.data
        else:
            if not isinstance(dn,int):
                dn = int(dn)
                logger.warning('注意:get_data() 输入的dn不为整数,已去小数位转为int类型')
            target_data = self.data[:,start_n:end_n:dn]
            self.target_data = target_data
        # print(self.target_data.shape)
        return self.target_data.shape

    def create_loadcase_str(self, left_arr=None, right_arr=None):
        """
            生成 loadcase 数据
            输入论条，转向默认为零
        """
        if left_arr == None:
            left_arr = self.wt_left
        if right_arr == None:
            right_arr = self.wt_right

        steplist = []
        for left,right in zip(left_arr, right_arr):
            temp = [str(round(left,2)),str(round(right,2))]
            temp.extend(['0.0' for n in range(17)])
            steplist.append(' '.join(temp))

        stepstr = '\n'.join(steplist)
        self.loadcase_file_str = LOADCASE_TITLE+stepstr
        return self.loadcase_file_str

    def write_file(self, str1=None, path=None):
        """
            文档写入 生成 loadcase 文档
            str1 导入的字符串
            path 导入目标路径
        """
        if str1 == None:
            str1 = self.loadcase_file_str
        else:
            self.loadcase_file_str = str1

        if path == None:
            path = self.lcf_path
        else:
            self.lcf_path = path

        with open(path,'w') as f:
            f.write(str1)

    def init_target_data(self, numleft=None, numright=None):
        """
            初始化 目标编辑
            目标值为拉线位移信号
            numleft     左
            numright    右
        """
        if numleft == None:
            self.target_left = self.target_data[0, :]
        else:
            self.target_left = self.target_data[0, numleft]

        if numright == None:
            self.target_right = self.target_data[1,:]
        else:
            self.target_right = self.target_data[1, numright]

        return True

    def init_wheel_travel(self, left=None, right=None, k=1):
        """
            初始化论条值，将初始拉线位移信号作为轮跳输入
            left 和 right 均为 numpy.array 一位数据
            wt_left 左轮跳
            wt_right 右轮跳
        """
        if left == None:
            self.wt_left = -self.target_left*k # 数据需取反，因为拉线位移拉伸为正
        else:
            self.wt_left = left

        if right==None:
            self.wt_right = -self.target_right*k
        else:
            self.wt_right = right

    def iterate_wheel_travel(self, sim_left, sim_right, k=1):
        """
            迭代轮跳，简化后的牛顿迭代
            减振器拉伸为正
            sim_left 和 sim_right 均为 numpy.array 一维数据，仿真结果数据，拉线位移
        """
        if isinstance(sim_left,list):
            sim_left = np.array(sim_left)
            sim_right = np.array(sim_right)

        self.wt_left = self.wt_left - k*(self.target_left - sim_left)
        self.wt_right = self.wt_right - k*(self.target_right - sim_right)

        self.sim_left = sim_left
        self.sim_right = sim_right

        return True

    def read_loadcase_wheel_travel(self, lcf_path):
        """
            读取lcf_path 的轮跳数据
        """
        with open(lcf_path,'r') as f:
            str1 = f.read()
        start = False
        wt_left_list = []
        wt_right_list = []
        for line in str1.split('\n'):
            if start and line!='':
                list1 = [n for n in line.split(' ') if n]
                # print(line)
                wt_left_list.append(float(list1[0]))
                wt_right_list.append(float(list1[1]))
            if '{ whl_z_l' in line:
                start = True

        self.wt_left = np.array(wt_left_list)
        self.wt_right = np.array(wt_right_list)

        return self.wt_left, self.wt_right

    def compare(self):
        # 对比数据
        t_left = [self.target_left.tolist()]
        t_right = [self.target_right.tolist()]
        s_left = [self.sim_left.tolist()]
        s_right = [self.sim_right.tolist()]

        lr = tscal.cal_rms_delta_percent(s_left, t_left)
        rr = tscal.cal_rms_delta_percent(s_right, t_right)

        lp = tscal.cal_pdi_relative(s_left, t_left)
        rp = tscal.cal_pdi_relative(s_right, t_right)

        return {'pdi':{'l':lp[0],'r':rp[0]}, 'drms':{'l':lr[0],'r':rr[0]}}

class SusIte: # 悬架装配系统 loadcase迭代
    
    def __init__(self, params):
        """
            输入数据:

            params = {
                'rsp_path'  str         迭代目标rsp路径，共2个通道，左位移&右位移信号
                'lcf_path'  str         loadcase文件路径
                'adm_path'  str         adm模型文件路径
                'requests'  list[str]   检测信号 requests
                'components' list[str]  检测信号 components
                'k'         float       迭代比值，k越高迭代越快
                'isStartLcf'bool        是否直接使用loadcase开始迭代
                'init_dis'  [float,float]       信号初始长度（eg:减振器初始长度）
                'loc_offset'int         仿真后处理截取，开始位置
                'channels'  [int, int]  rsp文件通道截取
            }   
            迭代还需 acf文件 与 adm文件 同路径

        """

        self.rsp_path       = params['rsp_path']
        self.lcf_path       = params['lcf_path']
        self.adm_path       = params['adm_path']
        self.requests       = params['requests']
        self.components     = params['components']
        self.k              = params['k']
        self.isStartLcf     = params['isStartLcf']
        self.init_dis       = params['init_dis']
        self.version        = str(params['version'])
        self.channels       = params['channels']
        self.isPlot         = params['isPlot']
        self.res_channels   = params['res_channels']

        if 'loc_offset' in params.keys():
            self.loc_offset = params['loc_offset']
        else:
            self.loc_offset = 2

        self.res_path = self.adm_path[:-4]+'.res'
        self.lcobj = LoadcaseCal(self.rsp_path, self.lcf_path, self.channels)

    def adm_run(self, step=None):
        """
            运行adm模型文件
        """
        adm_path = self.adm_path
        if step == None:
            step = len(self.lcobj.wt_left)

        admrun.admrun_car_sus(adm_path, step+1, step, version=self.version)

    def res_read(self, init_dis=None, offset=1):
        """
            res读取
            仿真数据 init_dis 初始长度
        """
        if init_dis == None:
            init_dis = self.init_dis
        components = self.components
        requests = self.requests
        res_path = self.res_path
        res_channels = self.res_channels

        dataobj = DataModel('sus_ite')
        dataobj.new_file(res_path, res_path)
        dataobj[res_path].set_reqs_comps(requests, components)
        dataobj[res_path].read_file_faster()
        dataobj[res_path].set_select_channels(None)
        dataobj[res_path].set_line_ranges([offset, None])
        csv_data = dataobj[res_path].get_data()

        # DataModel('res',res_path,reqs=requests,comps=components,isReload=True, isResRealTime=True)
        # DataModel.channels['res']     = None
        # DataModel.nranges['res']  = [offset, None]
        # csv_data = DataModel.get_data('res')

        file_edit.data2csv(self.lcf_path[:-3]+'csv', csv_data, reqs=requests, comps=components)
        
        # DataModel.channels['res'] = res_channels
        # DataModel.nranges['res']  = [None, None]
        # data = DataModel.get_data('res')

        dataobj[res_path].set_select_channels(res_channels)
        # dataobj['res'].set_line_ranges([None, None])
        data = dataobj[res_path].get_data()

        # resobj = result.ResFile(res_path)
        # data = resobj.data_request_get(requests, components, isSave=True)
        # data = np.array(data)

        data_arr = np.array(data) # [:,offset:]
        data_arr[0,:] = data_arr[0,:] - init_dis[0]
        data_arr[1,:] = data_arr[1,:] - init_dis[1]

        self.data = data_arr

        return self.data

    def adm_edit(self):
        """
            adm文件 spline 修改
        """
        admobj = admfile.AdmCar(self.adm_path)
        spobj = admobj.model.spline['testrig.loadcase_spline']
        ylist = [0]*20
        wt_left = self.lcobj.wt_left
        wt_right = self.lcobj.wt_right
        for loc in range(len(wt_left)):
            l = round(wt_left[loc],3)
            r = round(wt_right[loc],3)
            temp = [loc+1] + [l,r] + [0]*17
            ylist += temp
        spobj.updata_3d(ylist=ylist, x_gain=1, y_gain=1)
        admobj.updata()
        admobj.newfile()

    def first_iterate(self):
        """
            首次计算，进行初始赋值
        """
        self.lcobj.read_rsp()           # 读取rsp数据
        self.lcobj.get_data()           # 获取拉线位移数据
        self.lcobj.init_target_data()   # 初始化左右 拉线位移
        if self.isStartLcf:
            self.lcobj.read_loadcase_wheel_travel(self.lcf_path) # 导入loadcase数据
        else:
            self.lcobj.init_wheel_travel()  # 初始化轮跳值
        self.lcobj.create_loadcase_str()    # 拼成loadcase文件
        self.lcobj.write_file()             # 生成loadcase文件

        self.adm_edit()     # 模型修改
        self.adm_run()      

    def iterate(self, max_n=10, target_pdi_delta=0.05): # 迭代
        """
            max_n               int     最大迭代次数
            target_pdi_delta    float   目标相对伪损伤-差值，0为最优目标
        """

        for n in range(max_n):
            logger.info(f'Iteration num: {n+1}')
            data = self.res_read(offset=self.loc_offset) # 读取数据
            left, right = data[0,:], data[1,:]
            # 迭代更新
            self.lcobj.iterate_wheel_travel(left, right, k=self.k)

            res_dic = self.lcobj.compare()
            logger.info(f'res_dic:{res_dic}')
            if res_dic['pdi']['l']>1-target_pdi_delta and res_dic['pdi']['l']<1+target_pdi_delta :
                if res_dic['pdi']['r']>1-target_pdi_delta and res_dic['pdi']['r']<1+target_pdi_delta:
                    break

            if n == max_n-1:
                break

            self.lcobj.create_loadcase_str()
            self.lcobj.write_file()

            self.adm_edit()
            self.adm_run()

        plt.rcParams['savefig.dpi'] = 500
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.figsize'] = [16, 9]    # 尺寸
        target_data = self.lcobj.target_data
        current_data = self.data
        xs = list(range(len(target_data[0,:])))

        if self.isPlot:
            fig1 = plt.figure()
            ax1 = fig1.add_subplot(2, 1, 1)
            ax2 = fig1.add_subplot(2, 1, 2)

            ax1.plot(xs, target_data[0,:], 'k')
            ax1.plot(xs, current_data[0,:], 'r--')
            ax1.legend(['left 目标', 'left 仿真'])
            ax2.plot(xs, target_data[1,:], 'k')
            ax2.plot(xs, current_data[1,:], 'r--')
            ax2.legend(['right 目标', 'right 仿真'])

            plt.tight_layout()
            plt.savefig(self.adm_path[:-4]+'.png')
            plt.show()

        return res_dic

def sus_ite_threading(params):
    """
    params = {
        'max_threading' : int,              # 最大线程数
        'rsp_paths'     : [rsp_path,...],   # 目标数据
        'adm_path'      : adm_path, 
        'requests'      : ['dal_ride_damper_data', 'dar_ride_damper_data', 'nsl_ride_spring_data', 'nsr_ride_spring_data'],
        'components'    : ['displacement_front', 'displacement_front', 'displacement_front', 'displacement_front'],
        'k'             : 0.5,      # 迭代比例
        'isStartLcf'    : False,               # 是否从lcf文件开始计算
        'init_dis'      : [271.4453,271.4453], # 初始长度
        'loc_offset'    : 2,        # 计算结果res起始偏置
        'version'       : '2019',   # 计算adams版本
        'channels'      : [0, 1],   # 目标数据通道截取
        'isPlot'        : False,    # 是否作图
        'res_channels'  : [0,1],    # 计算结果通道截取
        'maxit'         : 4,        # 最大迭代数
    }
    """
    

    output_data = {}

    threadmax = threading.BoundedSemaphore(params['max_threading'])     # 多线程初始设置,设置线程上限
    sim_path = params['adm_path']

    threads = []
    for num, path in enumerate(params['rsp_paths']):
        
        new_sim_path, new_dir = threadingrun.threading_car_files(sim_path, num, prefix='sus_ite')
        params['adm_path'] = new_sim_path
        params['rsp_path'] = path
        params['lcf_path'] = path[:-4] + '.lcf'

        def main_cal(params):
            
            cur_path = params['rsp_path']
            # time.sleep(1)
            # logger.info(f'cur_path:{cur_path}')
            # output_data[cur_path] = num
            # res_dic = None
            subobj = SusIte(params)
            subobj.first_iterate()
            res_dic = subobj.iterate(params['maxit'])
            output_data[cur_path] = res_dic
            return res_dic

        new_func = threadingrun.threading_func(main_cal, threadmax=threadmax)
        thread = threading.Thread(target=new_func, args=(params, ))
        thread.start()
        threads.append(thread)
        threadmax.acquire()
        time.sleep(1)
        logger.info(f'run:{num}')
        logger.info(f'rsp_path:{path}')
    
    while threads:
        threads.pop().join()

    for key in output_data:
        logger.info(f'rsp_path:{key}')
        logger.info(f'res_dic:{output_data[key]}')

    return output_data


# =================================================================

# sus_ite 测试
def test_sus_ite():

    rsp_path = r'..\tests\car_sus_ite\sus_ite_init0.rsp'
    lcf_path = r'..\tests\car_sus_ite\test_load.lcf'
    adm_path = r'..\tests\car_sus_ite\test_front_sus_suspnsn.adm'
    rsp_path = os.path.abspath(rsp_path)
    lcf_path = os.path.abspath(lcf_path)
    adm_path = os.path.abspath(adm_path)

    # acf_path 与 adm_path同路径
    params = {
        'rsp_path' : rsp_path,
        'lcf_path' : lcf_path,
        'adm_path' : adm_path,
        'requests'  : ['dal_ride_damper_data', 'dar_ride_damper_data', 'nsl_ride_spring_data', 'nsr_ride_spring_data'],
        'components': ['displacement_front', 'displacement_front', 'displacement_front', 'displacement_front'],
        'k'        : 0.5,
        'isStartLcf' : False,
        'init_dis' : [271.4453,271.4453],
        'loc_offset' : 2,
        'version' : '2019',
        'channels': [0, 1],
        'isPlot'  : False,
        'res_channels' : [0,1],
    }

    subobj = SusIte(params)
    subobj.first_iterate()
    res_dic = subobj.iterate(1)

    # 多余文档删除
    cal_path = os.path.abspath(r'..\tests\car_sus_ite')

    file_edit.file_remove_pt(cal_path, prefix=None, file_type='sav')
    file_edit.file_remove_pt(cal_path, prefix=None, file_type='bak')
    file_edit.file_remove_pt(cal_path, prefix=None, file_type='wev')
    file_edit.file_remove_pt(cal_path, prefix=None, file_type='res')
    file_edit.file_remove_pt(cal_path, prefix=None, file_type='bat')
    file_edit.file_remove_pt(cal_path, prefix=None, file_type='csv')
    file_edit.file_remove_pt(cal_path, prefix=None, file_type='lcf')
    file_edit.file_remove_pt(cal_path, prefix=None, file_type='msg')

    print(res_dic)

    return None


# sus_ite 多线程计算测试
def test_sus_ite_threading():

    rsp_path = r'..\tests\car_sus_ite\sus_ite_init0.rsp'
    adm_path = r'..\tests\car_sus_ite\test_front_sus_suspnsn.adm'
    rsp_path = os.path.abspath(rsp_path)
    adm_path = os.path.abspath(adm_path)

    rsp_paths = [
        os.path.abspath(r'..\tests\car_sus_ite\sus_ite_init0.rsp'),
        os.path.abspath(r'..\tests\car_sus_ite\sus_ite_init0_0p8_gain.rsp'),
        os.path.abspath(r'..\tests\car_sus_ite\sus_ite_init0_0p8_gain_0.rsp'),
        ]

    params = {
        'max_threading' : 3, # 最大线程数
        'rsp_paths' : rsp_paths,
        'adm_path' : adm_path,
        'requests'  : ['dal_ride_damper_data', 'dar_ride_damper_data', 'nsl_ride_spring_data', 'nsr_ride_spring_data'],
        'components': ['displacement_front', 'displacement_front', 'displacement_front', 'displacement_front'],
        'k'        : 0.5,
        'isStartLcf' : False,
        'init_dis' : [271.4453,271.4453],
        'loc_offset' : 2,
        'version' : '2019',
        'channels': [0, 1],
        'isPlot'  : False,
        'res_channels' : [0,1],
        'maxit' : 1, # 最大迭代数
    }

    output_data = sus_ite_threading(params)


    print(output_data)
    # 判断
    # logger.info(f'output_data:{output_data}')
    for rsp_path in rsp_paths:
        if rsp_path not in output_data:
            assert 0, rsp_path


    # 删除文件夹
    for path in [
        os.path.abspath(r'..\tests\car_sus_ite\sus_ite_0'),
        os.path.abspath(r'..\tests\car_sus_ite\sus_ite_1'),
        os.path.abspath(r'..\tests\car_sus_ite\sus_ite_2'),]:

        shutil.rmtree(path)

    file_edit.file_remove_pt(r'..\tests\car_sus_ite', prefix=None, file_type='csv')
    file_edit.file_remove_pt(r'..\tests\car_sus_ite', prefix=None, file_type='lcf')


    return None


if __name__=='__main__':
    pass

    # test_sus_ite()
    test_sus_ite_threading()