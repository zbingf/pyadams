"""
    通过TCP通信, 操作adams
    version： ADAMS 2017.1
"""

import os
import copy
import re
from pprint import pprint

from pyadams.call import tcplink
cmds_run = tcplink.cmds_run # 直接运行,未处理的多个命令行
cmd_send = tcplink.cmd_send


# ------------------------------------------------
# ------------------------------------------------
# --------------------self-------------------------
# ------------------------------------------------
# ------------------------------------------------

# CMD命令替换
def _cmd_replace(cmd_str, **param_dict):

    for key in param_dict:
        key1 = '#' + key + '#'
        cmd_str = cmd_str.replace(key1, param_dict[key])

    return cmd_str


# 字典数据转换, 字典不允许有list
def _dict_data_change(data):
    data = copy.deepcopy(data)
    for key in data:
        if isinstance(data[key], bool): # 优先先判断
            data[key] = 'yes' if data[key] else 'no'
            continue

        if isinstance(data[key], float) or isinstance(data[key], int):
            data[key] = str(data[key])
            continue
        
    return data


def _query_send(cmd):

    return cmd_send(cmd, type_in='query').decode()


def _str2list(str1):
    if ',' in str1:
        list1 = eval(str1)
        list1 = list(list1)
    else:
        list1 = [str1]
    return list1


# 装饰器
def _query_str2list(func):
    
    def new_func(*args, **kwargs):
        str1 = func(*args, **kwargs)
        return _str2list(str1)

    return new_func


# ------------------------------------------------
# ------------------------------------------------
# --------------------SET-------------------------
# ------------------------------------------------
# ------------------------------------------------

# 添加数据库
CMD_ADD_CDB = """
acar toolkit database add &
 database_name="#cdb_name#" &
 database_path="#cdb_path#"
"""

# 添加数据库
def set_add_cdb(cdb_name, cdb_path):
    new_cmd = _cmd_replace(CMD_ADD_CDB, cdb_name=cdb_name, cdb_path=cdb_path)
    cmds_run(new_cmd)
    return None


CMD_DEFAULT_CDB = """
acar toolkit database default writable &
 database_name="#cdb_name#"
"""

# 设置默认数据库
def set_default_cdb(cdb_name):
    new_cmd = _cmd_replace(CMD_DEFAULT_CDB, cdb_name=cdb_name)
    cmds_run(new_cmd)
    return None


# # 打开asy总装配
# def set_open_asy(asy_path):
#     new_cmd = _cmd_replace(, asy_path=asy_path)
#     cmds_run(new_cmd)
#     return None


CMD_CLOSE_ASY = """
acar files assembly close assembly_name=#asy_name#
"""
# 关闭asy总装配
def set_close_asy(asy_name):
    new_cmd = _cmd_replace(CMD_CLOSE_ASY, asy_name=asy_name)
    cmds_run(new_cmd)
    return None


# ------------------------------------------------
# ------------------------------------------------

CMD_SPRING = """
acar standard_interface spring &
 spring=#name_full# &
 property_file="#path#" &
 user_value=#value# &
 value_type=#type# &
 symmetric=#symmetric# 
"""

# 解析spring命令,输出cmd
def parse_spring(data):

    return _cmd_replace(CMD_SPRING, **_dict_data_change(data))


# 设置spring
def set_spring(data):
    """
        设置ac_spring
        data {
            'length': 255,
            'minor': 'rear',
            'name_full': '.asy.sub.nsr_spring',
            'path': 'spring_path',
            'req_name': 'spring_data',
            'symmetric': True,
            'type': 'installed_length', 'preload',
            'value': 240.0
            }
    """
    new_cmd = parse_spring(data)
    # new_cmd = _cmd_replace(CMD_SPRING, **_dict_data_change(data))
    cmds_run(new_cmd)

    return None


# ------------------------------------------------
# ------------------------------------------------

CMD_BUMPSTOP = """
acar standard_interface bumpstop &
 bumpstop=#name_full# &
 property_file="#path#" &
 user_distance=#value# &
 distance_type=#type# &
 symmetric=#symmetric# 
"""


# 设置bumpstop
def set_bumpstop(data):
    """
        设置ac_bumpstop
    """
    new_cmd = _cmd_replace(CMD_BUMPSTOP, **_dict_data_change(data))
    cmds_run(new_cmd)

    return None


