"""
    卡车静力工况载荷分解 
    version: 1.0
    
    卡车工况轮胎接地点 Fx、Fy、Fz
        + 2轴车
    
    工况：
        + 倒车制动 front_brake_g
        + 紧急制动 rear_brake_g
        + 向前加速 acc_g
        + 转向    lateral_g
        + 满载重力 z_g
        + 转向制动 
          + 纵向加速度 brake_lateral_x
          + 侧向加速度 brake_lateral_y
        + 深坑路
          + 载荷转移量 single_hole_ratio 
        + 扭曲路-单轮
          + 载荷转移量 single_jack_ratio
        + 扭曲路-对角
          + 载荷转移量 diagonal_jack_ratio 
    
    整车状态car_param：
        + 两轴车
            + 质心高 mass_h
            + 质心距到前轴距离 mass_x
            + 总质量 mass_full
            + 轴距 wheel_base
            + 轮距 wheel_track
    
    仿真形式: cmd 调用 adams 进行仿真

"""

# 标准库
import abc
import copy
import time
import threading
import os
import re
import json
import copy
import logging
import pprint
import csv

# 调用库
import xlsxwriter

# 自建库
import pysnooper
from pyadams.call import threadingrun, cmdlink
from pyadams.file import result


# ----------
logger = logging.getLogger('truck_load')
logger.setLevel(logging.DEBUG)
is_debug = True


# ----------
DataModel = result.DataModel
cmd_file_send = cmdlink.cmd_file_send
cmd_send = cmdlink.cmd_send


# =================================================

# 字典参数转化为字符串
def change_dict_to_str(dict1):
    str_params = pprint.pformat(dict1)
    str_params = str_params.replace('\\n', '')
    str_params = str_params.replace('\'', '')
    str_params = re.sub('\n\s+\n', '\n', str_params)
    return str_params


# =================================================
# =================================================
# 常数
G = 9.8 # 重力加速度
FLOAT_ROUND = 2  # float保留位数
NAME_ROUND = 2   # 名称重点数字保留位数

# 质量相加, dict
def add_mass(mass1, mass2):
    mass_output = {}
    for key in mass1:
        mass_output[key] = mass1[key] + mass2[key]

    return mass_output

# 质量乘以常量, dict
def multi_mass(mass1, k):
    mass_output = {}
    for key in mass1:
        mass_output[key] = k * mass1[key]
    return mass_output

# 质量相减, dict
def sub_mass(mass1, mass2):
    mass_output = {}
    for key in mass1:
        mass_output[key] = mass1[key] - mass2[key]

    return mass_output     

# 2轴数据, 静态计算, 不考虑左右不对称问题
def mass_static_2axle(car_param):
    """
        2轴车 - 质量计算
        假定：左右轮荷载相等
        car_param 字典, 存储车辆数据
            + 总质量 mass_full
            + 质心高 mass_h
            + 轴距 wheel_base

        output:
            mass_static = {
                'fl': mass_front / 2,
                'fr': mass_front / 2,
                'rl': mass_rear / 2,
                'rr': mass_rear / 2,
            }
    """
    mass_x = car_param['mass_x']
    mass_full = car_param['mass_full']
    wheel_base = car_param['wheel_base']

    mass_rear  = (mass_x * mass_full) / wheel_base
    mass_front = mass_full - mass_rear

    mass_static = {
        'fl': mass_front / 2,
        'fr': mass_front / 2,
        'rl': mass_rear / 2,
        'rr': mass_rear / 2,
    }
    return mass_static


# =================================================
# =================================================
# 工况定义

# 两轴数据加载
class Load2Axle(abc.ABC):

    def __init__(self, car_param, event_param):
        self.car_param = car_param
        self.event_param = event_param
        self.mass_dz = {}
        self.mass_dy = {}
        self.mass_dx = {}

    @abc.abstractmethod
    def calc_z_delta_mass(self):
        pass

    @abc.abstractmethod
    def calc_y_delta_mass(self):
        pass

    @abc.abstractmethod
    def calc_x_delta_mass(self):
        pass

    # 静载轮荷计算
    def get_mass_static(self):
        """
            2轴车 - 质量计算
            假定：左右轮荷载相等
            car_param 字典, 存储车辆数据
                + 总质量 mass_full
                + 质心高 mass_h
                + 轴距 wheel_base
        """
        return mass_static_2axle(self.car_param)

    @staticmethod
    def get_mass_front_k(mass1):
        """
            前轴质量占比
        """
        front_mass = mass1['fl'] + mass1['fr']
        rear_mass = mass1['rl'] + mass1['rr']
        full_mass = front_mass + rear_mass
        return front_mass / full_mass

    @staticmethod
    def get_mass_left_k(mass1):
        """
            左右轮荷占比
        """
        front_left_k = mass1['fl'] / ( mass1['fl'] + mass1['fr'] )
        rear_left_k  = mass1['rl'] / ( mass1['rl'] + mass1['rr'] )
        return front_left_k, rear_left_k

    def get_xyz_delta_mass(self, x_param=None, y_param=None, z_param=None):
        """
            x、y、z计算
        """
        mass_d = {}
        type_names = ['dx', 'dy', 'dz']
        params = [x_param, y_param, z_param]
        funcs  = [self.calc_x_delta_mass, self.calc_y_delta_mass, self.calc_z_delta_mass]
        for type_name, n_param, func in zip(type_names, params, funcs):
            if n_param != None:
                mass_d[type_name] = func(**n_param)
            else:
                mass_d[type_name] = func()
        return mass_d



# 制动工况 向前\向后均可
class Brake2Axle(Load2Axle):
    """
        默认紧急制动, 即制动加速度:
            +为正常制动
            -为倒车制动
        Fx 正向朝车尾
    """
    def __init__(self, car_param, event_param):
        """
            event_param {
                'brake_g': float,
            }
            car_param {
                'wheel_base': float,
                'mass_h': float,
                'mass_full': float,
                'mass_x':float,
            }
        """
        super().__init__(car_param, event_param)
        # self.brake_g = event_param['brake_g']
        # self.brake_ratio = None

    def calc_z_delta_mass(self):
        brake_g      = self.event_param['brake_g']
        wheel_base   = self.car_param['wheel_base']
        mass_h       = self.car_param['mass_h']
        mass_full    = self.car_param['mass_full']
        mass_delta   = (mass_full * mass_h * brake_g) / wheel_base
        mass_dz = {
            'fl': mass_delta / 2,
            'fr': mass_delta / 2,
            'rl': -mass_delta / 2,
            'rr': -mass_delta / 2,
        }
        self.mass_dz = mass_dz
        return mass_dz

    def calc_x_delta_mass(self, mass_static=None):
        # 假定车轮抱死
        brake_g = self.event_param['brake_g']
        if mass_static==None: # 未定义mass_static
            mass_static = self.get_mass_static()
            mass_dz = self.calc_z_delta_mass()
        else:
            mass_dz = mass_static
        mass_z_cur = add_mass(mass_dz, mass_static)
        mass_dx = multi_mass(mass_z_cur, brake_g)

        self.mass_dx = mass_dx
        return mass_dx

    def calc_y_delta_mass(self):
        # 侧向不受力
        mass_dy = {
            'fl': 0,
            'fr': 0,
            'rl': 0,
            'rr': 0,
        }
        self.mass_dy = mass_dy
        return mass_dy


