"""
    通过TCP通信, 操作adams
    version： ADAMS 2017.1
"""

# 标准库
import os
import copy
import re
from pprint import pprint
import time
import logging


# 自建库
import tcp_link
cmd_send = tcp_link.cmds_run # 直接运行,未处理的多个命令行
query_send = tcp_link.cmd_send


# ----------
logger = logging.getLogger('auto')
logger.setLevel(logging.DEBUG)
is_debug = True


# ------------------------------------------------
# ------------------------------------------------
# --------------------self-------------------------
# ------------------------------------------------
# ------------------------------------------------

def _cmd_replace(cmd_str, **param_dict):
    """
        CMD命令替换
    """
    for key in param_dict:
        key1 = '#' + key + '#'
        cmd_str = cmd_str.replace(key1, param_dict[key])

    return cmd_str


def _dict_data_change(data):
    """
        字典数据转换, 字典不允许有list
    """
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

    return query_send(cmd, type_in='query').decode()


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

def set_add_cdb(cdb_name, cdb_path):
    """ 添加数据库 """
    new_cmd = _cmd_replace(CMD_ADD_CDB, cdb_name=cdb_name, cdb_path=cdb_path)
    cmd_send(new_cmd)
    return None


# 设置默认数据库
CMD_DEFAULT_CDB = """
acar toolkit database default writable &
 database_name="#cdb_name#"
"""

def set_default_cdb(cdb_name):
    """ 设置默认数据库 """
    new_cmd = _cmd_replace(CMD_DEFAULT_CDB, cdb_name=cdb_name)
    cmd_send(new_cmd)
    return None


CMD_CURRENT_MODEL = """
model display model_name=.#model_name# fit_to_view=yes
"""

def set_current_model(model_name):
    """切换当前模型"""
    new_cmd = _cmd_replace(CMD_CURRENT_MODEL, model_name=model_name)
    cmd_send(new_cmd)
    return None


# # 打开asy总装配
# def set_open_asy(asy_path):
#     new_cmd = _cmd_replace(, asy_path=asy_path)
#     cmd_send(new_cmd)
#     return None


CMD_CLOSE_ASY = """
acar files assembly close assembly_name=#asy_name#
"""

def set_close_asy(asy_name):
    """ 关闭asy总装配 """
    new_cmd = _cmd_replace(CMD_CLOSE_ASY, asy_name=asy_name)
    cmd_send(new_cmd)
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

def parse_spring(data):
    """ 解析spring命令,输出cmd """
    return _cmd_replace(CMD_SPRING, **_dict_data_change(data))


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
    cmd_send(new_cmd)

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

def set_bumpstop(data):
    """
        设置ac_bumpstop
    """
    new_cmd = _cmd_replace(CMD_BUMPSTOP, **_dict_data_change(data))
    cmd_send(new_cmd)

    return None


# ------------------------------------------------
# ------------------------------------------------


CMD_DAMPER = """
acar standard_interface damper &
 damper=#name_full# &
 property_file="#path#" &
 symmetric=#symmetric# 
"""

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
    cmd_send(new_cmd)

    return None



# ------------------------------------------------
# ------------------------------------------------
# --------------------QUERY-----------------------
# ------------------------------------------------
# ------------------------------------------------

def _query_db_exist(obj_name):
    """
        数据是否存在
    """
    str1 = _query_send(f'db_exists("{obj_name}")')
    if int(str1):
        return True
    else:
        return False


_TEMP_DB_CHILDREN = 'TEMP_DB_CHILDREN'

def _query_db_children(name_model_cur, obj_type):
    """
        指定类型检索子项
    """
    cmd_send(f'Variable create variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN} object_value=.{name_model_cur}')
    cmd_send(f'Variable modify variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN} object_value=(eval(db_children(.{name_model_cur}, "{obj_type}")))')
    str1 = _query_send(f'.{name_model_cur}.{_TEMP_DB_CHILDREN}')
    cmd_send(f'Variable delete variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN}')
    if str1 == 'No data from View':
        return False
    else:
        return _str2list(str1)


