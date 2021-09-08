"""
    蛇行试验-后处理
"""

from pyadams.file import result, office_docx, file_edit
DataModel = result.DataModel

import numpy as np
import math
import os
import logging
# logging.basicConfig(level=logging.INFO)   # logging设置
logger = logging.getLogger('post_handle_s')

# 子函数
list2str = lambda list1: ','.join([str(n) for n in list1])
list2negative = lambda list1: [-n for n in list1]
list2abs = lambda list1: [abs(n) for n in list1]
list2absmean = lambda list1: sum(list2abs(list1)) / len(list1)

def sorted_xy(xlist,ylist):
    '''从小到大排序'''
    dic1 = {x:y for x,y in zip(xlist,ylist)}
    # 排序
    x = sorted(dic1, key=lambda x:dic1[x], reverse=True)
    y = [dic1[xn] for xn in x]
    return x,y

def diff(list1):
    '''
        列表数值 差分 
        后一位减前一位
    '''
    return [list1[n+1]-list1[n] for n in range(len(list1)-1)]

def listloc(list1,locs):
    '''获取指定位置列表数据'''
    return [list1[n] for n in locs]

def data_peak_find(list1,distance = 2):
    '''
        使用三点数据对列表进行检索 ,返回潜在波峰位置
        当前：寻找波峰
        可用于：查找波峰、波谷
        list1 数据段 y
        distance 数据点间隔，默认2 
    '''
    list_loc = []
    for d in range((len(list1)-(distance*2))):
        up = d
        mid = d+distance
        down = d+distance*2
        # j1 = (list1[up]>list1[mid])*(list1[down]>list1[mid]) # 波谷寻找
        j2 = (list1[up]<list1[mid])*(list1[down]<list1[mid]) # 波峰寻找

        if j2:
            list_loc.append(mid)
    return list_loc

def peak_find(xlist,ylist,distance=2,xdistance=2):
    '''波峰寻找'''
    list_loc = data_peak_find(ylist,distance=distance)
    new_xlist = listloc(xlist,list_loc)
    diff_x = diff(new_xlist)
    nlens = []
    for it in range(100):
        nlens.append(len(diff_x))
        loc0 = []
        num = 0
        jump = False
        for n in range(len(diff_x)):
            if jump:
                jump = False
                continue
            if diff_x[n] < xdistance:
                # 间距国小
                if ylist[list_loc[n+1]] - ylist[list_loc[n]] >0:
                    # 后一位大于前一位 删除前一位
                    loc0.append(n)
                else:
                    loc0.append(n+1)
                num += 1
                jump = True
        for n in sorted(loc0,reverse=True):
            del list_loc[n]

        if num == 0:
            break

        new_xlist = listloc(xlist,list_loc)
        diff_x = diff(new_xlist)
    new_ylist = listloc(ylist,list_loc)
    
    return new_xlist,new_ylist,nlens

def handle_peak_find(xlist, ylist, distance=2, xdistance=2):
    """
    """
    
    xs1, ys1, _ = peak_find(xlist, ylist, distance, xdistance)
    xs2, ys2, _ = peak_find(xlist, list2negative(ylist), distance, xdistance)

    xs1.extend(xs2) 
    ys1.extend(list2negative(ys2))
    ys, xs = sorted_xy(ys1, xs1)

    xs.reverse()
    ys.reverse()

    assert len(set(xs)) == len(xs),  'xs 有重合'

    return xs, ys

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

