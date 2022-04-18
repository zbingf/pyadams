
# 默认单位 mm  km/h
# 
import math
import copy
import numpy as np

import matplotlib.pyplot as plt

class Body:

    def __init__(self):
        self.body_type = None
        self.dt = None  # 时间间隔

        self.l_length = None # 车长
        self.l_width = None # 车宽

        # 当前车速 km / s 
        self.cur_velocity = None

        # 当前body位置, 此处指代body几何中心
        self.cur_loc_body = None

        # 当前body相对原点坐标系旋转角 deg
        self.cur_r_body = None

        # 相对旋转中心
        self.cur_loc_st_relative = None

        # 
        self.step_locs = []
        # 
        self.step_states = []

        self.cur_locs = None

    def create_loc_edge_locs_relative(self, dis=5):
        """
            根据
                长、宽
                当前body位置
                当前body转角
        """
        # dis = 3

        L = self.l_length
        W = self.l_width

        locs = []

        for n in range(int(L/2/dis)):
            x = + n*dis
            y = + W/2
            
            loc_n = [x, y]
            locs.append(loc_n)
        locs.append([L/2, W/2])

        for n in range(int(W/2/dis)):
            x = + L/2
            y = + n*dis
            loc_n = [x, y]
            locs.append(loc_n)

        locs_right = copy.deepcopy(locs)
        for loc in locs_right:
            loc[0] = -loc[0]

        locs_right.extend(locs)

        locs_left = copy.deepcopy(locs_right)
        for loc in locs_left:
            loc[1] = -loc[1]

        locs = [] + locs_right + locs_left

        self.locs_relative = locs
        return self.locs_relative

    def get_cur_locs(self):

        locs_rotate = self.rotate_loc_relative(self.locs_relative, self.cur_r_body)
        new_locs = self.move_loc_relative(locs_rotate, self.cur_loc_body)

        self.cur_locs = new_locs
        
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

        self.step_locs.append(self.cur_locs)

        self.step_states.append(
            {'loc': self.cur_loc_body, 
            'angle': self.cur_r_body,
            'loc_st': self.cur_loc_st_relative,
            'velocity': self.cur_velocity,
            })

    def sim_step(self):

        # mm/s
        velocity = self.cur_velocity / 3.6 * 1000
        dt = self.dt

        if self.cur_loc_st_relative == None:
            # 直线行驶
            # 矢量移动中心点
            
            v = self.rotate_loc_relative([[1,0]], self.cur_r_body)[0]
            v * self.dt * self.cur_velocity
            self.cur_loc_body[0] = self.cur_loc_body[0] + v[0] * dt * velocity
            self.cur_loc_body[1] = self.cur_loc_body[1] + v[1] * dt * velocity

        else:
            # 转弯
            # 1、矢量移动中心点
            # 2、直线行驶
            
            x0 = -self.cur_loc_st_relative[0]
            y0 = -self.cur_loc_st_relative[1]
            
            R = (x0**2+y0**2)**0.5
            rotate_v = (velocity / R) # rad/s
            angle_deg = rotate_v*dt * 180/math.pi
            if y0<0: angle_deg = -angle_deg

            # 相对位移量
            x1, y1 = self.rotate_loc_relative([[x0, y0]], angle_deg)[0]
            x2 = x1 - x0
            y2 = y1 - y0

            # 旋转得到绝对矢量
            x3, y3 = self.rotate_loc_relative([[x2, y2]], self.cur_r_body)[0]

            # 重新定义状态
            self.cur_loc_body[0] = self.cur_loc_body[0] + x3
            self.cur_loc_body[1] = self.cur_loc_body[1] + y3

            self.cur_r_body = self.cur_r_body + angle_deg

        self.get_cur_locs() # 更新状态
        self.record_locs() # 记录        

    def display_steps(self, axes_obj):

        # ------------------
        # 显示
        xs, ys = [], []
        for step in self.step_locs:
            for loc in step:
                xs.append(loc[0])
                ys.append(loc[1])

        xmax, xmin = max(xs), min(xs)
        ymax, ymin = max(ys), min(ys)
        axes_obj.scatter(xs, ys)
        # axes_obj.set_xlim([xmin, xmax])
        # axes_obj.set_ylim([ymin, ymax])

    def goback_state(self, n_step):

        for n in range(n_step):
            cur_locs = self.step_locs.pop()
            cur_states = self.step_states.pop()

        # self.cur_locs = cur_locs
        self.cur_loc_body = cur_states['loc']
        self.cur_r_body = cur_states['angle']
        self.cur_loc_st_relative = cur_states['loc_st']
        self.cur_velocity = cur_states['velocity']
        self.get_cur_locs()

class CarAxle2:

    def __init__(self, params):
        """
            起始位置为 第一轴中点
        """
        self.L_front_sus = params['L_front_sus']
        self.L_rear_sus = params['L_rear_sus']
        self.L = params['L']
        self.W = params['W']
        self.wheelbase = params['wheelbase']
        self.ds = params['ds']

        self.length = self.L + self.L_front_sus + self.L_rear_sus
        self.width = self.W

        self.step_carstates = []

    def create_body(self):

        body = Body()

        x0 = self.L_front_sus - self.length/2
        y0 = 0
        body.cur_loc_body = [x0, y0]  # 几何中心位置

        body.l_length = self.length
        body.l_width = self.width
        body.create_loc_edge_locs_relative(self.ds)  # 边界创建

        body.cur_r_body = 0
        body.get_cur_locs()
        body.record_locs()

        self.body = body

    def set_velocity(self, velocity):
    
        self.body.cur_velocity = velocity
        self.cur_velocity = velocity

    def set_dt(self, dt):

        self.body.dt = dt

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
            y0 = (self.L / math.tan(angle_deg/180*math.pi) -self.wheelbase/2)
            self.body.cur_loc_st_relative = [x0, y0]

        elif angle_deg<0:
            # 左转
            x0 = -self.L
            y0 = -(self.L / math.tan(-angle_deg/180*math.pi) -self.wheelbase/2)

            self.body.cur_loc_st_relative = [x0, y0]

        self.cur_angle = angle_deg

    def goback_state(self, n_step):

        
        for n in range(n_step):
            cur_state = self.step_carstates.pop()

        self.set_velocity(cur_state['velocity'])
        self.set_wheel_angle(cur_state['angle'])

        self.body.goback_state(n_step)


    def sim_step(self):

        self.step_carstates.append({
            "velocity": self.cur_velocity,
            "angle": self.cur_angle,            
            })

        self.body.sim_step()





params = {
    "L_front_sus": 1000,
    "L_rear_sus": 1000,
    "L": 5000,
    "W": 2000,
    "wheelbase": 2000,
    "ds": 100,
    }

car = CarAxle2(params)
car.create_body()

car.set_dt(0.1)
for n in range(230):
    if n == 100: 
        car.goback_state(50)
        # break
    car.set_velocity(10)
    car.set_wheel_angle(30)
    car.sim_step()

# print(car.step_carstates)
# print(car.step_carstates)

# 显示
axes1 = plt.subplot(111)
car.body.display_steps(axes1)
plt.xlim([-40000, 40000])
plt.ylim([-40000, 40000])
plt.show()


