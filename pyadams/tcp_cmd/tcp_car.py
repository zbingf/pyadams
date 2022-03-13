
import pyadams.tcp_cmd.tcp_cmd_fun as tcmdf
import pyadams.datacal.plot as adams_plot

# help(tcmdf)
# asfd
from pyadams.file import result
DataModel = result.DataModel

import json
import re
import math
import os
import copy

from pprint import pprint

ACAR_FULL_BRAKE_PATH = "acar_full_brake_set.json"
ACAR_FULL_STATIC_PATH = "acar_full_static_set.json"


# 字符串','分割, list非空字符
_str_split = lambda str1: [n.strip() for n in str1.split(',') if n]

# model名称字符串'.'分割, 并选取范围
_name_range = lambda name,start,end=None: '.'.join([v for v in name.split('.') if v][start:end])

# 获取data_dicts的key数据
_parse_datads_by_key = lambda data_dic, data_keys, key: [data_dic[data_key][key] for data_key in data_keys]


# json数据读取
def _json_read(set_path):
    with open(set_path, 'r') as f:
        data = json.load(f)
    return data


# res后处理文件快速读取
def _res_read(name, name_res, res_path, reqs, comps, line_range=[4,None], isSamplerate=False):
    dataobj = DataModel(name)
    dataobj.new_file(res_path, name_res)
    dataobj[name_res].set_reqs_comps(reqs, comps)
    dataobj[name_res].set_line_ranges(line_range)
    dataobj[name_res].set_select_channels(None)
    dataobj[name_res].read_file()
    data = dataobj[name_res].get_data()
    
    if isSamplerate:
        samplerate = dataobj[name_res].get_samplerate()
    else:
        samplerate = None
    
    return data, samplerate


# res后处理文件数据再次获取, 不重复读取
def _res_read_again(name, name_res, reqs, comps, line_range=[4,None]):
    dataobj = DataModel(name)
    dataobj[name_res].set_reqs_comps(reqs, comps)
    dataobj[name_res].set_line_ranges(line_range)
    dataobj[name_res].read_file(isReload=False)    
    data = dataobj[name_res].get_data()
    
    return data


# res文件后处理,单位获取
# 暂时停用
def _res_units(res_path):
    # <Units angle="rad" length="mm" mass="kg" time="sec" />

    f = open(res_path, 'r')
    for n in range(100):
        line = f.readline().lower()
        if '<units' in line and '/>' in line:
            break
    f.close()
    line = line.replace(' ', '')
    
    angle_unit = re.match('.*angle="(\S+?)".*', line).group(1)
    length_unit = re.match('.*length="(\S+?)".*', line).group(1)
    mass_unit = re.match('.*mass="(\S+?)".*', line).group(1)
    time_unit = re.match('.*time="(\S+?)".*', line).group(1)
    units = {
        'angle' : angle_unit,
        'length': length_unit,
        'mass'  : mass_unit,
        'time'  : time_unit,
    }
    # print(angle)
    return units
    

# 暂时停用
def _angel_deg(units, list1):
    angle_unit = units['angle']
    if angle_unit == 'rad':
        return [v*180.0/math.pi for v in list1]

    if angle_unit == 'deg':
        return list1


# 批量编辑data_dic中的value(dict数据),指定key数据覆盖
# data_dic { data_key:{key:value}, ... }
def _edit_datads_by_key(data_dic, data_keys, key, values):
    assert len(data_dic) == len(values), "error: len(data_dic) != len(values)"
    new_data_dic = copy.deepcopy(data_dic)
    
    for data_key, value in zip(data_keys, values):
        new_data_dic[data_key][key] = value
        
    return new_data_dic


# car_comps组合
# car_names 指定key排序
def _parse_comps(datads, data_keys, comp='force'):
    minors = _parse_datads_by_key(datads, data_keys, 'minor')
    comps = []
    for minor in minors:
        if minor=='any':
            comps.append(comp)
        else:
            comps.append(comp+'_'+minor)
            
    return comps


