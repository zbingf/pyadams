"""
    TCP-CAR
    SIM-BRAKE
"""

# 标准库
import math
import copy
import logging
from pprint import pprint, pformat

# 自建库
from tcp_car import *
import tcp_cmd_fun as tcmdf


# ----------
logger = logging.getLogger('tcp_car_brake')
logger.setLevel(logging.DEBUG)
is_debug = True


def sim_brake_single(params):
    # 单个制动仿真 , 返回制动数据
    # 输入
    # {'brake': 100,
    #  'brake_max': 100,
    #  'comments': 'x_dis, y_dis, z_dis, pitch, velocity, x_acc',
    #  'components': 'longitudinal,lateral,vertical,pitch,longitudinal,longitudinal',
    #  'duration': 0.6,
    #  'gainit': 0.8,
    #  'gear': 1,
    #  'maxit': 5,
    #  'mode': 'interactive',
    #  'model_name': 'MDI_Demo_Vehicle',
    #  'req_units': 'mm,mm,mm,rad,velocity,g',
    #  'requests': 'chassis_displacements,chassis_displacements,chassis_displacements,chassis_displacements,chassis_velocities,chassis_accelerations',
    #  'sim_name': 'v60',
    #  'steer': 'locked',
    #  'step': 1000,
    #  't_end': 10,
    #  't_start': 1,
    #  'target_g': 0.5,
    #  'target_tolerance_g': 0.05,
    #  'velocity': 60.0,
    #  'velocity_list': '60,30'}
    # 
    # 输出
    # dend_dic 计算后的末位状态
    # {'pitch': 2.5,        相对开始制动时的状态
    #  'velocity': 4.6,     不取相对值
    #  'x_acc': -1.0,       不取相对值
    #  'x_dis': 15396.0,    相对开始制动时的状态
    #  'y_dis': 16.0,       相对开始制动时的状态
    #  'z_dis': 25.5        相对开始制动时的状态
    # }
    # new_result_dic 
    # {'pitch': [..],       时域, 相对开始制动时的状态
    #  'velocity': [..],    时域, 不取相对值
    #  'x_acc': [..],       时域, 不取相对值
    #  'x_dis': [..],       时域, 相对开始制动时的状态
    #  'y_dis': [..],       时域, 相对开始制动时的状态
    #  'z_dis': [..]        时域, 相对开始制动时的状态
    # }
    # samplerate 采样频率
    # result_dic 格式与new_result_dic一致, 数据为未处理状态
    if is_debug: logger.debug("call sim_brake_single")


    # 仿真调用
    result = tcmdf.sim_car_full_brake(params)
    res_path = result['res_path']
    
    # 后处理数据读取
    reqs = str_split(params['requests'])
    comps = str_split(params['components'])
    comments = str_split(params['comments'])
    req_units = str_split(params['req_units'])
    # res_units = res_units(res_path)

    brake_start_loc = params['t_start'] * params['step'] / params['t_end']
    brake_start_loc = int(brake_start_loc)-1

    init_v = int(params['velocity'])
    name_single = f'brake_{init_v}'
    data, samplerate = res_read('sim_full_brake', name_single, 
        res_path, reqs, comps, line_range=[4,None], isSamplerate=True)

    result_dic = {}
    for line, comment, req_unit in zip(data, comments, req_units):
        if req_unit == 'rad':
            result_dic[comment] = [n*180/math.pi for n in line]
            continue
        result_dic[comment] = line

    # start_dic = parase_dic_loc(result_dic, brake_start_loc)
    # end_dic   = parase_dic_loc(result_dic, -1)
    
    new_result_dic = parase_dic_init_loc(result_dic, brake_start_loc)
    new_result_dic['x_acc'] = result_dic['x_acc'][brake_start_loc:]       # 加速度, 不取相对值
    new_result_dic['velocity'] = result_dic['velocity'][brake_start_loc:] #   速度, 不取相对值
    dend_dic = parase_dic_loc(new_result_dic, -1)

    # x_dis, y_dis, velocity = data[0], data[1], data[3]
    # pitch = angel_deg(res_units, data[2])

    # return {'x_dis':x_dis, 'y_dis':y_dis, 'pitch':pitch, 'velocity':velocity}
    return dend_dic, new_result_dic, samplerate, result_dic


