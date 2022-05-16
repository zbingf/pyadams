# 默认单位 mm  km/h
# 坐标系
# 向前为X正
# 向左为Y正

# 车轮-右转为正
# 车轮-左转为负


# 标准库
import math
import copy
from pprint import pprint


# 
from tkui import VarSearchUi


# 调用库
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
from mat4py import loadmat, savemat


plt.rcParams['figure.figsize'] = [10, 10]


get_key_steps = lambda steps, key: [step[key] for step in steps]
get_np_linspace = lambda x_range, d_s: np.linspace(*x_range, num=int((x_range[1]-x_range[0])/d_s))


def get_join_list3d(list3d):
    new_list2d = []
    for list2d in list3d:
        for line in list2d:
            new_list2d.append(line)
    return new_list2d


class Body:

    # 车身
    def __init__(self):
        self.body_type = None
        self.cur_dt = None  # 时间间隔

        self.l_length = None # 车长
        self.l_width = None # 车宽
        self.cur_velocity = 0 # 当前车速 km / s 
        self.cur_loc_body = None # 当前body位置, 此处指代body几何中心
        self.cur_yaw_body = None # 当前body相对原点坐标系旋转角 deg
        self.cur_loc_st_relative = None # 相对旋转中心
        self.cur_loc_edge = None # 车身边缘数据-当前

        # 车身边缘数据-记录
        self.step_locs_edge = []
        # 车身状态数据
        self.step_states = []

    def create_loc_edge_locs_relative(self, x_dis, dis=5, isEdge=False):
        """
            根据
                长、宽创建
                    当前body位置
                    当前body转角

                x_dis   调整X位置
                dis     位移间隔
                isEdge  边界线创建
        """
        # dis = 3

        L = self.l_length
        W = self.l_width

        locs = []
        locs.append([L/2, -W/2])
        locs.append([L/2, W/2])
        locs.append([-L/2, W/2])
        locs.append([-L/2, -W/2])

        if isEdge: # 边创建
            locs_edge = []
            # 左上
            for n in range(int(L/2/dis)): 
                x = + n*dis
                y = + W/2
                loc_n = [x, y]
                locs_edge.append(loc_n)
            
            for n in range(int(W/2/dis)):
                x = + L/2
                y = + n*dis
                loc_n = [x, y]
                locs_edge.append(loc_n)

            locs_left = copy.deepcopy(locs_edge)

            # 左下
            for loc in locs_left:
                loc[0] = -loc[0]
            locs_left.extend(locs_edge) # 先下后上

            # 右下 & 右上
            locs_right = copy.deepcopy(locs_left)
            for loc in locs_right:
                loc[1] = -loc[1]

            locs = locs + locs_left + locs_right
        for loc in locs:
            loc[0] += x_dis
        # print(locs)
        self.locs_relative = locs
        return self.locs_relative

    def get_loc_direction(self, n):

        if n <= 3:
            direction_dic = {0:'FrontRight', 1:'FrontLeft', 2:'RearLeft', 4:'RearRight'}
            return direction_dic[n]

        else:
            n -= 3
            new_locs = self.locs_relative[4:]
            n_len = len(new_locs)/4
            direction_dic = {1:'RearLeft', 2:'FrontLeft', 3:'RearRight', 4:'FrontRight'}
            # print(len(new_locs))
            # print(self.locs_relative[n])
            return direction_dic[math.ceil(n / n_len)]

    def get_cur_locs(self):

        locs_rotate = self.rotate_loc_relative(self.locs_relative, self.cur_yaw_body)
        new_locs = self.move_loc_relative(locs_rotate, self.cur_loc_body)

        self.cur_loc_edge = new_locs
        return new_locs

    @staticmethod
    def rotate_loc_relative(locs, angle_deg):
        """
            数据默认逆时针
        """
        angle_rad = angle_deg/180*math.pi
        mr = np.array(
            [
                [math.cos(angle_rad), -math.sin(angle_rad)],
                [math.sin(angle_rad), math.cos(angle_rad)],
            ])

        new_locs = []
        for loc in locs:
            m_loc = np.array([[loc[0]], [loc[1]]])
            # m_loc = np.array(loc)
            m_loc_new = np.dot(mr, m_loc)
            # print(m_loc_new)
            loc_new = [m_loc_new[0][0], m_loc_new[1][0]]
            new_locs.append(loc_new)
        return new_locs

    @staticmethod
    def move_loc_relative(locs, loc_move):
        """
            几何中心移动坐标
        """
        new_locs = []
        for loc in locs:
            new_loc = [loc[0] + loc_move[0], loc[1] + loc_move[1]]
            new_locs.append(new_loc)

        return new_locs

    def record_locs(self):

        self.step_locs_edge.append(self.cur_loc_edge)

        self.step_states.append(
            {
            'loc': copy.deepcopy(self.cur_loc_body), 
            'yaw': self.cur_yaw_body,
            'loc_st': copy.deepcopy(self.cur_loc_st_relative),
            'velocity': self.cur_velocity,
            })

    def sim_step(self):

        # mm/s
        velocity = self.cur_velocity / 3.6 * 1000
        dt = self.cur_dt

        if self.cur_loc_st_relative == None:
            # 直线行驶
            # 矢量移动中心点
            
            v = self.rotate_loc_relative([[1,0]], self.cur_yaw_body)[0]
            self.cur_loc_body[0] = self.cur_loc_body[0] + v[0] * dt * velocity
            self.cur_loc_body[1] = self.cur_loc_body[1] + v[1] * dt * velocity

        else:
            # 转弯
            # 1、矢量移动中心点, 前轴中心
            # 2、直线行驶
            
            x0 = self.cur_loc_st_relative[0] # 轴距
            y0 = self.cur_loc_st_relative[1] # 旋转中心坐标
            # print(x0)
            
            R = (x0**2 + y0**2)**0.5 # 转弯半径
            rotate_v = (velocity / R) # rad/s
            angle_deg = rotate_v * dt * 180/math.pi # 旋转角
            # print(angle_deg)
            if y0 < 0: angle_deg = -angle_deg
            # print(angle_deg)

            # 相对位移量
            x1, y1 = self.rotate_loc_relative([[-x0, -y0]], angle_deg)[0]
            x2 = x1 + x0
            y2 = y1 + y0
            # print(x2, y2)

            # 旋转得到绝对矢量
            x3, y3 = self.rotate_loc_relative([[x2, y2]], self.cur_yaw_body)[0]
            # print(x3, y3)

            # 重新定义状态
            self.cur_loc_body[0] = self.cur_loc_body[0] + x3
            self.cur_loc_body[1] = self.cur_loc_body[1] + y3

            self.cur_yaw_body = self.cur_yaw_body + angle_deg

        self.get_cur_locs() # 更新状态
        self.record_locs() # 记录        

    def display_step_locs(self, axes_obj, d_recode=1):
        """
        """
        # ------------------
        # 显示
        locs_edge = self.step_locs_edge
        n_length = len(locs_edge)
        for num, step in enumerate(locs_edge):
            # print(step, num)
            if (n_length-1)!=num and num % d_recode != 0: continue

            xs, ys = [], []
            for loc in step[:4]:
                xs.append(loc[0])
                ys.append(loc[1])
            xs.append(step[0][0])
            ys.append(step[0][1])
            axes_obj.plot(xs[:2], ys[:2], 'r') # 车头
            axes_obj.plot(xs[1:], ys[1:], 'b')

        # xmax, xmin = max(xs), min(xs)
        # ymax, ymin = max(ys), min(ys)
        # axes_obj.scatter(xs, ys)
        
        # axes_obj.set_xlim([xmin, xmax])
        # axes_obj.set_ylim([ymin, ymax])

    def undo_steps(self, n_step):

        for n in range(n_step):
            cur_loc_edge = self.step_locs_edge.pop()
            cur_states = self.step_states.pop()

        # self.cur_loc_edge = cur_loc_edge
        self.cur_loc_body = cur_states['loc']
        self.cur_yaw_body = cur_states['yaw']
        self.cur_loc_st_relative = cur_states['loc_st']
        self.cur_velocity = cur_states['velocity']
        self.get_cur_locs()