# 根据质量数据,计算绕质心的转动惯量
def parse_I_center(mass_data):

    mass = mass_data['mass']
    x,y,z = mass_data['loc']
    ixx = mass_data['ixx'] - mass*(z**2+y**2)
    iyy = mass_data['iyy'] - mass*(z**2+x**2)
    izz = mass_data['izz'] - mass*(x**2+y**2)
    return [ixx, iyy, izz]


# ------------------------------------------------
# ---dict calc---

# dict处理, 获取字典指定位置的数据, 字典数据需均为list
def _parase_dic_loc(result_dic, loc):
    new_data = {}
    for key in result_dic:
        new_data[key] = result_dic[key][loc]
    return new_data


# dict处理, 字典中均为数值, dic1 - dic2
def _parase_dic_sub(dic1, dic2):
    new_dic = {}
    for key in dic1:
        new_dic[key] = dic1[key] - dic2[key]
    return new_dic


# dict处理, 舍去loc之前数据, 并减去loc位置的数据
def _parase_dic_init_loc(dic1, loc):
    new_dic = {}
    for key in dic1:
        line = dic1[key]
        value = line[loc]
        new_dic[key] = [v-value for v in line[loc:]]

    return new_dic


# dict处理, 对指定key中的list数据求绝对值
def _parase_dic_abs_key(dic1, key):
    dic2 = copy.deepcopy(dic1)
    dic2[key] = [abs(v) for v in dic2[key]]
    return dic2


# 列表中不放dict, 仅存放list | str | int | float
def round_list(data, new_data, n):
    for loc, line in enumerate(data):
        if isinstance(line, list):
            new_data.append([])
            round_list(line, new_data[loc], n)
            continue
        if isinstance(line, str):
            new_data.append(line)
        else:
            new_data.append(round(line, n))
    
    return new_data
            

# 对字典中数值进行round, 存放 dict | list | int | str | float
# 列表中不放dict, 仅存放list | str | int | float
def round_data_dict(data_dic, new_dic, n):
    for key in data_dic:
        v = data_dic[key]
        if isinstance(v, dict):
            new_dic[key] = round_data_dict(v, {}, n)
            continue
        
        if isinstance(v, str):
            new_dic[key] = data_dic[key]
            continue
        
        if isinstance(v, list):
            new_dic[key] = round_list(v, [], n)
            continue    
        
        new_dic[key] = round(v, n)
        
    return new_dic
        


# ------------------------------------------------
# ------------------------------------------------
# --------------------SIM-SPRING-PRELOAD----------
# ------------------------------------------------
# ------------------------------------------------

# 计算-静平衡弹簧预载调整
def sim_static_spring_preload(data):
    
    model_name = data['model_name']
    preload_path = os.path.abspath(data['preload_path']) #.replace('\\', '/')
    
    springs = tcmdf.get_model_nspring_datas(model_name)
    if springs==False: return False
    n_spring = len(springs)
    spring_names = list(springs.keys())
    
    reqs = _parse_datads_by_key(springs, spring_names, 'req_name')
    comps = _parse_comps(springs, spring_names, 'force')
    comps_dis = _parse_comps(springs, spring_names, 'displacement')
    
    # -------------------
    # 弹簧预载初始化
    new_springs = _edit_datads_by_key(springs, spring_names, 'type', ['preload']*n_spring)
    new_springs = _edit_datads_by_key(new_springs, spring_names, 'value', [0]*n_spring)
    new_springs = _edit_datads_by_key(new_springs, spring_names, 'symmetric', [False]*n_spring)
    new_springs = _edit_datads_by_key(new_springs, spring_names, 'path', [preload_path]*n_spring)
    
    for key in new_springs: tcmdf.set_spring(new_springs[key])
    
    # -------------------    
    # 静态计算
    result_static = tcmdf.sim_car_full_static(data)
    res_path = result_static['res_path']
    
    result_data, _ = _res_read('sim_full_static', 'static', res_path, reqs, comps, line_range=None)
    spring_values = [line[-1] for line in result_data]
    # print(spring_values)
    
    # -------------------
    # 弹簧校正
    new_springs_02 = _edit_datads_by_key(springs, spring_names, 'type', ['preload']*n_spring)
    new_springs_02 = _edit_datads_by_key(new_springs_02, spring_names, 'value', spring_values)
    new_springs_02 = _edit_datads_by_key(new_springs_02, spring_names, 'symmetric', [False]*n_spring)
    
    new_spring_edits = []
    for key in new_springs_02: 
        tcmdf.set_spring(new_springs_02[key])
        new_spring_edits.append(tcmdf.parse_spring(new_springs_02[key]))
        
        
    result_static = tcmdf.sim_car_full_static(data)
    res_path = result_static['res_path']
    result_data, _ = _res_read('sim_full_static', 'static', res_path, reqs, comps_dis, line_range=None)
    spring_lengths = [line[-1] for line in result_data]
    # print(spring_length)
    
    # print('\n'.join(new_spring_edits))
    
    output_data = {
        'spring_names'   : [_name_range(name,1) for name in spring_names],
        'spring_values'  : {_name_range(name,1):value for name, value in zip(spring_names, spring_values)},
        'spring_lengths' : {_name_range(name,1):value for name, value in zip(spring_names, spring_lengths)},
        'cmd'           : '\n'.join(new_spring_edits),
        }
    
    return output_data


