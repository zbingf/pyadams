"""
    Car 模块测试
"""
from pyadams.car import search_part_mass , search_spring_k, sus_ite, request_check
from pyadams.car import post_handle_s, post_handle_crc, post_force_load
from pyadams.car import cal_road_correlation

import shutil
import re
import os
import os.path
import logging
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


CAR_CDB_DIR = r'D:\software\MSC.Software\Adams\2019\acar'
TEST_PATH   = r'..\tests'

def path_join(file_dir, file_path):

    return os.path.abspath(os.path.join(file_dir, file_path))

# 删除文件夹内制定文件
def file_remove_pt(path, prefix=None, file_type=None): 
    '''
        仅仅删除文件夹内的文件，不删除子文件夹
        path 文件夹路径
        prefix 文件前缀
        file_type 文件后缀,类型
        示例：
            file_remove_pt(path,'sim_','adm')

            file_remove_pt(cal_path, prefix=None, file_type='bak') # 删除文件夹内整个带bak后缀的文件

    '''
    path_rems = []

    for line in os.listdir(path):
        # print(os.listdir(path))
        if file_type!=None and file_type.lower() == line[-len(file_type):] or file_type==None:
            if prefix!=None and prefix.lower() == line[:len(prefix)] or prefix==None:
                path_rems.append(line)

    for line in path_rems:
        target = os.path.join(path, line)
        if os.path.isfile(target):
            os.remove(target)
        # print(target)
    return True

# 删除文件夹
def remore_path(path):

    shutil.rmtree(path)#递归删除文件夹

# search_spring_k 测试
def test_search_spring_k():

    spring_data_path = os.path.join(TEST_PATH, r'search_spring_k\spring_mean.csv')
    search_spring_k.spring_k_mean(CAR_CDB_DIR, spring_data_path)

    with open(spring_data_path, 'r') as f:
        spring_file_str = f.read()

    print(spring_file_str)
    return None

# search_part_mass 测试
def test_search_part_mass():

    mass_data_path = os.path.join(TEST_PATH, r'search_part_mass\part_mass.csv')
    search_part_mass.body_mass_search(CAR_CDB_DIR, mass_data_path)

    with open(mass_data_path, 'r') as f:
        mass_file_str = f.read()

    print(mass_file_str)
    return None



# request 检查测试
def test_reference_mark_check():

    logger = logging.getLogger('test_reference_mark_check')

    adm_path = path_join(TEST_PATH, r'request_check\car_adm_sim_Car_Sim_brake.adm')
    obj = request_check.ReferenceMarkCHeck(adm_path)
    strs = obj.reference_mark_check(target_str='steering_assist', target_part_name='ground')

    logger.info(f'strs:{strs}')

    # 判断
    print(strs)

    return None


if __name__=='__main__':

    # with open(LOG_PATH, 'w', encoding='utf-8') as f: pass
    logging.FileHandler(LOG_PATH, mode='w', encoding='utf-8', delay=False)
    logging.basicConfig(level=logging.INFO, filename=LOG_PATH)
    # help(logging)

    # test_search_spring_k()

    # test_search_part_mass()

    test_sus_ite()

    # test_sus_ite_threading()

    # test_reference_mark_check()

    # test_post_handle_s()

    # test_post_handle_crc()

    # test_post_force_load()

    # test_cal_road_correlation()