def _query_db_descendants(name_model_cur, obj_type, a=1, l=2):
    """
        指定类型检索子项, 限制层数
    """
    cmd_send(f'Variable create variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN} object_value=.{name_model_cur}')
    cmd_send(f'Variable modify variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN} object_value=(eval(db_descendants(.{name_model_cur}, "{obj_type}", 1, 2)))')
    str1 = _query_send(f'.{name_model_cur}.{_TEMP_DB_CHILDREN}')
    cmd_send(f'Variable delete variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN}')
    if str1 == 'No data from View':
        return False
    else:
        return _str2list(str1)
    
    
def _query_db_children_filter(name_model_cur, obj_type, filter_str):
    """
        指定类型检索子项, 并指定名称范围
        _query_db_children_filter(model_name, "request", "*velocity*")
    """

    cmd_send(f'Variable create variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN} \
             object_value=.{name_model_cur}')
    cmd_send(f'Variable modify variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN} \
             object_value=(eval(db_filter_name(db_children(.{name_model_cur}, "{obj_type}"), "{filter_str}")))')
           
    str1 = _query_send(f'.{name_model_cur}.{_TEMP_DB_CHILDREN}')
    cmd_send(f'Variable delete variable_name=.{name_model_cur}.{_TEMP_DB_CHILDREN}')
    if str1 == 'No data from View':
        return False
    else:
        return _str2list(str1)


def get_variable(var_name):
    """ varibale 数据获取"""
    return _query_send(var_name)


def get_current_model():
    """获取当前界面的模型"""
    return _query_send('.gui.main.front.contents')[1:]


def get_current_cdb():
    """ 获取当前cdb数据库 """
    return _query_send('eval(cdb_get_write_default())')


def get_cwd():
    """ 获取当前运行路径 """
    return _query_send('getcwd()')


@_query_str2list
def get_current_asys():
    """获取当前打开的模型"""
    return _query_send('.acar.dboxes.dbox_fil_ass_clo.o_assembly_name.CHOICES')


def get_model_mass(name_model_cur):
    """ model质量获取 """
    str1 = _query_send(f'ac_info_mass(.{name_model_cur})')
    if str1 != "No data from View":
        return float(str1)
    else:
        return False


_parent_name = lambda name_full: '.'.join(name_full.split('.')[:-1])


def get_sub_minors(model_name):
    """ 获取sub的次特征 """
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


def get_sub_elem_minor(element_name):
    """ 根据子系统单元找子系统的minor """

    name = _parent_name(element_name)

    str1 = _query_send(f'DB_FILTER_NAME(db_descendants({name}, "variable", 1, 1), "minor_role")')
    minor = _query_send(str1)
    # print('--------', minor)
    return minor


def get_testrig_road_marker_z(model_name):
    """ 获取路面z坐标(只用于仿真后) """

    testrig_name_full = '.' + model_name + '.testrig.ground.std_tire_ref'
    # str1 = _query_send(f'{testrig_name_full}.loc')
    # return float(_str2list(str1)[-1])
    #
    return get_marker_loc_global(testrig_name_full)[-1]

    # print(get_testrig_road_marker_z(get_current_model()))


# ! ---------------
CMD_MASS_INFO = """
list_info aggregate_mass &
 model_name=.#model_name# &
 brief=on &
 write_to_terminal=off & 
 file_name="#path#"
"""

def get_aggregate_mass(model_name):
    """
        获取模型质量数据
        model_name = get_current_model()
        get_aggregate_mass(model_name)

    """
    cur_dir = get_cwd()
    temp_path = os.path.join(cur_dir, 'temp_mass_info.txt')
    if os.path.exists(temp_path): os.remove(temp_path)
    new_cmd = _cmd_replace(CMD_MASS_INFO, model_name=model_name, path=temp_path)
    cmd_send(new_cmd)

    for n in range(50):
        if not os.path.exists(temp_path):
            time.sleep(0.2)
        else:
            break

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


def get_marker_loc_global(marker):
    """
        获取marker的全局坐标LOC
    """
    return _str2list(_query_send(f'loc_global({{0,0,0}}, {marker})'))


