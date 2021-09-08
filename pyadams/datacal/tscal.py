# -*- coding: utf-8 -*-
"""
    时域数据处理
    二维数组-处理:
        RMS(list1-list2)/RMS(list2)
        RMS(list1)/RMS(list2)
        max(list1)/max(list2)
        min(list1)/min(list2)
        PDI(list1)/PDI(list2)
        PDI(list1)
        RMS(list1)
        (list1-list2)
        RMS(list1-list2)
"""
import math
import copy
import os.path
import logging

from pyadams.datacal import durablecal

# ==============================
# logging日志配置
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


# ==============================
# 耐久模块调用
cal_rainflow = durablecal.rainflow_3point      # 雨流计数
cal_goodman  = durablecal.cal_goodman          # 古德曼修正

# ==============================

def cal_rms_delta_percent(list1s,list2s): # 二维数组 RMS(list1-list2)/RMS(list2)
    """
        误差均方根 / 目标均方根
        等长评估, 以最短的为主
    """
    list1 = copy.deepcopy(list1s)
    list2 = copy.deepcopy(list2s)

    n_l1 = len(list1[0])
    n_l2 = len(list2[0])

    if n_l1 != n_l2 : 
        logging.warning(f'cal_rms_delta_percent 数据长度不等: {{ {n_l1} vs {n_l2} }} 自动去除较长部分')

    if n_l1 > n_l2 :
        for line in list1:
            del line[n_l2:]
    elif n_l1 < n_l2:
        for line in list2:
            del line[n_l1:]

    values_delta = cal_rms_delta(list1,list2)
    values_target = cal_rms(list2)

    list3 = [ n1/n2 for n1,n2 in zip(values_delta,values_target)]

    return list3

def cal_rms_percent(list1s,list2s): # 二维数组 RMS(list1)/RMS(list2)
    """
        测量均方根 / 目标信号均方根
        等长评估, 以最短的为主
        输入的list 为二维数组
    """
    list1 = copy.deepcopy(list1s)
    list2 = copy.deepcopy(list2s)

    n_l1 = len(list1[0])
    n_l2 = len(list2[0])

    if n_l1 != n_l2 : 
        logging.warning(f'cal_rms_percent 数据长度不等: {{ {n_l1} vs {n_l2} }} 自动去除较长部分')

    if n_l1 > n_l2 :
        for line in list1:
            del line[n_l2:]
    elif n_l1 < n_l2:
        for line in list2:
            del line[n_l1:]

    data = []
    data1 = cal_rms(list1)
    data2 = cal_rms(list2)
    for n in range(len(data1)):
        data.append(data1[n]/data2[n])

    return data

def cal_max_percent(list1s,list2s): # 二维数组 max(list1)/max(list2)
    """
        测量信号最大值 / 目标信号最大值
        等长评估, 以最短的为主
        输入的list 为二维数组
    """
    list1 = copy.deepcopy(list1s)
    list2 = copy.deepcopy(list2s)

    n_l1 = len(list1[0])
    n_l2 = len(list2[0])
    
    if n_l1 != n_l2 : 
        logging.warning(f'cal_max_percent 数据长度不等: {{ {n_l1} vs {n_l2} }} 自动去除较长部分')

    if n_l1 > n_l2 :
        for line in list1:
            del line[n_l2:]
    elif n_l1 < n_l2:
        for line in list2:
            del line[n_l1:]

    maxs1 = [max(line) for line in list1]
    maxs2 = [max(line) for line in list2]

    values = []
    for max1,max2 in zip(maxs1,maxs2):
        if max1==max2==0:
            values.append(1)
        elif max2==0:
            values.append((max1+0.01)/(max2+0.01))
        else:
            values.append(max1/max2)

    # values = [ max1 / max2 for max1,max2 in zip(maxs1,maxs2)]

    return values

def cal_min_percent(list1s,list2s): # 二维数组 min(list1)/min(list2)
    """
        测量信号最小值 / 目标信号最小值
        等长评估, 以最短的为主
        输入的list 为二维数组
    """
    list1 = copy.deepcopy(list1s)
    list2 = copy.deepcopy(list2s)

    n_l1 = len(list1[0])
    n_l2 = len(list2[0])

    if n_l1 != n_l2 : 
        logging.warning(f'cal_min_percent 数据长度不等: {{ {n_l1} vs {n_l2} }} 自动去除较长部分')

    if n_l1 > n_l2 :
        for line in list1:
            del line[n_l2:]
    elif n_l1 < n_l2:
        for line in list2:
            del line[n_l1:]

    mins1 = [min(line) for line in list1]
    mins2 = [min(line) for line in list2]

    values = []
    for min1,min2 in zip(mins1,mins2):
        if min1==min2==0:
            values.append(1)
        elif min2==0:
            # values.append(min1/(min1/1e2))
            values.append((min1+0.01)/(min2+0.01))
        else:
            values.append(min1/min2)

    # values = [ min1 / min2 for min1,min2 in zip(mins1,mins2)]

    return values

