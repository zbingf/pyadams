# 标准库
import os
import json
import re
import math
import copy
import pickle
from pprint import pprint, pformat

# 自建库
import result
DataModel = result.DataModel


# ------------
FILEDIR = os.path.dirname(os.path.abspath(__file__))
set_abs_path = lambda str1: os.path.abspath(os.path.join(FILEDIR, str1))
# ACAR_FULL_BRAKE_PATH = "./00_set/acar_full_brake_set.json"
# ACAR_FULL_STATIC_PATH = "./00_set/acar_full_static_set.json"
# ACAR_REQUEST_PATH = "./00_set/acar_request_set.json"
ACAR_FULL_BRAKE_PATH = set_abs_path("00_set/acar_full_brake_set.json")
ACAR_FULL_STATIC_PATH = set_abs_path("00_set/acar_full_static_set.json")
ACAR_REQUEST_PATH = set_abs_path("00_set/acar_request_set.json")


# 字符串','分割, list非空字符
str_split = lambda str1: [n.strip() for n in str1.split(',') if n]

# model名称字符串'.'分割, 并选取范围
name_range = lambda name,start,end=None: '.'.join([v for v in name.split('.') if v][start:end])

# 获取data_dicts的key数据
parse_datads_by_key = lambda data_dic, data_keys, key: [data_dic[data_key][key] for data_key in data_keys]


