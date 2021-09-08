"""
    leafspring 2019版 编辑
    针对ADAMS 2019版 钢板弹簧工具箱 - adm文件更改及后处理计算
        

"""
import re
from pyadams.call import admrun

STR_BUSHING = '''
!                       adams_view_name='BUSHING_#b_id#'
BUSHING/#b_id#
, I = #i_id#
, J = #j_id#
, C = #c_x#, #c_y#, #c_z#
, K = #k_x#, #k_y#, #k_z#
, CT = #ct_x#, #ct_y#, #ct_z#
, KT = #kt_x#, #kt_y#, #kt_z#
!
'''

def read_leafspring_adm(adm_path): # 读取leafspring adm文件,并解析分离 chassis bushing
    # 读取文档
    with open(adm_path, 'r') as f:
        file_lines = f.read().split('\n')

    # 区分 bushing
    lines_new = []
    line_cb = [] # ChassisBusing

    isChassisBusing = False
    for line in file_lines:
        
        if 'START ACHASSIS BUSHINGS' in line.upper():
            isChassisBusing = True

        if 'END ACHASSIS BUSHINGS' in line.upper():
            line_cb.append(line)
            isChassisBusing = False
            continue

        if isChassisBusing:
            line_cb.append(line)
        else:
            lines_new.append(line)        

    return lines_new,line_cb

def insert_lines_end(lines,lines_tar):
    # 结尾插入数据
    for n in range(1,100):
        line = lines[-n]
        if 'END' == re.sub('\s','', line).upper():
            isInsert = True
            n_deinsert = -n
            break

    return lines[:n_deinsert] + lines_tar + lines[n_deinsert:]

def parse_chassis_bushing(line_cb):

    isStart = False
    n_loc = 0
    bushings = []

    # 去空格, 拼接行
    new_lines_cb = []
    for line in line_cb:
        line_1 = re.sub('\s','',line)
        if line_1 :
            if line_1[0] == ',':
                new_lines_cb[-1] += line_1
            else:
                new_lines_cb.append(line_1)
    
    # print(new_lines_cb)

    for line in new_lines_cb:
        if 'adams_view_name=' in line.lower():
            isStart = True
            if n_loc != 0:
                bushing_dic['values'] = values
                bushings.append(bushing_dic)

            bushing_dic = {}
            n_loc += 1
        
        if isStart:
            if 'FIELD' in line:
                values = []

                id_obj = re.match('.*I=(\d*),J=(\d*),.*', line)

                if id_obj:
                    i_id = int(id_obj.group(1))
                    j_id = int(id_obj.group(2))
                    bushing_dic['i_id'] = i_id
                    bushing_dic['j_id'] = j_id

            if 'ARRAY' in line:
                if line[0] == '!':
                    continue
                values.append([float(v) for v in line.split('=')[-1].split(',') if v])
                # ! Bushing setup array format
                # ! ARRAY/ID,NUM=stiffness_type, stiffness_value, stiffness_scale
                # ! ,damping_type, damping_value, damping_scale
                # ! ,preload, displacement_offset, displacement_scale, velocity_offset, velocity_scale
    bushing_dic['values'] = values
    bushings.append(bushing_dic)
    # pprint.pprint(bushings)
    return bushings