# 主程序-当前-静平衡弹簧预载调整
def main_cur_static_preload():

    data = _json_read(ACAR_FULL_STATIC_PATH)
    data['model_name'] = tcmdf.get_current_model()
    # print(sim_static_spring_preload(data))
    return sim_static_spring_preload(data)


# ------------------------------------------------
# ------------------------------------------------
# --------------------SIM-STATIC-ONLY-------------
# ------------------------------------------------
# ------------------------------------------------


# 解析轮胎中心坐标数据
# 输入:tire_locs
# {
#  'msc_truck_drive_wheels.til_inside_wheel': [7405.9,-693.45,758.4],
#  'msc_truck_drive_wheels.til_outside_wheel': [7405.9, -1040.2,758.4],
#  'msc_truck_drive_wheels.tir_inside_wheel': [7405.9,693.45,758.4],
#  'msc_truck_drive_wheels.tir_outside_wheel': [7405.9,1040.2,758.4],
# }
# 输出
# Ls dict, 轴距
# Ws dict, 轮距
# x_start 第一轴 X 坐标
# tire_names list 排序后的名称,先左再右
def parse_tire_locs(tire_locs):

    right_tire_locs = {key:tire_locs[key] for key in tire_locs if tire_locs[key][1]>0}
    right_tire_names = sorted(right_tire_locs.keys(), key=lambda v: right_tire_locs[v][0])
    
    left_tire_locs = {key:tire_locs[key] for key in tire_locs if tire_locs[key][1]<0}
    left_tire_names = sorted(left_tire_locs.keys(), key=lambda v: left_tire_locs[v][0])
    
    Ls, Ws = {}, {}  
    loc1 = 1
    x_limit= 5
    last_name = right_tire_names[0]
    Ws[f"W-{loc1}-{last_name}"] = abs(right_tire_locs[last_name][1])*2
    for n in range(1, len(right_tire_names)):
        cur_name = right_tire_names[n]
        dx = right_tire_locs[cur_name][0] - right_tire_locs[last_name][0]
        if abs(dx) > x_limit: 
            Ls[f"L-{loc1}-{loc1+1}"] = dx
            loc1 += 1
            
        Ws[f"W-{loc1}-{cur_name}"] = abs(right_tire_locs[cur_name][1])*2
        last_name = cur_name
        
    # 第一轴 X 坐标
    x_start = right_tire_locs[right_tire_names[0]][0]
        
    tire_names = []
    for left, right in zip(left_tire_names, right_tire_names):
        tire_names.extend([left, right])
    
    return Ls, Ws, x_start, tire_names
    

