"""
    TCP-CAR
    SIM-SPRING-PRELOAD
"""

# 标准库
import os
from pprint import pprint, pformat

# 自建库
from pyadams.tcp_cmd.tcp_car import *
import pyadams.tcp_cmd.tcp_cmd_fun as tcmdf



# 计算-静平衡弹簧预载调整
# 
# 输入
# {'gear': 0,
#  'mode': 'interactive',
#  'model_name': 'MDI_Demo_Vehicle',
#  'preload_path': 'acar_full_static_preload_01.spr',       !!!!
#  'sim_name': 'auto_sim',
#  'sim_type': 'normal'}
# 
# 输出
# {
#  'cmd': str, 弹簧预载命令,
#  'res_path': 'D:\\document\\ADAMS\\tcp_sim_275\\tcp_sim_8\\auto_sim_static.res',
#  'spring_lengths': {'TR_Front_Suspension.nsl_ride_spring': 255.73,
#                     'TR_Front_Suspension.nsr_ride_spring': 255.73,
#                     'TR_Rear_Suspension.nsl_ride_spring': 255.74,
#                     'TR_Rear_Suspension.nsr_ride_spring': 255.73},
#  'spring_names': ['TR_Front_Suspension.nsl_ride_spring',
#                   'TR_Front_Suspension.nsr_ride_spring',
#                   'TR_Rear_Suspension.nsl_ride_spring',
#                   'TR_Rear_Suspension.nsr_ride_spring'],
#  'spring_values': {'TR_Front_Suspension.nsl_ride_spring': 5488.02,
#                    'TR_Front_Suspension.nsr_ride_spring': 5459.04,
#                    'TR_Rear_Suspension.nsl_ride_spring': 8017.92,
#                    'TR_Rear_Suspension.nsr_ride_spring': 7993.69}
# }
def sim_static_spring_preload(data):
    
    model_name = data['model_name']
    preload_path = os.path.abspath(data['preload_path']) # 绝对路径
    
    springs = tcmdf.get_model_nspring_datas(model_name)
    if springs==False: return False
    n_spring = len(springs)
    spring_names = list(springs.keys())
    
    reqs = parse_datads_by_key(springs, spring_names, 'req_name')
    comps = parse_comps(springs, spring_names, 'force')
    comps_dis = parse_comps(springs, spring_names, 'displacement')
    
    # -------------------
    # 弹簧预载初始化
    new_springs = edit_datads_by_key(springs, spring_names, 'type', ['preload']*n_spring)
    new_springs = edit_datads_by_key(new_springs, spring_names, 'value', [0]*n_spring)
    new_springs = edit_datads_by_key(new_springs, spring_names, 'symmetric', [False]*n_spring)
    new_springs = edit_datads_by_key(new_springs, spring_names, 'path', [preload_path]*n_spring)
    
    for key in new_springs: tcmdf.set_spring(new_springs[key])
    
    # -------------------    
    # 静态计算
    result_static = tcmdf.sim_car_full_static(data)
    res_path = result_static['res_path']
    
    result_data, _ = res_read('sim_full_static', 'static', res_path, reqs, comps, line_range=None)
    spring_values = [line[-1] for line in result_data]
    # print(spring_values)
    
    # -------------------
    # 弹簧校正
    new_springs_02 = edit_datads_by_key(springs, spring_names, 'type', ['preload']*n_spring)
    new_springs_02 = edit_datads_by_key(new_springs_02, spring_names, 'value', spring_values)
    new_springs_02 = edit_datads_by_key(new_springs_02, spring_names, 'symmetric', [False]*n_spring)
    
    new_spring_edits = []
    for key in new_springs_02: 
        tcmdf.set_spring(new_springs_02[key])
        new_spring_edits.append(tcmdf.parse_spring(new_springs_02[key]))
        
    result_static = tcmdf.sim_car_full_static(data)
    res_path = result_static['res_path']
    result_data, _ = res_read('sim_full_static', 'static', res_path, reqs, comps_dis, line_range=None)
    spring_lengths = [line[-1] for line in result_data]
    # print(spring_length)
    
    # print('\n'.join(new_spring_edits))
    
    output_data = {
        'spring_names'   : [name_range(name,1) for name in spring_names],
        'spring_values'  : {name_range(name,1):value for name, value in zip(spring_names, spring_values)},
        'spring_lengths' : {name_range(name,1):value for name, value in zip(spring_names, spring_lengths)},
        'cmd'           : '\n'.join(new_spring_edits),
        'res_path' : res_path,
        }
    
    return output_data


# 主程序-当前-静平衡弹簧预载调整
def main_cur_static_preload():

    data = json_read(ACAR_FULL_STATIC_PATH)
    data['model_name'] = tcmdf.get_current_model()
    # print(sim_static_spring_preload(data))
    result = sim_static_spring_preload(data)
    
    return round_data_dict(result, {}, 2)



if __name__=='__main__':
    pass
    result = main_cur_static_preload()
    pprint(result)
    # help(sim_static_spring_preload)