# 侧向（转弯）工况
class Lateral2Axle(Load2Axle):
    
    def __init__(self, car_param, event_param):
        """
            侧向加速度向右为正
            event_param {
                'lateral_g': float,
            }
            car_param {
                'wheel_base': float,
                'wheel_track': float,
                'mass_h': float,
                'mass_full': float,
                'mass_x': float,
            }
        """
        super().__init__(car_param, event_param)
        # self.lateral_g = None

    def calc_z_delta_mass(self, mass_static=None):
        """
            根据前后轴荷配比，确认前后载荷转移量
        """
        lateral_g = self.event_param['lateral_g']
        wheel_track = self.car_param['wheel_track']
        # wheel_base = self.car_param['wheel_base']
        mass_h = self.car_param['mass_h']
        mass_full = self.car_param['mass_full']
        # mass_x = self.car_param['mass_x']

        if mass_static==None:
            mass_static = self.get_mass_static()

        front_k = self.get_mass_front_k(mass_static)
        rear_k  = 1 - front_k
        mass_delta_z = ( mass_h * mass_full * lateral_g) / wheel_track
        mass_dz = {
            'fl': -mass_delta_z * front_k,
            'fr': mass_delta_z * front_k,
            'rl': -mass_delta_z * rear_k,
            'rr': mass_delta_z * rear_k,
        }
        self.mass_dz = mass_dz
        return mass_dz

    def calc_y_delta_mass(self, mass_static=None):
        """
            根据前后轴荷配比, 确定Y向受载
        """
        lateral_g = self.event_param['lateral_g']
        mass_h = self.car_param['mass_h']
        mass_full = self.car_param['mass_full']
        
        if mass_static==None:
            mass_static = self.get_mass_static()

        front_k = self.get_mass_front_k(mass_static)
        rear_k  = 1 - front_k

        front_left_k, rear_left_k = self.get_mass_left_k(mass_static)

        mass_delta_y = ( mass_full * lateral_g) 
        mass_dy = {
            'fl': mass_delta_y * front_k * front_left_k,
            'fr': mass_delta_y * front_k * ( 1 - front_left_k ),
            'rl': mass_delta_y * rear_k * rear_left_k,
            'rr': mass_delta_y * rear_k * ( 1 - rear_left_k ),
        }
        self.mass_dy = mass_dy
        return mass_dy

    def calc_x_delta_mass(self):
        """
            纵向不受力
        """
        mass_dx = {
            'fl': 0,
            'fr': 0,
            'rl': 0,
            'rr': 0,
        }
        self.mass_dx = mass_dx
        return mass_dx


# 后轴加速工况
class RAcc2Axle(Load2Axle):
    """
        后轮驱动

    """
    def __init__(self, car_param, event_param):
        """
            向前加速为正
            力值向前为负
            event_param {
                'acc_g': float,
            }
            car_param {
                'wheel_base': float,
                'wheel_track': float,
                'mass_h': float,
                'mass_full': float,
                'mass_x': float,
            }
        """
        super().__init__(car_param, event_param)

    def calc_z_delta_mass(self):
        """
            载荷转移量默认左右对称         
        """
        acc_g    = self.event_param['acc_g']
        wheel_base   = self.car_param['wheel_base']
        mass_h       = self.car_param['mass_h']
        mass_full    = self.car_param['mass_full']
        mass_delta   = (mass_full * mass_h * acc_g) / wheel_base

        mass_dz = {
            'fl': -mass_delta / 2,
            'fr': -mass_delta / 2,
            'rl': mass_delta / 2,
            'rr': mass_delta / 2,
        }
        self.mass_dz = mass_dz
        return mass_dz

    def calc_x_delta_mass(self, mass_static=None):
        """
            假定驱动力矩左右一致
        """
        acc_g    = self.event_param['acc_g']
        mass_full    = self.car_param['mass_full']
        mass_delta_x   = (mass_full * acc_g)

        # if mass_static==None:
        #   mass_static = self.get_mass_static()

        mass_dx = {
            'fl': 0,
            'fr': 0,
            'rl': -mass_delta_x / 2,
            'rr': -mass_delta_x / 2,
        }
        self.mass_dx = mass_dx
        return mass_dx

    def calc_y_delta_mass(self):
        """
            侧向不受力
        """
        mass_dy = {
            'fl': 0,
            'fr': 0,
            'rl': 0,
            'rr': 0,
        }
        self.mass_dy = mass_dy
        return mass_dy


# 垂向工况
class Vertical2Axle(Load2Axle):

    def __init__(self, car_param, event_param):
        super().__init__(car_param, event_param)

    def calc_x_delta_mass(self):
        """
            纵向不受力
        """
        mass_dx = {
            'fl': 0,
            'fr': 0,
            'rl': 0,
            'rr': 0,
        }
        self.mass_dx = mass_dx
        return mass_dx

    def calc_y_delta_mass(self):
        """
            侧向不受力
        """
        mass_dy = {
            'fl': 0,
            'fr': 0,
            'rl': 0,
            'rr': 0,
        }
        self.mass_dy = mass_dy
        return mass_dy

    def calc_z_delta_mass(self):
        pass


# 单轮顶起工况
class SingleJack2Axle(Vertical2Axle):

    def __init__(self, car_param, event_param):
        """
            侧向加速度向右为正
            event_param {
                'single_jack_ratio': float, # 左右载荷转移量
            }
        """

        super().__init__(car_param, event_param)

    def calc_z_delta_mass(self, loc, mass_static=None,):
        """
            假定前后无载荷转移
        """
        single_jack_ratio = self.event_param['single_jack_ratio']

        if mass_static==None:
            mass_static = self.get_mass_static()

        if loc[0] == 'f':
            load_type = 0
            if loc=='fl':
                otherside = 'fr'
            else:
                otherside = 'fl'
        else:
            load_type = 1
            if loc=='rl':
                otherside = 'rr'
            else:
                otherside = 'rl'
        
        if load_type == 0:
            # front
            mass_dz = {
                loc: + mass_static[loc] * single_jack_ratio,
                otherside: - mass_static[loc] * single_jack_ratio,
                'rl':0,
                'rr':0,
            }
        else:
            # rear
            mass_dz = {
                'fl':0,
                'fr':0,
                loc: + mass_static[loc] * single_jack_ratio,
                otherside: - mass_static[loc] * single_jack_ratio,
            }
        self.mass_dz = mass_dz
        return mass_dz


# 单轮胎下降
class SingleHole2Axle(Vertical2Axle):

    def __init__(self, car_param, event_param):
        """
            单轮胎下降
            event_param {
                'single_hole_ratio': float, # 左右载荷转移量
            }
        """
        super().__init__(car_param, event_param)

    def calc_z_delta_mass(self, loc, mass_static=None,):
        """
            假定前后无载荷转移
        """
        single_hole_ratio = self.event_param['single_hole_ratio']

        if mass_static==None:
            mass_static = self.get_mass_static()

        if loc[0] == 'f':
            load_type = 0
            if loc=='fl':
                otherside = 'fr'
            else:
                otherside = 'fl'
        else:
            load_type = 1
            if loc=='rl':
                otherside = 'rr'
            else:
                otherside = 'rl'
        
        if load_type == 0:
            # front
            mass_dz = {
                loc: -mass_static[loc] * single_hole_ratio,
                otherside: mass_static[loc] * single_hole_ratio,
                'rl':0,
                'rr':0,
            }
        else:
            # rear
            mass_dz = {
                'fl':0,
                'fr':0,
                loc: -mass_static[loc] * single_hole_ratio,
                otherside: mass_static[loc] * single_hole_ratio,
            }
        self.mass_dz = mass_dz
        return mass_dz