# ------------------------------------------------
# ------------------------------------------------


CMD_DAMPER = """
acar standard_interface damper &
 damper=#name_full# &
 property_file="#path#" &
 symmetric=#symmetric# 
"""


# 设置damper

def set_damper(data):
    """
        设置ac_damper
        data {
            'length': 511,
            'minor': 'front',
            'name_full': '.asy.sub.damper',
            'path': 'damper_path',
            'req_name': 'damper_data',
            'symmetric': True
            }
    """
    new_cmd = _cmd_replace(CMD_DAMPER, **_dict_data_change(data))
    cmds_run(new_cmd)

    return None




# ------------------------------------------------
# ------------------------------------------------
# --------------------QUERY-----------------------
# ------------------------------------------------
# ------------------------------------------------


# 数据是否存在
def _query_db_exist(obj_name):
    str1 = _query_send(f'db_exists("{obj_name}")')
    if int(str1):
        return True
    else:
        return False


_TEMP_DB_CHILDREN = 'TEMP_DB_CHILDREN'
# 指定类型检索子项
def _query_db_children(name_model_cur, obj_type):

    cmds_run(f'Variable create variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN} object_value=.{name_model_cur}')
    cmds_run(f'Variable modify variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN} object_value=(eval(db_children(.{name_model_cur}, "{obj_type}")))')
    str1 = _query_send(f'.{name_model_cur}.{_TEMP_DB_CHILDREN}')
    cmds_run(f'Variable delete variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN}')
    if str1 == 'No data from View':
        return False
    else:
        return _str2list(str1)


# 指定类型检索子项, 限制层数
def _query_db_descendants(name_model_cur, obj_type, a=1, l=2):

    cmds_run(f'Variable create variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN} object_value=.{name_model_cur}')
    cmds_run(f'Variable modify variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN} object_value=(eval(db_descendants(.{name_model_cur}, "{obj_type}", 1, 2)))')
    str1 = _query_send(f'.{name_model_cur}.{_TEMP_DB_CHILDREN}')
    cmds_run(f'Variable delete variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN}')
    if str1 == 'No data from View':
        return False
    else:
        return _str2list(str1)
    
    
# 指定类型检索子项, 并指定名称范围
# _query_db_children_filter(model_name, "request", "*velocity*")
def _query_db_children_filter(name_model_cur, obj_type, filter_str):

    cmds_run(f'Variable create variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN} \
             object_value=.{name_model_cur}')
    cmds_run(f'Variable modify variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN} \
             object_value=(eval(db_filter_name(db_children(.{name_model_cur}, "{obj_type}"), "{filter_str}")))')
           
    str1 = _query_send(f'.{name_model_cur}.{_TEMP_DB_CHILDREN}')
    cmds_run(f'Variable delete variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN}')
    if str1 == 'No data from View':
        return False
    else:
        return _str2list(str1)


# 获取当前界面的模型
def get_current_model():

    return _query_send('.gui.main.front.contents')[1:]


# 获取当前cdb数据库
def get_current_cdb():

    return _query_send('eval(cdb_get_write_default())')


# 获取当前运行路径
def get_cwd():

    return _query_send('getcwd()')



@_query_str2list
# 获取当前打开的模型
def get_current_asys():
    """获取当前打开的模型"""
    return _query_send('.acar.dboxes.dbox_fil_ass_clo.o_assembly_name.CHOICES')


# model质量获取
def get_model_mass(name_model_cur):

    str1 = _query_send(f'ac_info_mass(.{name_model_cur})')
    if str1 != "No data from View":
        return float(str1)
    else:
        return False


_parent_name = lambda name_full: '.'.join(name_full.split('.')[:-1])


# 获取sub的次特征
def get_sub_minors(model_name):
    # str1 = _query_send(f'DB_FILTER_NAME(db_children(.{model_name}, "variable"), "minor_role")')
    str1 = _query_send(f'DB_FILTER_NAME(db_descendants(.{model_name}, "variable", 1, 2), "minor_role")')
    sub2minor = {}
    for name in _str2list(str1):
        sub_name = _parent_name(name)
        sub2minor[sub_name] = _query_send(name)

    # {'.MDI_Demo_Vehicle.testrig': 'any', 
    # '.MDI_Demo_Vehicle.TR_Front_Suspension': 'front', 
    # '.MDI_Demo_Vehicle.TR_Rear_Suspension': 'rear', 
    # '.MDI_Demo_Vehicle.TR_Brake_System': 'any'}

    return sub2minor


