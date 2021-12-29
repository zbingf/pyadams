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

"""

import abc
import pprint
import pysnooper
import copy

g = 9.8 # 重力加速度
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

    # 两轴质量计算
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
        # mass_x = self.car_param['mass_x']
        # mass_full = self.car_param['mass_full']
        # wheel_base = self.car_param['wheel_base']

        # mass_rear  = (mass_x * mass_full) / wheel_base
        # mass_front = mass_full - mass_rear
        # mass_static = {
        #     'fl': mass_front / 2,
        #     'fr': mass_front / 2,
        #     'rl': mass_rear / 2,
        #     'rr': mass_rear / 2,
        # }
        return mass_static
  

    @staticmethod
    def get_mass_front_k(mass1):
        # 前轴质量占比
        front_mass = mass1['fl'] + mass1['fr']
        rear_mass = mass1['rl'] + mass1['rr']
        full_mass = front_mass + rear_mass
        return front_mass / full_mass

    @staticmethod
    def get_mass_left_k(mass1):
        # 左右轮荷占比
        front_left_k = mass1['fl'] / ( mass1['fl'] + mass1['fr'] )
        rear_left_k  = mass1['rl'] / ( mass1['rl'] + mass1['rr'] )
        return front_left_k, rear_left_k

    def get_mass_delta(self):
        return self.calc_x_delta_mass(), \
            self.calc_y_delta_mass(), \
            self.calc_z_delta_mass()


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
                    force_vecotr[side] = mass_vector[side] * g

        return self.force_events


class Truck2Axle(Car):

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

        # 加速工况
        acc_g = self.event_param['acc_g']
        ra_obj = RAcc2Axle(self.car_param,
            {'acc_g': acc_g,})
        mass_d = {}
        mass_d['dz'] = ra_obj.calc_z_delta_mass()
        mass_d['dx'] = ra_obj.calc_x_delta_mass()
        mass_d['dy'] = ra_obj.calc_y_delta_mass()
        self.add_mass_event('acc_{}g'.format(round(acc_g, NAME_ROUND)), mass_d)

        # 向前制动
        front_brake_g = self.event_param['front_brake_g']
        brake_obj = Brake2Axle(self.car_param,
            {'brake_g': front_brake_g,})
        mass_d = {}
        mass_d['dz'] = brake_obj.calc_z_delta_mass()
        mass_d['dx'] = brake_obj.calc_x_delta_mass()
        mass_d['dy'] = brake_obj.calc_y_delta_mass()
        self.add_mass_event('brake_{}g'.format(round(front_brake_g, NAME_ROUND)), mass_d)

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

        # 重力加速度
        z_g = self.event_param['z_g']
        v_obj = Vertical2Axle(None, None)
        mass_d = {}
        mass_d['dz'] = multi_mass(self.mass_static, z_g)
        mass_d['dx'] = v_obj.calc_x_delta_mass()
        mass_d['dy'] = v_obj.calc_y_delta_mass()
        event_name = 'vertical_{}g'.format(z_g)
        self.add_mass_event(event_name, mass_d)

        return None


# =================================================
# =================================================
# 工况制作

# 开头读取
with open(r'.\template\lcf_title_force_load.txt', 'r') as f:
    LCF_TITLE = f.read()
# print(LCF_TITLE)

# 过渡状态创建
def create_line_over(start_line, end_line, num):

    line_overs = [[] for n in range(num)]
    for start_v, end_v in zip(start_line, end_line):
        step = (end_v - start_v) / (num+1)
        for n in range(num):
            line_overs[n].append(start_v + step*(n+1))
        # print(step)

    return line_overs

class TruckForceEvent2AxleLcf:

    def __init__(self, force_events):
        self.force_events = force_events

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
        for event_name in force_events:
            line = self.get_event_name_status_side(side, event_name)
            # print(line)
            lines.append(line)
        return lines

    def get_line_steps_side(self, side, over_num=10):
        """
            over_num 过度间隔数量
            side 'f' or 'r' 前/后轴
        """
        lines = self.get_event_status_side(side)

        line_float_steps = []
        start_line = [0.0]*19
        # over_num = 5
        for line in lines: 
            line_float = [float(v) for v in line.split(' ')]
            line_overs_1 = create_line_over(start_line, line_float, over_num)
            line_overs_2 = create_line_over(line_float, start_line, over_num)

            line_float_steps.append(start_line)
            line_float_steps.extend(line_overs_1) # 过度
            line_float_steps.append(line_float) # 结尾
            line_float_steps.extend(line_overs_2) # 过度

        line_steps = [' '.join([str(round(v, FLOAT_ROUND)) for v in line]) for line in line_float_steps]

        return line_steps

    def create_lcf(self, side, file_path, over_num=10):
        """
            创建lcf文件
        """
        line_steps = self.get_line_steps_side(side, over_num)

        with open(file_path, 'w') as f:
            f.write(LCF_TITLE + '\n'.join(line_steps))



# =================================================
# =================================================
# 仿真调用

import os
import pyadams.call.cmdlink as cmdlink
cmd_file_send = cmdlink.cmd_file_send
cmd_send = cmdlink.cmd_send

# cmd_file_send(cmd_path=None, mode='car', res_path=None, minutes=30)
# cmd_send(cmds, cmd_path=None, mode='car', savefile=False, res_path=None, minutes=30)

# 悬架asy打开
CMD_OPEN_SUS_ASY = """
acar files assembly open &
    assembly_name="#asy_path#"
