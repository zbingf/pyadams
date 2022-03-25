"""
    稳态回转-后处理
    轮胎力request ： 包含 tire_force 、 normal_
"""

# 标准库
import json
import math
import os
import logging
from pprint import pprint, pformat

# 调用库
import numpy as np
from scipy import interpolate


# 自建库
from pyadams.file import result, office_docx, file_edit
DataModel = result.DataModel
# from pyadams.datacal import spline
from pyadams.car import post_handle_s
from pyadams import datacal


# ----------
logger = logging.getLogger('post_handle_crc')
logger.setLevel(logging.DEBUG)
is_debug = True


# 子函数
list2str = lambda list1: ','.join([str(n) for n in list1])
list2negative = lambda list1: [-n for n in list1]
list2abs = lambda list1: [abs(n) for n in list1]
list2absmean = lambda list1: sum(list2abs(list1)) / len(list1)


# 曲线拟合
def single_to_UnivariateSpline(data, d=1, **keys):
    """
        data [float, float, ...]
    """
    x = [n/d for n in range(len(data))]
    obj = interpolate.UnivariateSpline(x, data,**keys)
    return obj(x)


# 获取轮胎的reqeust设置 req\comp
def get_tire_normal_reqcomp(obj):
    """
        obj 为 result.ResFile 实例 
        获取轮荷request
    """
    requestId = obj._requestId
    tar_str = 'tire_force'
    tire_normals = []
    minor_roles = []
    for key in requestId:
        if tar_str in key and 'normal' in key:
            tire_normals.append(key)
            minor_role = key.split('normal_')[-1]
            minor_roles.append(minor_role)

    reqs_tire = [str1.split('.')[0] for str1 in tire_normals]
    comps_tire = [str1.split('.')[-1] for str1 in tire_normals]

    return reqs_tire, comps_tire