# 计算-静平衡计算
# {
#  'mass': 10844.35,
#  'I_center': [298688841.89, 1162890925.9, 1341023809.23],
#  'm_center': [1749.05, -1.42, 415.45],
#  'tire_forces': {'TR_Front_Tires.til_wheel': 3160.12,
#                  'TR_Front_Tires.tir_wheel': 3145.06,
#                  'TR_Rear_Tires.til_wheel': 4344.29,
#                  'TR_Rear_Tires.tir_wheel': 4331.96},
#  'tire_locs': {'TR_Front_Tires.til_wheel': [267.0, -760.0, 330.0],
#                'TR_Front_Tires.tir_wheel': [267.0, 760.0, 330.0],
#                'TR_Rear_Tires.til_wheel': [2827.0, -797.0, 350.0],
#                'TR_Rear_Tires.tir_wheel': [2827.0, 797.0, 350.0]},
#  'tire_names': list 排序后的名称,先左再右
#  'Ls': {'L-1-2': 5295.3, 'L-2-3': 1300.0},
#  'Ws': {'W-1-msc_truck_steer_wheels.tir_wheel': 2020.0,
#         'W-2-msc_truck_drive_wheels.tir_inside_wheel': 1386.9,
#         'W-2-msc_truck_drive_wheels.tir_outside_wheel': 2080.4,
#         'W-3-msc_truck_drive_wheels_2.tir_inside_wheel': 1386.9,
#         'W-3-msc_truck_drive_wheels_2.tir_outside_wheel': 2080.4},
# }
def sim_static_only(data):
    
    model_name = data['model_name']
    
    # -------------------    
    result_static = tcmdf.sim_car_full_static(data) # 静态计算
    res_path = result_static['res_path']
    
    mass_data = tcmdf.get_aggregate_mass(model_name)
    road_z = tcmdf.get_testrig_road_marker_z(model_name) # 必须计算后再测量路面高
    tire_datas = tcmdf.get_model_tire_data(model_name)
    
    tire_names = list(tire_datas.keys())
    reqs = _parse_datads_by_key(tire_datas, tire_names, 'req_name')
    comps = _parse_comps(tire_datas, tire_names, 'normal')
    
    result_data, _ = _res_read('sim_full_static_only', 'static_only', res_path, reqs, comps, line_range=None)
    tire_values = [line[-1] for line in result_data]
    # print(tire_values)
    
    tire_forces = {_name_range(name,1):value for name, value in zip(tire_names, tire_values)}
    tire_locs   = {_name_range(name,1):tire_datas[name]['loc'] for name in tire_names}
    
    # ---------------
    # 转动惯量, 质心高
    I_center = parse_I_center(mass_data)
    locs = mass_data['loc']
    locs[2] = locs[2]-road_z
    
    # 轮心坐标数据处理
    Ls, Ws, x_start, tire_names = parse_tire_locs(tire_locs)
    locs[0] = locs[0] - x_start # X坐标校正
    
    vehicle_data = {
        'mass' : mass_data['mass'],
        'I_center': I_center,
        'm_center': locs,
        'tire_names'  : tire_names,
        'tire_forces' : tire_forces,
        'tire_locs'   : tire_locs,
        'Ls' : Ls,
        'Ws' : Ws,
    }
    
    return vehicle_data
    

def main_cur_static_only():

    data = _json_read(ACAR_FULL_STATIC_PATH)
    data['model_name'] = tcmdf.get_current_model()
    vehicle_data = round_data_dict(sim_static_only(data), {}, 2)
    # pprint(round_data_dict({"a":vehicle_data, "b":{"b1":vehicle_data, 'b2':vehicle_data}}, {}, 1))
    
    return vehicle_data


# ------------------------------------------------
# ------------------------------------------------
# --------------------SIM-BRAKE-------------------
# ------------------------------------------------
# ------------------------------------------------

# 单个制动仿真
# 返回制动数据
def sim_brake_single(params):

    result = tcmdf.sim_car_full_brake(params)

    res_path = result['res_path']
    reqs = _str_split(params['requests'])
    comps = _str_split(params['components'])
    comments = _str_split(params['comments'])
    req_units = _str_split(params['req_units'])

    # res_units = _res_units(res_path)

    brake_start_loc = params['t_start'] * params['step'] / params['t_end']
    brake_start_loc = int(brake_start_loc)-1

    init_v = int(params['velocity'])
    name_single = f'brake_{init_v}'
    data, samplerate = _res_read('sim_full_brake', name_single, 
        res_path, reqs, comps)

    result_dic = {}
    for line, comment, req_unit in zip(data, comments, req_units):
        if req_unit == 'rad':
            result_dic[comment] = [n*180/math.pi for n in line]
            continue
        result_dic[comment] = line

    # start_dic = _parase_dic_loc(result_dic, brake_start_loc)
    # end_dic   = _parase_dic_loc(result_dic, -1)
    
    new_result_dic = _parase_dic_init_loc(result_dic, brake_start_loc)
    new_result_dic['x_acc'] = result_dic['x_acc'][brake_start_loc:]
    new_result_dic['velocity'] = result_dic['velocity'][brake_start_loc:]
    dend_dic = _parase_dic_loc(new_result_dic, -1)

    # x_dis, y_dis, velocity = data[0], data[1], data[3]
    # pitch = _angel_deg(res_units, data[2])

    # return {'x_dis':x_dis, 'y_dis':y_dis, 'pitch':pitch, 'velocity':velocity}
    return dend_dic, new_result_dic, samplerate


