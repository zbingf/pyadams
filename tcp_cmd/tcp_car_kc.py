# KC仿真
# 参数输入: 手动、自动


# 标准库
from pprint import pprint, pformat
import logging
import threading

# 调用库
from mat4py import loadmat, savemat

# 自建库
from tcp_car import *
import tcp_cmd_fun as tcmdf





def sim_kc(set_data):

    model_name = tcmdf.get_current_model()

    param_parallel = set_data['param']['parallel']
    param_parallel["model_name"] = model_name

    param_opposite = set_data['param']['opposite']
    param_opposite["model_name"] = model_name

    param_brake = set_data['param']['brake']
    param_brake["model_name"] = model_name

    param_damage = set_data['param']['damage']
    param_damage["model_name"] = model_name

    param_align = set_data['param']['align']
    param_align["model_name"] = model_name

    reqs_parallel = set_data['req_comp']['reqs_parallel']
    comps_parallel = set_data['req_comp']['comps_parallel']

    reqs_opposite = set_data['req_comp']['reqs_opposite']
    comps_opposite = set_data['req_comp']['comps_opposite']

    reqs_damage = set_data['req_comp']['reqs_damage']
    comps_damage = set_data['req_comp']['comps_damage']

    reqs_brake = set_data['req_comp']['reqs_brake']
    comps_brake = set_data['req_comp']['comps_brake']

    reqs_align = set_data['req_comp']['reqs_align']
    comps_align = set_data['req_comp']['comps_align']


    # SIM
    result_parallel = tcmdf.sim_car_sus_parallel(param_parallel)
    result_opposite = tcmdf.sim_car_sus_opposite(param_opposite)
    result_brake = tcmdf.sim_car_full_static_load(param_brake)
    result_damage = tcmdf.sim_car_full_static_load(param_damage)
    result_align = tcmdf.sim_car_full_static_load(param_align)


    # 等待计算结束
    tcmdf.watting_sim_finished(result_parallel['res_path'])
    tcmdf.watting_sim_finished(result_opposite['res_path'])
    tcmdf.watting_sim_finished(result_brake['res_path'])
    tcmdf.watting_sim_finished(result_damage['res_path'])
    tcmdf.watting_sim_finished(result_align['res_path'])


    # RESULT READ
    data_parallel, __ = res_read("KC_res", "parallel", result_parallel['res_path'], 
        reqs_parallel, comps_parallel, line_range=[1,None], isSamplerate=False)

    data_opposite, __ = res_read("KC_res", "opposite", result_opposite['res_path'], 
        reqs_opposite, comps_opposite, line_range=[1,None], isSamplerate=False)

    data_brake, __ = res_read("KC_res", "brake", result_brake['res_path'], 
        reqs_brake, comps_brake, line_range=[1,None], isSamplerate=False)

    data_damage, __ = res_read("KC_res", "damage", result_damage['res_path'], 
        reqs_damage, comps_damage, line_range=[1,None], isSamplerate=False)

    data_align, __ = res_read("KC_res", "align", result_align['res_path'], 
        reqs_align, comps_align, line_range=[1,None], isSamplerate=False)

    # print(data_parallel)
    # print(data_opposite)
    # print(data_brake)
    # print(data_damage)
    # print(data_align)

    datas_2d = [data_parallel, data_opposite, data_brake, data_damage, data_align]
    reqs_2d = [reqs_parallel, reqs_opposite, reqs_brake, reqs_damage, reqs_align]
    comps_2d = [comps_parallel, comps_opposite, comps_brake, comps_damage, comps_align]

    result = {
        'datas_2d':datas_2d,
        'reqs_2d':reqs_2d,
        'comps_2d':comps_2d,
    }

    return result

def parse_kc_data(set_data, result):

    datas_2d = result['datas_2d']
    reqs_2d = result['reqs_2d']
    comps_2d = result['comps_2d']

    names = set_data['name_replace']
    strs_pre = set_data['strs_pre']
    list_params = {}
    for data, reqs, comps, str_pre in zip(datas_2d, reqs_2d, comps_2d, strs_pre):
        for req, comp, line in zip(reqs, comps, data):
            if req in names:
                new_req = names[req]
            else:
                new_req = req

            if comp in names:
                new_comp = names[comp]
            else:
                new_comp = comp

            list_params[f'{str_pre}_{new_req}_{new_comp}'] = line

    data_mat = {
        "value": {"a":1}, 
        "list": list_params,
        "samplerate":1,
    }

    # print(list_params.keys())
    # print(sorted(list_params, key=lambda a: len(a)))
    # print(len(sorted(list_params, key=lambda a: len(a))[-1]))
    return data_mat


    

    
if __name__=='__main__':
    pass

    set_data = json_read(ACAR_SUS_KC_PATH)
    result = sim_kc(set_data)
    data_mat = parse_kc_data(set_data, result)

    savemat(r"D:\document\ADAMS\test.KC.mat", data_mat)

    print('end')



# --------------------------------------
# --------------------------------------
# params = [
#     data_brake, 
#     data_parallel, 
#     data_opposite,
#     ]
# funcs = [
#     tcmdf.sim_car_full_static_load, 
#     tcmdf.sim_car_sus_parallel, 
#     tcmdf.sim_car_sus_opposite,
#     ]
# # 多线程初始设置,设置线程上限, 默认设置
# threadmax = threading.BoundedSemaphore(4)  

# threads = []
# for param, func in zip(params, funcs):
#     thread = threading.Thread(target=func, args=(param, ))
#     thread.start()
#     threads.append(thread)
#     threadmax.acquire()