# 稳态回转后处理-主要计算模块
def res_handle_crc_cal(res_path, L, docx_path=None, reqs=None, comps=None, spline_s=0.1):
    """
        单位 m/s deg m/s^2 m
        1、输入参数：
            轴距、车重
            起始时间、结果时间
            后处理文件路径
        2、读取后处理数据-稳态回转：
            request需求：车速、方向盘转角、侧倾角、侧向加速度、横摆角速度
            计算：不足转向度、中性转向点、半径比
        3、评分计算
        
        参数:
            res_path str 目标res文件路径
            L float 轴距 单位:m
            docx_path str 目标doc路径
            reqs [str1, str2, str3, ...]
            comps [str1, str2, str3, ...]
            spline_s 拟合曲线光滑程度 数值越大,越光滑
    """
    # 数据读取
    # 数据读取
    if reqs==None:
        reqs=["chassis_accelerations","chassis_velocities",
            "chassis_velocities","chassis_displacements",
            "jms_steering_wheel_angle_data","chassis_displacements",
            "chassis_displacements"]
    if comps==None:
        comps=["lateral","yaw",
            "longitudinal","roll",
            "displacement","lateral",
            "longitudinal"]

    dataobj = DataModel('post_handle_crc')
    dataobj.new_file(res_path, 'handle_crc')
    dataobj['handle_crc'].set_reqs_comps(reqs, comps)
    dataobj['handle_crc'].set_line_ranges([4,None])
    dataobj['handle_crc'].set_select_channels(None)
    dataobj['handle_crc'].read_file()
    data = dataobj['handle_crc'].get_data()
    samplerate_mean = dataobj['handle_crc'].get_samplerate(nlen=20, loc_start=4)

    # 整车质量
    dataobj['handle_crc'].set_reqs_comps(*get_tire_normal_reqcomp(dataobj['handle_crc']))
    dataobj['handle_crc'].read_file(isReload=False)
    tire_datas = dataobj['handle_crc'].get_data()
    tire_loads = []
    for n in range(len(tire_datas[0])):
        value = 0
        for line in tire_datas:
            value += line[n]
        tire_loads.append(value)
    tire_loads = np.array(tire_loads)
    mean_loads  = np.mean(tire_loads)
    mean_mass   = mean_loads / 9.80665

    # 转矩阵
    resData=np.array(data)
    # 单位转换
    lateralAcc,yawV,xV,rollDis,steerWheelDis=resData[0]*9.8,resData[1]/math.pi*180,resData[2]/3.6,resData[3]/math.pi*180,resData[4]/math.pi*180
    yDis,xDis=resData[5]/1000,resData[6]/1000
    
    nloc = abs(lateralAcc) <=2 # 指定区间段筛选

    # 转弯半径 m
    yawV[abs(yawV)<0.1] = yawV[abs(yawV)>0][0]
    Rk = 180 / math.pi * xV / yawV
    if np.mean(Rk) < 0:
        Rk = -Rk

    R0 = Rk[Rk>0][0]
    Rk[Rk<1e-3] = R0

    # 侧偏角差值
    delta_a = 180 / math.pi * L * (1/R0 - 1/Rk)

    # 0.4g 状态对应侧偏角
    loc_04g = abs(lateralAcc) > (0.4*9.8)
    rollDis_04g = rollDis[loc_04g][0]
    # 2m/s^2 状态
    loc_2acc    = abs(lateralAcc) > 2
    rollDis_2acc= abs(rollDis[loc_2acc][0])
    delta_a_2acc= delta_a[loc_2acc][0]
    # 2m/s^2 不足转向度
    U_2acc = delta_a_2acc / 2
    # 2m/s^2 侧倾度
    rollDisK_2acc = rollDis_2acc / 2
    
    fit_lateralAcc = single_to_UnivariateSpline(lateralAcc, d=samplerate_mean, s=spline_s) # spline_s 位于 **kwargs
    fit_delta_a = single_to_UnivariateSpline(delta_a, d=samplerate_mean, s=spline_s)
    
    # 中性转向点 截取
    if sum(fit_delta_a[loc_2acc]) > 0:
        # for num, n in enumerate(fit_delta_a):
        #   if n == max(fit_delta_a):
        #       break
        temp_loc = abs(lateralAcc)>2  # 2m/s^2之后数据
        xlist = np.array(range(len(lateralAcc)))
        temp_start = xlist[temp_loc][0] # 计算起始位置
        ylist = fit_delta_a[temp_start:]
        xlist = xlist[temp_start:]
        xdistance = int(len(xlist)/50)
        mid_locs, mid_steer_point_accs = post_handle_s.handle_peak_find(xlist, ylist, distance=2, xdistance=xdistance)
        if not mid_locs:
            num = len(fit_delta_a)-1 # 取末位数据
            logger.info(f'中性转向点: 无峰值截取末尾侧向加速度作为中性转向点:{lateralAcc[num]:.2f} m/s^2')
        else:
            num = mid_locs[0]
            logger.info(f'中性转向点: 截取第一个波峰/波谷为中性转向点:{mid_steer_point_accs[0]:.2f} m/s^2')

    else:
        # 车辆起始为过多转向, 则 中性转向点 置零
        num = 0
        logger.info(f'中性转向点: 车辆起始为过多转向, 中性转向点置零')       
        # for num,n in enumerate(delta_a):
        #   if n == min(delta_a):
        #       break
    mid_steer_acc_loc = num

    max_lateralAcc = max(abs(lateralAcc))
    mean_steerWheelDis = abs(np.mean(steerWheelDis))

    import matplotlib.pyplot as plt
    plt.rcParams['savefig.dpi'] = 500
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    size_gain = 0.6
    linewidth = 1
    plt.rcParams['figure.figsize'] = [16*size_gain, 9*size_gain]    # 尺寸

    figs = []
    figs.append(plt.figure())
    plt.plot(xDis, yDis, 'b')
    plt.plot(xDis[0], yDis[0], '*b')
    plt.plot(xDis[nloc], yDis[nloc], 'r')
    plt.ylabel('侧向位移 Y(m)', fontsize=15)
    plt.xlabel('纵向位移 X(m)', fontsize=15)
    plt.tick_params(labelsize=15)
    plt.tight_layout()
    plt.grid(True)

    figs.append(plt.figure())
    plt.plot(lateralAcc, yawV, 'b')
    plt.plot(lateralAcc[nloc], yawV[nloc], 'r')
    plt.plot(lateralAcc[nloc][-1], yawV[nloc][-1], '*b')
    plt.plot(lateralAcc[mid_steer_acc_loc], yawV[mid_steer_acc_loc], '*r')
    plt.ylabel('横摆角速度 yaw(deg/s)', fontsize=15)
    plt.xlabel('侧向加速度 m/s^2', fontsize=15)
    plt.tick_params(labelsize=15)
    plt.tight_layout()
    plt.grid(True)


    figs.append(plt.figure())
    plt.plot(lateralAcc, delta_a, 'b')
    plt.plot(lateralAcc[nloc], delta_a[nloc], 'r')
    plt.plot(fit_lateralAcc, fit_delta_a, 'g--')
    plt.plot(lateralAcc[nloc][-1], delta_a[nloc][-1], '*b')
    plt.plot(lateralAcc[mid_steer_acc_loc], delta_a[mid_steer_acc_loc], '*r')
    plt.ylabel('前后侧偏角差值 deg', fontsize=15)
    plt.xlabel('侧向加速度 m/s^2', fontsize=15)
    plt.legend(['原数据', '前2m/s^2数据', '拟合数据', '2m/s^2点', '中性点'])
    plt.tick_params(labelsize=15)
    plt.tight_layout()
    plt.grid(True)

    figs.append(plt.figure())
    plt.plot(lateralAcc, rollDis, 'b')
    plt.plot(lateralAcc[nloc], rollDis[nloc], 'r')
    plt.plot(lateralAcc[nloc][-1], rollDis[nloc][-1], '*b')
    plt.ylabel('侧倾角 deg', fontsize=15)
    plt.xlabel('侧向加速度 m/s^2', fontsize=15)
    plt.tick_params(labelsize=15)
    plt.tight_layout()
    plt.grid(True)

    figs.append(plt.figure())
    xV = [round(value,1)*3.6 for value in xV]
    xV = np.array(xV)
    # new_xV = spline.single_to_UnivariateSpline(xV, d=samplerate_mean, s=1)
    plt.plot(lateralAcc, xV, 'b')
    # plt.plot(lateralAcc, new_xV, 'g')
    plt.plot(lateralAcc[nloc], xV[nloc], 'r')
    plt.plot(lateralAcc[nloc][-1], xV[nloc][-1], '*b')
    plt.ylabel('车速 km/h', fontsize=15)
    plt.xlabel('侧向加速度 m/s^2', fontsize=15)
    plt.tick_params(labelsize=15)
    plt.tight_layout()
    plt.grid(True)

    fig_paths = []
    if docx_path != None:
        for n, fig in enumerate(figs):
            fig_path = '.'.join(docx_path.split('.')[:-1]) + f'_{n}.png'
            fig.savefig(fig_path)
            fig_paths.append(fig_path)

    crc_data = {
        'R0'                : R0, 
        'mid_steer_point'   : abs(lateralAcc[mid_steer_acc_loc]),
        'U_2acc'            : U_2acc,
        'rollDisK_2acc'     : abs(rollDisK_2acc),
        'rollDis_04g'       : abs(rollDis_04g),
        'mass'              : mean_mass,
        'max_lateralAcc'    : max_lateralAcc,
        'steerWheelDis'     : abs(mean_steerWheelDis),
        'L'                 : L,
        'max_xv'            : max(abs(xV)),
        }

    crc_data['fig_paths'] = fig_paths
    crc_data['fig_paths_name'] = ['侧向位移', '横摆角速度', '前后侧偏角差值', '侧倾角', '车速']

    data_plot = {'xDis':xDis, 'yDis':yDis, 'lateralAcc':lateralAcc, 
        'yawV':yawV, 'delta_a':delta_a, 'rollDis':rollDis, 'xV':xV} # 图片数据

    for key in data_plot:
        if not isinstance(data_plot, list):
            data_plot[key] = data_plot[key].tolist()

    for key in crc_data:
        if isinstance(crc_data[key], float) :
            crc_data[key] = round(crc_data[key],2)

    for fig in figs:
        fig.clf()

    return crc_data, data_plot


