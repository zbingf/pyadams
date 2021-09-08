"""
"""

import copy
import math
import json
import os

import pysnooper
import post_signal

create_post_signal = post_signal.create_post_signal

# 路面配置读取
set_path = os.path.join(os.path.dirname(__file__), 
    'altoona_road_set.json')
with open(set_path, 'r') as f: altoona_road_set = json.load(f)

# print(altoona_road_set)

#子函数
add_list   = lambda list1, value: [ n + value for n in list1 ]
multi_list = lambda list1, value: [ n * value for n in list1 ]

# line_csv生成
def write_lines_two(csv_path, xs_l, zs_l, xs_r, zs_r):
    
    with open(csv_path, 'w') as f:
        f.write('left_x,left_z,right_x,right_z,\n')
        for xl, zl, xr, zr in zip(xs_l, zs_l, xs_r, zs_r):
            f.write(f'{xl},{zl},{xr},{zr},\n')
    
    return None

def test_write_lines_two():
    csv_path = './tests/write_lines_two.csv'
    xs_l = [1,1,1,1]
    zs_l = [2,2,2,2]
    xs_r = [3,3,3,3]
    zs_r = [4,4,4,4]
    write_lines_two(csv_path, xs_l, zs_l, xs_r, zs_r)



# ------------------------------------------------------
# ca-7 创建左轮过、右轮过、双轮过
# @pysnooper.snoop()
def lines_ca_7(params):
    # 输入
    x_start = params['x_start']         # 起始位置
    x_1     = params['x_dis_up_down']   # 上/下坡距离
    x_2     = params['x_dis_down']      # 底部距离 
    h       = params ['height']         # 深度 mm
    csv_path= r'Altoona_ca_7.csv'          # csv保存路径

    #计算
    x_end      = 2*x_start + 2*x_1 + x_2
    line_ca7_x = [0, x_start, x_start+x_1, x_start+x_1+x_2, x_start+2*x_1+x_2, x_end,]
    line_ca7_z = [0,       0,           h,               h,                 0,     0,]
    zero_z     = [0 for n in line_ca7_z]

    # left 左侧过坑
    xs_l = copy.deepcopy(line_ca7_x)
    zs_l = copy.deepcopy(line_ca7_z)

    xs_r = copy.deepcopy(line_ca7_x)
    zs_r = copy.deepcopy(zero_z)

    csv_path_left = csv_path[:-4] + '_left.csv'
    write_lines_two(csv_path_left, 
        xs_l, zs_l, xs_r, zs_r)

    # right 左侧过坑
    xs_l = copy.deepcopy(line_ca7_x)
    zs_l = copy.deepcopy(zero_z)

    xs_r = copy.deepcopy(line_ca7_x)
    zs_r = copy.deepcopy(line_ca7_z)

    csv_path_right = csv_path[:-4] + '_right.csv'
    write_lines_two(csv_path_right, 
        xs_l, zs_l, xs_r, zs_r)

    # double 双轮过坑
    xs_l = copy.deepcopy(line_ca7_x)
    zs_l = copy.deepcopy(line_ca7_z)

    xs_r = copy.deepcopy(line_ca7_x)
    zs_r = copy.deepcopy(line_ca7_z)

    csv_path_double = csv_path[:-4] + '_double.csv'
    write_lines_two(csv_path_double, 
        xs_l, zs_l, xs_r, zs_r)

    return [csv_path_left, csv_path_right, csv_path_double]


# ------------------------------------------------------
# CA-2 创建 , 扭曲路
# @pysnooper.snoop()
def lines_ca_2(params):
    # 右侧先过
    x_start  = params['x_start']
    h        = params['height']
    x_1      = params['x_dis_up_down']
    x_2      = params['x_dis_up']
    x_delta  = params['x_dis_delta']

    x_end    = 2*x_start + 2*x_1 + x_2

    csv_path = r'Altoona_ca_2.csv' 

    lines_ca2_x = [0, x_start, x_start+x_1, x_start+x_1+x_2, x_start+2*x_1+x_2, x_end,]
    lines_ca2_z = [0,       0,           h,               h,                 0,     0,]

    xs_r = copy.deepcopy(lines_ca2_x)
    zs_r = copy.deepcopy(lines_ca2_z)

    xs_l = add_list(xs_r, x_delta)
    zs_l = copy.deepcopy(lines_ca2_z)

    write_lines_two(csv_path, 
        xs_l, zs_l, xs_r, zs_r)

    return [csv_path]


