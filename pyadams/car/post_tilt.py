"""
    静侧翻台架计算结果后处理
    
    目标文件:
        adams/car result文件后处理
"""

# ===================================
from pyadams import datacal
from pyadams.file import result
from pyadams.file import file_edit, office_docx
DataModel = result.DataModel

# ===================================
import math, os
import time
import copy
import pprint
import matplotlib.pyplot as plt
import os.path

# ===================================
LEFT = 'left'               # 左翻
RIGHT = 'right'             # 右翻

plt.rcParams['savefig.dpi'] = 500
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ===================================

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


def get_tilt_result_data(res_path): # 读取数据
    
    reqs  = ['table_angle']
    comps = ['table_angle']

    dataobj = DataModel('post_tilt')
    dataobj.new_file(res_path, 'tilt')
    dataobj['tilt'].set_reqs_comps(reqs, comps)
    dataobj['tilt'].read_file()
    dataobj['tilt'].set_line_ranges([4,None])
    dataobj['tilt'].set_select_channels(None)

    table_angle = dataobj['tilt'].get_data()[0]
    table_angle = [value/math.pi*180 for value in table_angle] # 弧度转角度 deg

    reqs_tire, comps_tire = get_tire_normal_reqcomp(dataobj['tilt'])
    dataobj['tilt'].set_reqs_comps(reqs_tire, comps_tire)
    dataobj['tilt'].read_file(isReload=None)
    data2 = dataobj['tilt'].get_data()
    data2 = [[value/9.8 for value in line] for line in data2] # N 转 kg

    left_res = {'req':[],'comp':[],'data':[]}
    right_res = {'req':[],'comp':[],'data':[]}

    for req, comp, line in zip(reqs_tire, comps_tire, data2):
        if 'til' == req[:3]:
            left_res['req'].append(req)
            left_res['comp'].append(comp)
            left_res['data'].append(line)
        else:
            right_res['req'].append(req)
            right_res['comp'].append(comp)
            right_res['data'].append(line)

    return table_angle, left_res, right_res  # 单位 deg, kg


def get_tilt_side(table_angle, left_res, right_res):
    """
        left_res = {'req':[],'comp':[],'data':[]}
        right_res = {'req':[],'comp':[],'data':[]}
    """
    value_start = 0
    value_end   = 0
    for line in left_res['data']:
        value_start += line[0]
        value_end   += line[-1]

    if math.cos(max(table_angle)*math.pi/180)*value_start-value_end > 0:
        # 右翻转
        tilt_direction = RIGHT
        ourter_res = left_res
        inner_res  = right_res

    else:
        tilt_direction = LEFT
        ourter_res = right_res  
        inner_res  = left_res

    return tilt_direction, ourter_res, inner_res


def get_table_angle_loc(table_angle, angles):
    """
        默认 table_angle 单调递增
    """

    locs = []
    for target_angle in angles:
        for loc, angle in enumerate(table_angle):
            if angle >= target_angle:
                locs.append(loc)
                break
        if angle < target_angle:
            str1 = f'未达到指定侧翻角:{target_angle} deg'
            # print(str1)
            # assert False, str1
            locs.append(loc)
    
    # print(locs)
    return locs


def get_target_res(table_angle, ourter_res, locs): # 获取指定点的数据

    keys = []

    target_res = {}
    for loc in locs:
        angle = table_angle[loc]
        keys.append(angle)

        target_res[angle] = {}
        ourter_full = 0
        for req, comp, line in zip(ourter_res['req'], ourter_res['comp'], ourter_res['data']):

            if comp in target_res[angle]:
                target_res[angle][comp] += line[loc]
            else:
                target_res[angle][comp] = line[loc]

            ourter_full += line[loc]

        target_res[angle]['ourter_full'] = ourter_full

    return keys, target_res


def get_table_angle(table_angle, ourter_res, mass_lift=50): # 外侧轮胎离地对应角度
    
    ourter_angle = {}
    keys = []
    for req, comp, line in zip(ourter_res['req'], ourter_res['comp'], ourter_res['data']):
        key = req+'.'+comp
        keys.append(key)
        ourter_angle[key] = None
        for loc, value in enumerate(line):
            if value <= mass_lift: # 小于数值kg则认为离地
                # print(value)
                ourter_angle[key] = table_angle[loc]
                break
        
        if ourter_angle[key] == None:
            ourter_angle[key] = table_angle[-1]

        ourter_angle['keys'] = keys

    ourter_angle['max'] = max([ourter_angle[key] for key in ourter_angle['keys']])
    # print(ourter_angle)

    return ourter_angle