def get_marker_ori_global(marker):
    """
        获取marker在全局方向ORI
    """
    return _str2list(_query_send(f'ori_global({{0,0,0}}, {marker})'))    


def get_request_by_filter(model_name, filter_str):
    """
        通过filter获取指定request
    """
    return _query_db_children_filter(model_name, "request", filter_str)


def get_request_data_one(req):
    """
        request 数据获取
        REQUEST_TYPE 
            0: 'expr',
            4: 'force',
    """

    result = {}
    comp_names = _query_send(f'{req}.cnames')
    result_name = _query_send(f'{req}.results_name')

    req_type = _query_send(f'{req}.type')
    if int(req_type) == 0 : # expr
        # f2 = _query_send(f'{req}.f2')
        # f2 = _query_send(f'{req}.f2.type')
        exprs = []
        ref_objs = []
        for n in [1,2,3,4,5,6,7,8]:
            f_expr = _query_send(f'{req}.f{n}.exprs')
            if f_expr == 'No data from View': continue
            exprs.append(f_expr)
            ref_objs.append( _str2list(_query_send(f'{req}.f{n}.r_ref_objs')) )
            
        ref_objs_set = []
        for ref_obj in ref_objs:
            for ref_name in ref_obj:
                if ref_name not in ref_objs_set:
                    ref_objs_set.append(ref_name)
                    
        ref_dict = {}
        for ref_name in ref_objs_set:
            loc = get_marker_loc_global(ref_name)
            ori = get_marker_ori_global(ref_name)
            ref_dict[ref_name] = {'loc':loc, 'ori':ori}
            
            
        result.update({
            'type' : 'expr', 
            'exprs' : exprs,  # 表达式
            'ref_objs' : ref_objs, # 各表达式中的 marker
            'ref_dict' : ref_dict, # 各marker对应的坐标&方向
        })
        # print(ref_dict)

    if int(req_type) == 4: # force
        i_marker = _query_send(f'{req}.i')
        j_marker = _query_send(f'{req}.j')
        rm_marker = _query_send(f'{req}.rm')
        
        i_loc = get_marker_loc_global(i_marker)
        j_loc = get_marker_loc_global(j_marker)
        rm_loc = get_marker_loc_global(rm_marker)
        rm_ori = get_marker_ori_global(rm_marker)
        
        result.update({
            'type': 'force',
            'i_loc' : i_loc,
            'j_loc' : j_loc,
            'i_marker' : i_marker,
            'j_marker' : j_marker,
            'rm_marker' : rm_marker,
            'rm_ori' : rm_ori,
            'rm_loc' : rm_loc,
        })
        
    result.update({
        'result_name' : result_name,
        'comp_names' : comp_names,
        })

    return result



# ------------------------------------------------
# ------------------------------------------------
# --------------------判断及设置-------------------
# ------------------------------------------------
# ------------------------------------------------

def is_current_model_event_class(event_class='__MDI_SDI_TESTRIG'):
    """
        当前模型界面判断 event_class类型
        is_main_model : 是否为主模型
        is_event_class: 是否为目标台架类型
        cur_model_name: 当前模型名称
        model_name    : 主模型名称
    """
    # 前置判断
    model_name = get_current_model()
    cur_model_name = model_name
    is_main_model, is_event_class = True, True

    if is_debug: logger.debug(f"model_name : {model_name}")
    if '.' in model_name: is_main_model = False
    model_name = model_name.split('.')[0]

    cur_event_class = get_variable(f'.{model_name}.event_class').upper()
    if is_debug: logger.debug(f"event_class : {cur_event_class}")
    if event_class != cur_event_class: is_event_class = False

    return is_main_model, is_event_class, cur_model_name, model_name


def set_current_asy_with_event_class(event_class='__MDI_SDI_TESTRIG'):
    """
        Car模块 设置当前asy装配模型
            + 指定 event_class 台架类型
    """
    is_main_model, is_event_class, cur_model_name, model_name = is_current_model_event_class(event_class)
    
    if not is_event_class:
        if is_debug: logger.error(f"current model not asy SDI : {model_name}")
        return False

    if not is_main_model and is_event_class:
        if is_debug: logger.info(f"change current model {cur_model_name} to {model_name}")
        set_current_model(model_name)

    return True


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