# 评分计算
def handle_crc_score(crc_data):
    """
        评分 - 企业标准评分 
    """
    mass = crc_data['mass']/1000
    if mass <= 2.5:
        cal_type = 1
        车辆类别 = '最大总质量 ≤2.5t'
    elif mass <= 9:
        cal_type = 2
        车辆类别 = '2.5t< 最大总质量 ≤9t'
    else:
        cal_type = 3
        车辆类别 = '最大总质量 >9t'

    # 0.2g 不足转向  deg/(m/s^2)
    U_2acc = crc_data['U_2acc']
    if U_2acc > 1.0:
        N_u = '不可接受'
    elif U_2acc >= 0.8:
        N_u = '可接受'
    elif U_2acc >= 0.5:
        N_u = '优秀'
    elif U_2acc >= 0.3:
        N_u = '可接受'
    else:
        N_u = '不可接受'

    # 0.2g 车身侧倾度 deg/(m/s^2)
    rollDisK_2acc = crc_data['rollDisK_2acc']
    if cal_type < 3 :
        if rollDisK_2acc > 1.1:
            N_r = '不可接受'
        elif rollDisK_2acc >= 0.6:
            N_r = '可接受'
        else:
            N_r = '优秀'
    else:
        if rollDisK_2acc >1.2:
            N_r = '不可接受'
        elif rollDisK_2acc >=0.7:
            N_r = '可接受'
        else:
            N_r = '优秀'
    
    # 中性转向点 m/s^2
    mid_steer_point = crc_data['mid_steer_point']   
    if cal_type == 1:
        m_60, m_100 = 5, 8
    elif cal_type == 2:
        m_60, m_100 = 4, 6.5
    elif cal_type == 3:
        m_60, m_100 = 3, 5

    if mid_steer_point > m_100:
        N_m = '优秀'
    elif mid_steer_point >= m_60:
        N_m = '可接受'
    else:
        N_m = '不可接受'

    score_data = {
        'N_u' : N_u,
        'N_r' : N_r,
        'N_m' : N_m,
        '车辆类别' : 车辆类别,
    }

    return score_data