def cal_estimate_vehicle_mass(inner_res, ourter_res): # 整车质量估计
    """
        return :
            {
                'normal_front': 642.6916660730025, 
                'normal_rear': 884.6857739900756, 
                'full': 1527.3774400630782, 
                'keys': ['normal_front', 'normal_rear', 'full']
            }
    """
    inner_res['data']
    ourter_res['data']

    def cal_one_side(res):
        mass_dic  = {}
        side_full = 0
        for req, comp, line in zip(res['req'], res['comp'], res['data']):
            if comp in mass_dic:
                mass_dic[comp] += line[0]
            else:
                mass_dic[comp] = line[0]

            
            side_full += line[0]
        mass_dic['full'] = side_full

        return mass_dic

    mass_outer = cal_one_side(inner_res)
    mass_inner = cal_one_side(ourter_res)
    mass_full = {}
    for key in mass_outer:
        mass_full[key] = mass_outer[key] + mass_inner[key]

    # print(mass_full)
    # mass_full['keys'] = ourter_res['comp'] + ['full']
    mass_full['keys'] = list(mass_outer.keys())

    return mass_full


def cal_tilt(res_path, target_angles): # 主计算函数
    """
        
        return :
        { 
          fig_path :  str ,
          inner_res : { comp : [ str.. ],  data : [[ float.. ]],  req : [ str.. ]},
          ourter_angle : { keys : [ str.. ],
                           max :  float ,
                           til_wheel_tire_forces.normal_front :  float ,
                           til_wheel_tire_forces.normal_rear :  float },
          ourter_res : { comp : [ str.. ],  data : [[ float.. ]],  req : [ str.. ]},
          res_path :  str ,
          table_angle : [ float.. ],
          target_keys : [ float.. ],
          target_res : {14.4999999999995: { normal_front :  float ,
                                            normal_rear :  float ,
                                            ourter_full :  float },
                        28.33974176151278: { normal_front :  float ,
                                             normal_rear :  float ,
                                             ourter_full :  float }},
          tilt_direction :  str ,
          vehicle_mass : { full :  float ,
                           keys : [ str.. ],
                           normal_front :  float ,
                           normal_rear :  float }
        }
    """
    res_path = os.path.abspath(res_path)

    table_angle, left_res, right_res = get_tilt_result_data(res_path)
    tilt_direction, ourter_res, inner_res = get_tilt_side(table_angle, left_res, right_res)
    locs = get_table_angle_loc(table_angle, target_angles)
    target_keys, target_res = get_target_res(table_angle, ourter_res, locs)

    mass_full = cal_estimate_vehicle_mass(inner_res, ourter_res)
    ourter_angle = get_table_angle(table_angle, ourter_res)

    for req, comp, line in zip(ourter_res['req'], ourter_res['comp'], ourter_res['data']):
        plt.plot(table_angle, line)

    if tilt_direction==LEFT:
        plt.title('左翻')
    else:
        plt.title('右翻')


    plt.legend(ourter_res['comp'])
    plt.xlabel('侧翻角度 deg')
    plt.ylabel('外出轮胎荷载 kg')
    fig_path = f'{res_path}_{tilt_direction}.png'
    plt.savefig(fig_path)
    plt.close()

    output_data = {
        'tilt_direction':tilt_direction,
        'table_angle':table_angle,
        'ourter_res':ourter_res,
        'inner_res':inner_res,
        'target_keys':target_keys,
        'target_res':target_res,
        'fig_path':fig_path,
        'vehicle_mass':mass_full,
        'ourter_angle':ourter_angle, # 离地角度
        'res_path':res_path,
    }

    return output_data


# ===================================
# pdf 文件生成

