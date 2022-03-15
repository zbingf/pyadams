import pyadams.tcp_cmd.tcp_car as tcp_car

from pyadams.file import office_docx
WordEdit = office_docx.WordEdit

from pyadams.datacal import plot

from pprint import pprint, pformat
import os


POST_BRAKE = {

    }

# 当前-制动后处理
# results[int(velocity)] = {
#     "params": data,      # 对应参数
#     "dend": dend_n,       # 紧急制动, 结束位置的数据
#     "result": result_n,   # 紧急制动, 开始制动之后的数据
#     "result_total": result_total_n, # 紧急制动, 完整数据 dict_keys(['x_dis', 'y_dis', 'pitch', 'velocity', 'x_acc'])
#     "dend_t": dend_t,     # 目标加速度制动, 结束位置的数据
#     "result_t": result_t, # 目标加速度制动, 开始制动之后的数据
#     "result_total_t": result_total_t, # 目标加速度制动, 完整数据
#     "brake_t": brake_t,  # 目标加速度制动
#     "g_t": data['target_g'], # 目标加速度
#     "samplerate": samplerate, # 采样Hz
#     }
def post_brake(results):
    # model_name = tcmdf.get_current_model()
    
    fig_dict, str_dict = {}, {}

    for velocity in results:
        # print(velocity)
        sub_result = results[velocity]
        fig_path = post_brake_sub_result_fig(sub_result, 'result')
        fig_path_t = post_brake_sub_result_fig(sub_result, 'result_t')    
        fig_dict[velocity] = [fig_path, fig_path_t]
        
        str_dict[velocity] = post_brake_sub_result_str(sub_result)
        
        
    print(fig_dict)
    print(str_dict)


POST_BRAKE_STR = {
    'x_dis': '制动距离',
    'y_dis': '跑偏距离',
    'z_dis': '沉头量',
    'pitch': '纵倾角',
    'x_acc': '最大加速度',
    }

max_abs = lambda list1: max([abs(v) for v in list1])

def post_brake_sub_result_str(sub_result):
    
    params = sub_result['params']
    velocity = int(params['velocity'])
    
    dend = sub_result['dend']
    dend_t = sub_result['dend_t']
    
    # 最大沉头量
    z_max = max_abs(sub_result['result']['z_dis'])
    z_max_t = max_abs(sub_result['result_t']['z_dis'])
    
    # 最大制动加速度
    x_acc_max = max_abs(sub_result['result']['x_acc'])
    x_acc_max_t = max_abs(sub_result['result_t']['x_acc']) 
    
    # 制动距离
    x_dis_max = dend['x_dis']
    x_dis_max_t = dend_t['x_dis']
    
    # 最后跑偏量
    y_dis_end = dend['y_dis']
    y_dis_end_t = dend_t['y_dis']
    
    output = {
        'velocity': velocity,
        'z_max':z_max,
        'z_max_t':z_max_t,
        'x_acc_max':x_acc_max,
        'x_acc_max_t':x_acc_max_t,
        'x_dis_max':x_dis_max,
        'x_dis_max_t':x_dis_max_t,
        'y_dis_end':y_dis_end,
        'y_dis_end_t':y_dis_end_t,
        }
    
    return output
    
    
# 后处理
POST_BRAKE_YLABEL = {
    'x_dis' : 'X dis (mm)',
    'y_dis' : 'Y dis (mm)',
    'z_dis' : 'Z dis (mm)',
    'pitch' : 'pitch (deg)',
    'velocity' : 'velocity (km/h)',
    'x_acc' : 'x acc (g)',
    }


# sub_result, 图像后处理
# data_key 指定数据
def post_brake_sub_result_fig(sub_result, data_key):
    
    params = sub_result['params']
    # print(params)
    velocity = int(params['velocity'])
    result_total = sub_result[data_key]
    # print(result_total.keys())
    v_len = len(result_total['x_dis'])
    samplerate = sub_result['samplerate']
    # print(samplerate)
    
    ts = [n/samplerate for n in range(v_len)]
    names, lines = [], []
    for key in result_total:
        # print(key)
        names.append(POST_BRAKE_YLABEL[key])
        lines.append(result_total[key])

    # 图像生成
    fig_obj = plot.FigPlotRealTime(f'v{velocity}_{data_key}')
    fig_obj.set_figure(nums=[2,3], figsize='16:9')
    fig_obj.set_legend([f'{velocity} km/h'])
    fig_obj.set_ylabel(names, 'ts')
    fig_obj.set_xlabel('time(s)', 'ts')
    
    ts_2d = [ts]*len(result_total)
    fig_obj.plot_ts([lines], [ts_2d], linetypes=['b'])

    fig_paths = fig_obj.fig_paths['ts']
    return fig_paths[0]
    

def test_cur_brake():
    # results = tcp_car.sim_cur_brake()
    # pprint(1)
    post_brake(results)


test_cur_brake()

