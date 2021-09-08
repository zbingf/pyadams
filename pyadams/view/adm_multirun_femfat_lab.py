"""
    adm文件 批量计算
    多线程计算
    用于FEMFAT-LAB白噪声
"""

import pprint
from pyadams.car import adm_sim
from pyadams.file import result, file_edit

DataModel = result.DataModel
data_obj  = DataModel('multirun_femfat_lab')
SUFFIX    = '_noise_ch{}.adm'

def multirun_femfat_lab(params, isRead=True):
    """
        多线程计算

    """
    # ===================================== 参数
    adm_path        = params['adm_path']
    csv_path        = params['csv_path']
    simtime         = params['simtime']
    samplerate      = params['samplerate']
    n_load          = params['n_load']
    simlimit        = params['simlimit']
    max_threading   = params['max_threading']
    reqs            = params['reqs']
    comps           = params['comps']
    nchannel        = params['nchannel']
    version         = params['version']  # 2017.2 or 2019
    suffix          = params['suffix'] if 'suffix' in params else SUFFIX

    
    step            = simtime * samplerate
    nrange          = params['nrange']  # [1, step+1]       
    # ==========================================
    adm_paths = []
    for n in range(1, n_load+1):
        adm_paths.append(adm_path[:-4] + suffix.format(n))

    admsim_obj = adm_sim.AdmSimControl(adm_path)
    sim_param  = {'simtype':adm_sim.VIEW, 'samplerate':samplerate, 'simtime':simtime, 
        'step':None, 'version':version, 'simlimit':simlimit}

    for adm_path in adm_paths:
        admsim_obj.new_adm_paths[adm_path] = adm_path
        admsim_obj.set_sim_param(adm_path, sim_param)
        admsim_obj.isSimeds[adm_path]      = False
        admsim_obj.res_paths[adm_path]     = adm_path[:-3] + 'res'

    admsim_obj.amd_sim_threading(max_threading-1)
    res_paths = admsim_obj.res_paths

    if not isRead: return None

    res_data = {}
    for sub_name in res_paths:
        data_obj.new_file(res_paths[sub_name], sub_name)
        data_obj[sub_name].set_reqs_comps(reqs, comps)
        data_obj[sub_name].set_select_channels(nchannel)
        data_obj[sub_name].set_line_ranges(nrange)
        data_obj[sub_name].read_file_faster()
        res_data[sub_name] = data_obj[sub_name].get_data()
        for line in res_data[sub_name]: line[0] = 0

    data_all = []
    for loc, adm_path in enumerate(adm_paths):
        if loc==0:
            for line in res_data[adm_path]: data_all.append(line)
        else:
            for num, line in enumerate(res_data[adm_path]): data_all[num].extend(line)

    file_edit.data2csv(csv_path, data_all, reqs=reqs, comps=comps)

    return None
