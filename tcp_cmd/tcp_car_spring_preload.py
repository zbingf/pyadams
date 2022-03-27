"""
    TCP-CAR
    SIM-SPRING-PRELOAD
"""

# 标准库
import os
from pprint import pprint, pformat
import logging

# 自建库
from tcp_car import *
import tcp_cmd_fun as tcmdf


# ----------
logger = logging.getLogger('tcp_car_spring_preload')
logger.setLevel(logging.DEBUG)
is_debug = True


def sim_static_spring_preload(params):
    """
        计算-静平衡弹簧预载调整
        
        输入
        {'gear': 0,
         'mode': 'interactive',
         'model_name': 'MDI_Demo_Vehicle',
         'preload_path': 'acar_full_static_preload_01.spr',       !!!!
         'sim_name': 'auto_sim',
         'sim_type': 'normal'}
        
        输出
        {
         'cmd': str, 弹簧预载命令,
         'res_path': 'D:\\document\\ADAMS\\tcp_sim_275\\tcp_sim_8\\auto_sim_static.res',
         'spring_lengths': {'TR_Front_Suspension.nsl_ride_spring': 255.73,
                            'TR_Front_Suspension.nsr_ride_spring': 255.73,
                            'TR_Rear_Suspension.nsl_ride_spring': 255.74,
                            'TR_Rear_Suspension.nsr_ride_spring': 255.73},
         'spring_names': ['TR_Front_Suspension.nsl_ride_spring',
                          'TR_Front_Suspension.nsr_ride_spring',
                          'TR_Rear_Suspension.nsl_ride_spring',
                          'TR_Rear_Suspension.nsr_ride_spring'],
         'spring_values': {'TR_Front_Suspension.nsl_ride_spring': 5488.02,
                           'TR_Front_Suspension.nsr_ride_spring': 5459.04,
                           'TR_Rear_Suspension.nsl_ride_spring': 8017.92,
                           'TR_Rear_Suspension.nsr_ride_spring': 7993.69}
        }
    """
    if is_debug: logger.debug("Call sim_static_spring_preload")

    model_name = params['model_name']
    preload_path = os.path.abspath(params['preload_path']) # 绝对路径
    
    springs = tcmdf.get_model_nspring_datas(model_name)
    if springs==False: return False
    n_spring = len(springs)
    spring_names = list(springs.keys())
    
    reqs = parse_datads_by_key(springs, spring_names, 'req_name')
    comps = parse_comps(springs, spring_names, 'force')
    comps_dis = parse_comps(springs, spring_names, 'displacement')
    
    # -------------------
    # 弹簧预载初始化
    if is_debug: logger.debug(f"spring_edit init")
    new_springs = edit_datads_by_key(springs, spring_names, 'type', ['preload']*n_spring)
    new_springs = edit_datads_by_key(new_springs, spring_names, 'value', [0]*n_spring)
    new_springs = edit_datads_by_key(new_springs, spring_names, 'symmetric', [False]*n_spring)
    new_springs = edit_datads_by_key(new_springs, spring_names, 'path', [preload_path]*n_spring)
    
    for key in new_springs: tcmdf.set_spring(new_springs[key])
    
    # -------------------    
    # 静态计算
    if is_debug: logger.debug("first static sim")
    result_static = tcmdf.sim_car_full_static(params)
    res_path = result_static['res_path']
    
    result_data, _ = res_read('sim_full_static', 'static', res_path, reqs, comps, line_range=None)
    spring_values = [line[-1] for line in result_data]
    # print(spring_values)
    
    # -------------------
    # 弹簧校正
    if is_debug: logger.debug(f"spring_edit")
    new_springs_02 = edit_datads_by_key(springs, spring_names, 'type', ['preload']*n_spring)
    new_springs_02 = edit_datads_by_key(new_springs_02, spring_names, 'value', spring_values)
    new_springs_02 = edit_datads_by_key(new_springs_02, spring_names, 'symmetric', [False]*n_spring)
    
    new_spring_edits = []
    for key in new_springs_02: 
        tcmdf.set_spring(new_springs_02[key])
        new_spring_edits.append(tcmdf.parse_spring(new_springs_02[key]))
    
    if is_debug: logger.debug("second static sim")
    result_static = tcmdf.sim_car_full_static(params)
    res_path = result_static['res_path']
    result_data, _ = res_read('sim_full_static', 'static', res_path, reqs, comps_dis, line_range=None)
    spring_lengths = [line[-1] for line in result_data]
    # print(spring_length)
    if is_debug: logger.debug(f"spring_lengths {spring_lengths}")

    # print('\n'.join(new_spring_edits))
    
    output_data = {
        'spring_names'   : [name_range(name,1) for name in spring_names],
        'spring_values'  : {name_range(name,1):value for name, value in zip(spring_names, spring_values)},
        'spring_lengths' : {name_range(name,1):value for name, value in zip(spring_names, spring_lengths)},
        'cmd'           : '\n'.join(new_spring_edits),
        'res_path' : res_path,
        }
    
    if is_debug: logger.debug("End sim_static_spring_preload")
    return output_data


def main_cur_static_preload(**params_replace):
    """
        当前-静平衡弹簧预载调整
        params_replace 用于对json设置数据的 增改
    """
    params = json_read(ACAR_FULL_STATIC_PATH)
    params['model_name'] = tcmdf.get_current_model()
    for key in params_replace: params[key] = params_replace[key]

    # print(sim_static_spring_preload(params))
    result = sim_static_spring_preload(params)
    
    return round_data_dict(result, {}, 2)



if __name__=='__main__':
    pass
    result = main_cur_static_preload()
    pprint(result)
    # help(sim_static_spring_preload)