class CarAxle2:
    """
        两轴车
    """

    def __init__(self, params):
        """
            起始位置为 第一轴中点
        """
        self.L_front_sus = params['L_front_sus']
        self.L_rear_sus = params['L_rear_sus']
        self.L = params['L']
        self.W = params['W']
        self.wheelbase = params['wheelbase']
        self.ds_edge = params['ds_edge']
        self.isEdge = params['isEdge']

        self.length = self.L + self.L_front_sus + self.L_rear_sus
        self.width = self.W

        # 状态记录 
        # 车速 \ 车轮转角
        self.step_states = []
        self.step_states.append({
            "velocity": 0,
            "wheel_angle": 0,
            "dt": 0,
            })
        
        self.create_body()

    def create_body(self):

        body = Body()

        # x0 = self.length/2 - self.L_rear_sus
        x0 = self.L_front_sus - self.length/2
        # y0 = 0
        # body.cur_loc_body = [x0, y0]  # 几何中心位置
        body.cur_loc_body = [0, 0]  # 几何中心位置

        body.l_length = self.length
        body.l_width = self.width
        body.create_loc_edge_locs_relative(x0, self.ds_edge, self.isEdge)  # 边界创建

        body.cur_yaw_body = 0

        body.get_cur_locs()
        body.record_locs()

        self.body = body

    def set_velocity(self, velocity):
    
        self.body.cur_velocity = velocity
        self.cur_velocity = velocity

    def set_dt(self, dt):

        self.body.cur_dt = dt
        self.cur_dt = dt

    def set_wheel_angle(self, angle_deg):
        """
            右转为正
            左转为负
        """
        # 
        if angle_deg == 0:
            self.body.cur_loc_st_relative = None

        elif angle_deg>0:
            # 右转
            x0 = -self.L
            y0 = -(self.L / math.tan(angle_deg/180*math.pi) -self.wheelbase/2)
            self.body.cur_loc_st_relative = [x0, y0] # 旋转中心
            # print(x0, y0)

        elif angle_deg<0:
            # 左转
            x0 = -self.L
            y0 = (self.L / math.tan(-angle_deg/180*math.pi) -self.wheelbase/2)

            self.body.cur_loc_st_relative = [x0, y0]

        self.cur_wheel_angle = angle_deg

    def undo_steps(self, n_step):

        
        for n in range(n_step):
            cur_state = self.step_states.pop()

        self.set_velocity(cur_state['velocity'])
        self.set_wheel_angle(cur_state['wheel_angle'])

        self.body.undo_steps(n_step)

    def sim_step(self):

        self.step_states.append({
            "velocity": self.cur_velocity,
            "wheel_angle": self.cur_wheel_angle,
            "dt": self.cur_dt
            })

        self.body.sim_step()

    def get_result_data(self):

        data_mat = {
            'loc': get_key_steps(self.body.step_states, 'loc'),
            'yaw': get_key_steps(self.body.step_states, 'yaw'),
            'velocity': get_key_steps(self.step_states, 'velocity'),
            'dt': get_key_steps(self.step_states, 'dt'),
            'wheel_angle': get_key_steps(self.step_states, 'wheel_angle'),
            'loc_edge': get_join_list3d(self.body.step_locs_edge),
        }

        return data_mat
    