def get_tire_data(name_full):
    """ 根据ac_tire类型name(全称),获取tire数据 """
    minor = get_sub_elem_minor(name_full)
    path = _query_send(f'{name_full}.property_file')

    center_loc = _query_send(f'{name_full}.i_marker')
    # .MDI_Demo_Vehicle.TR_Rear_Tires.whl_wheel.loc
    center_loc = _str2list(_query_send(f'{_parent_name(center_loc)}.loc'))
    center_loc = [round(float(v), 2) for v in center_loc]

    req_name = name_full.split('.')[-1]+'_tire_forces'

    return {'path':path, 'name_full':name_full, 'loc':center_loc,
        'req_name':req_name, 'minor':minor}

        
def get_model_tire_data(model_name):
    """ 获取model_name(开头无'.')里所有的tire数据 """
    return _get_model_obj_data(model_name, get_model_tire_names, get_tire_data)

# print(get_model_tire_data(get_current_model()))


# -------------------------------------------
# ---ac_susp_tire---
# 与tire一致

def get_model_sus_tire_names(model_name):

    return _query_db_children(model_name, "ac_susp_tire")

def get_model_sus_tire_data(model_name):
    """ 获取model_name(开头无'.')里所有的tire数据 """
    return _get_model_obj_data(model_name, get_model_sus_tire_names, get_tire_data)



# ------------------------------------------------
# ------------------------------------------------
# --------------------SET-SIM---------------------
# ------------------------------------------------
# ------------------------------------------------


def set_analysis_del(sim_name):
    """
        删除仿真
    """
    cmd_send(f"analysis delete analysis_name={sim_name}")
    return None


SIM_DIR_PREFIX = 'tcp_sim' # 仿真文件夹名称前缀


def sim_pre_calc():
    """
        仿真计算-前置
        创建仿真子文件夹
        调整工作路径到子文件夹
    """

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



def sim_post_calc(cur_dir):
    """
        仿真计算-后置
        调整工作路径回原路径
    """
    cur_dir = cur_dir.replace('\\','/')
    _query_send(f'chdir("{cur_dir}")')



def sim_car(data, sim_name_func, set_sim_func, res_name_func):
    """
       car集成, 仿真
        data dict, 包含仿真工况(不能有list)
        sim_name_func 函数, 获取仿真名称 sim_name_func(sim_name)
        set_sim_func 函数, 运行指定仿真  set_sim_func(data)
        res_name_func 函数, 输出指定后处理路径 res_name_func(sim_dir, sim_name)
    """
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
    cmd_send(new_cmd)
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

def set_sim_car_full_static(data):
    """
    运行仿真
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
    cmd_send(new_cmd)
    return None

def sim_car_full_static(data):
    """ 完整car静平衡仿真 """
    return sim_car(data, _sim_name_full_static, set_sim_car_full_static, _sim_res_full_static)


# -------------------------------------------
# ---悬架-平行轮跳仿真---

_sim_name_sus_parallel = lambda sim_name: sim_name + '_parallel_travel'
_sim_res_sus_parallel = lambda sim_dir, sim_name: os.path.join(sim_dir, sim_name+'_parallel_travel.res')

CMD_SIM_CAR_PARALLEL_SUS = """
acar analysis suspension parallel_travel submit &
 assembly=.#model_name# &
 variant=default &
 output_prefix="#sim_name#" &
 nsteps=#step# &
 bump_disp=#bump# &
 rebound_disp=#rebound# &
 stat_steer_pos=#steer# &
 steering_input=angle &
 vertical_setup=wheel_center_height &
 vertical_input=wheel_center_height &
 vertical_type=absolute &
 comment="" &
 analysis_mode=#mode# &
 log_file=yes