# 根据子系统单元找子系统的minor
def get_sub_elem_minor(element_name):
    name = _parent_name(element_name)

    str1 = _query_send(f'DB_FILTER_NAME(db_descendants({name}, "variable", 1, 1), "minor_role")')
    minor = _query_send(str1)
    # print('--------', minor)
    return minor

# 获取路面z坐标(只用于仿真后)
def get_testrig_road_marker_z(model_name):

    testrig_name_full = '.' + model_name + '.testrig.ground.std_tire_ref'
    str1 = _query_send(f'{testrig_name_full}.loc')
    return float(_str2list(str1)[-1])

# print(get_testrig_road_marker_z(get_current_model()))


# ! ---------------
CMD_MASS_INFO = """
list_info aggregate_mass &
 model_name=.#model_name# &
 brief=on &
 write_to_terminal=off & 
 file_name="#path#"
"""

# 获取模型质量数据
# model_name = get_current_model()
# get_aggregate_mass(model_name)
def get_aggregate_mass(model_name):

    cur_dir = get_cwd()
    temp_path = os.path.join(cur_dir, 'temp_mass_info.txt')
    if os.path.exists(temp_path): os.remove(temp_path)
    new_cmd = _cmd_replace(CMD_MASS_INFO, model_name=model_name, path=temp_path)
    cmds_run(new_cmd)

    with open(temp_path, 'r') as f:
        lines = f.read().lower().split('\n')

    # print(lines)
    mass_data = {}
    list1 = ['mass', 'ixx', 'iyy', 'izz', 'ixy', 'iyz', 'izx']
    for line in lines:
        loc_obj = re.match(r'.*location\s*:\s*(\S+),\s*(\S+),\s*(\S+).*', line)
        ori_obj = re.match(r'.*orientation\s*:\s*(\S+),\s*(\S+),\s*(\S+).*', line)

        for name in list1:
            obj1 = re.match(f'.*{name}\s*:\s*(\S+)\s*.*', line)
            if obj1: mass_data[name] = obj1.group(1)
            
        if loc_obj: mass_data['loc'] = loc_obj.groups()
        if ori_obj: mass_data['ori'] = ori_obj.groups()

    for key in mass_data:
        if isinstance(mass_data[key], str):
            mass_data[key] = float(mass_data[key])
        else:
            mass_data[key] = [float(v) for v in mass_data[key]]
    # print(mass_data)
    mass_data['model_name'] = model_name
    return mass_data


# 通过filter获取指定request
def get_request_by_filter(model_name, filter_str):
    
    return _query_db_children_filter(model_name, "request", filter_str)


# ------------------------------------------------
# ------------------------------------------------
# --------------------QUERY-MODEL-----------------
# ------------------------------------------------
# ------------------------------------------------

# !获取数据
# model_name 模型名称
# func_names 函数, func_names(model_name) 获取model_name模型下的指定name_fulls(list)
# func_get_data 函数, func_get_data(name_full) 获取单个name_full的数据
def _get_model_obj_data(model_name, func_names, func_get_data):
    data = {}
    name_fulls = func_names(model_name)
    if not name_fulls: return False
    for name_full in name_fulls:
        if '.' in name_full:
            # print(name_full)
            data[name_full] = func_get_data(name_full)

    return data


# -------------------------------------------
# ---spring---

# 根据model_name(开头无'.'), 获取spring名称
def get_model_nspring_names(model_name):

    return _query_db_children(model_name, "ac_spring")


# 根据spring全称, 获取spring数据
def get_nspring_data(spring_name_full):
    value = _query_send(f'{spring_name_full}.user_value.DATAS')
    spring_path = _query_send(f'{spring_name_full}.property_file.DATAS')
    value_type = _query_send(f'{spring_name_full}.value_type.DATAS')
    symmetric = False if _query_db_exist(f'{spring_name_full}.assymmetric.DATAS') else True
    length = float(_query_send(f'DM({spring_name_full}.i_marker, {spring_name_full}.j_marker)'))
    # req_name = _query_send(f'{spring_name_full}.request.result_name.DATAS')

    minor = get_sub_elem_minor(spring_name_full)

    req_name = spring_name_full.split('.')[-1]+'_data'


    return {'value':float(value), 'path':spring_path, 'symmetric':symmetric, 
        'type':value_type, 'name_full':spring_name_full, 'req_name':req_name, 
        'length':length, 'minor': minor}