# 对角顶起工况
class DiagonalJack2Axle(Vertical2Axle):

    def __init__(self, car_param, event_param):
        """
            对角顶起载荷转移量
            event_param {
                'diagonal_jack_ratio': float, # 左右载荷转移量
            }
        """
        super().__init__(car_param, event_param)

    def calc_z_delta_mass(self, loc, mass_static=None):
        """
            假定前后载荷转移比例一致
        """
        diagonal_jack_ratio = self.event_param['diagonal_jack_ratio']
        
        if mass_static==None:
            mass_static = self.get_mass_static()

        if loc=='l':
            # 左前右后
            mass_dz = {
                'fl': +mass_static['fl'] * diagonal_jack_ratio,
                'fr': -mass_static['fl'] * diagonal_jack_ratio,
                'rl': -mass_static['rr'] * diagonal_jack_ratio,
                'rr': +mass_static['rr'] * diagonal_jack_ratio,
            }
        elif loc=='r':
            # 右前左后
            mass_dz = {
                'fl': -mass_static['fr'] * diagonal_jack_ratio,
                'fr': +mass_static['fr'] * diagonal_jack_ratio,
                'rl': +mass_static['rl'] * diagonal_jack_ratio,
                'rr': -mass_static['rl'] * diagonal_jack_ratio,
            }

        self.mass_dz = mass_dz
        return mass_dz


# =================================================
# =================================================
# 工况拼接
# 2017.1 太假使用

class Car:

    def __init__(self, name):
        self.car_name = name
        self.car_param = None
        self.event_param = None
        self.mass_static = None
        self.mass_events = {}  # 各工况数据-质量
        self.force_events = {} # 各工况数据-力值

    # 车辆参数设置
    def set_car_param(self, car_param):
        self.car_param = car_param
        return None

    # 工况参数设置
    def set_event_param(self, event_param):
        self.event_param = event_param
        return None

    # 设置车辆状态
    def set_mass_static(self, mass_static):
        self.mass_static = mass_static
        return None

    # @pysnooper.snoop()
    def add_mass_event(self, event_name, event_mass_delta):
        """
            添加工况
            将质量转化为绝对值
        """
        mass_event = copy.deepcopy(event_mass_delta)
        mass_event['dz'] = add_mass(self.mass_static, mass_event['dz'])
        self.mass_events[event_name] = mass_event
        return None


    def remove_mass_event(self, event_name):
        """
            移除工况
        """
        self.mass_events.remove(event_name)
        return None


    def get_event_names(self):
        
        return list(self.mass_events.keys())


    def get_mass_event(self, event_name):
        """
            获取指定工况的质量加载
        """
        return self.mass_events[event_name]


    def mass2force(self):
        """
            质量转力值
        """
        for event_name in self.mass_events:
            self.force_events[event_name] = {}
            for vector in self.mass_events[event_name]:
                self.force_events[event_name][vector] = {}
                mass_vector = self.mass_events[event_name][vector]
                force_vecotr = self.force_events[event_name][vector]
                for side in mass_vector:
                    force_vecotr[side] = mass_vector[side] * G

        return self.force_events