# 坐标区域扩展
def _area_xy(x, y):
    xs = [x+1, x, x-1]
    ys = [y+1, y, y-1]
    areas = []
    for x in xs:
        for y in ys:
            areas.append((x, y))
    return areas


# 坐标划分
def area_cal(xs, ys, dis_limit=10):
    # dis_limit 区域限制 mm
    
    # areas = set()
    areas = []
    areas_to_ns = {}
    n = 0
    for x, y in zip(xs, ys):
        
        x = round(x / dis_limit)
        y = round(y / dis_limit)
        key = (x, y)
        area = _area_xy(*key)
        areas.extend(area)
        for temp_key in area:
            if temp_key not in areas_to_ns: areas_to_ns[temp_key] = []
            areas_to_ns[temp_key].append(n)
        # areas = areas | set(area)
        # print(areas)
        n += 1
    
    return set(areas), areas_to_ns


def area_check(edge_areas, cur_areas):

    for loc in cur_areas:
        if loc in edge_areas:
            # 干涉
            return loc
    return True



# ------------------------------
# ------------------------------

# 边界
def limit_edge_crose():

    d_s = 10

    y_left = 2000 # 左侧边线位置
    x_limit = 10000   # 前遮挡钱位置
    y_left_offset = 3000    # 左侧边线偏移
    
    y_right = -5000

    # 横坐标线
    x_range = [-10000, x_limit]
    xs_1 = get_np_linspace(x_range, d_s)
    ys_1 = np.array([y_left for n in range(len(xs_1))])

    # 纵坐标线
    ys_2 = get_np_linspace([y_left-y_left_offset, y_left], d_s)
    xs_2 = np.array([x_limit for n in range(len(ys_2))])

    # 横坐标线
    x_range_3 = [x_limit, 100000]
    xs_3 = get_np_linspace(x_range_3, d_s)
    ys_3 = np.array([y_left-y_left_offset for n in range(len(xs_3))]) 

    # 横坐标线
    x_range_4 = [-10000, 100000]
    xs_4 = get_np_linspace(x_range_4, d_s)
    ys_4 = np.array([y_right for n in range(len(xs_4))])     


    xs_list = [xs_1, xs_2, xs_3, xs_4]
    ys_list = [ys_1, ys_2, ys_3, ys_4]
    
    return xs_list, ys_list