"""

# 悬架asy分析调用
CMD_SIM_LOADCASE = """
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

CMD_QUIT = 'quit'

def sim_sus(sim_param):
    """
        悬架仿真计算 
            + adams cmd命令仿真
    """
    sus_asy_path = sim_param['sus_asy_path']
    lcf_path     = sim_param['lcf_path']
    sim_prefix   = sim_param['sim_prefix']
    run_dir      = sim_param['run_dir']

    asy_name = os.path.basename(sus_asy_path)[:-4]

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

    res_name = sim_prefix + '_' + os.path.basename(lcf_path)[:-4]
    msg_name = sim_prefix + '_' + 'suspnsn'

    # 提前删除文件
    file_remove_pt(run_dir, prefix=res_name, file_type=None)
    file_remove_pt(run_dir, prefix=msg_name, file_type=None)

    res_path = os.path.join(run_dir, res_name) + '.res'
    msg_path = os.path.join(run_dir, msg_name) + '.msg'
    cmd_path = os.path.join(run_dir, 'temp_AutoSimCommand.cmd')
    cmd_str = '\n'.join(cmd_to_runs)
    cmd_send(cmd_str, 
        cmd_path=cmd_path, 
        mode='car', 
        savefile=False, 
        res_path=msg_path, 
        minutes=30,
        true_res_path=res_path)
    
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
import threading
from pyadams.call import threadingrun
import time

# name, car_param, event_param, front_asy_path, 
# rear_asy_path, front_lcf_path, rear_lcf_path,
# run_dir

def truck_load_calc(calc_param):

    name = calc_param['name']
    car_param = calc_param['car_param']
    event_param = calc_param['event_param']
    front_asy_path = calc_param['front_asy_path']
    rear_asy_path = calc_param['rear_asy_path']
    # front_lcf_path = calc_param['front_lcf_path']
    # rear_lcf_path = calc_param['rear_lcf_path']
    run_dir = calc_param['run_dir']

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

    tfe_obj.create_lcf('f', front_lcf_path)
    tfe_obj.create_lcf('r', rear_lcf_path)

    # ---------------------------
    # 仿真
    class ResPath:
        res_paths = []

    # 装饰目标函数
    def func_res_get(func):
        # 多进程计算调用函数
        # 装饰
        def new_func(*args, **kwargs):
            result = func(*args,**kwargs)
            ResPath.res_paths.append(result)
            return result

        return new_func

    asy_paths = [front_asy_path, rear_asy_path]
    lcf_paths = [front_lcf_path, rear_lcf_path]
    # threadmax = threading.BoundedSemaphore(2)     # 多线程初始设置,设置线程上限
    ResPath.res_paths = []
    # cur_dir = os.getcwd()
    # os.chdir(run_dir) # 更改当前路径为计算路径
    cur_n = 0
    for asy_path, lcf_path in zip(asy_paths, lcf_paths):
        run_dir_n = os.path.join(run_dir, f"AutoSim_{cur_n}")
        cur_n += 1
        if not os.path.exists(run_dir_n):
            os.mkdir(run_dir_n)

        sim_prefix = "AutoSim_" + os.path.basename(asy_path)[:-4]
        sim_param = {
            'sus_asy_path': asy_path,
            'lcf_path': lcf_path,
            'sim_prefix': sim_prefix,
            'run_dir': run_dir,  # ---------------
        }
        ResPath.res_paths.append(sim_sus(sim_param))
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

    # os.chdir(cur_dir)

    # print(ResPath.res_paths)
    return ResPath.res_paths


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

    sus_asy_path = r""
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


def test_truck_load_calc():


    calc_param = {
        'name': 'T5DB',
        'car_param': test_car_param,
        'event_param': test_event_param,
        'front_asy_path': r'',
        'rear_asy_path': r'',
        # 'front_lcf_path': ,
        # 'rear_lcf_path': ,
        'run_dir': 'E:/adams_work',
    }

    print(truck_load_calc(calc_param))


if __name__=='__main__':
    pass
    import logging
    logging.basicConfig(level=logging.INFO)

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
    truck_load_calc()