class Truck2Axle(Car):
    """
        卡车两轴 工况拼接
    """
    def __init__(self, name, car_param, event_param):
        """
            car_param = {
                'mass_h': 1000,
                'wheel_base': 4000,
                'wheel_track': 2000,
                'mass_x': 2500,
                'mass_full': 5000,
            }
            event_param = {
                'single_hole_ratio': 1,     # 单轮过坑
                'single_jack_ratio': 1,     # 单轮顶起
                'acc_g': 0.4 ,              # 后驱向前加速
                'front_brake_g': 0.8,       # 前进紧急制动
                'rear_brake_g': 0.3,        # 倒车紧急制动
                'brake_lateral_x': 0.8,     # 转向制动 - 制动
                'brake_lateral_y': 0.5,     # 转向制动 - 转向
                'lateral_g': 0.5,           # 转向
                'diagonal_jack_ratio': 0.5，# 对角顶起(扭曲路)
                'z_g': 2,                   # 垂向重力
            }
        """
        super().__init__(name)

        self.set_car_param(car_param)
        self.set_event_param(event_param)
        self.set_mass_static(mass_static_2axle(car_param))


    # @pysnooper.snoop(watch="self.mass_events.keys()")
    def create_event(self):

        # 单轮过坑
        single_hole_ratio = self.event_param['single_hole_ratio']
        sh_obj = SingleHole2Axle(self.car_param,
            {'single_hole_ratio': single_hole_ratio,})
        for key in ['fl', 'fr', 'rl', 'rr']:
            mass_d = {}
            mass_d['dz'] = sh_obj.calc_z_delta_mass(key)
            mass_d['dx'] = sh_obj.calc_x_delta_mass()
            mass_d['dy'] = sh_obj.calc_y_delta_mass()
            self.add_mass_event('single_hole_{}_{}'.format(key, single_hole_ratio), mass_d)
        if is_debug: logger.info(f"Truck2Axle:工况创建: 单轮过坑")

        # 单轮顶起
        single_jack_ratio = self.event_param['single_jack_ratio']
        sj_obj = SingleJack2Axle(self.car_param,
            {'single_jack_ratio': single_jack_ratio,})
        for key in ['fl', 'fr', 'rl', 'rr']:
            mass_d = {}
            mass_d['dz'] = sj_obj.calc_z_delta_mass(key)
            mass_d['dx'] = sj_obj.calc_x_delta_mass()
            mass_d['dy'] = sj_obj.calc_y_delta_mass()
            self.add_mass_event('single_jack_{}_{}'.format(key, single_jack_ratio), mass_d)
        if is_debug: logger.info(f"Truck2Axle:工况创建: 单轮顶起")

        # 加速工况
        acc_g = self.event_param['acc_g']
        ra_obj = RAcc2Axle(self.car_param,
            {'acc_g': acc_g,})
        mass_d = {}
        mass_d['dz'] = ra_obj.calc_z_delta_mass()
        mass_d['dx'] = ra_obj.calc_x_delta_mass()
        mass_d['dy'] = ra_obj.calc_y_delta_mass()
        self.add_mass_event('acc_{}g'.format(round(acc_g, NAME_ROUND)), mass_d)
        if is_debug: logger.info(f"Truck2Axle:工况创建: 加速工况{acc_g}g")

        # 向前制动
        front_brake_g = self.event_param['front_brake_g']
        brake_obj = Brake2Axle(self.car_param,
            {'brake_g': front_brake_g,})
        mass_d = {}
        mass_d['dz'] = brake_obj.calc_z_delta_mass()
        mass_d['dx'] = brake_obj.calc_x_delta_mass()
        mass_d['dy'] = brake_obj.calc_y_delta_mass()
        self.add_mass_event('brake_{}g'.format(round(front_brake_g, NAME_ROUND)), mass_d)
        if is_debug: logger.info(f"Truck2Axle:工况创建: 向前制动{front_brake_g}g")

        # 倒车制动
        rear_brake_g = self.event_param['rear_brake_g']
        if rear_brake_g > 0: rear_brake_g = -rear_brake_g
        rear_brake_obj = Brake2Axle(self.car_param,
            {'brake_g': rear_brake_g,})
        mass_d = {}
        mass_d['dz'] = rear_brake_obj.calc_z_delta_mass()
        mass_d['dx'] = rear_brake_obj.calc_x_delta_mass()
        mass_d['dy'] = rear_brake_obj.calc_y_delta_mass()
        self.add_mass_event('brake_{}g'.format(round(rear_brake_g, NAME_ROUND)), mass_d)
        if is_debug: logger.info(f"Truck2Axle:工况创建: 倒车制动{rear_brake_g}g")

        # 转向工况
        lateral_g = self.event_param['lateral_g']
        for v in [1, -1]:
            lateral_g = v*lateral_g
            st_obj = Lateral2Axle(self.car_param,
                {'lateral_g': lateral_g,})
            mass_d = {}
            mass_d['dz'] = st_obj.calc_z_delta_mass()
            mass_d['dx'] = st_obj.calc_x_delta_mass()
            mass_d['dy'] = st_obj.calc_y_delta_mass()
            event_name = 'lateral_{}g'.format(round(lateral_g, NAME_ROUND))
            self.add_mass_event(event_name, mass_d)
        if is_debug: logger.info(f"Truck2Axle:工况创建: 转向工况{lateral_g}g")

        # 转向制动工况
        brake_lateral_x = self.event_param['brake_lateral_x']
        brake_lateral_y = self.event_param['brake_lateral_y']
        for v in [1, -1]:
            brake_lateral_y = v*brake_lateral_y

            lat_obj = Lateral2Axle(self.car_param, {'lateral_g': brake_lateral_y,})
            lon_obj = Brake2Axle(self.car_param, {'brake_g': brake_lateral_x,})

            mass_static = self.mass_static
            mass_dz_lat = lat_obj.calc_z_delta_mass()
            mass_static_1 = add_mass(mass_static, mass_dz_lat) # 侧向载荷转移
            mass_dz_lon = lon_obj.calc_z_delta_mass()
            mass_static_2 = add_mass(mass_static_1, mass_dz_lon) # 纵向载荷转移

            mass_d = {}
            mass_d['dx'] = lon_obj.calc_x_delta_mass(mass_static_2)
            # print(mass_static_2, mass_d['dx'])
            mass_d['dy'] = lat_obj.calc_y_delta_mass(mass_static_2)
            mass_d['dz'] = sub_mass(mass_static_2, mass_static)
            event_name = 'brake_{}g_lateral_{}g'.format(round(brake_lateral_x, NAME_ROUND), round(brake_lateral_y, NAME_ROUND))
            self.add_mass_event(event_name, mass_d)

        if is_debug: logger.info(f"Truck2Axle:工况创建: 转向制动工况, 制动{brake_lateral_x}g, 转向{brake_lateral_y}g")

        # 对角顶起
        diagonal_jack_ratio = self.event_param['diagonal_jack_ratio']
        dj_obj = DiagonalJack2Axle(self.car_param, {'diagonal_jack_ratio': diagonal_jack_ratio,})
        for side in ['l', 'r']:
            mass_d = {}
            mass_d['dz'] = dj_obj.calc_z_delta_mass(side)
            mass_d['dx'] = dj_obj.calc_x_delta_mass()
            mass_d['dy'] = dj_obj.calc_y_delta_mass()
            event_name = 'diagonal_jack_{}_{}'.format(side, diagonal_jack_ratio)
            self.add_mass_event(event_name, mass_d)
        if is_debug: logger.info(f"Truck2Axle:工况创建: 对角顶起")

        # 重力加速度
        z_g = self.event_param['z_g']
        v_obj = Vertical2Axle(None, None)
        mass_d = {}
        mass_d['dz'] = multi_mass(self.mass_static, z_g)
        mass_d['dx'] = v_obj.calc_x_delta_mass()
        mass_d['dy'] = v_obj.calc_y_delta_mass()
        event_name = 'vertical_{}g'.format(z_g)
        self.add_mass_event(event_name, mass_d)
        if is_debug: logger.info(f"Truck2Axle:工况创建: {z_g}g重力")

        return None


# =================================================
# =================================================
# 工况制作

_LCF_TITLE = """$---------------------------------------------------------------------MDI_HEADER
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
$---------------------------------------------------------------------------MODE
[MODE]
 STEERING_MODE  =  'angle'
 VERTICAL_MODE_FOR_SETUP  =  'contact_patch_height'
 VERTICAL_MODE  =  'wheel_vertical_force'
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

# 开头读取
try:
    lcf_template = os.path.join(os.path.dirname(__file__), r'template\lcf_title_force_load.txt')
    
    if os.path.exists(lcf_template):
        with open(lcf_template, 'r') as f:
            LCF_TITLE = f.read()
    else:
        if is_debug: logger.info(f"lcf模板路径不存在： {lcf_template} ; LCF_TITLE = _LCF_TITLE")
        LCF_TITLE = _LCF_TITLE
except:
    LCF_TITLE = _LCF_TITLE
    if is_debug: logger.info(f"lcf_template设置失败: LCF_TITLE = _LCF_TITLE")


# 过渡状态创建
def create_line_over(start_line, end_line, num):

    line_overs = [[] for n in range(num)]
    for start_v, end_v in zip(start_line, end_line):
        step = (end_v - start_v) / (num+1)
        for n in range(num):
            line_overs[n].append(start_v + step*(n+1))
        # print(step)

    return line_overs


# LoadCase 文件创建
class TruckForceEvent2AxleLcf:
    """
        两轴卡车-工况创建
        force_events
    """
    def __init__(self, force_events):
        self.force_events = force_events
        self.num_event   = len(force_events) # 工况数

        # -------------
        self.line_steps  = None
        self.lcf_path    = None
        self.over_num    = None
        self.event_names = None

    def get_event_name_status_side(self, side, event_name):

        force_events = self.force_events
        side_left = side + 'l'
        side_right = side + 'r'
        # for event_name in force_events:
        force_event = force_events[event_name]

        fz_l = force_event['dz'][side_left]
        fy_l = force_event['dy'][side_left]
        fx_l = force_event['dx'][side_left]

        fz_r = force_event['dz'][side_right]
        fy_r = force_event['dy'][side_right]
        fx_r = force_event['dx'][side_right]

        """
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
        """

        line = f"{fz_l} {fz_r} {fy_l} {fy_r} 0 0 0 0 0 0 {fx_l} {fx_r} 0 0 0 0 0 0 0"
        line = ' '.join([str(round(float(v), FLOAT_ROUND)) for v in line.split(' ')])
        assert len(line.split(' '))==19 
        # print(line)
        return line

    def get_event_status_side(self, side):
        
        force_events = self.force_events
        lines = []
        event_names = []
        for event_name in force_events:
            line = self.get_event_name_status_side(side, event_name)
            # print(line)
            lines.append(line)
            event_names.append(event_name)

        self.event_names = event_names
        return lines

    def get_line_steps_side(self, side, over_num=10, car_param=None):
        """
            over_num 过渡间隔数量
            side 'f' or 'r' 前/后轴
        """
        lines = self.get_event_status_side(side)

        line_float_steps = []
        if car_param == None:
            start_line = [0.0]*19
        else:
            mass_static = mass_static_2axle(car_param)
            force_v = mass_static[side+'l']*9.8
            start_line = [force_v, force_v] + [0.0]*17

        # over_num = 5
        for line in lines: 
            line_float = [float(v) for v in line.split(' ')]
            line_overs_1 = create_line_over(start_line, line_float, over_num)
            line_overs_2 = create_line_over(line_float, start_line, over_num)

            line_float_steps.append(start_line)
            line_float_steps.extend(line_overs_1) # 过渡
            line_float_steps.append(line_float) # 结尾
            line_float_steps.extend(line_overs_2) # 过渡

        line_steps = [' '.join([str(round(v, FLOAT_ROUND)) for v in line]) for line in line_float_steps]
        self.line_steps = line_steps
        return line_steps

    def create_lcf(self, side, file_path, over_num=10, car_param=None):
        """
            创建lcf文件
        """
        line_steps = self.get_line_steps_side(side, over_num, car_param)

        with open(file_path, 'w') as f:
            f.write(LCF_TITLE + '\n'.join(line_steps))

        self.lcf_path = file_path
        self.over_num = over_num
        if is_debug: logger.info(f"TruckForceEvent2AxleLcf: lcf创建 over_num(过渡step):{over_num}")
        if is_debug: logger.info(f"TruckForceEvent2AxleLcf: lcf创建 lcf_path:{file_path}")
        return None

    def get_status_locs(self, start_n):
        """
            根据start_n 工况起始位置
            计算各工况所在位置
            需求：
                工况过渡步数 over_num
                工况数      num_event
        """
        num = self.over_num
        status_len = self.num_event

        loc1 = start_n + ( num + 1 )
        loc2 = loc1 + 2* ( num +1 )
        if status_len == 1:
            return [loc1]
        if status_len == 2:
            return [loc1, loc2]
        elif status_len > 2:
            loc_last = loc2
            locs = [loc1, loc2]
            for n in range(2, status_len):
                loc_n = loc_last + 2* ( num +1 )
                locs.append(loc_n)
                loc_last = loc_n

            return locs


# =================================================
# =================================================
# 仿真调用

# cmd命令-悬架asy打开
CMD_OPEN_SUS_ASY = """
acar files assembly open &
    assembly_name="#asy_path#"