"""蛇形后处理"""
def res_handle_s_cal(res_path, docx_path, xdistance=50, xdis_start=95, xdis_end=305,
        reqs=None, comps=None):
    """
        输入：
            res_path: res 后处理文件
            docx_path: 处理结果输出指定文件路径，若不输出则为None
            xdistance: 间距判定，用于避免局部波峰 ,单位m
            xdis_start: 数据段截取，起始X距离，单位m
            xdis_end: 数据段截取，终止X距离 单位m
        
        输出：
        单位 m/s deg m/s^2 m
        1、输入参数：
            轴距、车重
            起始时间、结果时间
    """
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


    dataobj = DataModel('post_handle_s')
    dataobj.new_file(res_path, 'handle_s')
    dataobj['handle_s'].set_reqs_comps(reqs, comps)
    dataobj['handle_s'].set_line_ranges([4,None])
    dataobj['handle_s'].set_select_channels(None)
    dataobj['handle_s'].read_file()
    data = dataobj['handle_s'].get_data()

    # 整车质量
    dataobj['handle_s'].set_reqs_comps(*get_tire_normal_reqcomp(dataobj['handle_s']))
    dataobj['handle_s'].read_file(isReload=False)
    tire_datas = dataobj['handle_s'].get_data()

    tire_loads = []
    for n in range(len(tire_datas[0])):
        value = 0
        for line in tire_datas:
            value += line[n]
        tire_loads.append(value)
    tire_loads = np.array(tire_loads)

    # 转矩阵
    resData=np.array(data)
    # 单位转换
    lateralAcc,yawV,xV,rollDis,steerWheelDis=resData[0]*9.8,resData[1]/math.pi*180,resData[2]/3.6,resData[3]/math.pi*180,resData[4]/math.pi*180
    yDis,xDis=resData[5]/1000,resData[6]/1000
    nloc=(xDis>xdis_start)*(xDis<xdis_end)  # 指定区间段筛选

    xs_yacc, ys_yacc    = handle_peak_find(xDis[nloc], lateralAcc[nloc], distance=4, xdistance=xdistance)
    xs_yawv, ys_yawv    = handle_peak_find(xDis[nloc], yawV[nloc], distance=4, xdistance=xdistance)
    xs_roll, ys_roll    = handle_peak_find(xDis[nloc], rollDis[nloc], distance=4, xdistance=xdistance)
    xs_st,   ys_st      = handle_peak_find(xDis[nloc], steerWheelDis[nloc], distance=4, xdistance=xdistance)
    xs_ydis, ys_ydis    = handle_peak_find(xDis[nloc], yDis[nloc], distance=4, xdistance=xdistance)

    mean_loads  = np.mean(tire_loads[nloc])
    mean_mass   = mean_loads / 9.80665

    mean_yacc       = list2absmean(ys_yacc)
    mean_yawv       = list2absmean(ys_yawv)
    mean_roll       = list2absmean(ys_roll)
    mean_st         = list2absmean(ys_st)
    mean_xv         = list2absmean(xV[nloc])
    mean_xv         = round(mean_xv*3.6, 2)
    
    mean_data = {
        'st'    : mean_st,
        'yacc'  : mean_yacc,
        'yawv'  : mean_yawv,
        'xv'    : mean_xv,
        'roll'  : mean_roll,
        'mass'  : mean_mass,
    }

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
    plt.plot(xDis[nloc], yDis[nloc], 'r')
    plt.plot(xs_ydis, ys_ydis, '*b')
    plt.ylabel('侧向位移 Y(m)', fontsize=15)
    plt.xlabel('纵向位移 X(m)', fontsize=15)
    plt.tick_params(labelsize=15)
    plt.tight_layout()
    plt.grid(True)

    figs.append(plt.figure())
    plt.plot(xDis, yawV, 'b')
    plt.plot(xDis[nloc], yawV[nloc], 'r')
    plt.plot(xs_yawv, ys_yawv, '*b')
    plt.ylabel('横摆角速度 yaw(deg/s)', fontsize=15)
    plt.xlabel('纵向位移 X(m)', fontsize=15)
    plt.tick_params(labelsize=15)
    plt.tight_layout()
    plt.grid(True)

    figs.append(plt.figure())
    plt.plot(xDis, lateralAcc, 'b')
    plt.plot(xDis[nloc], lateralAcc[nloc], 'r')
    plt.plot(xs_yacc, ys_yacc, '*b')
    plt.ylabel('侧向加速度 Yacc(m/s^2)', fontsize=15)
    plt.xlabel('纵向位移 X(m)', fontsize=15)
    plt.tick_params(labelsize=15)
    plt.tight_layout()
    plt.grid(True)


    figs.append(plt.figure())
    plt.plot(xDis, steerWheelDis, 'b')
    plt.plot(xDis[nloc], steerWheelDis[nloc], 'r')
    plt.plot(xs_st, ys_st, '*b')
    plt.ylabel('方向盘转角 deg', fontsize=15)
    plt.xlabel('纵向位移 X(m)', fontsize=15)
    plt.tick_params(labelsize=15)
    plt.tight_layout()
    plt.grid(True)

    figs.append(plt.figure())
    plt.plot(xDis, rollDis, 'b')
    plt.plot(xDis[nloc], rollDis[nloc], 'r')
    plt.plot(xs_roll, ys_roll, '*b')
    plt.ylabel('侧倾角 deg', fontsize=15)
    plt.xlabel('纵向位移 X(m)', fontsize=15)
    plt.tick_params(labelsize=15)
    plt.tight_layout()
    plt.grid(True)

    figs.append(plt.figure())
    xV2 = xV[nloc]
    xV = [round(value,1)*3.6 for value in xV]
    xV2 = [round(value,1)*3.6 for value in xV2]
    plt.plot(xDis, xV, 'b')
    plt.plot(xDis[nloc], xV2, 'r')
    plt.ylabel('车速 km/h', fontsize=15)
    plt.xlabel('纵向位移 X(m)', fontsize=15)
    plt.tick_params(labelsize=15)
    plt.tight_layout()
    plt.grid(True)

    fig_paths = []
    if docx_path != None:
        for n, fig in enumerate(figs):
            fig_path = '.'.join(docx_path.split('.')[:-1]) + f'_{n}.png'
            logger.info(f'图片生成:{fig_path}')
            fig.savefig(fig_path)
            plt.close()
            fig_paths.append(fig_path)

    mean_data['fig_paths'] = fig_paths
    mean_data['fig_paths_name'] = ['侧向位移', '横摆角速度', '侧向加速度', '方向盘转角', '侧倾角', '车速']

    for key in mean_data:
        if isinstance(mean_data[key], float) :
            mean_data[key] = round(mean_data[key], 2)

    # for fig in figs:
    #     fig.clf()

    return mean_data

