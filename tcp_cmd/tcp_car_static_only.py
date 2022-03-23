"""
    TCP-CAR
    SIM-STATIC-ONLY
"""

# 标准库
from pprint import pprint, pformat
import logging

# 自建库
from tcp_car import *
import tcp_cmd_fun as tcmdf


# ----------
logger = logging.getLogger('tcp_car_static_only')
logger.setLevel(logging.DEBUG)
is_debug = True


def parse_tire_locs(tire_locs):
    # 解析轮胎中心坐标数据
    # 
    # 输入:tire_locs 轮心坐标
    # {
    # 'TR_Front_Tires.til_wheel': [267.0, -760.0, 330.0],
    #  'TR_Front_Tires.tir_wheel': [267.0, 760.0, 330.0],
    #  'TR_Rear_Tires.til_wheel': [2827.0, -797.0, 350.0],
    #  'TR_Rear_Tires.tir_wheel': [2827.0, 797.0, 350.0]
    # }
    # 
    # 输出
    # {
    # 'Axles': {'TR_Front_Tires.til_wheel': 1,         轮胎所属轴
    #            'TR_Front_Tires.tir_wheel': 1,
    #            'TR_Rear_Tires.til_wheel': 2,
    #            'TR_Rear_Tires.tir_wheel': 2},
    #  'Ls': {'L-1-2': 2560.0},                         轴距
    #  'Ws': {'W-1-TR_Front_Tires.tir_wheel': 1520.0,   轮距
    #         'W-2-TR_Rear_Tires.tir_wheel': 1594.0},
    #  'axle_num': 2,                                   车轴数
    #  'tire_names': ['TR_Front_Tires.til_wheel',       轮胎名称, 有序
    #                 'TR_Front_Tires.tir_wheel',
    #                 'TR_Rear_Tires.til_wheel',
    #                 'TR_Rear_Tires.tir_wheel'],
    #  'x_start': 267.0                                 第一轴 X 坐标                          
    # }


    # 右侧数据, 排序
    right_tire_locs = {key:tire_locs[key] for key in tire_locs if tire_locs[key][1]>0}
    right_tire_names = sorted(right_tire_locs.keys(), key=lambda v: right_tire_locs[v][0])
    
    # 左侧数据, 排序
    left_tire_locs = {key:tire_locs[key] for key in tire_locs if tire_locs[key][1]<0}
    left_tire_names = sorted(left_tire_locs.keys(), key=lambda v: left_tire_locs[v][0])
    
    # 轴距和轮距
    Ls, Ws, Axles = {}, {}, {}
    axle_num = 1 # 车轴数
    x_limit= 5   # X距离容差

    # 右侧为准
    last_name = right_tire_names[0]
    Ws[f"W-{axle_num}-{last_name}"] = abs(right_tire_locs[last_name][1])*2
    Axles[left_tire_names[0]], Axles[right_tire_names[0]] = axle_num, axle_num
    for n in range(1, len(right_tire_names)): 
        cur_name = right_tire_names[n]
        dx = right_tire_locs[cur_name][0] - right_tire_locs[last_name][0]
        if abs(dx) > x_limit: 
            Ls[f"L-{axle_num}-{axle_num+1}"] = dx
            axle_num += 1
        
        Axles[left_tire_names[n]], Axles[right_tire_names[n]] = axle_num, axle_num
        Ws[f"W-{axle_num}-{cur_name}"] = abs(right_tire_locs[cur_name][1])*2
        last_name = cur_name
        
    # 第一轴 X 坐标
    x_start = right_tire_locs[right_tire_names[0]][0]
        
    tire_names = []
    for left, right in zip(left_tire_names, right_tire_names):
        tire_names.extend([left, right])
    
    output = {
        'Ls': Ls,
        'Ws': Ws,
        'x_start': x_start,
        'tire_names': tire_names,
        'axle_num': axle_num,
        'Axles': Axles,
    }

    return output
    