"""

# cmd命令-悬架asy分析调用
CMD_SIM_LOADCASE = """
executive set equilibrium model = .#asy_name# error = 1
executive set equilibrium model = .#asy_name# maxit = 100
executive set equilibrium model = .#asy_name# tlimit = 5

acar analysis suspension loadcase submit &
    assembly=.#asy_name# &
    variant=default &
    output_prefix="#sim_prefix#" &
    loadcase_files="file://#lcf_path#" &
    load_results=yes &
    comment="" &
    analysis_mode=interactive &
    log_file=yes
"""

# cmd命令-退出
CMD_QUIT = 'quit'

# 仿真运行-悬架装配系统
def sim_sus(sim_param):
    """
        悬架仿真计算 
            + 使用adams cmd命令仿真

        sim_param = {
            sus_asy_path: asy悬架装配模型路径
            lcf_path : loadcase文件路径
            sim_prefix : 仿真前缀
            run_dir : 仿真运行路径
        }
    """

    # 参数设置
    sus_asy_path = sim_param['sus_asy_path']
    lcf_path     = sim_param['lcf_path']
    sim_prefix   = sim_param['sim_prefix']
    run_dir      = sim_param['run_dir']

    asy_name = os.path.basename(sus_asy_path)[:-4]

    # 命令设置及编辑
    cmd_list = [CMD_OPEN_SUS_ASY, CMD_SIM_LOADCASE, CMD_QUIT]
    replace_dict = {
        '#asy_path#': sus_asy_path,
        '#asy_name#': asy_name,
        '#sim_prefix#': sim_prefix,
        '#lcf_path#': lcf_path,
    }

    cmd_to_runs = []
    for line_cmd in cmd_list:
        for key in replace_dict:
            line_cmd = line_cmd.replace(key, replace_dict[key])
        cmd_to_runs.append(line_cmd)

    # 仿真相关文件定义
    res_name = sim_prefix + '_' + os.path.basename(lcf_path)[:-4]
    msg_name = sim_prefix + '_' + 'suspnsn'

    # 提前删除文件
    file_remove_pt(run_dir, prefix=res_name, file_type=None)
    file_remove_pt(run_dir, prefix=msg_name, file_type=None)

    # 仿真
    res_path = os.path.join(run_dir, res_name) + '.res'
    msg_path = os.path.join(run_dir, msg_name) + '.msg'
    cmd_path = os.path.join(run_dir, f'temp_AutoSimCommand_{res_name}.cmd')
    cmd_str = '\n'.join(cmd_to_runs)
    cmd_send(cmd_str, 
        cmd_path=cmd_path, 
        mode='car', 
        savefile=False, 
        res_path=msg_path, # 监测msg用
        # minutes=30,
        true_res_path=res_path, # 实际res文件
        )
    
    assert os.path.exists(res_path)
    return res_path


# 删除文件夹内制定文件
def file_remove_pt(path, prefix=None, file_type=None): 
    '''
        仅仅删除文件夹内的文件，不删除子文件夹
        path 文件夹路径
        prefix 文件前缀
        file_type 文件后缀,类型
        示例：
            file_remove_pt(path,'sim_','adm')

            file_remove_pt(cal_path, prefix=None, file_type='bak') # 删除文件夹内整个带bak后缀的文件

    '''
    path_rems = []

    for line in os.listdir(path):
        # print(os.listdir(path))
        if file_type!=None and file_type.lower() == line[-len(file_type):].lower() or file_type==None:
            if prefix!=None and prefix.lower() == line[:len(prefix)].lower() or prefix==None:
                path_rems.append(line)

    for line in path_rems:
        target = os.path.join(path, line)
        if os.path.isfile(target):
            os.remove(target)
        # print(target)
    return True


# =================================================
# =================================================
# 集成
"""
input data:
    + name
    + front_asy_path
    + rear_asy_path
    + run_dir
    + car_param
    + event_param

过程:
    + 创建工况 lcf
    + 仿真输出 res
    + 读取res结果