def handle_s_score(mean_data, isBus=True, isArticulated=False):
    """
        评分 - 企业标准评分 
    """
    mass = mean_data['mass']/1000
    if isBus: # 客车
        if mass<=5:
            cal_type = 2
            车辆类别 = 'M2类'
        elif isArticulated==False:
            cal_type = 3
            车辆类别 = 'M3类'
        else:
            cal_type = 4
            车辆类别 = 'M3类(铰接客车)'
    else:   # 卡车
        if mass <= 3.5:
            cal_type = 1
            车辆类别 = 'N1类'
        elif mass <= 12:
            cal_type = 2
            车辆类别 = 'N2类'
        elif mass <= 15:
            cal_type = 3
            车辆类别 = 'N3类(≤15t)'
        else:
            cal_type = 4
            车辆类别 = 'N3类(>15t)'

    if cal_type == 1:
        标桩间距    = 30
        v_base      = 65
        r_60        = 19
        r_100       = 15
        theta_60    = 150
        theta_100   = 90

    if cal_type == 2:
        标桩间距    = 30
        v_base      = 50
        r_60        = 17
        r_100       = 15
        theta_60    = 150
        theta_100   = 90

    if cal_type == 3:
        标桩间距    = 50
        v_base      = 60
        r_60        = 10
        r_100       = 8.5
        theta_60    = 130
        theta_100   = 90

    if cal_type == 4:
        标桩间距    = 50
        v_base      = 50
        r_60        = 10
        r_100       = 8
        theta_60    = 130
        theta_100   = 90

    if mean_data['yawv'] > r_60:
        N_r = '不可接受'
    elif mean_data['yawv'] < r_100:
        N_r = '好'
    else:
        N_r = '可接受'

    if mean_data['st'] > theta_60:
        N_theta = '不可接受'
    elif mean_data['st'] < theta_100:
        N_theta = '好'
    else:
        N_theta = '可接受'

    score_data = {'N_r':N_r, 'N_theta':N_theta, '标桩间距':标桩间距, 'v_base':v_base,
        'isBus':isBus, 'isArticulated':isArticulated, '车辆类别':车辆类别}
    # score_data['isBus'] = isBus
    # score_data['isArticulated'] = isArticulated
    # score_data['车辆类别'] = 车辆类别

    return score_data