# 当前-模型制动仿真
# 包含紧急制动及目标加速度的制动迭代
# 指定踏板深度计算
# results[int(velocity)] = {
#     "params": data,      # 对应参数
#     "dend":dend_n,       # 紧急制动, 结束位置的数据
#     "result":result_n,   # 紧急制动, 开始制动之后的数据
#     "dend_t":dend_t,     # 目标加速度制动, 结束位置的数据
#     "result_t":result_t, # 目标加速度制动, 开始制动之后的数据
#     "brake_t": brake_t,  # 目标加速度制动
#     "g_t":data['target_g'], # 目标加速度
#     "samplerate": samplerate, # 采样Hz
#     }
def sim_cur_brake():

    abs_min_acc = lambda result: abs(min(result['x_acc']))

    model_name = tcmdf.get_current_model()

    data = _json_read(ACAR_FULL_BRAKE_PATH)

    velocity_list = [float(v) for v in data['velocity_list'].split(',') if v]

    data['model_name'] = model_name
    
    target_tolerance_g = data['target_tolerance_g']
    target_g = data['target_g']

    
    def ite_run(data, last_acc, gain=0.8, n_ite=10):
        # 迭代仿真
        cur_brake = 100 / last_acc * target_g
        d_brake = 100 / last_acc * gain
        for calc_n in range(n_ite):
            data['brake'] = cur_brake
            dend_dic, result, samplerate = sim_brake_single(data)
            cur_acc = abs_min_acc(result)

            # print('d_acc: ')
            if abs(target_g - cur_acc) < target_tolerance_g:  
                # print('符合计算')
                break
                
            # d_brake = (last_brake-cur_brake) / (last_acc - cur_acc)
            last_brake, last_acc = cur_brake, cur_acc
            cur_brake = last_brake + d_brake*(target_g - cur_acc) 
        return dend_dic, result, cur_brake

    results = {}
    for velocity in velocity_list:
        # 紧急制动
        data['brake'] = 100    
        data['sim_name'] = f'v{int(velocity)}'
        data['velocity'] = velocity
        dend_n, result_n, samplerate = sim_brake_single(data)

        # 目标加速度, 迭代仿真
        data['sim_name'] = data['sim_name'] + '_limit'
        last_acc = abs_min_acc(result_n)
        dend_t, result_t, brake_t = ite_run(data, last_acc)

        results[int(velocity)] = {
            "params": data,      # 对应参数
            "dend":dend_n,       # 紧急制动, 结束位置的数据
            "result":result_n,   # 紧急制动, 开始制动之后的数据
            "dend_t":dend_t,     # 目标加速度制动, 结束位置的数据
            "result_t":result_t, # 目标加速度制动, 开始制动之后的数据
            "brake_t": brake_t,  # 目标加速度制动
            "g_t":data['target_g'], # 目标加速度
            "samplerate": samplerate, # 采样Hz
            }

    # print(results)
    return results


# 当前-制动后处理
def post_cur_brake(results):
    pass
    
    # model_name = tcmdf.get_current_model()
    
    for velocity in results:
        print(velocity)
        print(results[velocity])
        
    
    
    # print(model_name)
    print(results[30]['dend'])
    

# results = sim_cur_brake()
# results = []
# pprint(results)
# post_cur_brake(results)


if __name__ == '__main__':
    pass
    
    
    pprint(main_cur_static_preload())
    pprint(main_cur_static_only())
    # vehicle_data
   
    