# ------------------------------------------------------
# CA-5 创建 , 方坑路
# @pysnooper.snoop()
def lines_ca_5(params):

    x_start   = params['x_start']
    csv_path  = r'Altoona_ca_5.csv'
    csv_path2 = r'Altoona_ac_5.csv'

    # B路
    line_ca5_x1 = [0, 1219,   457, 305,   305, 1219,   229, 2438,  1829, 305,   457, 914,   610, 914,   305,]
    line_ca5_z1 = [0,    0, -25.4,   0, -25.4,    0, -25.4,    0, -25.4,   0, -25.4,   0, -25.4,   0, -25.4,]

    # A路
    line_ca5_x2 = [0, 914,   229, 2438,  1829, 305,   457, 914,   610, 1219,   457, 305,   305, 1219,   305,]
    line_ca5_z2 = [0,   0, -25.4,    0, -25.4,   0, -25.4,   0, -25.4,    0, -25.4,   0, -25.4,    0, -25.4,]

    new_line_ca5_x1 = []
    new_line_ca5_z1 = []
    for loc, value in enumerate(line_ca5_x1):
        x_value = sum(line_ca5_x1[:loc+1])

        new_line_ca5_x1.append(x_value)
        new_line_ca5_z1.append(line_ca5_z1[loc])

        if x_value > 0:
            new_line_ca5_x1.append(x_value+1)
            if loc+1 < len(line_ca5_x1):
                new_line_ca5_z1.append(line_ca5_z1[loc+1])
            else:
                new_line_ca5_z1.append(0)

    new_line_ca5_x2 = []
    new_line_ca5_z2 = []
    for loc, value in enumerate(line_ca5_x2):
        x_value = sum(line_ca5_x2[:loc+1])

        new_line_ca5_x2.append(x_value)
        new_line_ca5_z2.append(line_ca5_z2[loc])
        if x_value > 0:
            new_line_ca5_x2.append(x_value+1)
            if loc+1 < len(line_ca5_x2):
                new_line_ca5_z2.append(line_ca5_z2[loc+1])
            else:
                new_line_ca5_z2.append(0)

    # ------------------------------------------------------
    # CA路创建
    x1 = add_list(new_line_ca5_x1, x_start)
    x2 = add_list(new_line_ca5_x2, x_start+max(new_line_ca5_x1))

    z1 = copy.deepcopy(new_line_ca5_z1)
    z2 = copy.deepcopy(new_line_ca5_z2)

    # 右轮
    line_ca5_x_right = [0] + x1 + x2[1:] + [max(x2)+x_start]
    line_ca5_z_right = [0] + z1 + z2[1:] + [0]

    x1 = add_list(new_line_ca5_x2, x_start)
    x2 = add_list(new_line_ca5_x1, x_start+max(new_line_ca5_x2))

    z1 = copy.deepcopy(new_line_ca5_z2)
    z2 = copy.deepcopy(new_line_ca5_z1)

    line_ca5_x_left = [0] + x1 + x2[1:] + [max(x2)+x_start]
    line_ca5_z_left = [0] + z1 + z2[1:] + [0]

    write_lines_two(csv_path, 
        line_ca5_x_left, line_ca5_z_left, line_ca5_x_right, line_ca5_z_right)

    # ------------------------------------------------------
    # AC路创建
    line_ac5_x_left  = copy.deepcopy(line_ca5_x_right)
    line_ac5_z_left  = copy.deepcopy(line_ca5_z_right)
    line_ac5_x_right = copy.deepcopy(line_ca5_x_left)
    line_ac5_z_right = copy.deepcopy(line_ca5_z_left)
    line_ac5_x_left.reverse()
    line_ac5_z_left.reverse()
    line_ac5_x_right.reverse()
    line_ac5_z_right.reverse()

    line_ac5_x_left  = [-n+max(line_ac5_x_left) for n in line_ac5_x_left]
    line_ac5_x_right = [-n+max(line_ac5_x_right) for n in line_ac5_x_right]

    write_lines_two(csv_path2, 
        line_ac5_x_left, line_ac5_z_left, line_ac5_x_right, line_ac5_z_right)

    # print(sum(line_ca5_x1))
    # print(sum(line_ca5_x2))

    return [csv_path, csv_path2]


# ------------------------------------------------------
# CA-6 创建搓板路

