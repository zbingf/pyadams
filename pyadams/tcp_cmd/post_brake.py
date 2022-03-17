"""
    POST
    BRAKE
"""

# 标准库
from pprint import pprint, pformat
# import os

# 自建库
from pyadams.datacal import plot

# POST_BRAKE_STR = {
#     'x_dis': '制动距离',
#     'y_dis': '跑偏距离',
#     'z_dis': '沉头量',
#     'pitch': '纵倾角',
#     'x_acc': '最大加速度',
#     }

max_abs = lambda list1: max([abs(v) for v in list1])


# 单个计算的后处理
def post_brake_sub_result_str(sub_result):
    
    params = sub_result['params']
    velocity = int(params['velocity'])
    
    dend = sub_result['dend']
    dend_t = sub_result['dend_t']
    
    # 最大沉头量
    z_dis_max = max_abs(sub_result['result']['z_dis'])
    z_dis_max_t = max_abs(sub_result['result_t']['z_dis'])
    
    # 最大制动加速度
    x_acc_max = max_abs(sub_result['result']['x_acc'])
    x_acc_max_t = max_abs(sub_result['result_t']['x_acc']) 
    
    # 制动距离
    x_dis_max = dend['x_dis']
    x_dis_max_t = dend_t['x_dis']
    
    # 最后跑偏量
    y_dis_end = dend['y_dis']
    y_dis_end_t = dend_t['y_dis']
    
    # 最大纵倾角
    pitch_max = max_abs(sub_result['result']['pitch'])
    pitch_max_t = max_abs(sub_result['result_t']['pitch']) 

    output = {
        # 'velocity': velocity,
        'z_dis_max':z_dis_max,
        'z_dis_max_t':z_dis_max_t,
        'x_acc_max':x_acc_max,
        'x_acc_max_t':x_acc_max_t,
        'x_dis_max':x_dis_max,
        'x_dis_max_t':x_dis_max_t,
        'y_dis_end':y_dis_end,
        'y_dis_end_t':y_dis_end_t,
        'pitch_max':pitch_max,
        'pitch_max_t':pitch_max_t,
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
    



# 制动后处理
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

# 输出, 用于word替换
# [old_figs, new_figs], [old_strs, new_strs]
# 
def post_brake(results):
    # model_name = tcmdf.get_current_model()
    
    fig_dict, str_dict = {}, {}

    for velocity in results:
        # print(velocity)
        sub_result = results[velocity]
        fig_path = post_brake_sub_result_fig(sub_result, 'result')
        fig_path_t = post_brake_sub_result_fig(sub_result, 'result_t')    
        fig_dict[f'{velocity}_fig'] = fig_path
        fig_dict[f'{velocity}_fig_t'] = fig_path_t
        
        str_dict[velocity] = post_brake_sub_result_str(sub_result)
        
        target_g = sub_result['params']['target_g']

    old_figs, new_figs = [], []
    for key in fig_dict:
        old_figs.append('#'+key+'#')
        new_figs.append(fig_dict[key])
    
    # print(old_figs, new_figs)

    old_strs, new_strs = [], []
    for key_v in str_dict:
        for key_d in str_dict[key_v]:
            old_strs.append('$'+str(key_v)+'_'+key_d+'$')
            new_strs.append(str_dict[key_v][key_d])
    # print(old_strs, new_strs)
    
    old_strs.append('$target_g$')
    new_strs.append(target_g)

    
    for loc, v in enumerate(new_strs):
        if isinstance(v, float):
            new_strs[loc] = round(v, 2)
    new_strs = [str(v) for v in new_strs]

    return [old_figs, new_figs], [old_strs, new_strs]



def test_cur_brake():
    from pyadams.file import office_docx
    WordEdit = office_docx.WordEdit
    
    # results = tcp_car.sim_cur_brake()
    # pprint(1)
    r_figs, r_strs = post_brake(results)
    print(r_figs)
    print(r_strs)

    # word文档编辑 测试
    word_path = r'post_static_only.docx'
    new_word_path = r'new_post_static_only.docx'
    word_obj = WordEdit(word_path)
    word_obj.replace_edit(*r_figs)
    word_obj.replace_edit(*r_strs)
    word_obj.save(new_word_path)
    word_obj.close()


if __name__=='__main__':
    pass
    test_cur_brake()