# 根据model_name(开头无'.'), 获取弹簧所有数据
def get_model_nspring_datas(model_name):

    return _get_model_obj_data(model_name, get_model_nspring_names, get_nspring_data)



# -------------------------------------------
# ---bumpstop---

# 根据model_name(开头无'.'), 获取bumpstop名称
def get_model_bumpstop_names(model_name):

    return _query_db_children(model_name, "ac_bumpstop")


# 根据bumpstop全称, 获取数据
def get_bumpstop_data(bumpstop_name_full):
    value = _query_send(f'{bumpstop_name_full}.user_distance.DATAS')
    distance_type = _query_send(f'{bumpstop_name_full}.distance_type.DATAS')
    file_path = _query_send(f'{bumpstop_name_full}.property_file.DATAS')
    symmetric = False if _query_db_exist(f'{bumpstop_name_full}.assymmetric.DATAS') else True

    return {'value':float(value), 'type':distance_type, 'path':file_path, 
        'symmetric':symmetric, 'name_full':bumpstop_name_full}


# 根据model_name(开头无'.'), 获取所有bumpstop数据
def get_model_bumpstop_datas(model_name):

    return _get_model_obj_data(model_name, get_model_bumpstop_names, get_bumpstop_data)


# ---------------------------------------------
# ---rebuound---

# 根据model_name(开头无'.'),获取rebound名称
def get_model_reboundstop_names(model_name):

    return _query_db_children(model_name, "ac_reboundstop")


# 根据rebound全称,获取数据
def get_reboundstop_data(reboundstop_name_full):

    return get_bumpstop_data(reboundstop_name_full)


# 根据model_name(开头无'.'),获取所有reboundstop数据
def get_model_reboundstop_data(model_name):
    
    return _get_model_obj_data(model_name, get_model_reboundstop_names, get_reboundstop_data)


# -------------------------------------------
# ---damper---

# 根据model_name(开头无'.'),获取damper名称
def get_model_damper_names(model_name):

    return _query_db_children(model_name, "ac_damper")


# 根据damper全称,获取damper数据
def get_damper_data(name_full):
    
    path = _query_send(f'{name_full}.property_file.DATAS')
    symmetric = False if _query_db_exist(f'{name_full}.assymmetric.DATAS') else True
    length = float(_query_send(f'DM({name_full}.i_marker, {name_full}.j_marker)'))
    # req_name = _query_send(f'{name_full}.request.result_name.DATAS')
    minor = get_sub_elem_minor(name_full)
    req_name = name_full.split('.')[-1]+'_data'

    return {'path':path, 'symmetric':symmetric, 
        'name_full':name_full, 'req_name':req_name, 
        'length':length, 'minor':minor}


# 根据model_name(开头无'.'),获取所有damper数据
def get_model_damper_data(model_name):
    
    return _get_model_obj_data(model_name, get_model_damper_names, get_damper_data)


# -------------------------------------------
# ---tire---

# 获取model_name(开头无'.')里的ac_tire类型name(全称)
def get_model_tire_names(model_name):

    return _query_db_children(model_name, "ac_tire")


# 根据ac_tire类型name(全称),获取tire数据
def get_tire_data(name_full):

    minor = get_sub_elem_minor(name_full)
    path = _query_send(f'{name_full}.property_file')

    center_loc = _query_send(f'{name_full}.i_marker')
    # .MDI_Demo_Vehicle.TR_Rear_Tires.whl_wheel.loc
    center_loc = _str2list(_query_send(f'{_parent_name(center_loc)}.loc'))
    center_loc = [round(float(v), 2) for v in center_loc]

    req_name = name_full.split('.')[-1]+'_tire_forces'

    return {'path':path, 'name_full':name_full, 'loc':center_loc,
        'req_name':req_name, 'minor':minor}

        
# 获取model_name(开头无'.')里所有的tire数据
def get_model_tire_data(model_name):

    return _get_model_obj_data(model_name, get_model_tire_names, get_tire_data)