def handle_s_docx(docx_path, mean_data, score_data):
    """
        docx 文件生成
    """
    obj = office_docx.DataDocx(docx_path)

    obj.add_heading('操纵稳定性-蛇行试验', level=0, size=20)
    obj.add_heading('数据-作图', level=1, size=15)

    for fig_path , fig_name in zip(mean_data['fig_paths'], mean_data['fig_paths_name']):
        obj.add_docx_figure(fig_path, fig_name, width=16)

    obj.add_page_break()
    obj.add_heading('数据评价参考', level=1, size=15)
    obj.add_list_bullet('车辆分类参照《GB/T 15089-2001 机动车辆及挂车分类》')
    obj.add_list_bullet('数据评价参照《Q/BYDQ-A1901.1315-2020 商用车转向操纵稳定性能通用评价规范》')

    str1 = '标桩间距及标准车速-企标'
    list1 = [
        ['车型',                      '桩距(m)',    '基准车速(km/h)'],
        ['N1类',                         '30',       '65'],
        ['M2类、N2类',                     '30',       '50'],
        ['M3类、N3类(≤15t)',               '50',       '60'],
        ['M3类(铰接客车)、N3类(>15t)',     '50',       '50'],
    ]
    obj.add_table(str1, list1)

    str2 = '平均转角峰值-评价'
    list2 = [
        ['车型',                      '好',    '可接受',  '不可接受'],
        ['N1类',                         '<90',  '90~150',   '>150'],
        ['M2类、N2类',                     '<90',  '90~150',   '>150'],
        ['M3类、N3类(≤15t)',               '<90',  '90~130',   '>130'],
        ['M3类(铰接客车)、N3类(>15t)',     '<90',  '90~130',   '>130'],
    ]
    obj.add_table(str2, list2)

    str3 = '平均横摆角速度-评价'
    list3 = [
        ['车型',                      '好',    '可接受',  '不可接受'],
        ['N1类',                         '<15',  '15~19',    '>19'],
        ['M2类、N2类',                     '<15',  '15~17',    '>17'],
        ['M3类、N3类(≤15t)',               '<8.5', '8.5~10',   '>10'],
        ['M3类(铰接客车)、N3类(>15t)',     '<8',   '8~10',     '>10'],
    ]
    obj.add_table(str3, list3)

    obj.add_page_break()
    obj.add_heading('数据评价', level=1, size=15)
    str_list = [
        ['项目', '数值', '评价'],
        ['平均横摆角速度峰值 deg/s',     mean_data['yawv'],          score_data['N_r']],
        ['平均侧倾角峰值 deg',         mean_data['roll'],          '-'],
        ['平均方向盘转角峰值 deg',   mean_data['st'],            score_data['N_theta']],
        ['平均侧向加速度 m/s^2',       mean_data['yacc'],          '-'],
        ['平均车速 km/h',           mean_data['xv'],            '-'],
        ['基准车速 km/h',           score_data['v_base'],       '-'],
        ['标桩间距 m',              score_data['标桩间距'],         '-'],
        ['整车质量估算 kg',           mean_data['mass'],          '-'],
        ['车辆类型',                score_data['车辆类别'],     '-'],
    ]
    obj.add_table('计算结果', str_list)

    v_base = score_data['v_base']
    v_mean = mean_data['xv']
    if abs(v_base-v_mean) < 4 :
        logger.info(f'基准车速错误 目标:{v_base} km/h 仿真平均:{v_mean} km/h')
    else:
        logger.warning(f'基准车速错误 目标:{v_base} km/h 仿真平均:{v_mean} km/h')

    obj.save()
    docx_path = os.path.abspath(docx_path)
    pdf_path  = docx_path[:-4]+'pdf'
    office_docx.doc2pdf(docx_path)
    
    logger.info(f'docx文件生成:{docx_path}')
    logger.info(f'pdf文件生成:{pdf_path}')

    os.popen(pdf_path)
    
    # for fig_path in mean_data['fig_paths']:
    #   logger.info(f'删除图片:{fig_path}')
    #   file_edit.del_file(fig_path)

    return None

def handle_s(res_path, docx_path, xdistance, xdis_start, xdis_end, isBus, isArticulated,
        reqs=None, comps=None):

    mean_data = res_handle_s_cal(res_path, docx_path, xdistance=xdistance, xdis_start=xdis_start, xdis_end=xdis_end,
        reqs=reqs, comps=comps)
    
    score_data = handle_s_score(mean_data, isBus=isBus, isArticulated=isArticulated)

    handle_s_docx(docx_path, mean_data, score_data)
    # del mean_data['fig_paths']
    # del mean_data['fig_paths_name']
    logger.info(f'mean_data:{mean_data}')
    logger.info(f'score_data:{score_data}')
    logger.info(f'蛇行试验-后处理计算结束')

    return mean_data, score_data