def pdf_mass(obj, output_data):

    vehicle_mass = output_data['vehicle_mass']
    mass_strs = []
    for key in vehicle_mass['keys']:
        value = vehicle_mass[key]
        if 'full' == key:
            str1 = '{:50} : {:12.2f} kg'.format('full_mass', value)
        elif 'key' != key:
            str1 = f'{key:50} : {value:12.2f} kg'
        else:
            continue
        mass_strs.append(str1)

    obj.add_paragraph('\n')
    obj.add_heading('质量数据估计', level=1, size=15)
    obj.add_paragraph('\n'.join(mass_strs))


def pdf_ourter_angle(obj, output_data):

    ourter_angle = output_data['ourter_angle']
    strs = []
    for key in ourter_angle['keys']:
        value = ourter_angle[key]
        str1 = f'{key:50} : {value:12.2f} deg'
        strs.append(str1)

    obj.add_paragraph('\n')
    obj.add_heading('各轮离地角度', level=1, size=15)
    obj.add_paragraph('\n'.join(strs))


# pdf-指定角度对应外侧轮荷
def pdf_target_angle(obj, output_data):
    """
        target_keys : [ float.. ],
        target_res : {14.50: { normal_front :  float ,
                                        normal_rear :  float ,
                                        ourter_full :  float },
                    28.34: { normal_front :  float ,
                                         normal_rear :  float ,
                                         ourter_full :  float }},
    """
    target_res  = output_data['target_res']
    target_keys = output_data['target_keys']
    strs = []
    for key in target_keys:
        str1 = '{} : {:0.2f} deg'.format('侧翻角度', float(key))
        strs.append(str1)

        key2s = list(target_res[key].keys())
        del key2s[key2s.index('ourter_full')]
        key2s.append('ourter_full')

        for key2 in key2s: # target_res[key]
            value = target_res[key][key2]
            if 'ourter_full' == key2:
                strs.append('='*70)
            str1  = f'{key2:50} : {value:12.2f} kg'
            strs.append(str1)

        strs.append('\n')

    obj.add_paragraph('\n')
    obj.add_heading('侧翻角度对应外侧轮荷', level=1, size=15)
    obj.add_paragraph('\n'.join(strs))

# pdf-侧翻方向
def pdf_tilt_direction(obj, output_data):

    tilt_direction = output_data['tilt_direction']
    obj.add_paragraph('\n')
    obj.add_heading(f'侧翻方向 : {tilt_direction}', level=1, size=20)

# pdf-侧翻图片
def pdf_figure(obj, output_data):

    fig_path = output_data['fig_path']
    fig_path = os.path.abspath(fig_path)
    obj.add_docx_figure(fig_path, '侧翻角-外侧轮荷', width=19)

# pdf-创建
def pdf_create(docx_path, output_data): # pdf创建

    res_path = output_data['res_path']

    docx_path = os.path.abspath(docx_path)
    res_name  = os.path.basename(res_path)

    obj = office_docx.DataDocx(docx_path)  # word编写
    obj.set_page_margin(x=1.27, y=1.27)

    page_one = {
        'title_main':'静侧翻稳定性',
        'title_minor':'--ADAMS/Car TILT',
        'file_paths':[res_name]
    }
    # pdf_cover_page(obj, page_one)
    obj.add_cover_page(page_one)
    obj.add_page_break()

    pdf_tilt_direction(obj, output_data)
    pdf_mass(obj, output_data)
    pdf_ourter_angle(obj, output_data)

    obj.add_page_break()
    pdf_target_angle(obj, output_data)

    obj.add_page_break()
    pdf_figure(obj, output_data)

    # 页眉
    title_png = os.path.split(os.path.realpath(__file__))[0] + '/template/docx_title.png'
    obj.add_header_figure(title_png)

    obj.save()
    
    # 转pdf
    pdf_path = office_docx.doc2pdf(docx_path)

    return pdf_path


# ===================================
# 测试

def test_cal_tilt():

    res_path = r'..\tests\car_post_tilt\test_up_tilt.res'
    res_path = r'..\tests\car_post_tilt\test_down_right_tilt.res'
    res_path = r'..\tests\car_post_tilt\test_1000_down_right_tilt.res'

    target_angles = [14, 28 , 35]

    output_data = cal_tilt(res_path, target_angles)

    print(datacal.str_view_data_type(output_data))  # 数据结构

    pdf_path = pdf_create(r'..\tests\car_post_tilt\test.docx', output_data)
    os.popen(pdf_path)



if __name__=='__main__':
    pass
    
    test_cal_tilt()