# print(get_model_tire_data(get_current_model()))


# ------------------------------------------------
# ------------------------------------------------
# --------------------SET-SIM---------------------
# ------------------------------------------------
# ------------------------------------------------

# 删除仿真
def set_analysis_del(sim_name):
    cmds_run(f"analysis delete analysis_name={sim_name}")
    return None


SIM_DIR_PREFIX = 'tcp_sim' # 仿真文件夹名称前缀

# 仿真计算-前置
# 创建仿真子文件夹
# 调整工作路径到子文件夹
def sim_pre_calc():
    cur_dir = get_cwd()
    n = 0
    while True:
        pass
        sim_dir = os.path.join(cur_dir, f'{SIM_DIR_PREFIX}_{n}')
        if not os.path.exists(sim_dir): break
        n += 1
    os.mkdir(sim_dir)

    # 路径变更
    sim_dir = sim_dir.replace('\\','/')
    if int(_query_send(f'chdir("{sim_dir}")')):
        # print('变更成功')
        return cur_dir, sim_dir
    else:
        return cur_dir, False


# 仿真计算-后置
# 调整工作路径回原路径
def sim_post_calc(cur_dir):

    cur_dir = cur_dir.replace('\\','/')
    _query_send(f'chdir("{cur_dir}")')


# car集成, 仿真
# data dict, 包含仿真工况(不能有list)
# sim_name_func 函数, 获取仿真名称 sim_name_func(sim_name)
# set_sim_func 函数, 运行指定仿真  set_sim_func(data)
# res_name_func 函数, 输出指定后处理路径 res_name_func(sim_dir, sim_name)
def sim_car(data, sim_name_func, set_sim_func, res_name_func):

    # sim_name = 'TEST1'
    sim_name = data['sim_name']
    
    # 前置
    cur_dir, sim_dir = sim_pre_calc()
    set_analysis_del(sim_name_func(sim_name))

    # 仿真
    set_sim_func(data)
    
    # 后置
    sim_post_calc(cur_dir)

    res_path = res_name_func(sim_dir, sim_name)
    
    result = {
        'cur_dir' : os.path.abspath(cur_dir),
        'sim_dir' : os.path.abspath(sim_dir),
        'res_path': os.path.abspath(res_path),
    }

    return result

# -------------------------------------------
# ---brake制动仿真---

_sim_name_brake = lambda sim_name: sim_name + '_brake'
_sim_res_brake = lambda sim_dir, sim_name: os.path.join(sim_dir, sim_name+'_brake.res')

CMD_SIM_CAR_BRAKE = """
acar analysis full_vehicle brake_test submit &
 assembly=.#model_name# &
 variant=default &
 output_prefix="#sim_name#" &
 end_time=#t_end# &
 number_of_steps=#step# &
 analysis_mode=#mode# &
 road_data_file="mdids://acar_shared/roads.tbl/2d_flat.rdf" &
 steering_input=#steer# &
 initial_velocity=#velocity# &
 velocity_units=km_hr &
 start_value=#t_start# &
 gear_position=#gear# &
 final_brake=#brake# &
 step_duration=#duration# &
 qstatic_prephase=yes &
 log_file=yes &
 comment=""
"""

# 运行仿真
def set_sim_car_full_brake(data):
    """
    仅运行制动仿真 full_vehicle brake_test
    data = {
        "model_name":
        "sim_name"  : 
        "t_end"  :
        "step"      :
        "mode"      :
        "steer"     :
        "velocity"  :
        "t_start":
        "gear"      :
        "brake" :
        "duration":
        }
    """
    # model_name
    # sim_name
    if "t_end" not in data: data["t_end"] = 10
    if "step" not in data: data["step"] = 1000
    if "mode" not in data: data["mode"] = 'interactive'
    if "steer" not in data: data["steer"] = 'locked'
    # velocity
    if "t_start" not in data: data["t_start"] = 1
    if "gear" not in data: data["gear"] = 1
    if "brake" not in data: data["brake"] = 100
    if "duration" not in data: data["duration"] = 0.6

    new_cmd = _cmd_replace(CMD_SIM_CAR_BRAKE, **_dict_data_change(data))
    # print(new_cmd)
    cmds_run(new_cmd)
    return None