def cal_pdi_relative(list1s,list2s, b=5000.0, k=-5.0): # 二维数组 PDI(list1)/PDI(list2)
    """
        测量信号PDI / 目标信号PDI
        等长评估, 以最短的为主
        输入的list 为二维数组
    """
    list1 = copy.deepcopy(list1s)
    list2 = copy.deepcopy(list2s)

    n_l1 = len(list1[0])
    n_l2 = len(list2[0])

    if n_l1 != n_l2 : 
        logging.warning(f'cal_pdi_relative 数据长度不等: {{ {n_l1} vs {n_l2} }} 自动去除较长部分')

    if n_l1 > n_l2 :
        for line in list1:
            del line[n_l2:]
    elif n_l1 < n_l2:
        for line in list2:
            del line[n_l1:]

    damage1 = cal_pdi(list1, b, k)
    damage2 = cal_pdi(list2, b, k)

    values = [ d1/d2 for d1,d2 in zip(damage1,damage2)]

    return values

def cal_rainflow_pdi_relative(list1s, list2s, b=5000.0, k=-5.0): # 二维数组 rainflow_PDI(list1)/rainflow_PDI(list2)
    """
        基于雨流计数计算
        测量信号PDI / 目标信号PDI
        输入的list 为二维数组
    """
    list1 = copy.deepcopy(list1s)
    list2 = copy.deepcopy(list2s)

    damage1 = cal_rainflow_pdi(list1, b, k)
    damage2 = cal_rainflow_pdi(list2, b, k)

    values = [ d1/d2 for d1,d2 in zip(damage1,damage2)]

    return values

def cal_pdi(list1, b=5000.0, k=-5.0):# 二维数组 PDI(list1)
    """
        伪损伤
        输入的list 为二维数组
    """
    import math

    A = math.log10(b)
    B = 1.0/k

    damage = [ sum( [ 1/10**((math.log10(abs(n))-A)/B) for n in line if n!=0 ] ) for line in list1]

    return damage

def cal_rms(list1): # 二维数组 RMS(list1)
    """
        RMS 均方根计算
        输入的list 为二维数组
    """
    nlist = len(list1)
    len_value = len(list1[0])
    data = []
    for n in range(nlist):
        templist = []
        for n1 in range(len_value):
            temp = list1[n][n1]**2 / len_value
            templist.append(temp)
        value1 = sum(templist) ** 0.5
        data.append(value1)
    return data

def cal_max(list2d): # 最大值计算

    return [max(line) for line in list2d]

def cal_min(list2d): # 最小值计算

    return [min(line) for line in list2d]

def cal_delta(list1, list2): # 二维数组 (list1-list2)
    """
        计算两组数据的差值
        list1 - list2 
        输入的list 为二维数组
    """

    # 
    nlist = len(list1)
    len_value = len(list1[0])
    data = [] # 重新创立数组
    for n in range(nlist):
        templist = []
        for n1 in range(len_value):
            templist.append(list1[n][n1]-list2[n][n1])
        data.append(templist)
    return data

def cal_rms_delta(list1, list2): # 二维数组 RMS(list1-list2)
    """
        计算 两个list的差值 对应的 rms
        输入的list 为二维数组
    """
    list3 = cal_delta(list1,list2)
    data = cal_rms(list3)
    return data

def cal_multiply(list1, value): # 二维数组 list1*value
    """
        计算 list1 中数据 乘以 value
        输入的list 为二维数组
    """
    return [[n*value for n in line] for line in list1]

def cal_rainflow_pdi(list2d, b=5000.0, k=-5.0):# 二维数组 PDI(list1)
    """
        伪损伤
        输入的list 为二维数组
    """
    
    new_list2d = []
    for line in list2d:
        try:
            values, means = cal_rainflow(line)
        except:
            values, means = [0], [0]
            logger.warning('cal_rainflow_pdi is false, set pdi:0')

        values = [2*n for n in values] # 幅值2倍
        new_list2d.append(values)

    return cal_pdi(new_list2d, b, k)


# ==============================
# ==============================
# 测试

def test_tscal():

    import matplotlib.pyplot as plt
    from pyadams import datacal
    value2str_list1 = datacal.value2str_list1
    from pyadams.file import result

    # 数据读取
    rsp_file = r'..\code_test\datacal\tscal\cuoban_acc.rsp'
    dataobj = result.DataModel('tscal')
    dataobj.new_file(rsp_file ,'tscal')
    dataobj['tscal'].read_file()
    data_list = dataobj['tscal'].get_data()
    name_channels = dataobj['tscal'].get_titles()
    data_list_gain = cal_multiply(data_list, 0.98)

    # 计算测试
    print('cal_rms')
    print(value2str_list1(cal_rms(data_list)))
    print(value2str_list1(cal_rms(data_list_gain)))

    print('cal_pdi')
    print(value2str_list1(cal_pdi(data_list)))
    print(value2str_list1(cal_pdi(data_list_gain)))

    print('cal_rainflow_pdi')
    print(value2str_list1(cal_rainflow_pdi(data_list)))
    print(value2str_list1(cal_rainflow_pdi(data_list_gain)))


    print('cal_rms_delta_percent')
    print(value2str_list1(cal_rms_delta_percent(data_list_gain, data_list)))
    print('cal_rms_percent')
    print(value2str_list1(cal_rms_percent(data_list_gain, data_list)))
    print('cal_max_percent')
    print(value2str_list1(cal_max_percent(data_list_gain, data_list)))
    print('cal_min_percent')
    print(value2str_list1(cal_min_percent(data_list_gain, data_list)))
    print('cal_pdi_relative')
    print(value2str_list1(cal_pdi_relative(data_list_gain, data_list)))
    print('cal_rainflow_pdi_relative')
    print(value2str_list1(cal_rainflow_pdi_relative(data_list_gain, data_list)))

    return None


if __name__ == '__main__':
    pass

    test_tscal()