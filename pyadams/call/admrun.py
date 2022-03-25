"""
    python version : 3.7
    Adams version : 2017.2
    用于运行 adm 文件
    
    2020/09
"""
import subprocess
import os
import re
import psutil
import time
import os.path
import logging
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


from pyadams.call import cmd_link

# cmd 调用命令
CMD = r"""
{}
cd {}
call {} acar ru-solver {}
"""
ADAMS_BAT_NAME = 'adams2017_2'

ADAMS_2019 = 'adams2019'

SIM_LIMIT_MINUTE = 60 # 仿真时限

class AcfFile:
    """
        ACF 文件 生成模块
    """
    def __init__(self,filepath,simtime,samplerate):
        # adm 路径 
        self.filepath = filepath
        # 仿真时间
        self.simtime = simtime
        # 采样频率
        self.samplerate = samplerate

        self.name = os.path.basename(filepath)[:-4]
        # print(self.name)

        self.acfpath = self.filepath[:-3]+'acf'

        self.acf_write()
        

    def acf_write(self):
        strlist = []
        strlist.append(self.name)
        strlist.append(' ')
        strlist.append('SIM/STA')
        strlist.append(
            'SIMULATE/DYN, END= {}, STEPS= {}'.format(self.simtime,int(self.simtime*self.samplerate)) # +1
            )  
        strlist.append('STOP')
        with open(self.filepath[:-3]+'acf','w') as f:
            f.write('\n'.join(strlist))


def admrun(adm_path,simtime,samplerate,simlimit=SIM_LIMIT_MINUTE,version='2017.2'):
    """
        adm 运行
        输入：
            adm_path  adm文件路径
            simtime 仿真时间
            samplerate 采样频率
            simlimit 分析时长上限

        运行前需确认是否已存在相应后处理文件

    """
    if version == '2017.2':
        version = ADAMS_BAT_NAME
    if version == '2019':
        version = ADAMS_2019

    obj = AcfFile(adm_path,simtime,samplerate)

    # bat 字符串 
    # 用于生成调用 acf文件 的bat文件
    cmd = CMD.format(
        obj.acfpath[:2],
        os.path.split(obj.acfpath)[0],
        cmd_link.bat_path_search(version),
        obj.acfpath)
    
    bat_path = adm_path[:-3]+'bat'
    with open(bat_path,'w') as f:
        f.write(cmd)
    
    res_path = adm_path[:-3]+'res'

    return cmd_link.call_bat_sim(bat_path, res_path, simlimit=simlimit)


def admrun_car(adm_path, version='2017.2', simlimit=SIM_LIMIT_MINUTE):
    """
        car模块的adm文件运行
        主要针对 整车车辆控制如 制动、操稳
    
        注意点：
            1、默认路径为本地磁盘
            2、adm、xml、acf 三个文件均需位于同一目录下
    """

    # bat 字符串 
    # 用于生成调用 acf文件 的bat文件

    if version == '2017.2':
        version = ADAMS_BAT_NAME
    if version == '2019':
        version = ADAMS_2019

    acf_path = adm_path[:-3]+'acf'
    bat_path = adm_path[:-3]+'bat'

    cmd = CMD.format(
        adm_path[:2],
        os.path.split(acf_path)[0],
        cmd_link.bat_path_search(version),
        acf_path)
    
    with open(bat_path,'w') as f:
        f.write(cmd)

    res_path = adm_path[:-3]+'res'

    return cmd_link.call_bat_sim(bat_path, res_path, simlimit=simlimit)


def admrun_car_sus(adm_path, simtime, step, version='2017.2', simlimit=SIM_LIMIT_MINUTE):
    """
        CAR模块-悬架计算
        adm_path    : adm文件路径
        simtime     : 仿真时间   对于静态仿真计算，则应按1Hz采样处理
        step        : 仿真步长
        version     : 仿真版本
        sisimlimit  : 仿真计算时长限制 单位min分钟
    """

    if version == '2017.2':
        version = ADAMS_BAT_NAME
    elif version == '2019':
        version = ADAMS_2019

    acf_path = adm_path[:-3]+'acf'
    bat_path = adm_path[:-3]+'bat'
    cmd = CMD.format(
        adm_path[:2],
        os.path.split(acf_path)[0],
        cmd_link.bat_path_search(version),
        acf_path)

    with open(bat_path, 'w') as f:
        f.write(cmd)

    with open(acf_path, 'r') as f:
        acf_list = f.readlines()

    for loc,line in enumerate(acf_list):
        line = re.sub(r'\s', '', line).lower()
        if 'simulate/static' in line:
            new_str = f'simulate/static, end={simtime}, steps={int(step)} \n'
            acf_list[loc] = new_str
        if 'out=' in line:
            new_str = line.split('out=')[0] + 'out=' + os.path.basename(adm_path)[:-4] +'\n'
            acf_list[loc] = new_str

    with open(acf_path,'w') as f:
        f.write(''.join(acf_list))

    # 批处理调用
    res_path = adm_path[:-3]+'res'

    return cmd_link.call_bat_sim(bat_path, res_path, simlimit=simlimit)


# ==============================================
# ==============================================
# 测试模块

def test_admrun():

    adm_path = r'..\tests\call_admrun\admrun\test_admrun.adm'
    adm_path = os.path.abspath(adm_path)
    res_path = admrun(adm_path, 1, 512)
    for filetype in ['res', 'req', 'gra']:
        try:
            file_path = adm_path[:-3]+filetype
            os.remove(file_path)
        except:
            logger.warning(f'file: {os.path.basename(file_path)} is not exists')
            pass
    print(res_path)

def test_admrun_car():

    adm_path = r'..\tests\call_admrun\admrun_car\test_amdrun_car_2017p2_brake.adm'
    adm_path = os.path.abspath(adm_path)
    res_path = admrun_car(adm_path)
    for filetype in ['res', 'req', 'gra']:
        try:
            file_path = adm_path[:-3]+filetype
            os.remove(file_path)
        except:
            logger.warning(f'file: {os.path.basename(file_path)} is not exists')
            pass
    print(res_path)

def test_admrun_car_sus():

    adm_path = r'..\tests\call_admrun\admrun_car_sus\test_admrun_car_sus_2017p2_opposite_travel.adm'
    adm_path = os.path.abspath(adm_path)
    res_path = admrun_car_sus(adm_path,101,100)
    for filetype in ['res', 'req', 'gra']:
        try:
            file_path = adm_path[:-3]+filetype
            # os.remove(file_path)
        except:
            logger.warning(f'file: {os.path.basename(file_path)} is not exists')
            pass
    print(res_path)


if __name__ == '__main__':
    pass
    # test_admrun()
    # test_admrun_car()
    # test_admrun_car_sus()
