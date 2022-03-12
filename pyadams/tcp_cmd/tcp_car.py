
import pyadams.tcp_cmd.tcp_cmd_fun as tcmdf
# help(tcmdf)
# asfd
from pyadams.file import result
DataModel = result.DataModel

import json
import re
import math
import os
import copy



acar_full_brake_path = "acar_full_brake_set.json"
acar_full_static_path = "acar_full_static_set.json"


# 字符串','分割, list非空字符
_str_split = lambda str1: [n.strip() for n in str1.split(',') if n]


# json数据读取
def _json_read(set_path):
    with open(set_path, 'r') as f:
        data = json.load(f)
    return data

# res后处理文件快速读取
def _res_read(name, name_res, res_path, reqs, comps, line_range=[4,None]):
    dataobj = DataModel(name)
    dataobj.new_file(res_path, name_res)
    dataobj[name_res].set_reqs_comps(reqs, comps)
    dataobj[name_res].set_line_ranges(line_range)
    dataobj[name_res].set_select_channels(None)
    dataobj[name_res].read_file()
    data = dataobj[name_res].get_data()
    
    return data

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


# 根据质量数据,计算绕质心的转动惯量
def parse_I_center(mass_data):

    mass = mass_data['mass']
    x,y,z = mass_data['loc']
    ixx = mass_data['ixx'] - mass*(z**2+y**2)
    iyy = mass_data['iyy'] - mass*(z**2+x**2)
    izz = mass_data['izz'] - mass*(x**2+y**2)
    # print()
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
    data = _res_read('sim_full_brake', name_single, 
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
    return dend_dic, new_result_dic


# 当前-模型制动仿真
# 包含紧急制动及目标加速度的制动迭代
# 指定踏板深度计算
def sim_cur_brake():

    abs_min_acc = lambda result: abs(min(result['x_acc']))

    model_name = tcmdf.get_current_model()

    data = _json_read(acar_full_brake_path)

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
            dend_dic, result = sim_brake_single(data)
            cur_acc = abs_min_acc(result)

            # print('d_acc: ')
            if abs(target_g - cur_acc) < target_tolerance_g:  
                # print('符合计算')
                break
                
            # d_brake = (last_brake-cur_brake) / (last_acc - cur_acc)
            last_brake, last_acc = cur_brake, cur_acc
            cur_brake = last_brake + d_brake*(target_g - cur_acc) 
        return dend_dic, result

    results = {}
    for velocity in velocity_list:
        # 紧急制动
        data['brake'] = 100    
        data['sim_name'] = f'v{int(velocity)}'
        data['velocity'] = velocity
        dend_n, result_n = sim_brake_single(data)

        # 目标加速度, 迭代仿真
        data['sim_name'] = data['sim_name'] + '_limit'
        last_acc = abs_min_acc(result_n)
        dend_t, result_t = ite_run(data, last_acc)

        results[int(velocity)] = {"dend":dend_n, "result":result_n, "dend_t":dend_t, "result_t":result_t}

    # print(results)
    return results
    
    
    # # -------------------
    # # v60
    # data['sim_name'] = 'v60'
    # data['velocity'] = 60
    # dend_v60, result_v60 = sim_brake_single(data)

    # # -------------------
    # # v30
    # data['sim_name'] = 'v30'
    # data['velocity'] = 30
    # dend_v30, result_v30 = sim_brake_single(data)

    # # -------------------
    # data['sim_name'] = 'v60_limit'
    # data['velocity'] = 60
    # last_acc = abs_min_acc(result_v60)
    # dend_v60_t, result_v60_t = ite_run(data, last_acc)

    # # -------------------
    # data['sim_name'] = 'v30_limit'
    # data['velocity'] = 30
    # last_acc = abs_min_acc(result_v30)
    # dend_v30_t, result_v30_t = ite_run(data, last_acc)


    # print(dend_v30)
    # print(dend_v30_t)
    # print(dend_v60)
    # print(dend_v60_t)

# 当前-制动后处理
def post_cur_brake(results):
    pass
    
    model_name = tcmdf.get_current_model()
    mass_data = tcmdf.get_aggregate_mass(model_name)
    road_z = tcmdf.get_testrig_road_marker_z(model_name)
    tire_data = tcmdf.get_model_tire_data(model_name)
    
    
    # 转动惯量
    I_center = parse_I_center(mass_data)
    locs = mass_data['loc']
    locs[2] = locs[2]-road_z
    
    print(mass_data)
    print(I_center, locs)
    print(tire_data)
    
    
# results = sim_cur_brake()
# results = []
# post_cur_brake(results)


# ------------------------------------------------
# ------------------------------------------------
# --------------------SIM-SPRING-PRELOAD----------
# ------------------------------------------------
# ------------------------------------------------

# spring_data = tcmdf.get_model_nspring_datas(model_name)
# print(spring_data)

# 获取data_dicts的key数据
_parse_datads_by_key = lambda data_dic, data_keys, key: [data_dic[data_key][key] for data_key in data_keys]


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


# 计算-静平衡弹簧预载调整
def sim_static_preload(data):
    
    model_name = data['model_name']
    preload_path = os.path.abspath(data['preload_path']) #.replace('\\', '/')
    
    springs = tcmdf.get_model_nspring_datas(model_name)
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
    
    result_data = _res_read('sim_full_static', 'static', res_path, reqs, comps, line_range=None)
    spring_values = [line[-1] for line in result_data]
    print(spring_values)
    
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
    result_data = _res_read('sim_full_static', 'static', res_path, reqs, comps_dis, line_range=None)
    spring_length = [line[-1] for line in result_data]
    print(spring_length)
    
    # print(new_spring_edits)
    
    return '\n'.join(new_spring_edits)


# 主程序-当前-静平衡弹簧预载调整
def main_cur_static_preload():

    data = _json_read(acar_full_static_path)
    data['model_name'] = tcmdf.get_current_model()
    print(sim_static_preload(data))



if __name__ == '__main__':
    pass
    # main_cur_static_preload()

