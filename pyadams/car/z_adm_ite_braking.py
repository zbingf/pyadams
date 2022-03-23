"""
    制动模块
    
"""
# 
# braking
import re
from pyadams.car import adm_sim

# brake xml 工况编辑
def edit_xml_brake(xml_path, finalValue, start_time=None, duration=None, initial_velocity=None, new_xml_path=None):
    """
        # 制动数据获取
        finalValue       : 最终制动力设置
        start_time       : 制动开始时间 sec
        initial_velocity : 60 # 单位 km/h
        xml_path         : xml路径 
        new_xml_path     : 新xml路径

    """
    # ===============================================
    # xml读取
    with open(xml_path, 'r') as f:
        xml_str = f.read()
    new_xml_str = xml_str  # 新xml存储

    # ===============================================
    # DcfDemand
    dcf_demands = re.findall('<\s*DcfDemand\s.*?>', xml_str, flags=re.S)
    dcf_demand_braking = None
    for dcf_demand in dcf_demands:
        braking_obj = re.search('name\s*=\s*\"braking\"',dcf_demand, flags=re.S)
        if braking_obj:
            # 制动控制数据
            dcf_demand_braking = dcf_demand
    # dcf_demand_braking

    # ===============================================
    # 单位获取
    units = ['time', 'length']
    unit_sets = re.findall('<afc:UnitSetting\s*name\s*=\s*".*?"\s*current\s*=\s*".*?"\s*/>'.lower(), xml_str.lower(), flags=re.S)
    unit_dic = {}
    for unit_set in unit_sets:
        for unit in units:
            if re.match(f'.*name\s*=\s*"\s*{unit}\s*".*', unit_set.lower(), flags=re.S):
                temp = re.match('.*current="(\S+)".*', unit_set, flags=re.S)
                unit_dic[unit] = temp.group(1).lower()
    # unit_dic

    # ===============================================
    # 制动数据编辑
    # 制动开始时间 s
    # 最大制动值 
    # print(dcf_demand_braking)
    new_dcf_braking = dcf_demand_braking
    # final value
    new_dcf_braking = re.sub('finalValue\s*=\s*".*?"', f'finalValue="{finalValue:0.4f}"', new_dcf_braking, flags=re.S)
    # start time
    if start_time!=None:
        new_dcf_braking = re.sub('startTime\s*=\s*".*?"', f'startTime="{start_time:0.4f}"', new_dcf_braking, flags=re.S)
    # duration
    if duration!=None:
        new_dcf_braking = re.sub('duration\s*=\s*".*?"', f'duration="{duration:0.4f}"', new_dcf_braking, flags=re.S)

    # 替换
    new_xml_str = new_xml_str.replace(dcf_demand_braking, new_dcf_braking)

    # ===============================================
    # 车速定义-初始车速
    # initial_velocity
    # initialSpeed="13923.055556" # 单位 mm/s
    if initial_velocity == None:
        temp = re.match('.*initialspeed="(\S+)".*', new_xml_str.lower(), flags=re.S)
        initial_velocity = float(temp.group(1))
    else:
        # initial_velocity单位转换
        if unit_dic['length']=='mm' and unit_dic['time']=='sec':
            initial_velocity = initial_velocity/3.6*1000
        if unit_dic['length']=='m' and unit_dic['time']=='sec':
            initial_velocity = initial_velocity/3.6

    new_xml_str = re.sub('initialSpeed="(\S+)"', f'initialSpeed="{initial_velocity:0.4f}"', new_xml_str, flags=re.S)

    if new_xml_path==None:
        new_xml_path = xml_path
    with open(new_xml_path, 'w') as f:
        f.write(new_xml_str)

    return None


# ===============================================
# 制动数据获取
finalValue = 100
start_time = 1
initial_velocity = 60 # 单位 km/h
duration = 0.6
xml_path = r'D:\document\ADAMS\braking_brake.xml'
new_xml_path = None

edit_xml_brake(xml_path, finalValue, start_time, duration=duration, initial_velocity=initial_velocity, new_xml_path=new_xml_path)

adm_path = r'D:\document\ADAMS\braking_brake.adm'
# admfd_obj = adm_sim.AdmFileManager(adm_path)
# admfd_obj.updata_dir(r'D:\document\ADAMS\temp1')
sim_param = {'simtype':adm_sim.CAR, 'samplerate':None, 'simtime':None, 'step':None, 
    'version':'2017.2', 'simlimit':60}


admsim_obj = adm_sim.AdmSimControl(adm_path)
admsim_obj.set_sub_dir('braking_1')
admsim_obj.set_sim_param('braking_1', sim_param)


max_threading = 4
admsim_obj.amd_sim_threading(max_threading)
res_paths = admsim_obj.res_paths
print(res_paths)