# json数据读取
def json_read(json_path):

    lines = [] 
    with open(json_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if line.strip().startswith('//'):
                continue
            lines.append(line)
    data = json.loads('\n'.join(lines))
    return set_file_abs_path(data)
    

def set_file_abs_path(data, new_data=None):
    """
        json set 数据路径转为绝地路径
        
        相对路径必须为 ./ 开头
    """

    if new_data==None: new_data = {}
    for key in data:
        line = data[key]
        if isinstance(line, dict):
            new_data[key] = set_file_abs_path(data[key])
            # print(new_data[key])
            continue

        if '_path' in key[-5:]:
            
            if isinstance(line, str):
                if '.' == line[0]:
                    new_data[key] = os.path.abspath(os.path.join(FILEDIR, line[2:]))
                    continue

        new_data[key] = line

    return new_data


# res后处理文件快速读取
def res_read(name, name_res, res_path, reqs, comps, line_range=None, isSamplerate=False):
    # if line_range==None: line_range = [4,None]
        
    dataobj = DataModel(name)
    dataobj.new_file(res_path, name_res)
    dataobj[name_res].set_reqs_comps(reqs, comps)
    dataobj[name_res].set_line_ranges(line_range)
    dataobj[name_res].set_select_channels(None)
    dataobj[name_res].read_file()
    data = dataobj[name_res].get_data()
    
    if isSamplerate:
        samplerate = dataobj[name_res].get_samplerate()
    else:
        samplerate = None
    
    return data, samplerate


# res后处理文件数据再次获取, 不重复读取
def res_read_again(name, name_res, reqs, comps, line_range=None):
    # if line_range==None: line_range = [4,None]
    
    dataobj = DataModel(name)
    dataobj[name_res].set_reqs_comps(reqs, comps)
    dataobj[name_res].set_line_ranges(line_range)
    dataobj[name_res].read_file(isReload=False)    
    data = dataobj[name_res].get_data()
    
    return data


# res文件后处理,单位获取
# 暂时停用
def res_units(res_path):
    # <Units angle="rad" length="mm" mass="kg" time="sec" />

    f = open(res_path, 'r')
    for n in range(100):
        line = f.readline().lower()
        if '<units' in line and '/>' in line:
            break
    f.close()
    line = line.replace(' ', '')
    
    angle_unit = re.match('.*angle="(\S+?)".*', line).group(1)
    length_unit = re.match('.*length="(\S+?)".*', line).group(1)
    mass_unit = re.match('.*mass="(\S+?)".*', line).group(1)
    time_unit = re.match('.*time="(\S+?)".*', line).group(1)
    units = {
        'angle' : angle_unit,
        'length': length_unit,
        'mass'  : mass_unit,
        'time'  : time_unit,
    }
    # print(angle)
    return units
    

# 暂时停用
def angel_deg(units, list1):
    angle_unit = units['angle']
    if angle_unit == 'rad':
        return [v*180.0/math.pi for v in list1]

    if angle_unit == 'deg':
        return list1


# 批量编辑data_dic中的value(dict数据),指定key数据覆盖
# data_dic { data_key:{key:value}, ... }
def edit_datads_by_key(data_dic, data_keys, key, values):
    assert len(data_dic) == len(values), "error: len(data_dic) != len(values)"
    new_data_dic = copy.deepcopy(data_dic)
    
    for data_key, value in zip(data_keys, values):
        new_data_dic[data_key][key] = value
        
    return new_data_dic


# car_comps组合
# car_names 指定key排序
def parse_comps(datads, data_keys, comp='force'):
    minors = parse_datads_by_key(datads, data_keys, 'minor')
    comps = []
    for minor in minors:
        if minor=='any':
            comps.append(comp)
        else:
            comps.append(comp+'_'+minor)
            
    return comps


# 根据质量数据,计算绕质心的转动惯量
def parse_I_center(mass_data):

    mass = mass_data['mass']
    x,y,z = mass_data['loc']
    ixx = mass_data['ixx'] - mass*(z**2+y**2)
    iyy = mass_data['iyy'] - mass*(z**2+x**2)
    izz = mass_data['izz'] - mass*(x**2+y**2)
    return [ixx, iyy, izz]


# ------------------------------------------------
# ---dict calc---

# dict处理, 获取字典指定位置的数据, 字典数据需均为list
def parase_dic_loc(result_dic, loc):
    new_data = {}
    for key in result_dic:
        new_data[key] = result_dic[key][loc]
    return new_data


# dict处理, 字典中均为数值, dic1 - dic2
def parase_dic_sub(dic1, dic2):
    new_dic = {}
    for key in dic1:
        new_dic[key] = dic1[key] - dic2[key]
    return new_dic


# dict处理, 舍去loc之前数据, 并减去loc位置的数据
def parase_dic_init_loc(dic1, loc):
    new_dic = {}
    for key in dic1:
        line = dic1[key]
        value = line[loc]
        new_dic[key] = [v-value for v in line[loc:]]

    return new_dic


# dict处理, 对指定key中的list数据求绝对值
def parase_dic_abs_key(dic1, key):
    dic2 = copy.deepcopy(dic1)
    dic2[key] = [abs(v) for v in dic2[key]]
    return dic2


# 列表中不放dict, 仅存放list | str | int | float
def round_list(data, new_data, n):
    for loc, line in enumerate(data):
        if isinstance(line, list):
            new_data.append([])
            round_list(line, new_data[loc], n)
            continue
        if isinstance(line, str):
            new_data.append(line)
        else:
            new_data.append(round(line, n))
    
    return new_data
            

# 对字典中数值进行round, 存放 dict | list | int | str | float
# 列表中不放dict, 仅存放list | str | int | float
def round_data_dict(data_dic, new_dic, n):
    for key in data_dic:
        v = data_dic[key]
        if isinstance(v, dict):
            new_dic[key] = round_data_dict(v, {}, n)
            continue
        
        if isinstance(v, str):
            new_dic[key] = data_dic[key]
            continue
        
        if isinstance(v, list):
            new_dic[key] = round_list(v, [], n)
            continue    
        
        new_dic[key] = round(v, n)
        
    return new_dic
        



def save_var(path, data):
    """
        保存变量数据
        path 变量存储路径
        data 数据
    """
    with open(path, 'wb') as f:
        pickle.dump(data, f)
    return None


def read_var(path):
    """
        读取变量存储数据
        path 目标数据路径
    """

    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data


# ------------------------------------------
# 测试
def test_var_read_and_save():
    test = {'a':[1,2,3],'b':'asdf'}
    save_var('temp.var', test)
    print(read_var('temp.var'))


if __name__ == '__main__':
    pass


