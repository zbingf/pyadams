"""
    static only
    静态计算结果数据后处理
"""

# 标准库
import os.path
import getpass
import time
from pprint import pprint, pformat
import logging

# 自建库
# //

# ----------
logger = logging.getLogger('post_car_static')
logger.setLevel(logging.DEBUG)
is_debug = True

get_cur_time = lambda: time.strftime('%Y:%m:%d-%H:%M', time.localtime(time.time()))
USER_NAME = getpass.getuser()


""" result 格式
    result:
    {'Axles': {'TR_Front_Tires.til_wheel': 1,
               'TR_Front_Tires.tir_wheel': 1,
               'TR_Rear_Tires.til_wheel': 2,
               'TR_Rear_Tires.tir_wheel': 2},
     'I_center': [298688841.89, 1162890925.9, 1341023809.23],
     'Ls': {'L-1-2': 2560.0},
     'Ws': {'W-1-TR_Front_Tires.tir_wheel': 1520.0,
            'W-2-TR_Rear_Tires.tir_wheel': 1594.0},
     'axle_num': 2,
     'm_center': [1482.05, -1.42, 415.45],
     'mass': 1527.68,
     'model_name': 'MDI_Demo_Vehicle',
     'tire_forces': {'TR_Front_Tires.til_wheel': 3159.3,
                     'TR_Front_Tires.tir_wheel': 3145.1,
                     'TR_Rear_Tires.til_wheel': 4345.73,
                     'TR_Rear_Tires.tir_wheel': 4331.3},
     'tire_locs': {'TR_Front_Tires.til_wheel': [267.0, -760.0, 330.0],
                   'TR_Front_Tires.tir_wheel': [267.0, 760.0, 330.0],
                   'TR_Rear_Tires.til_wheel': [2827.0, -797.0, 350.0],
                   'TR_Rear_Tires.tir_wheel': [2827.0, 797.0, 350.0]},
     'tire_names': ['TR_Front_Tires.til_wheel',
                    'TR_Front_Tires.tir_wheel',
                    'TR_Rear_Tires.til_wheel',
                    'TR_Rear_Tires.tir_wheel']}
"""

len_max_dict_key = lambda dict1: max([len(key) for key in dict1])
str_list_e1 = lambda list1, prelist, istr='\n': istr.join([f'{p} : {v:0.3e} ' for p,v in zip(prelist, list1)])
str_dict_1 = lambda dict1, istr='\n': istr.join([f'{key.ljust(len_max_dict_key(dict1))}: {dict1[key]} ' for key in dict1])
_str_I_center = lambda I_center: str_list_e1(I_center, ['Ixx', 'Iyy' ,'Izz'], '\n')


#轮胎垂向力
def _str_tire_forces(result):

    tire_forces = result['tire_forces']
    Axles = result['Axles']
    lines = []
    names, values = [], []
    for loc, key in enumerate(tire_forces):
        # if loc%2==1: continue
        name = key.split('.')[-1]
        num = Axles[key]
        names.append(f'Axle{num}-{name}')
        values.append(tire_forces[key])

    len_max = max([len(name) for name in names])
    for name, value in zip(names, values):
        line = name.ljust(len_max) + f'(N): {value}'
        lines.append(line)

    return '\n'.join(lines)


# 轮胎中心
def _str_tire_locs(result):

    tire_locs = result['tire_locs']
    Axles = result['Axles']
    lines = []
    names, values = [], []
    for loc, key in enumerate(tire_locs):
        if loc%2==0: continue
        name = key.split('.')[-1]
        num = Axles[key]
        names.append(f'Axle{num}-{name}')
        values.append(tire_locs[key])

    len_max = max([len(name) for name in names])
    for name, value in zip(names, values):
        line = name.ljust(len_max) + f': {pformat(value)}'
        lines.append(line)

    return '\n'.join(lines)


# 轮距
def _str_Ws(result):
    Ws = result['Ws']
    new_keys, values = [], []
    for key in Ws:
        new_key = '-'.join(key.split('-')[:2])+ '-' + key.split('.')[-1]
        new_keys.append(new_key)
        values.append(Ws[key])

    len_max = max([len(key) for key in new_keys])
    lines = []
    for key, value in zip(new_keys, values):
        line = key.ljust(len_max) + f': {value}'
        lines.append(line)
    # print(lines)
    return '\n'.join(lines)


# 质心
def _str_m_center(result):

    m_center = result['m_center']
    x_line = f'X :{m_center[0]:10} (距离第1轴)'
    y_line = f'Y :{m_center[1]:10}'
    z_line = f'Z :{m_center[2]:10} (离地高)'
    return '\n'.join([x_line, y_line, z_line])