# word文档生成
def handle_crc_docx(docx_path, crc_data, score_data):
    """
        docx 文件生成
    """
    obj = office_docx.DataDocx(docx_path)

    obj.add_heading('操纵稳定性-稳态回转', level=0, size=20)
    obj.add_heading('数据-作图', level=1, size=15)

    for fig_path , fig_name in zip(crc_data['fig_paths'], crc_data['fig_paths_name']):
        obj.add_docx_figure(fig_path, fig_name, width=16)

    obj.add_page_break()
    obj.add_heading('数据评价参考', level=1, size=15)
    obj.add_list_bullet('数据评价参照《Q/BYDQ-A1901.1315-2020 商用车转向操纵稳定性能通用评价规范》')

    str1 = '0.2g不足转向度 deg/(m/s^2) 评价'
    list1 = [
        ['车型',                      '优秀',       '可接受',  '不可接受'],
        ['最大总质量 ≤2.5t',             '0.5~0.8',  '0.3~0.5 或 0.8~1.0',    '<0.3 或 >1.0'],
        ['2.5t< 最大总质量 ≤9t',         '0.5~0.8',  '0.3~0.5 或 0.8~1.0',    '<0.3 或 >1.0'],
        ['最大总质量 >9t',               '0.5~0.8',  '0.3~0.5 或 0.8~1.0',    '<0.3 或 >1.0'],
    ]
    obj.add_table(str1, list1)


    str2 = '0.2g车身侧倾度 deg/(m/s^2) 评价'
    list2 = [
        ['车型',                      '优秀',       '可接受',  '不可接受'],
        ['最大总质量 ≤2.5t',             '<0.6',     '0.6~1.1',  '>1.1'],
        ['2.5t< 最大总质量 ≤9t',         '<0.6',     '0.6~1.1',  '>1.1'],
        ['最大总质量 >9t',               '<0.7',     '0.7~1.2',  '>1.2'],
    ]
    obj.add_table(str2, list2)

    str3 = '中性转向点 m/s^2 评价'
    list3 = [
        ['车型',                      '优秀',       '可接受',  '不可接受'],
        ['最大总质量 ≤2.5t',             '>8.0',     '5.0~8.0',  '<5.0'],
        ['2.5t< 最大总质量 ≤9t',         '>6.5',     '4.0~6.5',  '<4.0'],
        ['最大总质量 >9t',               '>5.0',     '3.0~5.0',  '<3.0'],
    ]
    obj.add_table(str3, list3)

    obj.add_page_break()
    obj.add_heading('数据评价', level=1, size=15)
    str_list = [
        ['项目', '数值', '评价'],
        ['0.2g不足转向度 deg/(m/s^2)',   crc_data['U_2acc'],         score_data['N_u']],
        ['0.2g车身侧倾度 deg/(m/s^2)',   crc_data['rollDisK_2acc'],  score_data['N_r']],
        ['中性转向点 m/s^2',             crc_data['mid_steer_point'],score_data['N_m']],
        ['0.4g车身侧倾角 deg',           crc_data['rollDis_04g'],    '-'],
        ['初始转弯半径 m',                crc_data['R0'],             '-'],
        ['方向盘转角 deg',               crc_data['steerWheelDis'],  '-'],
        ['仿真-最大侧向加速度 m/s^2',        crc_data['max_lateralAcc'], '-'],
        ['仿真-最大车速 km/h',            crc_data['max_xv'],         '-'],
        ['计算过程-整车质量估算 kg',      crc_data['mass'],           '-'],
        ['轴距 m',                        crc_data['L'],              '-'],
        ['车辆类型',                    score_data['车辆类别'],     '-'],
    ]

    obj.add_table('计算结果', str_list)
    obj.save()
    docx_path = os.path.abspath(docx_path)
    # office_docx.doc2pdf(docx_path)
    os.popen(docx_path[:-4]+'pdf')
    # for fig_path in crc_data['fig_paths']:
    #   file_edit.del_file(fig_path)

    return None