def handle_s_docx_template(template_path, new_docx_path, mean_data, score_data):
    """
        win32com 文档替换
        
    score_data = {
        'N_r':N_r,          横摆角评估
        'N_theta':N_theta,  方向盘转角评估
        '标桩间距':标桩间距,  m
        'v_base':v_base,    基准车速 km/h
        'isBus':isBus, 'isArticulated':isArticulated, '车辆类别':车辆类别}
    
    mean_data = {
        'st'    : mean_st,      平均峰值方向盘转角 deg
        'yacc'  : mean_yacc,    平均侧向加速度 m/s^2
        'yawv'  : mean_yawv,    平均峰值横摆角速度 deg/(m/s^2)
        'xv'    : mean_xv,      平均车速 km/h
        'roll'  : mean_roll,    平均侧倾角 deg
        'mass'  : mean_mass,    预估质量 kg
    }


    """
    oldList, newList = [], []
    for fig_path, fig_name in zip(mean_data['fig_paths'], mean_data['fig_paths_name']):
        oldList.append(f'#s_{fig_name}#')
        newList.append(fig_path)
    del mean_data['fig_paths']
    del mean_data['fig_paths_name']
    for key in mean_data:
        oldList.append(f'$s_{key}$')
        newList.append(str(mean_data[key]))

    for key in score_data:
        oldList.append(f'$s_{key}$')
        newList.append(str(score_data[key]))

    template_path = os.path.abspath(template_path)
    new_docx_path = os.path.abspath(new_docx_path)
    word_obj = office_docx.WordEdit(template_path)
    word_obj.replace_edit(oldList, newList)
    word_obj.save(new_docx_path)
    word_obj.close()

    return None



# ====================================================
# 测试模块

def test_handle_s():

    res_path = r'..\tests\file_result\GB_T_s.res'
    docx_path = r'..\tests\car_post_handle_s\GT_T_s.docx'
    xdistance = 25
    xdis_start = 95
    xdis_end = 300
    isBus = True
    isArticulated = False
    reqs = ["chassis_accelerations", "chassis_velocities", "chassis_velocities", "chassis_displacements",
            "jms_steering_wheel_angle_data", "chassis_displacements", "chassis_displacements"]
    comps = ["lateral", "yaw", "longitudinal", "roll", "displacement", "lateral", "longitudinal"]

    mean_data, score_data = handle_s(res_path, docx_path, xdistance, xdis_start, xdis_end, isBus, isArticulated,
        reqs, comps)

    return mean_data, score_data



def test_handle_s_docx_template():

    mean_data, score_data = test_handle_s()
    template_path = r'..\tests\car_post_handle_s\handle_s_template.docx'
    new_docx_path = r'..\tests\car_post_handle_s\handle_s_new.docx'

    handle_s_docx_template(template_path, new_docx_path, mean_data, score_data)


if __name__ == '__main__':
    pass

    # test_handle_s()

    test_handle_s_docx_template()

    # res_path = r'..\code_test\car\post_handle_s/GB_T_s.res'
    # docx_path = r'..\code_test\car\post_handle_s/GT_T_s.docx'
    # xdistance = 25
    # xdis_start = 95
    # xdis_end = 300
    # isBus = True
    # isArticulated = False
    # reqs = ["chassis_accelerations", "chassis_velocities", "chassis_velocities", "chassis_displacements",
    #         "jms_steering_wheel_angle_data", "chassis_displacements", "chassis_displacements"]
    # comps = ["lateral", "yaw", "longitudinal", "roll", "displacement", "lateral", "longitudinal"]

    # handle_s(res_path, docx_path, xdistance, xdis_start, xdis_end, isBus, isArticulated,
    #     reqs, comps)
    
    # mean_data = res_handle_s_cal(res_path, docx_path, xdistance=xdistance, xdis_start=xdis_start, xdis_end=xdis_end)
    # # print(mean_data)
    # score_data = handle_s_score(mean_data, isBus=isBus, isArticulated=isArticulated)
    # # print(score_data)

    # handle_s_docx(docx_path, mean_data, score_data)
    
    