# 创建 单个正弦波路 (搓板路) XZ平面
def point_sin(length, hight, dx, x0=0.0, z0=0.0): 
    """
        sin 正弦波 - 中心线
        单个凸包 中心线生成 正弦函数形状
        length 凸包长 X
        hight 凸包高度 Z
        dx 采点的 X向 间隔
        x0 初始X位置 
    """

    num = int(length//dx)
    xs, zs = [], []
    for n in range(num):
        xs.append(n*dx+x0)
        zs.append(hight*math.sin(math.pi/length*n*dx+z0))
    
    xs[-1] = length+x0
    zs[-1] = z0

    return xs,zs

# @pysnooper.snoop()
def lines_ca_6(params):

    w             = params['w']    # 轮距
    x_start       = params['x_start']
    y_angle       = params['y_angle_deg']
    num_washboard = params['num_washboard']
    h             = params['height']
    length        = params['length_washboard']
    x_washboard   = params['x_dis_washboard']

    csv_path_name = r'Altoona_ca_6'
    x_end         = x_washboard*num_washboard + x_start*2

    xs, zs = point_sin(length, h, dx=2, x0=0.0, z0=0.0)

    xs += [x_washboard]
    zs += [0]

    x_cur = 0
    for n in range(num_washboard):
        if x_cur==0:
            line_x = [0]
            line_z = [0]
            x_cur  = x_start
        xs_cur = add_list(copy.deepcopy(xs), x_cur)
        zs_cur = zs
        line_x.extend(xs_cur[:-1])
        line_z.extend(zs_cur[:-1])
        x_cur += x_washboard

    line_x += [x_end]
    line_z += [0]

    csv_paths = []
    for loc, value in enumerate(w):

        csv_path = csv_path_name + f'_A{loc}.csv'
        x_delta  = value*math.tan(y_angle*math.pi/180) # 搓板间距
        
        line_ca6_x_right = copy.deepcopy(line_x)
        line_ca6_z_right = copy.deepcopy(line_z)

        line_ca6_x_left = add_list(copy.deepcopy(line_x), x_delta)
        line_ca6_z_left = copy.deepcopy(line_z)

        write_lines_two(csv_path, 
            line_ca6_x_left, line_ca6_z_left, line_ca6_x_right, line_ca6_z_right)

        csv_paths.append(csv_path)

    return csv_paths


# 前后轴数据拼接
def csv_ca6_res_change(csv_6s_res):
    
    data_dic = {}
    n_axle   = 0
    for loc, csv_path in enumerate(csv_6s_res):
        n_axle += 1
        data    = []
        line_len = None
        with open(csv_path, 'r') as f:
            lines = [n for n in f.read().split('\n') if n]
            for str_n in lines:
                line = [n for n in str_n.split(',') if n]
                if line_len == None:
                    line_len = len(line)
                    data = [[] for n in range(line_len)]
                for loc_2, value in enumerate(line):
                    data[loc_2].append(value)

        data_dic[loc] = data

    for loc in range(n_axle):
        if loc == 0:
            data_base = data_dic[0]
            continue
        data_base[1+2*loc]   = data_dic[loc][1+2*loc]
        data_base[1+2*loc+1] = data_dic[loc][1+2*loc+1]

    csv_path_6_base = csv_6s_res[0].replace('_A0', '')
    with open(csv_path_6_base, 'w') as f:
        n_len = len(data_base)
        for loc1 in range(len(data_base[0])):
            for loc2 in range(len(data_base)):
                f.write(data_base[loc2][loc1] + ',')
            f.write('\n')

    return csv_path_6_base


# ------------------------------------------------------
# Altoona 路面信号创建
def altoona_road(params):

    params_2 = altoona_road_set['ca_2']
    params_5 = altoona_road_set['ca_5']
    params_6 = altoona_road_set['ca_6']
    params_7 = altoona_road_set['ca_7']
    params_6.update(params)

    csv_2s = lines_ca_2(params_2)
    csv_5s = lines_ca_5(params_5)
    csv_6s = lines_ca_6(params_6)
    csv_7s = lines_ca_7(params_7)

    csv_res_paths = []
    csv_6s_res    = []
    for csv_paths, param_n in zip([csv_2s, csv_5s, csv_6s, csv_7s], 
        [params_2, params_5, params_6, params_7]):

        samplerate = param_n['samplerate']
        for csv_path in csv_paths:
            csv_res_path = csv_path[:-4] + f'_res_{samplerate}Hz.csv'
            create_post_signal(
                params = {
                    'csv_res_path'  : csv_res_path,
                    'csv_line_path' : csv_path,
                    'vel'           : param_n['velocity'], # 车速 km/h
                    'time_len'      : param_n['time'],     # 时间长度 s
                    'x_axle'        : params['x_axle'],    # 各轴到第1轴的距离 mm
                })
            if 'num_washboard' in param_n:
                csv_6s_res.append(csv_res_path)
            else:
                csv_res_paths.append(csv_res_path)

    csv_6_res = csv_ca6_res_change(csv_6s_res)
    csv_res_paths.append(csv_6_res)

    for path in csv_6s_res: os.remove(path)
    for path in csv_2s: os.remove(path)
    for path in csv_5s: os.remove(path)
    for path in csv_6s: os.remove(path)
    for path in csv_7s: os.remove(path)

    return csv_res_paths

if __name__ == '__main__':
    pass
    params = {
        'w'      :[2175.24, 1923.4], # 前→后轴 轮距
        'x_axle' :[7214.0],          # 前→后轴 ,到第1轴轴距
    }
    altoona_road(params)
    print('计算结束')

    