# while threads:
#     threads.pop().join()

# pprint(result_brake)
# pprint(result_parallel)
# pprint(result_opposite)



# pprint(set_data);asdf

# param_parallel = {
#     "model_name": model_name,
#     "sim_name" : "kc_sim",
#     "mode"     : "background",
#     "step" : 100,
#     "bump" : 50,
#     "rebound" : -50,
# }

# param_opposite = {
#     "model_name": model_name,
#     "sim_name" : "kc_sim",
#     "mode"     : "background",
#     "step" : 100,
#     "bump" : 50,
#     "rebound" : -50,
# }


# param_brake = {
#     "model_name": model_name,
#     "sim_name" : "kc_sim_brake",
#     "mode"     : "background",
#     "step"     : 100,
#     "brake_for_upr_l" : 5000,
#     "brake_for_upr_r" : 5000,
#     "brake_for_lwr_l" : -5000,
#     "brake_for_lwr_r" : -5000,
# }


# param_damage = {
#     "model_name": model_name,
#     "sim_name" : "kc_sim_damage",
#     "mode"     : "background",
#     "step"     : 100,
#     "damage_for_upr_l" : 5000,
#     "damage_for_upr_r" : 5000,
#     "damage_for_lwr_l" : -5000,
#     "damage_for_lwr_r" : -5000,
# }


# param_align = {
#     "model_name": model_name,
#     "sim_name" : "kc_sim_align",
#     "mode"     : "background",
#     "step"     : 100,
#     "align_tor_upr_l" : 5000,
#     "align_tor_upr_r" : 5000,
#     "align_tor_lwr_l" : -5000,
#     "align_tor_lwr_r" : -5000,
# }

# 
# reqs_parallel = ['wheel_travel','wheel_travel','left_tire_forces','right_tire_forces',
#     'toe_angle','toe_angle','camber_angle','camber_angle',
#     'wheel_travel_track','wheel_travel_track',
#     'wheel_travel_base','wheel_travel_base','caster_angle','caster_angle',
#     'caster_moment_arm','caster_moment_arm','kingpin_incl_angle','kingpin_incl_angle',
#     'scrub_radius','scrub_radius','anti_dive_braking','anti_dive_braking',
#     'anti_lift_acceleration','anti_lift_acceleration','ride_rate','ride_rate',
#     'wheel_rate','wheel_rate'];

# comps_parallel = ['vertical_left','vertical_right','normal','normal',
#     'left','right','left','right',
#     'track_left','track_right',
#     'base_left','base_right','left','right',
#     'left','right','left','right',
#     'left','right','left','right',
#     'left','right','left','right',
#     'left','right']

# reqs_opposite = ['wheel_travel','wheel_travel','left_tire_forces','right_tire_forces',
#     'toe_angle','toe_angle','camber_angle','camber_angle',
#     'wheel_travel_track','wheel_travel_track',
#     'wheel_travel_base','wheel_travel_base','caster_angle','caster_angle',
#     'caster_moment_arm','caster_moment_arm','kingpin_incl_angle','kingpin_incl_angle',
#     'scrub_radius','scrub_radius',
#     'susp_roll_rate','total_roll_rate','roll_center_location']
# comps_opposite = ['vertical_left','vertical_right','normal','normal',
#     'left','right','left','right',
#     'track_left','track_right',
#     'base_left','base_right','left','right',
#     'left','right','left','right',
#     'left','right',
#     'suspension_roll_rate','total_roll_rate','vertical']

# reqs_brake= ['left_tire_forces','right_tire_forces',
#     'toe_angle','toe_angle','camber_angle','camber_angle',
#     'caster_angle','caster_angle',
#     'anti_dive_braking','anti_dive_braking',
#     'anti_lift_acceleration','anti_lift_acceleration',
#     'fore_aft_wheel_center_stiffness','fore_aft_wheel_center_stiffness',
#     'total_track','wheel_travel_base','wheel_travel_base']
# comps_brake= ['longitudinal','longitudinal',
#     'left','right','left','right',
#     'left','right','left','right',
#     'left','right',
#     'left','right','track','base_left','base_right']


# reqs_damage= ['left_hub_forces','right_hub_forces',
#     'toe_angle','toe_angle','camber_angle','camber_angle',
#     'wheel_travel_track','wheel_travel_track',
#     'total_track','wheel_travel_base','wheel_travel_base',
#     ]
# comps_damage= ['lateral','lateral',
#     'left','right','left','right',
#     'track_left','track_right',
#     'track','base_left','base_right'
#     ]


# reqs_align= ['left_tire_forces','right_tire_forces',
#     'toe_angle','toe_angle','camber_angle','camber_angle',
#     'total_track','wheel_travel_base','wheel_travel_base',
#     ]
# comps_align= ['aligning_torque','aligning_torque',
#     'left','right','left','right',
#     'track','base_left','base_right',
#     ]




# names = {
#     "left_tire_forces": "tire_force_L",
#     "right_tire_forces": "tire_force_R",
#     "toe_angle": "toe",
#     "camber_angle": "camber",
#     "fore_aft_wheel_center_stiffness": "wheelKFx",
#     "left": "L",
#     "right": "R",
#     "base_left": "bL",
#     "base_right": "bR",
#     "aligning_torque": "align",
#     "track_left": "tL",
#     "track_right": "tR",

#     "suspension_roll_rate": "sKR",
#     "total_roll_rate": "tKR",
#     "vertical_left":"vL",
#     "vertical_right":"vR",
# }

# strs_pre = ['p', 'o', 'bra', 'dam', 'ali']