# 稳态回转-主函数
def handle_crc(res_path, docx_path, L, reqs, comps, spline_s):
    # print(kwargs, spline_s)
    crc_data, data_plot = res_handle_crc_cal(res_path, L, docx_path, reqs, comps, spline_s)
    score_data = handle_crc_score(crc_data)

    with open(docx_path[:-4]+'json', 'w') as f:
        json.dump({'crc_data':crc_data, 'score_data':score_data, 'data_plot':data_plot}, f)

    handle_crc_docx(docx_path, crc_data, score_data)

    return crc_data, score_data, data_plot


# 指定文档模板,并进行替换文字及图片
def handle_crc_docx_template(template_path, new_docx_path, crc_data, score_data):
    """
        win32com 文档替换

    score_data = {
        'N_u' : N_u,    0.2g 不足转向度 评价
        'N_r' : N_r,    0.2g 车身侧倾度 评价
        'N_m' : N_m,    中性转向 评价
        '车辆类别' : 车辆类别,
    }

    crc_data = {
        'R0'                : R0, 
        'mid_steer_point'   : abs(lateralAcc[mid_steer_acc_loc]),
        'U_2acc'            : U_2acc,
        'rollDisK_2acc'     : abs(rollDisK_2acc),
        'rollDis_04g'       : abs(rollDis_04g),
        'mass'              : mean_mass,
        'max_lateralAcc'    : max_lateralAcc,
        'steerWheelDis'     : abs(mean_steerWheelDis),
        'L'                 : L,
        'max_xv'            : max(abs(xV)),
        }
    """
    oldList, newList = [], []
    for fig_path, fig_name in zip(crc_data['fig_paths'], crc_data['fig_paths_name']):
        oldList.append(f'#crc_{fig_name}#')
        newList.append(fig_path)
    
    del crc_data['fig_paths']
    del crc_data['fig_paths_name']

    for key in crc_data:
        oldList.append(f'$crc_{key}$')
        newList.append(str(crc_data[key]))

    for key in score_data:
        oldList.append(f'$crc_{key}$')
        newList.append(str(score_data[key]))

    logger.info(f'oldList: {pformat(oldList)}')
    logger.info(f'newList: {pformat(newList)}')

    template_path = os.path.abspath(template_path)
    new_docx_path = os.path.abspath(new_docx_path)
    word_obj = office_docx.WordEdit(template_path)
    word_obj.replace_edit(oldList, newList)
    word_obj.save(new_docx_path)
    word_obj.close()

    return None


# ====================================================
# 测试模块

def test_handle_crc():
    
    res_path = r'..\tests\file_result\GB_T_crc.res'
    docx_path = r'..\tests\car_post_handle_crc\GB_T_crc.docx'
    L = 4
    reqs  = ['chassis_accelerations','chassis_velocities','chassis_velocities','chassis_displacements','jms_steering_wheel_angle_data','chassis_displacements','chassis_displacements']
    comps = ['lateral','yaw','longitudinal','roll','displacement','lateral','longitudinal']
    data = {'spline_s':0.1}
    
    crc_data, score_data, data_plot = handle_crc(res_path, docx_path, L, reqs, comps, **data)
    # print(crc_data)
    print('crc_data')
    print(datacal.str_view_data_type(crc_data))

    return crc_data, score_data, data_plot


def test_handle_crc_docx_template():

    template_path = r'..\tests\car_post_handle_crc\handle_crc_template.docx'
    new_docx_path = r'..\tests\car_post_handle_crc\handle_crc_new.docx'
    crc_data, score_data = test_handle_crc()

    handle_crc_docx_template(template_path, new_docx_path, crc_data, score_data)


if __name__ == '__main__':
    pass    

    test_handle_crc()
    # test_handle_crc_docx_template()
    