# ------------------------------
# ------------------------------
# 

class Driver:

    def __init__(self, param_driver):

        self.param_driver = param_driver
        self.dis_limit_edge = param_driver.get("dis_limit_edge", 50)
        self.dt = param_driver.get("dt", 0.1)
        self.velocity = param_driver.get("velocity", 5)

    # 边界设置
    def set_limit_edge(self, func):

        dis_limit_edge = self.dis_limit_edge

        self.xs_edge_list, self.ys_edge_list = func()
        self.xs_edge, self.ys_edge = np.hstack(self.xs_edge_list), np.hstack(self.ys_edge_list)
        # 边界
        self.edge_areas, __ = area_cal(self.xs_edge, self.ys_edge, dis_limit=dis_limit_edge)

    # 设置Car
    def set_car(self, car_class, param_car):
        
        self.car = car_class(param_car)

    # 驾驶
    def dirve_sim(self, fit_wheel_angle, duration):
        """
            duration : 时长
        """
        # params = self.params
        # car = CarAxle2(params)
        dis_limit_edge = self.dis_limit_edge
        car = self.car
        dt = self.dt
        velocity = self.velocity
        
        num_step = math.ceil(duration / dt)
        # wheel_angle_rate_limit = 10  # deg/s 转角速度限制
        cur_t = 0
        # wheel_angles = []
        # is_success = True
        result = None
        for n in range(num_step):

            # 计算
            car.set_dt(dt)
            car.set_velocity(velocity)
            cur_wheel_angle = fit_wheel_angle(cur_t)
            car.set_wheel_angle(cur_wheel_angle)
            car.sim_step()
            cur_t += dt

            # 检测
            xs_cur = [loc[0] for loc in car.body.cur_loc_edge]
            ys_cur = [loc[1] for loc in car.body.cur_loc_edge]
            cur_areas, cur_areas_to_ns = area_cal(xs_cur, ys_cur, dis_limit=dis_limit_edge)
            check_result = area_check(self.edge_areas, cur_areas)
            
            if check_result != True: # 干涉
                n_checks = cur_areas_to_ns[check_result]
                # print(n_checks)
                for n_loc in n_checks:
                    # print(car.body.get_loc_direction(n_loc))
                    result = car.body.get_loc_direction(n_loc)
                    # print(result, n_loc)
                # car.undo_steps(10) # 回退
                # is_success = False
                break # 终止
            # print(data_mat)

        # data_mat = car.get_result_data()
        # print(cur_t, duration, result)

        return result, cur_t


    def display(self, axes1=None):
        # 结果显示
    
        car = self.car
        # --------------------------------------
        # 显示1
        data_mat = car.get_result_data()

        x_min_1 = min(data_mat['loc_edge'], key=lambda data: data[0])[0]
        x_max_1 = max(data_mat['loc_edge'], key=lambda data: data[0])[0]

        y_min_1 = min(data_mat['loc_edge'], key=lambda data: data[1])[1]
        y_max_1 = max(data_mat['loc_edge'], key=lambda data: data[1])[1]

        n_min = min([x_min_1, y_min_1])
        n_max = max([x_max_1, y_max_1])

        if axes1==None:
            axes1 = plt.subplot(111)
        car.body.display_step_locs(axes1, 5)

        # --------------------------------------
        # 边界
        for xs_n, ys_n in zip(self.xs_edge_list, self.ys_edge_list):
            axes1.plot(xs_n, ys_n, 'g')

        plt.xlim([n_min, n_max])
        plt.ylim([n_min, n_max])
        plt.show()