def sim_static_only(params, res_path=None):
    # 计算-静平衡计算
    # 
    # 输入
    # {'gear': 0,
    #  'mode': 'interactive',
    #  'model_name': 'MDI_Demo_Vehicle',
    #  'preload_path': 'acar_full_static_preload_01.spr',
    #  'sim_name': 'auto_sim',
    #  'sim_type': 'settle'}
    # res_path 后处理有输入则不再进行静态计算
    # 
    # 输出
    # {'Axles': {'TR_Front_Tires.til_wheel': 1,
    #            'TR_Front_Tires.tir_wheel': 1,
    #            'TR_Rear_Tires.til_wheel': 2,
    #            'TR_Rear_Tires.tir_wheel': 2},
    #  'I_center': [298688841.89, 1162890925.9, 1341023809.23],
    #  'Ls': {'L-1-2': 2560.0},
    #  'Ws': {'W-1-TR_Front_Tires.tir_wheel': 1520.0,
    #         'W-2-TR_Rear_Tires.tir_wheel': 1594.0},
    #  'axle_num': 2,
    #  'm_center': [1482.05, -1.42, 415.45],
    #  'mass': 1527.68,
    #  'model_name': 'MDI_Demo_Vehicle',
    #  'tire_forces': {'TR_Front_Tires.til_wheel': 3159.3,
    #                  'TR_Front_Tires.tir_wheel': 3145.1,
    #                  'TR_Rear_Tires.til_wheel': 4345.73,
    #                  'TR_Rear_Tires.tir_wheel': 4331.3},
    #  'tire_locs': {'TR_Front_Tires.til_wheel': [267.0, -760.0, 330.0],
    #                'TR_Front_Tires.tir_wheel': [267.0, 760.0, 330.0],
    #                'TR_Rear_Tires.til_wheel': [2827.0, -797.0, 350.0],
    #                'TR_Rear_Tires.tir_wheel': [2827.0, 797.0, 350.0]},
    #  'tire_names': ['TR_Front_Tires.til_wheel',
    #                 'TR_Front_Tires.tir_wheel',
    #                 'TR_Rear_Tires.til_wheel',
    #                 'TR_Rear_Tires.tir_wheel']}
    if is_debug: logger.debug(f"Call sim_static_only")

    model_name = params['model_name']
    
    # -------------------    
    if res_path==None:
        if is_debug: logger.debug(f"sim static")
        result_static = tcmdf.sim_car_full_static(params) # 静态计算
        res_path = result_static['res_path']
    
    mass_data = tcmdf.get_aggregate_mass(model_name)
    road_z = tcmdf.get_testrig_road_marker_z(model_name) # 必须计算后再测量路面高
    tire_datas = tcmdf.get_model_tire_data(model_name)
    
    tire_names = list(tire_datas.keys())
    reqs  = parse_datads_by_key(tire_datas, tire_names, 'req_name')
    comps = parse_comps(tire_datas, tire_names, 'normal')
    
    result_data, _ = res_read('sim_full_static_only', 'static_only', res_path, reqs, comps, line_range=None)
    tire_values = [line[-1] for line in result_data]
    # print(tire_values)
    
    tire_forces = {name_range(name,1):value for name, value in zip(tire_names, tire_values)}
    tire_locs   = {name_range(name,1):tire_datas[name]['loc'] for name in tire_names}
    
    # ---------------
    # 转动惯量, 质心高
    I_center = parse_I_center(mass_data)
    locs = mass_data['loc']
    locs[2] = locs[2]-road_z
    
    # 轮心坐标数据处理
    # Ls, Ws, x_start, tire_names, axle_num, Axles = parse_tire_locs(tire_locs)
    tire_data = parse_tire_locs(tire_locs)
    tire_names = tire_data['tire_names']

    locs[0] = locs[0] - tire_data['x_start'] # X坐标校正

    vehicle_data = {
        'model_name' : model_name,  # 模型名称
        'mass' : mass_data['mass'], 
        'axle_num' : tire_data['axle_num'],      # 车轴数
        'I_center': I_center,
        'm_center': locs,
        'tire_names'  : tire_names, # 有序列表
        'tire_forces' : {tire_name:tire_forces[tire_name] for tire_name in tire_names}, # 有序
        'tire_locs'   : {tire_name:tire_locs[tire_name] for tire_name in tire_names}, # 有序
        'Ls' : tire_data['Ls'],
        'Ws' : tire_data['Ws'],
        'Axles': tire_data['Axles'], # 轮胎所属车轴
    }
    pass

    if is_debug: logger.debug(f"vehicle_data:\n{pformat(vehicle_data)}")
    if is_debug: logger.debug(f"End sim_static_only")
    return vehicle_data
    

def main_cur_static_only(res_path=None, **params_replace):
    """
        仅静态计算
        res_path 若为None, 则进行仿真计算; 否则直接调用res_path数据计算
        params_replace 用于对json设置数据的 增改
    """
    params = json_read(ACAR_FULL_STATIC_PATH) # 静态数据存放读取
    params['model_name'] = tcmdf.get_current_model()
    for key in params_replace: params[key] = params_replace[key]
    
    vehicle_data = round_data_dict(sim_static_only(params, res_path), {}, 2) # 保留2位数据
    # pprint(params)
    # 
    return vehicle_data



if __name__=='__main__':
    pass
    vehicle_data = main_cur_static_only()
    pprint(vehicle_data)