# 完整car整车制动仿真
def sim_car_full_brake(data):

    return sim_car(data, _sim_name_brake, set_sim_car_full_brake, _sim_res_brake)


# -------------------------------------------
# ---static静平衡仿真---

_sim_name_full_static = lambda sim_name: sim_name + '_static'
_sim_res_full_static = lambda sim_dir, sim_name: os.path.join(sim_dir, sim_name+'_static.res')

CMD_SIM_CAR_STATIC_FULL = """
acar analysis full_vehicle static submit &
 assembly=#model_name# &
 variant=default &
 output_prefix="#sim_name#" &
 comment="" &
 analysis_mode=#mode# &
 road_data_file="mdids://acar_shared/roads.tbl/2d_ssc_flat.rdf" &
 gear_position=#gear# &
 static_task=#sim_type# &
 linear=no &
 log_file=yes
"""

# 运行仿真
def set_sim_car_full_static(data):
    """
    仅运行静平衡仿真 full_vehicle static
    data = {
        "model_name":
        "sim_name"  : 
        "mode"      :
        "gear"      :
        "sim_type"  :
        }
    """
    # model_name
    # sim_name
    if "mode" not in data: data["mode"] = 'interactive'
    if "gear" not in data: data["gear"] = 0
    if "sim_type" not in data: data["sim_type"] = 'settle'

    new_cmd = _cmd_replace(CMD_SIM_CAR_STATIC_FULL, **_dict_data_change(data))
    # print(new_cmd)
    cmds_run(new_cmd)
    return None


# 完整car静平衡仿真
def sim_car_full_static(data):

    return sim_car(data, _sim_name_full_static, set_sim_car_full_static, _sim_res_full_static)


# ------------------------------------------------
# ------------------------------------------------
# --------------------TEST------------------------
# ------------------------------------------------
# ------------------------------------------------

# 
def test_sub_minors():

    model_name = get_current_model()
    sub2minor = get_sub_minors(model_name)
    print(sub2minor)



def test_query_data():
    name_model_cur = get_current_model()
    cur_asys = get_current_asys()
    cur_cdb = get_current_cdb()
    cur_path = get_cwd()

    pprint(name_model_cur)
    pprint(cur_cdb)
    pprint(cur_path)
    pprint(cur_asys)
    pprint(get_model_mass(name_model_cur))


def test_query_element_model():

    name_model_cur = get_current_model()
    spring_data = get_model_nspring_datas(name_model_cur)
    # bumpstop_data = get_model_bumpstop_datas(name_model_cur)
    # reboundstop_data = get_model_reboundstop_data(name_model_cur)
    damper_data = get_model_damper_data(name_model_cur)

    if spring_data:
        print('spring exist')
        spr_name_full = list(spring_data.keys())[0]
        spring_data[spr_name_full]['symmetric'] = False
        set_spring(spring_data[spr_name_full])
        
    # if bumpstop_data:
    #     print('bumpstop exist')
    #     bump_name_full = list(bumpstop_data.keys())[0]
    #     bumpstop_data[bump_name_full]['symmetric'] = False
    #     set_bumpstop(bumpstop_data[bump_name_full])
    
    if damper_data:
        print('damper exist')
        dam_name_full = list(damper_data.keys())[0]
        damper_data[dam_name_full]['symmetric'] = False
        set_damper(damper_data[dam_name_full])

    pprint(spring_data)
    # pprint(bumpstop_data)
    # pprint(reboundstop_data)
    pprint(damper_data)
    


def test_sim_brake():
    model_name = get_current_model()
    data = {
        'model_name': model_name,
        'sim_name':'TEST1',
        'velocity':60
        }
    result = sim_car(data, _sim_name_brake, set_sim_car_full_brake, _sim_res_brake)
    pprint(result)


def test_sim_full_static():
    model_name = get_current_model()
    data = {
        "model_name": model_name,
        "sim_name" : "auto_sim",
    }
    result = sim_car_full_static(data)
    pprint(result)


# test_sim_brake()
# test_query_element_model()



def test():
    model_name = get_current_model()
    
    print(get_request_by_filter(model_name, '*velocity*'))
    
    return None



if __name__=='__main__':

    pass
    test()
    
    model_name = get_current_model()
    # set_default_cdb('T75E01')
    # set_close_asy(model_name)
    
    # test_query_element_model()
    # print(_query_db_descendants(model_name, "request"))