# 加载
def load_sim():

    car = CarAxle2(params)

    data_mat = loadmat(r'state.mat')

    ts = []
    n = -1
    for dt, wheel_angle, velocity in zip(data_mat['dt'], data_mat['wheel_angle'], data_mat['velocity']):
        n += 1
        if n==0: continue
        car.set_dt(dt)
        car.set_velocity(velocity)
        car.set_wheel_angle(wheel_angle)
        car.sim_step()
    
    view_result(car)


RESULT_DICT = {None:0, 'RearLeft':1, 'FrontLeft':2, 'RearRight':3, 'FrontRight':4}

def test_run(wheel_angles):

    param_car = {
        "L_front_sus": 1000,
        "L_rear_sus": 1000,
        "L": 5000,
        "W": 2000,
        "wheelbase": 2000, # 主销间距
        "ds_edge": 50,    # edge间隙
        "isEdge": True,
        }

    param_driver = {
        "dis_limit_edge": 50, # 边界监测范围
        "dt": 0.1,
        "velocity": 5,
        }

    spline_s = 0.1
    ts = [n for n in range(len(wheel_angles))]
    fit_obj = interpolate.UnivariateSpline(ts, wheel_angles, s=spline_s)

    driver = Driver(param_driver)
    driver.set_limit_edge(limit_edge_crose)
    driver.set_car(CarAxle2, param_car)
    result, cur_t = driver.dirve_sim(fit_obj, len(wheel_angles))
    # print(result, cur_t)
    data_mat = driver.car.get_result_data()
    # print(data_mat)
    # savemat(r'state.mat', data_mat)
    # driver.display()

    # return result, cur_t, data_mat, driver
    return len(wheel_angles)-cur_t


from optimization_pso import pso

if __name__=='__main__':
    pass
    wheel_angles = [0, 15, 15, 8, -4, 0, 0, 0, -5, -5, -10, -4, 0, 0, 0, 0]

    # result, cur_t, data_mat, driver = test_run(wheel_angles)
    # test_run(wheel_angles)
    lb = [-1, -30, -30, -30, -30, -30, -30, -30, -30, -30, -30, -30, -30, -30, -30, -1]        # 参数上限设定
    ub = [1, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 1]     # 参数下限设定
    g, fg, g_record, fg_record = pso(test_run, lb, ub, ieqcons=[], f_ieqcons=None, args=(), kwargs={}, 
            swarmsize=200, omega=0.5, phip=0.5, phig=0.5, maxiter=100, 
            minstep=1e-8, minfunc=1e-8, debug=False, processes=1,
            particle_output=False)
    print(g, fg)

    
    # driver.display()

    # a = VarSearchUi('test', len(wheel_angles), values=wheel_angles, fun_cal=test_run, var_cal=None).run()



    # load_sim()
    # test_area_split()