"""

def set_sim_car_sus_parallel(data):
    """
    运行仿真
    data = {
        "model_name":
        "sim_name"  : 
        "step"      :
        "bump"      :
        "rebound"   :
        "steer"     :
        "mode"  :
        }
    """
    # model_name
    # sim_name

    if "mode" not in data: data["mode"] = 'interactive'
    if "steer" not in data: data["steer"] = 0

    new_cmd = _cmd_replace(CMD_SIM_CAR_PARALLEL_SUS, **_dict_data_change(data))
    # print(new_cmd)
    cmd_send(new_cmd)
    return None


def sim_car_sus_parallel(data):
    """ 完整car静平衡仿真 """
    return sim_car(data, _sim_name_sus_parallel, set_sim_car_sus_parallel, _sim_res_sus_parallel)


# -------------------------------------------
# ---悬架-反向轮跳仿真---

_sim_name_sus_opposite = lambda sim_name: sim_name + '_opposite_travel'
_sim_res_sus_opposite = lambda sim_dir, sim_name: os.path.join(sim_dir, sim_name+'_opposite_travel.res')

CMD_SIM_CAR_OPPOSITE_SUS = """
acar analysis suspension opposite_travel submit &
 assembly=.#model_name# &
 variant=default &
 output_prefix="#sim_name#" &
 nsteps=#step# &
 bump_disp=#bump# &
 rebound_disp=#rebound# &
 stat_steer_pos=#steer# &
 steering_input=angle &
 vertical_setup=wheel_center_height &
 vertical_input=wheel_center_height &
 vertical_type=absolute &
 comment="" &
 analysis_mode=#mode# &
 log_file=yes
"""

def set_sim_car_sus_opposite(data):
    """
    运行仿真
    data = {
        "model_name":
        "sim_name"  : 
        "step"      :
        "bump"      :
        "rebound"   :
        "steer"     :
        "mode"  :
        }
    """
    # model_name
    # sim_name

    if "mode" not in data: data["mode"] = 'interactive'
    if "steer" not in data: data["steer"] = 0

    new_cmd = _cmd_replace(CMD_SIM_CAR_OPPOSITE_SUS, **_dict_data_change(data))
    # print(new_cmd)
    cmd_send(new_cmd)
    return None


def sim_car_sus_opposite(data):
    """ 完整car静平衡仿真 """
    return sim_car(data, _sim_name_sus_opposite, set_sim_car_sus_opposite, _sim_res_sus_opposite)



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


def test_sim_car_sus_parallel():
    pass
    model_name = get_current_model()
    data = {
        "model_name": model_name,
        "sim_name" : "auto_sim",
        "step" : 100,
        "bump" : 50,
        "rebound" : -50,
    }
    result = sim_car_sus_parallel(data)
    pprint(result)
    # test_sim_car_sus_parallel()


def test_set_sim_car_sus_opposite():
    pass
    model_name = get_current_model()
    data = {
        "model_name": model_name,
        "sim_name" : "auto_sim",
        "step" : 100,
        "bump" : 50,
        "rebound" : -50,
    }
    result = sim_car_sus_opposite(data)
    pprint(result)
    # test_set_sim_car_sus_opposite()


# test_sim_brake()
# test_query_element_model()


def test():
    model_name = get_current_model()
        
    reqs = get_request_by_filter(model_name, '*frame_force*')
    print(reqs)
    if reqs:
        for req in reqs:
            result = get_request_data_one(req)
        # print(req, req_type, comp_names, attr)
    
        print(result)

    print(get_aggregate_mass(model_name))
    
    # print(req, req_type)
    # f_req = reqs[-1]
    # f_req_type = _query_send(f'{f_req}.type')
    # print(f_req, f_req_type)

    return None



def adams_python_run(line):
    """
        运行 adams的python
        line: 单行命令
    """
    return _query_send(f"eval(run_python_code('{line}'))")



if __name__=='__main__':

    pass
    # test()
    print(adams_python_run('import os'))
    print(adams_python_run('os.getcwd()'))
    # model_name = get_current_model()
    # set_default_cdb('T75E01')
    # set_close_asy(model_name)
    
    # test_query_element_model()
    # print(_query_db_descendants(model_name, "request"))