# 后处理
POST_STATIC = {
    'model_name' : '模型名称',
    'mass' : '整车质量',
    'm_center' : '整车质心',
    'I_center' : '整车绕质心转动惯量',
    'Ls' : '轴距',
    'Ws' : '轮距',
    'axle_num' : '轴数',
    'tire_forces' : '轮胎垂向力',
    'tire_locs' : '轮胎中心坐标',
}



def post_car_static(result):
    """
        word 文档 需变更数据输出
        old_list = 
            ['$模型名称$', '$整车质量$', '$整车质心$', '$整车绕质心转动惯量$', 
            '$轴距$', '$轮距$', '$轴数$', '$轮胎垂向力$', '$轮胎中心坐标$']
        new_list = [...]
    """

    old_list, new_list = [], []
    for key in POST_STATIC:
        old_list.append('$' + POST_STATIC[key] + '$')
        if isinstance(result[key], str):
            str1 = result[key]
        elif key == 'm_center':
            str1 = _str_m_center(result)
        elif key == 'I_center':
            str1 = _str_I_center(result[key])
        elif key == 'Ls':
            str1 = str_dict_1(result[key])
        elif key == 'Ws':
            str1 = _str_Ws(result)
        elif key =='tire_forces':
            str1 = _str_tire_forces(result)
        elif key == 'tire_locs':
            str1 = _str_tire_locs(result)
        else:
            str1 = pformat(result[key])

        new_list.append(str1)


    return old_list, new_list



# ---------------------------
# record

def _csv_str_Ws(result):
    """
        轮距数据处理
    """
    data = result['Ws']
    # print(data)
    new_Ws = {}
    for key in data:
        str_num = key.split('-')[1]
        if str_num not in new_Ws: new_Ws[str_num] = []
        new_Ws[str_num].append(data[key])
    # print(new_Ws)
    lines = []
    for num in new_Ws:
        v_mean = sum(new_Ws[num])/len(new_Ws[num])
        line = f'A{num}[{v_mean}]'
        lines.append(line)

    return ';'.join(lines)


def csv_post_static(result):
    old_list, new_list = [], []
    for key in POST_STATIC:
        if key == 'model_name':
            str1 = result[key]
            old_list.append(POST_STATIC[key])
        
        elif key == 'mass':
            str1 = str(result[key])
            old_list.append(POST_STATIC[key])

        elif key == 'm_center':
            str1 = ','.join([str(v) for v in result[key]])
            old_list.append('x(距第1轴),y,z(离地高)')

        elif key == 'I_center':
            str1 = ','.join([str(v) for v in result[key]])
            old_list.append('Ixx,Iyy,Izz')

        elif key == 'Ls':
            dict1 = result[key]
            str1 = ';'.join([str(dict1[key1]) for key1 in dict1])
            old_list.append(POST_STATIC[key])

        elif key == 'Ws':
            str1 = _csv_str_Ws(result)
            old_list.append(POST_STATIC[key])

        else:
            continue

        new_list.append(str1)

    # print(old_list)
    # print(new_list)
    
    old_list.append('时间')
    new_list.append(get_cur_time())
    
    old_list.append('用户')
    new_list.append(USER_NAME)

    old_line = ','.join(old_list)
    new_line = ','.join(new_list)

    return old_line, new_line


def csv_post_static_start(csv_path, result):

    r_strs = csv_post_static(result)
    # print(r_strs)
    with open(csv_path, 'w') as f:
        f.write('\n'.join(r_strs))
        f.write('\n')


def csv_post_static_append(csv_path, result):
    r_strs = csv_post_static(result)
    with open(csv_path, 'a') as f:
        f.write(r_strs[-1])
        f.write('\n')


def csv_post_static_print(path, result):
    """
        static 仿真结果数据记录到csv文件
    """
    if os.path.exists(path):
        csv_post_static_append(path, result)
        if is_debug: logger.debug("record vehicle data, append")
    else:
        csv_post_static_start(path, result)
        if is_debug: logger.debug("record vehicle data, new file write")



# ------------------------------------------------
# --------------------TEST------------------------

def test_cur_static_word():
    import office_docx
    WordEdit = office_docx.WordEdit

    # word文档编辑 测试
    word_path = r'post_car_static.docx'
    new_word_path = r'new_post_static.docx'

    # result = tcp_car.main_cur_static()
    # pprint(result)
    # old_list, new_list = post_car_static(result)

    # word_obj = WordEdit(word_path)
    # word_obj.replace_edit(old_list, new_list)
    # word_obj.save(new_word_path)
    # word_obj.close()

def test_cur_static_csv():
    pass
    # import tcp_car
    # RECORD_PATH = tcp_car.json_read(tcp_car.ACAR_FULL_STATIC_PATH)['record_path']
    # csv_path = 'post_car_static.csv'
    csv_post_static_print(RECORD_PATH, result)




if __name__=='__main__':
    pass
    test_cur_static_csv()