def sim_cur_brake(params):
    """
    当前-模型制动仿真
    包含紧急制动及目标加速度的制动迭代
    指定踏板深度计算
    
    输出
    results[int(velocity)] = {
        "params": copy.deepcopy(params),      # 对应参数
        "dend": dend_n,                     # 紧急制动, result的结束状态
        "result": result_n,                 # 紧急制动, 相对开始制动时的状态(速度和加速度绝对值)
        "result_total": result_total_n,     # 紧急制动, 完整数据, 未处理
        "dend_t": dend_t,                   # 目标加速度制动, result_t的结束状态
        "result_t": result_t,               # 目标加速度制动, 相对开始制动时的状态(速度和加速度绝对值)
        "result_total_t": result_total_t,   # 目标加速度制动, 完整数据, 未处理
        "brake_t": brake_t,                 # 目标加速度制动
        "g_t": params['target_g'],            # 目标加速度
        "samplerate": samplerate,           # 采样Hz
        }
    """
    if is_debug: logger.debug("Call sim_cur_brake")

    min_abs_acc = lambda result: abs(min(result['x_acc']))

    # model_name = tcmdf.get_current_model()
    # params = json_read(ACAR_FULL_BRAKE_PATH) # 计算参数
    # params['model_name'] = model_name

    velocity_list = [float(v) for v in params['velocity_list'].split(',') if v]
    
    target_tolerance_g = params['target_tolerance_g']
    target_g = params['target_g']
    brake_max = params['brake_max']
    maxit = params['maxit'] # 最大迭代次数
    gainit = params['gainit'] # 迭代增益 0.8
    
    def ite_run(params, last_acc, gain=gainit, n_ite=maxit):

        if is_debug: logger.debug("Call sim_cur_brake-ite_run")

        # 迭代仿真
        cur_brake = 100 / last_acc * target_g
        d_brake = 100 / last_acc * gain
        last_brake = cur_brake
        for calc_n in range(n_ite):
            if is_debug: logger.debug(f"ite_run cur_brake:{round(cur_brake,2)}")
            params['brake'] = cur_brake
            dend_dic, result, samplerate, result_total = sim_brake_single(params)
            cur_acc = min_abs_acc(result)

            if is_debug: logger.debug(f"ite : {calc_n} cur_acc : {round(cur_acc,2)} g")
            if is_debug: logger.debug(f"ite : {calc_n} d_brake : {round(d_brake,2)}")

            # print('d_acc: ')
            if abs(target_g - cur_acc) < target_tolerance_g:  
                # print('符合计算')
                break
            
            if (last_brake-cur_brake)==0 or (last_acc-cur_acc)==0:
                d_brake = 100 / last_acc * gain
            else:
                d_brake = (last_brake-cur_brake) / (last_acc - cur_acc)
                if d_brake < 0:
                    d_brake = cur_brake / cur_acc * gain

            last_brake, last_acc = cur_brake, cur_acc
            cur_brake = last_brake + d_brake*(target_g - cur_acc) 

        return dend_dic, result, cur_brake, result_total

    results = {}
    for velocity in velocity_list:
        # 紧急制动
        params['brake'] = brake_max   # 100
        params['sim_name'] = f'v{int(velocity)}'
        params['velocity'] = velocity

        if is_debug: logger.debug(f"init brake velocity: {velocity} km/h")

        dend_n, result_n, samplerate, result_total_n = sim_brake_single(params)

        # 目标加速度, 迭代仿真
        params['sim_name'] = params['sim_name'] + '_limit'
        last_acc = min_abs_acc(result_n)
        dend_t, result_t, brake_t, result_total_t = ite_run(params, last_acc)
        
        results[int(velocity)] = {
            "params": copy.deepcopy(params),      # 对应参数
            
            "dend": dend_n,                     # 紧急制动, result的结束状态
            "result": result_n,                 # 紧急制动, 相对开始制动时的状态(速度和加速度绝对值)
            "result_total": result_total_n,     # 紧急制动, 完整数据, 未处理
            
            "dend_t": dend_t,                   # 目标加速度制动, result_t的结束状态
            "result_t": result_t,               # 目标加速度制动, 相对开始制动时的状态(速度和加速度绝对值)
            "result_total_t": result_total_t,   # 目标加速度制动, 完整数据, 未处理
            "brake_t": brake_t,                 # 目标加速度制动值
            "g_t": params['target_g'],            # 目标加速度

            "samplerate": samplerate,           # 采样Hz
            }

    if is_debug: logger.debug(f"End sim_cur_brake")
    # print(results)
    return results


def main_cur_brake(**params_replace):

    params = json_read(ACAR_FULL_BRAKE_PATH) 
    params['model_name'] = tcmdf.get_current_model()

    for key in params_replace: params[key] = params_replace[key]

    return sim_cur_brake(params) # 保留2位数据




if __name__=='__main__':
    pass
    result = main_cur_brake()
    # pprint(result)
    # help(sim_static_spring_preload)
    
    