def create_bushing(bushings, param_in=None):

    b_id_init = 9901000
    lines_bushing = []
    for n, bushing in enumerate(bushings):
        values = bushing['values']
        b_id = b_id_init + n
        i_id = bushing['i_id']
        j_id = bushing['j_id']
        
        if param_in==None:
            k_x = values[0][1]
            k_y = values[1][1]
            k_z = values[2][1]

            c_x = values[0][4]
            c_y = values[1][4]
            c_z = values[2][4]

            kt_x = values[3][1]
            kt_y = values[4][1]
            kt_z = values[5][1]

            ct_x = values[3][4]
            ct_y = values[4][4]
            ct_z = values[5][4]

        else:
            k_x = param_in['k_x']
            k_y = param_in['k_y']
            k_z = param_in['k_z']

            c_x = param_in['c_x']
            c_y = param_in['c_y']
            c_z = param_in['c_z']

            kt_x = param_in['kt_x']
            kt_y = param_in['kt_y']
            kt_z = param_in['kt_z']

            ct_x = param_in['ct_x']
            ct_y = param_in['ct_y']
            ct_z = param_in['ct_z']


        new_str = STR_BUSHING.replace('#b_id#', str(b_id))
        new_str = new_str.replace('#i_id#', str(i_id))
        new_str = new_str.replace('#j_id#', str(j_id))

        new_str = new_str.replace('#c_x#', str(c_x))
        new_str = new_str.replace('#c_y#', str(c_y))
        new_str = new_str.replace('#c_z#', str(c_z))
        
        new_str = new_str.replace('#k_x#', str(k_x))
        new_str = new_str.replace('#k_y#', str(k_y))
        new_str = new_str.replace('#k_z#', str(k_z))

        new_str = new_str.replace('#ct_x#', str(ct_x))
        new_str = new_str.replace('#ct_y#', str(ct_y))
        new_str = new_str.replace('#ct_z#', str(ct_z))

        new_str = new_str.replace('#kt_x#', str(kt_x))
        new_str = new_str.replace('#kt_y#', str(kt_y))
        new_str = new_str.replace('#kt_z#', str(kt_z))

        lines_bushing.append(new_str)

        # print(new_str)

    return lines_bushing

def del_senser_by_id(lines, sensor_ids):

    is_sensor_start = False
    new_lines = []
    for line in lines:
        if 'SENSOR' in line.upper():
            id_obj = re.match('SENSOR/(\d+).*', line.upper())
            if id_obj:
                cur_id = id_obj.group(1)
                if int(cur_id) in sensor_ids:
                    is_sensor_start = True
                    continue

        if is_sensor_start:
            if line[0] != ',':
                is_sensor_start = False
                new_lines.append(line)
            continue
        
        new_lines.append(line)

    return new_lines

def main_edit_adm_leafspring(adm_path, new_adm_path, param_in=None):  # 主程序
    
    new_adm_path_1 = new_adm_path[:-4]+'_1.adm'

    lines_new, line_cb = read_leafspring_adm(adm_path)

    bushings_param = parse_chassis_bushing(line_cb)
    lines_bushing = create_bushing(bushings_param, param_in)

    # 到达设计状态
    lines_file = insert_lines_end(lines_new, lines_bushing)

    # 到达指定位置
    lines_file_1 = del_senser_by_id(lines_file, [1,2,3])

    str_new = '\n'.join(lines_file)
    with open(new_adm_path, 'w') as f:
        f.write(str_new)

    str_new = '\n'.join(lines_file_1)
    with open(new_adm_path_1, 'w') as f:
        f.write(str_new) 

    return new_adm_path, new_adm_path_1  # 设计状态, 目标状态

def test_run():

    # import pprint

    adm_path = r'D:\document\ADAMS\example_tempBuildFiles\example_temp_leaf.adm'
    new_adm_path = adm_path[:-4]+'edit_new.adm'

    param_in = {
        'k_x':10000,
        'k_y':10000,
        'k_z':10000,

        'c_x':10,
        'c_y':10,
        'c_z':10,

        'kt_x':500000,
        'kt_y':500000,
        'kt_z':1000,

        'ct_x':10,
        'ct_y':10,
        'ct_z':1,
    }

    # main_edit_adm_leafspring(adm_path, new_adm_path, param_in=None)
    new_adm_path, new_adm_path_1 = main_edit_adm_leafspring(adm_path, new_adm_path, param_in=param_in)

    res_path   = admrun.admrun(new_adm_path, 100, 60, version='2019')
    res_path_1 = admrun.admrun(new_adm_path_1, 100, 60, version='2019')

    req_path   = res_path[:-3]+'req'
    req_path_1 = res_path[:-3]+'req'

    print(req_path)
    print(req_path_1)




if __name__ == '__main__':

    test_run()

    
    # pprint.pprint()
    # # print(lines_new)