"""

# 行列转换
def list2d_reshape(list2d):
    """
    """
    new_list2d = []
    for n1 in range(len(list2d[0])):
        line = []
        for n2 in range(len(list2d)):
            line.append(list2d[n2][n1])
        new_list2d.append(line)
    return new_list2d


# 卡车两轴提载控制
class TruckLoad2AxleControl:
    """
        + 仿真运行
        + res文件读取
    """
    def __init__(self, calc_param, car_param, event_param):
        """
            calc_param = {
                'name' : 
                'front_asy_path' : 
                'rear_asy_path' : 
                'run_dir' : 
            }
            car_parm = {
                
            }
            event_parm = {
                
            }

        """
        self.calc_param = calc_param
        self.car_param = car_param
        self.event_param = event_param

        # --------------------
        self.res_dict = None
        self.force_events = None
        self.status_locs = None
        self.tfe_obj = None
        self.event_names = None
        self.request_param = None

    def load_calc(self):
        """
            仿真计算输出 res文件路径

        """
        calc_param = self.calc_param
        car_param = self.car_param
        event_param = self.event_param

        if is_debug: logger.info(f"TruckLoad2AxleControl.load_calc 开始")
        if is_debug: logger.info(f"  仿真计算 calc_param:\n{change_dict_to_str(calc_param)}")

        name = calc_param['name']
        front_asy_path = calc_param['front_asy_path']
        rear_asy_path = calc_param['rear_asy_path']
        run_dir = calc_param['run_dir']
        over_num = calc_param['over_num']

        # ---------------------------
        # 工况创建
        truck_obj = Truck2Axle(name, car_param, event_param)
        truck_obj.create_event()
        force_events = truck_obj.mass2force()
        tfe_obj = TruckForceEvent2AxleLcf(force_events)
         
        front_lcf_name = 'Truck2Axle_F.lcf'
        rear_lcf_name  = 'Truck2Axle_R.lcf'
         
        front_lcf_path = os.path.join(run_dir, front_lcf_name)
        rear_lcf_path = os.path.join(run_dir, rear_lcf_name)

        tfe_obj.create_lcf('f', front_lcf_path, over_num=over_num, car_param=car_param)
        tfe_obj.create_lcf('r', rear_lcf_path, over_num=over_num, car_param=car_param)

        # ---------------------------
        # 仿真
        """
            多线程计算暂无法使用
        """

        # 数据保存
        class ResPath:
            res_paths = []
            res_dict  = {}

        # 装饰目标函数
        def func_res_get(func):
            # 多进程计算调用函数
            # 装饰
            def new_func(*args, **kwargs):
                result = func(*args,**kwargs)
                ResPath.res_paths.append(result)
                return result
            return new_func

        ResPath.res_paths = []
        ResPath.res_dict  = {}
        asy_paths = [front_asy_path, rear_asy_path]
        lcf_paths = [front_lcf_path, rear_lcf_path]
        res_keys  = ['front', 'rear']
        # threadmax = threading.BoundedSemaphore(2)     # 多线程初始设置,设置线程上限
        cur_n = 0
        for asy_path, lcf_path, res_key in zip(asy_paths, lcf_paths, res_keys):

            # run_dir_n = os.path.join(run_dir, f"AutoSim_{cur_n}")
            # cur_n += 1
            # if not os.path.exists(run_dir_n):
            #     os.mkdir(run_dir_n)
            run_dir_n = run_dir

            # 仿真前缀提前定义
            sim_prefix = "AutoSim_" + os.path.basename(asy_path)[:-4]
            sim_param = {
                'sus_asy_path': asy_path, 
                'lcf_path': lcf_path, 
                'sim_prefix': sim_prefix, 
                'run_dir': run_dir_n, 
            }
            res_path = sim_sus(sim_param)
            ResPath.res_paths.append(res_path)
            ResPath.res_dict[res_key] = res_path
        #     new_func = threadingrun.threading_func(sim_sus, threadmax=threadmax)
        #     new_func2 = func_res_get(new_func)
        #     threads = []
        #     thread  = threading.Thread(target=new_func2, args=(sim_param, ))
        #     thread.start()
        #     threads.append(thread)
        #     threadmax.acquire()
        #     time.sleep(30)

        # while threads:
        #     threads.pop().join()

        # print(ResPath.res_paths)

        # 
        self.res_dict = ResPath.res_dict
        self.force_events = force_events
        self.tfe_obj = tfe_obj
        self.event_names = tfe_obj.event_names

        # if is_debug: logger.info(f"  仿真计算, 结束, res_dict:{change_dict_to_str(res_dict)}")
        if is_debug: logger.info(f"TruckLoad2AxleControl.load_calc 结束")
        return self.res_dict

    def parse_res(self, request_param):
        """
            读取res, 解析数据
            data_name : 数据名称

            res_dict  : {
                'front': res_path, 
                'rear':res_path
            }

            request_param: {
                'front': {'req':[str,], 'comp':[str,]},
                'rear' : {'req':[str,], 'comp':[str,]},
            }

        """
        if is_debug: logger.info(f"TruckLoad2AxleControl.parse_res: ")
        # if is_debug: logger.info(f"  res读取, request_param:{change_dict_to_str(request_param)}")
        if is_debug: logger.info(f"  res读取, request_param:{request_param}")

        self.request_param = request_param
        data_name = self.calc_param['name']
        res_dict  = self.res_dict

        dataobj = DataModel(data_name)
        data_full = []
        reqs_full, comps_full = [], []
        for res_key in res_dict:
            reqs  = request_param[res_key]['req']
            reqs_full.extend(reqs)
            comps = request_param[res_key]['comp']
            comps_full.extend(comps)

            dataobj.new_file(res_dict[res_key], res_key)
            dataobj[res_key].set_reqs_comps(reqs, comps)
            dataobj[res_key].set_line_ranges(None)
            dataobj[res_key].set_select_channels(None)
            dataobj[res_key].read_file(isReload=True)
            data = dataobj[res_key].get_data()

            # 拼接前后request
            data_full.extend(data)

        self.data_full = data_full
        self.reqs_full  = reqs_full
        self.comps_full = comps_full
        if is_debug: logger.info(f"TruckLoad2AxleControl.parse_res 结束")
        return data_full

    def get_status(self, loc):
        """
            截取状态
        """
        return [line[loc] for line in self.data_full]

    def get_status_data(self):
        """
            获取工况数据
        """
        res_path = self.res_dict['front']
        start_n = self.get_res_sus_loadcase_start(res_path)
        locs = self.tfe_obj.get_status_locs(start_n)
        data_status = []
        for loc in locs:
            data_status.append(self.get_status(loc))

        self.data_status = data_status
        return data_status

    @staticmethod
    def get_res_sus_loadcase_start(res_path):
        """
            准静态计算起始位置
            list直接索引
        """
        f = open(res_path, 'r')
        line = f.readline()
        n = -1
        while line:
            line = line.lower()
            if re.match('<step\s+type', line):
                n += 1
                if 'type="quasistatic"' in line:
                    break
            line = f.readline()
        f.close()
        return n

    def print_to_csv(self, csv_param):
        """
            导出csv
            csv_param = {
                'num_force_comp' : int  # 六分力 or n分力
                'csv_view_path' : csv 查看用
                'csv_hm_path' : csv 对接hm二次开发用
            }
        """
        if is_debug: logger.info(f"TruckLoad2AxleControl.print_to_csv 开始")
        if is_debug: logger.info(f"  导出CSV, csv_param:{change_dict_to_str(csv_param)}")

        num_force_comp = csv_param['num_force_comp']
        csv_view_path = csv_param['csv_view_path']
        csv_hm_path = csv_param['csv_hm_path']
        # 获取工况数据
        data_status = self.get_status_data()
        event_names = self.event_names
        reqs_full = self.reqs_full
        comps_full = self.comps_full
        
        num_reqs = len(reqs_full)
        num_force_point = num_reqs / num_force_comp
        assert num_force_point == int(num_force_point)
        num_force_point = int(num_force_point)

        lines_event_2d = []
        for n in range(num_force_comp):
            line = []
            for data in data_status:
                line.extend(data[n::num_force_comp])
            lines_event_2d.append(line)

        lines_event_2d = copy.deepcopy(lines_event_2d)
        lines_event_2d = list2d_reshape(lines_event_2d)
        lines_event_1d = [','.join([str(v) for v in line]) for line in lines_event_2d]

        # --------------------------
        # csv对接hm, 主要数据
        # lines_event_1d, event_names, num_force_comp, reqs_full, num_force_point
        # csv_hm_path
        lines_main = []
        for n in range(num_force_point):
            lines_main.append(','.join(lines_event_1d[n::num_force_point]))

        # 增加标题行
        line_title = ','.join([event_name+','*(num_force_comp-1) for event_name in event_names])
        lines_main.insert(0, line_title)

        # 开头增加坐标列
        for loc, line in enumerate(lines_main):
            lines_main[loc] = ',,,'+line

        output_str = '\n'.join(lines_main)
        
        with open(csv_hm_path, 'w') as f:
            f.write(output_str)

        # --------------------------
        # csv 阅读用
        # lines_event_1d, event_names, num_force_comp, reqs_full, comps_full, num_force_point
        # csv_view_path
        lines_view = []
        num_view = 3 # 空行间隔数
        force_comp_names = ['Fx(N)', 'Fy(N)', 'Fz(N)', 'Tx(N*mm)', 'Ty(N*mm)', 'Tz(N*mm)']

        # 加载点名称定义
        reqs  = reqs_full[0::num_force_comp]
        comps = comps_full[0::num_force_comp]
        req_views = []
        for req, comp in zip(reqs, comps):
            if '_' in comp:
                req = req + '.' + '_'.join(comp.split('_')[1:])
            req_views.append(req)

        for n in range(len(event_names)): # 工况检索
            title_view = event_names[n] + ',' + ','.join(force_comp_names[:num_force_comp])
            lines_view.append(title_view)

            # 增加首列, 注释列
            for loc, line in enumerate(lines_event_1d[ num_force_point*n : num_force_point*(n+1) ]):
                lines_view.append(req_views[loc] + ',' + line)

            for n2 in range(num_view):
                lines_view.append(','*num_force_comp)

        output_str = '\n'.join(lines_view)

        with open(csv_view_path, 'w') as f:
            f.write(output_str)

        if is_debug: logger.info("  导出CSV, 完成")
        if is_debug: logger.info(f"TruckLoad2AxleControl.print_to_csv 结束")
        return None


# csv 转 excel  xlsx
def csv2excel_xlsx(workbook, csv_path, sheet_name):
    """
        xlsxwriter、csv 库

        csv文件读取 并转化为excel的表跟数据
        workbook    xlwt.Workbook 实例
        csv_path    目标csv文件路径
        sheet_name  目标表跟数据的sheet名称
    """
    if len(sheet_name)>31: # excel表格名称字符不能超31
        sheet_name = sheet_name[-31:]

    worksheet = workbook.add_worksheet(name = sheet_name)
    with open(csv_path, 'r') as f:
        rows = csv.reader(f)
        for irow, row in enumerate(rows):
            for icol, value in enumerate(row):
                try:
                    value = float(value)
                except:
                    pass
                worksheet.write(irow, icol, value)

    return workbook


def collect_csv2excel(excel_path, csv_paths):
    # 文件保存 - xlsx
    assert excel_path[-5:].lower()=='.xlsx'

    init_excel_path = excel_path
    n = 1
    while True:
        if os.path.exists(excel_path):
            excel_path = init_excel_path[:-5] + f'_{n}.xlsx'
        else:
            break
        n += 1

    workbook = xlsxwriter.Workbook(filename=excel_path)

    for csv_path in csv_paths:
        name = os.path.basename(csv_path)[:-4]
        csv2excel_xlsx(workbook, csv_path, name)

    workbook.close()
    return None


def load_json(json_path):

    lines = [] 
    with open(json_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if line.strip().startswith('//'):
                continue
            lines.append(line)

    return json.loads('\n'.join(lines))


def main_truck2axle(car_param, calc_param, event_param, csv_param, request_param):
    
    tlc = TruckLoad2AxleControl(calc_param, car_param, event_param)
    tlc.load_calc()
    tlc.parse_res(request_param)
    tlc.print_to_csv(csv_param)

    excel_path = csv_param['excel_path']
    csv_paths = [csv_param['csv_view_path'], csv_param['csv_hm_path']]
    collect_csv2excel(excel_path, csv_paths)
    return None

# =================================================
# =================================================
# 测试

test_car_param = {
    'mass_h': 1000,
    'wheel_base': 4000,
    'wheel_track': 2000,
    'mass_x': 2500,
    'mass_full': 5000,
}

test_event_param = {
    'single_hole_ratio': 1,     # 单轮过坑
    'single_jack_ratio': 1,     # 单轮顶起
    'acc_g': 0.4 ,              # 后驱向前加速
    'front_brake_g': 0.8,       # 前进紧急制动
    'rear_brake_g': 0.3,        # 倒车紧急制动
    'brake_lateral_x': 0.8,     # 转向制动 - 制动
    'brake_lateral_y': 0.5,     # 转向制动 - 转向
    'lateral_g': 0.5,           # 转向
    'diagonal_jack_ratio': 0.5, # 对角顶起(扭曲路)
    'z_g':2,                    # 重力加速度
}

test_calc_param = {
    'name': 'T5DB',
    'front_asy_path': r'\\sjnas02\BRDI03\4.VehicleDynamic\01_model\ADAMS_Data\T5DB.cdb\assemblies.tbl\T5DB_front_sus.asy',
    'rear_asy_path': r'\\sjnas02\BRDI03\4.VehicleDynamic\01_model\ADAMS_Data\T5DB.cdb\assemblies.tbl\T5DB_rear_sus.asy',
    'run_dir': 'E:/adams_work',
}

test_request_param = {
    'front': {'req':['L_shock_to_frame_Force', 'L_shock_to_frame_Force', 'L_shock_to_frame_Force', 'R_shock_to_frame_Force', 'R_shock_to_frame_Force', 'R_shock_to_frame_Force'], 
            'comp':['Fx_front', 'Fy_front', 'Fz_front', 'Fx_front', 'Fy_front', 'Fz_front']},
    'rear' : {'req':['L_shock_to_frame_Force', 'L_shock_to_frame_Force', 'L_shock_to_frame_Force', 'R_shock_to_frame_Force', 'R_shock_to_frame_Force', 'R_shock_to_frame_Force'], 
            'comp':['Fx_rear', 'Fy_rear', 'Fz_rear', 'Fx_rear', 'Fy_rear', 'Fz_rear']},
}

test_csv_param = {
    'num_force_comp': 6, # 六分力 or n分力
    'csv_view_path': r'E:\adams_work\__view.csv', 
    'csv_hm_path': r'E:\adams_work\__hm.csv', 
    'excel_path': r'E:\adams_work\T5DB_truck2axle_force.xlsx',
}


test_sus_asy_path = r'\\sjnas02\BRDI03\4.VehicleDynamic\01_model\ADAMS_Data\T5DB.cdb\assemblies.tbl\T5DB_front_sus.asy',


def test_Truck2Axle():

    truck_obj = Truck2Axle('T5DB', test_car_param, test_event_param)
    truck_obj.create_event()
    # pprint.pprint(truck_obj.mass2force())
    return truck_obj.mass2force()


# 单论过坑
# @pysnooper.snoop(prefix='SingleHole2Axle: ')
def test_SingleHole2Axle():

    sh_obj = SingleHole2Axle(test_car_param,
        {'single_hole_ratio': 1,})

    load_data = []
    for key in ['fl', 'fr', 'rl', 'rr']:
        mass_d = {}
        mass_d['dz'] = sh_obj.calc_z_delta_mass(key)
        mass_d['dx'] = sh_obj.calc_x_delta_mass()
        mass_d['dy'] = sh_obj.calc_y_delta_mass()
        load_data.append(mass_d)
    pprint.pprint(load_data)

# 单轮顶起
def test_SingleJack2Axle():

    sh_obj = SingleJack2Axle(test_car_param,
        {'single_jack_ratio': 1,})

    # rr = {'fl': 0, 'fr': 0, 'rl': -1250.0, 'rr':1250.0}
    # print(sh_obj.calc_z_delta_mass('rr') == rr)

    load_data = []
    for key in ['fl', 'fr', 'rl', 'rr']:
        mass_d = {}
        mass_d['dz'] = sh_obj.calc_z_delta_mass(key)
        mass_d['dx'] = sh_obj.calc_x_delta_mass()
        mass_d['dy'] = sh_obj.calc_y_delta_mass()
        load_data.append(mass_d)
    pprint.pprint(load_data)

# 驱动
def test_RAcc2Axle():

    sh_obj = RAcc2Axle(test_car_param,
        {'acc_g': 0.2,})

    mass_d = {}
    mass_d['dz'] = sh_obj.calc_z_delta_mass()
    mass_d['dx'] = sh_obj.calc_x_delta_mass()
    mass_d['dy'] = sh_obj.calc_y_delta_mass()
    pprint.pprint(mass_d)

# 制动
def test_Brake2Axle():

    sh_obj = Brake2Axle(test_car_param,
        {'brake_g': 1,})

    mass_d = {}
    mass_d['dz'] = sh_obj.calc_z_delta_mass()
    mass_d['dx'] = sh_obj.calc_x_delta_mass()
    mass_d['dy'] = sh_obj.calc_y_delta_mass()
    pprint.pprint(mass_d)

# 转向
def test_Lateral2Axle():

    sh_obj = Lateral2Axle(test_car_param,
        {'lateral_g': 0.5,})

    mass_d = {}
    mass_d['dz'] = sh_obj.calc_z_delta_mass()
    mass_d['dx'] = sh_obj.calc_x_delta_mass()
    mass_d['dy'] = sh_obj.calc_y_delta_mass()
    pprint.pprint(mass_d)

# 转向制动
def test_brake_lateral_2axle():
    # 优先计算垂向
    # 转弯制动,先转弯后制动
    # 1、 静态载荷
    # 2、 侧向-垂向载荷
    # 3、 纵向-垂向载荷
    # 4、 纵向-纵向载荷
    # 5、 侧向-侧向载荷

    lat_obj = Lateral2Axle(test_car_param,
        {'lateral_g': 0.5,})

    lon_obj = Brake2Axle(test_car_param, 
        {'brake_g':0.8,})

    mass_static = lat_obj.get_mass_static()
    mass_dz_lat = lat_obj.calc_z_delta_mass()
    mass_static_1 = add_mass(mass_static, mass_dz_lat) # 侧向载荷转移
    mass_dz_lon = lon_obj.calc_z_delta_mass()
    mass_static_2 = add_mass(mass_static_1, mass_dz_lon) # 纵向载荷转移

    mass_dz = sub_mass(mass_static_2, mass_static)
    mass_dx = lon_obj.calc_x_delta_mass(mass_static_2)
    mass_dy = lat_obj.calc_y_delta_mass(mass_static_2)

    mass_d = {}
    mass_d['dz'] = mass_dz
    mass_d['dx'] = mass_dx
    mass_d['dy'] = mass_dy
    pprint.pprint(mass_d)

# 对角顶起
def test_DiagonalJack2Axle():
    pass
    sh_obj = DiagonalJack2Axle(test_car_param,
        {'diagonal_jack_ratio': 0.5,})

    mass_d = {}
    mass_d['dz'] = sh_obj.calc_z_delta_mass('l')
    mass_d['dx'] = sh_obj.calc_x_delta_mass()
    mass_d['dy'] = sh_obj.calc_y_delta_mass()
    print('test_DiagonalJack2Axle:')
    pprint.pprint(mass_d)

# truck lcf创建测试
def test_TruckForceEvent2AxleLcf():
    force_events = test_Truck2Axle()
    tfe_obj = TruckForceEvent2AxleLcf(force_events)
    side  = 'f'
    front_lcf_path = 'D:/temp/test_f.lcf'
    rear_lcf_path = 'D:/temp/test_r.lcf'
     
    tfe_obj.create_lcf('f', front_lcf_path)
    tfe_obj.create_lcf('r', rear_lcf_path)

# 悬架仿真测试
def test_sim_sus():
    
    sus_asy_path = test_sus_asy_path
    lcf_path = r"E:\adams_work\test_f.lcf"
    run_dir = r"E:\adams_work"

    sim_prefix = "AutoSim_" + os.path.basename(sus_asy_path)[:-4]
    sim_param = {
        'sus_asy_path': sus_asy_path,
        'lcf_path': lcf_path,
        'sim_prefix': sim_prefix,
        'run_dir': run_dir,
    }

    cur_dir = os.getcwd()
    # 更改当前路径为计算路径
    os.chdir(run_dir)

    res_path = sim_sus(sim_param)

    os.chdir(cur_dir)


def test_TruckLoad2AxleControl():

    car_param   = test_car_param
    calc_param  = test_calc_param
    event_param = test_event_param
    csv_param   = test_csv_param
    request_param = test_request_param

    pprint.pprint(calc_param)

    tlc = TruckLoad2AxleControl(calc_param, car_param, event_param)
    tlc.load_calc()
    tlc.parse_res(request_param)
    tlc.print_to_csv(csv_param)

    excel_path = csv_param['excel_path']
    csv_paths = [csv_param['csv_view_path'], csv_param['csv_hm_path']]
    collect_csv2excel(excel_path, csv_paths)


def test_TruckLoad2AxleControl2(json_path):

    params = load_json(json_path)
    main_truck2axle(**params)


if __name__=='__main__':
    pass
    log_format = '%(levelname)s : %(module)s : %(funcName)s : %(lineno)s : %(message)s'
    logging.basicConfig(format=log_format)
    # test_Truck2Axle()
    # test_SingleHole2Axle()
    # test_SingleJack2Axle()
    # test_RAcc2Axle()
    # test_Brake2Axle()
    # test_Lateral2Axle()
    # test_brake_lateral_2axle()
    # test_DiagonalJack2Axle()

    # test_TruckForceEvent2AxleLcf()
    # print(mass_static_2axle(test_car_param))

    # print('\n'.join(line_steps))

    # test_sim_sus()
    # test_TruckLoad2AxleControl()
    test_TruckLoad2AxleControl2('./00_set/truck_load.json')

