"""
    adm文件仿真及相关应用

"""

from pyadams.call import threadingrun
from pyadams.file import admfile, result
from pyadams.call import admrun
from pyadams.datacal import OAT
from pyadams.datacal import var_map
DataModel = result.DataModel
DataModelCompare = result.DataModelCompare

import re
import os
import time
import copy
import shutil
import pprint
import threading
import pysnooper

import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


# ==============================
# 仿真文件管理
class AdmFileData: # 仿真文件管理
    """
        源路径
        self.adm_path       str
        self.acf_path       str
        self.mtx_paths      [str, str]
        self.target_dir     str 新路径目录
        新路径
        self.new_adm_path   str
        self.new_acf_path   str
        self.new_mtx_paths  [str, str]
    """
    def __init__(self, adm_path):

        self.adm_path = os.path.abspath(adm_path)
        self.acf_path = self.adm_path[:-3]+'acf'
        self.xml_path = self.adm_path[:-3]+'xml'
        self.mtx_paths = []
        self.rdf_paths = []
        self.target_dir = None

        if not self.is_acf_exists():
            with open(self.acf_path, 'w') as f: pass
            logger.warning('acf路径不存在, 创建新文件')

        if not self.is_xml_exists():
            with open(self.xml_path, 'w') as f: pass
            logger.warning('xml路径不存在, 创建新文件')

        self.parase_adm_for_mtx()
        self.parase_adm_for_rdf()

    def parase_adm_for_rdf(self):
        """
            解析adm文件 , 获取rdf文件路径
        """
        strcal = lambda str1: re.sub(r'\s', '', str1).lower()

        adm_path  = self.adm_path
        rdf_paths = self.rdf_paths

        # adm文件读取
        with open(adm_path, 'r') as f:
            lines = f.readlines()
        # 柔性体mtxs文件查找
        rdfs = []
        for loc, line in enumerate(lines):
            line = strcal(line)
            re1 = re.match(r',string=(.*\.rdf)\Z', line)
            if re1:
                if '.rpf_file' in lines[loc-2].lower():
                    rdfs.append(re1.group(1))

        rdf_names = set(rdfs) # 去重
        for name in rdf_names:
            if os.path.exists(name):
                temp_path = os.path.abspath(name)
            else:
                temp_dir  = os.path.dirname(adm_path)
                temp_path = os.path.join(temp_dir, name)
                if not os.path.exists(temp_path): 
                    # 没找到路径不列入计算
                    logger.info(f'未检测到rdf路径: {temp_path}')
                    continue
            rdf_paths.append(temp_path)

        self.rdf_paths = rdf_paths
        return rdf_paths

    def parase_adm_for_mtx(self):
        """
            解析adm文件 , 获取mtx文件路径
        """
        strcal = lambda str1: re.sub(r'\s', '', str1).lower()
        # adm文件读取
        with open(self.adm_path, 'r') as f:
            lines = f.readlines()
        # 柔性体mtxs文件查找
        mtxs = []
        for line in lines:
            line = strcal(line)
            re1 = re.match(r',file=(.*\.mtx)\Z', line)
            if re1:
                mtxs.append(re1.group(1))

        mtx_names = set(mtxs)
        for name in mtx_names:
            if os.path.exists(name):
                temp_path = os.path.abspath(name)
            else:
                temp_dir  = os.path.dirname(self.adm_path)
                temp_path = os.path.join(temp_dir, name)
                if not os.path.exists(temp_path): raise f'未检测到mtx路径: {temp_path}'

            self.mtx_paths.append(temp_path)

        return self.mtx_paths

    def is_acf_exists(self):
        """ acf文件是否存在 """
        return os.path.exists(self.acf_path)

    def is_xml_exists(self):
        """ xml文件是否存在 """
        return os.path.exists(self.xml_path)

    def create_target_dir(self):
        """ 创建目标路径 """
        target_dir = self.target_dir
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        self.target_dir = target_dir

        return target_dir

    def copy_files(self):
        """ 复制文件到目标路径 """
        target_dir = self.target_dir
        new_adm_path = os.path.join(target_dir, os.path.basename(self.adm_path))
        new_acf_path = os.path.join(target_dir, os.path.basename(self.acf_path))
        new_xml_path = os.path.join(target_dir, os.path.basename(self.xml_path))
        
        new_mtx_paths = []
        for mtx_path in self.mtx_paths:
            new_mtx_paths.append(os.path.join(target_dir, os.path.basename(mtx_path)))

        new_rdf_paths = []
        for rdf_path in self.rdf_paths:
            new_rdf_paths.append(os.path.join(target_dir, os.path.basename(rdf_path)))

        shutil.copy(self.adm_path, new_adm_path)
        shutil.copy(self.acf_path, new_acf_path)
        shutil.copy(self.xml_path, new_xml_path)

        for new_mtx_path, mtx_path in zip(new_mtx_paths, self.mtx_paths):
            shutil.copy(mtx_path, new_mtx_path)

        for new_rdf_path, rdf_path in zip(new_rdf_paths, self.rdf_paths):
            shutil.copy(rdf_path, new_rdf_path)

        self.new_adm_path = new_adm_path
        self.new_acf_path = new_acf_path
        self.new_mtx_paths= new_mtx_paths
        self.new_xml_path = new_xml_path
        self.new_rdf_paths= new_rdf_paths

        path_dir = {
            'adm_path'  : new_adm_path,
            'acf_path'  : new_acf_path,
            'mtx_paths' : new_mtx_paths,
            'xml_path'  : new_xml_path,
            'rdf_paths' : new_rdf_paths,
            'target_dir': target_dir,
        }

        logger.info(f'文件新路径: {path_dir}')
        
        return path_dir

    def updata_dir(self, target_dir):
        """ 更新&复制路径 """

        self.target_dir = os.path.abspath(target_dir)
        self.create_target_dir()
        path_dir = self.copy_files()

        return path_dir


# ==============================
# adm文件编辑
class AdmEditData: # adm文件编辑
    """
        AdmEditData 用于编辑adm文件
    """
    def __init__(self, adm_path):
        """ adm_path """
        adm_path = os.path.abspath(adm_path)
        self.edits = []

        self.adm_path = adm_path
        self.amdobj = admfile.AdmCar(adm_path)
        self.editobj = admfile.AdmEdit(self.amdobj)

    def edit_values_data(self, value_cmd, list1d_value):
        """ 
            value-数值编辑 
            value_cmd    : str 数值变更-命令
            list1d_value : list 数值数据作为输入
        """
        self.editobj.edit(value_cmd, list1d_value)
        return None

    def edit_strs_data(self, str_cmd, list1d_str):
        """ 
            str-字符串编辑 
            str_cmd      : str 字符串变更-命令
            list1d_str   : [int, int, ...] 字符串选择
        """
        str_loc_dic = {}
        for num,loc in enumerate(list1d_str):
            str_loc_dic[num] = loc
        self.editobj.read_str(str_cmd)
        self.editobj.edit_str(str_loc_dic)
        return None

    def edit_ts_load(self, spline_ids, list2d, samplerate):
        """
            时域加载信号加载 - spline
            spline_ids : [int, int, ...] id号
            list2d     : [[float, float, ...], []] 加载数据
            samplerate : 采样频率Hz
        """
        xlist = [n/samplerate for n in range(len(list2d[0]))]
        for num, nid in enumerate(spline_ids):
            self.amdobj.model.splinenum[nid].updata(xlist, list2d[num])
        return None

    def updata(self):
        """
            adm文件更新
        """
        edit_cmdlists = self.amdobj.updata()
        self.amdobj.newfile(self.adm_path)

        # 编辑记录
        str_line = '\n\n'+'='*20+'编辑片段\n'
        edit_file_path =  self.adm_path+'_edited.txt'
        is_spline_start = False
        with open(edit_file_path, 'w', encoding='utf-8') as f:
            for lines in edit_cmdlists:
                f.write(str_line)
                if len(lines)>20:
                    if 'SPLINE/' in lines[1].upper():
                        f.write('\n'.join(lines[:20]))
                        f.write('\n... ...')
                        continue
                f.write('\n'.join(lines[:-1]))

        with open(edit_file_path, 'r', encoding='utf-8') as f: 
            temp_str = f.read()

        logger.info(f'edit_str: {temp_str}')


        return edit_cmdlists


# ==============================
# adm仿真管理

# simtype 仿真类型定义
VIEW           = 1  # 
CAR            = 2  # 
CAR_SUS_STATIC = 3  # 

class AdmSimControl: 
    """ 
        AdmSimControl 仿真控制 
    """
    models      = {}
    model_names = []

    def __init__(self, adm_path):
        adm_path = os.path.abspath(adm_path)
        
        if adm_path not in AdmSimControl.model_names:
            # 创建
            AdmSimControl.model_names.append(adm_path)            
            AdmSimControl.models[adm_path] = self

            self.admfd_obj     = AdmFileData(adm_path)
            self.res_paths     = {}
            self.new_adm_paths = {}
            self.sub_dirs      = {}
            self.isSimeds      = {}
            self.sim_params    = {}
            self.edit_params   = {}

        else:
            # 已存在 key(adm_path) 直接赋值
            self.admfd_obj     = AdmSimControl.models[adm_path].admfd_obj
            self.res_paths     = AdmSimControl.models[adm_path].res_paths
            self.new_adm_paths = AdmSimControl.models[adm_path].new_adm_paths
            self.sub_dirs      = AdmSimControl.models[adm_path].sub_dirs
            self.isSimeds      = AdmSimControl.models[adm_path].isSimeds
            self.sim_params    = AdmSimControl.models[adm_path].sim_params
            self.edit_params   = AdmSimControl.models[adm_path].edit_params

        self.adm_path = adm_path

    def set_sub_dir(self, sub_name):
        """根据subname设置子路径"""
        sub_dir = os.path.join(os.path.dirname(self.adm_path), sub_name)

        self.admfd_obj.updata_dir(sub_dir)
        self.new_adm_paths[sub_name] = self.admfd_obj.new_adm_path
        self.res_paths[sub_name]     = self.new_adm_paths[sub_name][:-3]+'res'
        self.sub_dirs[sub_name]      = sub_dir
        self.isSimeds[sub_name]      = False

        return None

    def set_adm_edit(self, sub_name, edit_param):

        self.edit_params[sub_name] = edit_param

        admfd_obj = AdmEditData(self.new_adm_paths[sub_name])

        if edit_param['value_edit']['list1d_value'] != None:
            admfd_obj.edit_values_data(edit_param['value_edit']['value_cmd'], 
                edit_param['value_edit']['list1d_value'])

        if edit_param['str_edit']['list1d_str'] != None:
            admfd_obj.edit_strs_data(edit_param['str_edit']['str_cmd'], edit_param['str_edit']['list1d_str'])

        if edit_param['load_edit']['spline_ids'] != None:
            admfd_obj.edit_ts_load(edit_param['load_edit']['spline_ids'], 
                edit_param['load_edit']['list2d'],
                edit_param['load_edit']['samplerate'])

        admfd_obj.updata()

        return None

    def set_sim_param(self, sub_name, sim_param):
        self.sim_params[sub_name] = sim_param
        return None

    def adm_sim(self, sub_name):
        """adm仿真"""
        if not self.isSimeds[sub_name]:
            self.isSimeds[sub_name] = True
        else:
            return None

        sim_param = self.sim_params[sub_name]
        adm_path  = self.new_adm_paths[sub_name]

        version   = sim_param['version']
        simlimit  = sim_param['simlimit']
        samplerate= sim_param['samplerate']
        simtime   = sim_param['simtime']
        step      = sim_param['step']
        simtype   = sim_param['simtype']

        if simtype==VIEW:
            if simtime==None or samplerate==None: raise '缺少参数:simtime or samplerate'
            admrun.admrun(adm_path, simtime, samplerate,
                version=version, simlimit=simlimit)

        elif simtype==CAR:
            admrun.admrun_car(adm_path,
                version=version, simlimit=simlimit)

        elif simtype==CAR_SUS_STATIC:
            if step==None: raise '缺少参数:step'
            admrun.admrun_car_sus(adm_path, step+1, step,
                version=version, simlimit=simlimit)

        return None

    def amd_sim_threading(self, max_threading=4):
        """进行多线程计算"""
        threadmax = threading.BoundedSemaphore(max_threading)
        threads   = []
        for sub_name in self.sim_params:
            new_func = threadingrun.threading_func(self.adm_sim, threadmax=threadmax)
            thread   = threading.Thread(target=new_func, args=(sub_name, ))
            thread.start()
            logger.info(f'running:{sub_name}')
            threads.append(thread)
            threadmax.acquire()
            time.sleep(1)

        while threads:
            threads.pop().join()

        return self.res_paths


# ==============================
# adm变量编辑管理
class AdmParam:

    def __init__(self, edit_param):
        """
            edit_param = {
                'value_edit': {'value_cmd': value_cmd, 'list1d_value':[1.5]},
                'str_edit'  : {'str_cmd':None, 'list1d_str':None},
                'load_edit' : {'spline_ids': None, 'list2d': None, 'samplerate': None}
            }
        """        
        self.value_dic   = {}           # 存储数值变量数据 {key:value_edit, ...}
        self.str_dic     = {}           # 存储字符变量数据 {key:str_edit, ...}
        self.edit_param  = edit_param
        self.edit_params = {}

    # 批量-edit_params ; value_edit\str_edit更改
    def create_edit_params(self, base_name='m'):
        """
            base_name 为原edit_param设置的key
        """
        edit_param = copy.deepcopy(self.edit_param)

        value = edit_param['value_edit']['list1d_value']
        if isinstance(value, float) or isinstance(value, int):
            edit_param['value_edit']['list1d_value'] = [value]

        str_value = edit_param['str_edit']['list1d_str']
        if isinstance(str_value, float) or isinstance(str_value, int):
            edit_param['str_edit']['list1d_str'] = [str_value]
        
        self.edit_params[base_name] = edit_param
        
        for key in self.value_dic:
            edit_param = copy.deepcopy(edit_param)
            edit_param['value_edit']['list1d_value'] = self.value_dic[key]
            self.edit_params[key] = edit_param

        for key in self.str_dic:
            edit_param = copy.deepcopy(edit_param)
            edit_param['str_edit']['list1d_str'] = self.str_dic[key]
            self.edit_params[key] = edit_param

        return self.edit_params

    # 批量-edit_params ; spline加载设置
    def create_load_multi_params(self, load_dic):
        """
            load_dic :  { key1: {'load_edit'}, key2: {'load_edit'},}
                一组load_edit 对应一个 key
        """
        edit_param = copy.deepcopy(self.edit_param)
        for key in load_dic:
            edit_param_n = copy.deepcopy(edit_param)
            edit_param_n['load_edit'] = load_dic[key]
            self.edit_params[key] = edit_param_n

        return self.edit_params

    # values-数值变量设置-单一变量
    def set_values_gain_2(self, list1d_tar, k_gains): 
        """
            数值变量更改
                数值双变量

            list1d_tar : [int, int, ...] 选取的数据
            k_gains    : [float, float, ...] 数值增益
            len(list1d_tar) == len(k_gains)

            k_gains: float or int or list

            value_dic - key: [f'v_p{n}_{k_gain}_u']
        """
        edit_param   = self.edit_param
        list1d_value = edit_param['value_edit']['list1d_value']
        value_cmd    = edit_param['value_edit']['value_cmd']

        # 数值设置
        if isinstance(list1d_value, float) or isinstance(list1d_value, int):
            list1d_value = [list1d_value]

        if isinstance(list1d_tar, float) or isinstance(list1d_tar, int):
            list1d_tar = [list1d_tar]

        # ==============================终止条件
        if not list1d_tar or not k_gains:     return None
        if not list1d_value or not value_cmd: return None

        # 参数选取
        if isinstance(list1d_tar, str):
            if list1d_tar.lower()=='all': list1d_tar = range(len(list1d_value))
        
        # 所选参数的增益
        if isinstance(k_gains, float) or isinstance(k_gains, int):
            k_gains = [k_gains for n in range(len(list1d_tar))]

        # ==============================
        for n, k_gain in zip(list1d_tar, k_gains):
            list1d_value_u = copy.deepcopy(list1d_value)
            list1d_value_u[n] *= (1+k_gain)
            list1d_value_l = copy.deepcopy(list1d_value)
            list1d_value_l[n] *= (1-k_gain)

            self.value_dic[f'v_p{n}_{k_gain}_u'] = list1d_value_u
            self.value_dic[f'v_p{n}_{k_gain}_l'] = list1d_value_l

        return None

    # values-数值变量设置-正交设计
    def set_value_orthogonal(self, list1d_tar, k_gains): 
        """
        """
        edit_param   = self.edit_param
        list1d_value = edit_param['value_edit']['list1d_value']
        value_cmd    = edit_param['value_edit']['value_cmd']

        # 数值设置
        if isinstance(list1d_value, float) or isinstance(list1d_value, int):
            list1d_value = [list1d_value]

        if isinstance(list1d_tar, float) or isinstance(list1d_tar, int):
            list1d_tar = [list1d_tar]

        # ==============================终止条件
        if not list1d_tar or not k_gains:     return None
        if not list1d_value or not value_cmd: return None

        # 参数选取
        if isinstance(list1d_tar, str):
            if list1d_tar.lower()=='all': list1d_tar = range(len(list1d_value))
        
        # 所选参数的增益
        if isinstance(k_gains, float) or isinstance(k_gains, int):
            k_gains = [k_gains for n in range(len(list1d_tar))]

        # ==============================
        var_tuples = []
        for n, k_gain in zip(list1d_tar, k_gains):
            list1 = [list1d_value[n]*(1-k_gain), list1d_value[n], list1d_value[n]*(1+k_gain)]
            var_tuples.append((n, list1))

        keys, results = OAT.cal_oat(var_tuples)
        for key in keys:
            new_key = key.replace('0','L')
            new_key = new_key.replace('1','M')
            new_key = new_key.replace('2','U')
            self.value_dic['v_'+new_key] = results[key]

        logger.info(f'set_value_orthogonal:results:\n{results}')

        return None

    # strs-字符串变量更改
    def set_strs_n(self, list1d_tar, isCal):
        """
            字符串变量更改
            str_dic - key: [f's_p{n}_{value}']

            目标变量选择
                list1d_tar: 'all' or [int1, int2, ..]
            是否计算 
                isCal : True or False

        """
        edit_param = self.edit_param
        list1d_str = edit_param['str_edit']['list1d_str']
        str_cmd    = edit_param['str_edit']['str_cmd']

        # 参数位置
        if isinstance(list1d_str, float) or isinstance(list1d_str, int):
            list1d_str = [list1d_str]

        if isinstance(list1d_tar, float) or isinstance(list1d_tar, int):
            list1d_tar = [list1d_tar]
            
        # ==============================终止条件
        if not list1d_tar:                return None
        if not list1d_str or not str_cmd: return None
        if not isCal:                     return None

        # ==============================数据编辑
        # 选取参数
        if isinstance(list1d_tar, str):
            if list1d_tar.lower() == 'all': list1d_tar = range(len(list1d_str))

        # ==============================
        num_dic = self.strcmd_cal(self.edit_param['str_edit']['str_cmd'])
        for n in list1d_tar:
            n_range = num_dic[n]
            for value in range(n_range):
                new_list1d_str    = copy.deepcopy(list1d_str)
                new_list1d_str[n] = value
                self.str_dic[f's_p{n}_{value}'] = new_list1d_str

        return None

    @staticmethod
    def strcmd_cal(str_cmd, str_split='|'): # 获取各字符串变量的可变换个数
        blocks = [] # 类型段落
        for line1 in str_cmd.split('$$'):
            list1 = []
            for line2 in [n for n in line1.split('\n') if n]:
                line3 = line2.split('#')[0]
                line3 = re.sub(r'\s','',line3)
                line3 = line3.replace(';','')
                if line3:
                    list1.append(line3.lower())

            if list1:
                blocks.append(list1)

        num_dic = {}
        for lines in blocks:
            for line in lines[1:]:
                strs, n_param = line.split(str_split)[1:]
                num = len(strs.split(','))
                n_param = int(n_param)
                num_dic[n_param] = num

        return num_dic


# ==============================
# adm计算结果 后处理
class AdmResult:

    def __init__(self, name='multi_adm_result'):
        """
        """
        self.data_obj = DataModel(name)
        self.dmc_obj  = DataModelCompare(self.data_obj)
        self.res_paths= None

    def read_res_paths(self, res_paths, params):
        """
            res_paths = {key:res_path, ...}
            params = {
                'reqs'    : [str1,...]
                'comps'   : [str1,...]
                'nrange'  : [start, end]
                'nchannel': [int, int, int,...]
            }
        """
        data_obj = self.data_obj
        reqs     = params['reqs']
        comps    = params['comps']
        nrange   = params['nrange']
        nchannel = params['nchannel']

        for sub_name in res_paths:
            data_obj.new_file(res_paths[sub_name], sub_name)
            data_obj[sub_name].set_reqs_comps(reqs, comps)
            data_obj[sub_name].set_select_channels(nchannel)
            data_obj[sub_name].set_line_ranges(nrange)
            data_obj[sub_name].read_file_faster()

        self.res_paths = res_paths

        return None

    def create_pdf(self, edit_params, params, lower_name='m', pdfType=1): # pdf 创建
        """
            edit_params = {key:edit_param, ...}
            params      = {
                'block_size' : {'u':128, 'l':128},
                'hz_range'   : [0, 50],
                'docx_path'  : docx路径,
                }
            lower_name  基础 key

            res_paths 与 edit_params 的key一致
        """
        res_paths   = self.res_paths
        
        # ==================================编辑
        edit_params = copy.deepcopy(edit_params)
        if lower_name in edit_params:
            edit_params[lower_name]['load_edit']['list2d'] = None

        for sub_name in edit_params: # spline_ids 显示编辑
            spline_ids = edit_params[sub_name]['load_edit']['spline_ids']
            if isinstance(spline_ids, list):
                str1 = '[' + ','.join([str(n) for n in spline_ids]) + ']'
                edit_params[sub_name]['load_edit']['spline_ids'] = str1

        # ==================================
        for sub_name in res_paths:
            edit_params[sub_name]['load_edit']['list2d'] = None

            if lower_name in res_paths:
                str_input = f'\n{sub_name}:\n'              +\
                    pprint.pformat(edit_params[sub_name])   +\
                    f'\n\n{lower_name}:\n'                  +\
                    pprint.pformat(edit_params[lower_name])
            else:
                str_input = f'\n{sub_name}:\n'              +\
                    pprint.pformat(edit_params[sub_name])   +\
                    f'\n\n{lower_name}:\n'                  +\
                    ' '*10 + 'None'

            str_input = str_input.replace('\\n', '')
            str_input = str_input.replace('\'', '')
            str_input = re.sub('\n\s+\n', '\n', str_input)

            temp = {
                'block_size' : params['block_size'],
                'hz_range'   : params['hz_range'],
                'docx_path'  : params['docx_path'][:-5] + f'_{sub_name}.docx',
                'fig_path'   : params['docx_path'][:-5] + f'_{sub_name}',
                'str_input'  : str_input,
                'nums'       : [3,2],
            }

            self.dmc_obj.run(sub_name, lower_name, temp, pdfType=pdfType)
            logger.info('创建pdf:{}'.format(temp['docx_path'][:-4]+'pdf'))

        return self.dmc_obj.result_compare

    def parse_result_compare(self, csv_path='result.csv', str_input=None): # CSV文件生成
        """
            解析 result_compare 数据
        """

        result_compare = self.dmc_obj.result_compare

        targets = ['u_max_divide_l_max', 'u_min_divide_l_min', 
            'u_pdi_divide_l_pdi', 'u_rms_divide_l_rms']

        with open(csv_path, 'w') as f: pass

        isCalRA = True
        for target in targets:
            csv_lines = []
            for key in result_compare:
                list1d = result_compare[key][target]
                line   = ','.join([str(value) for value in list1d])
                csv_lines.append(key+','+line)
            str_csv   = '\n'.join(csv_lines)
            title     = result_compare[key]['u_title']
            str_title = target + ',' + ','.join(title)

            with open(csv_path, 'a') as f:
                f.write(str_title + '\n' + str_csv + '\n\n')
            
            if 'None' in str_csv: isCalRA = False

        if len(result_compare)>1 and isCalRA:
            var_map.cal_var_color_map(csv_path, str_input)

        return None


# ==============================



# ==================================+
# 测试

def test_AdmFileData():

    adm_path = r'..\tests\car_adm_sim\cuoban_v30_maintain.adm'
    admfd_obj = AdmFileData(adm_path)
    admfd_obj.updata_dir(r'..\tests\car_adm_sim\temp')

    
    return admfd_obj


def test_AdmEditData():
    
    admfd_obj = test_AdmFileData()

    admed_obj = AdmEditData(admfd_obj.new_adm_path)

    # adams_view_name='TR_Front_Suspension.nsr_ride_spring.spline' 329
    admed_obj.edit_ts_load([329], [[1,2,3]], 512)
    # admed_obj.updata()
    # !              adams_view_name='TR_Front_Tires.tir_wheel.rpf_file'
    # STRING/104
    # , STRING =mdids://For_loadcal/roads.tbl/test2.rdf
    str_cmd = """
    $$tire.road 
    TR_Front_Tires.til_wheel|road1_7,road2_7,road3_7|0 
    TR_Front_Tires.tir_wheel|road1_7,road2_7,road3_7|0 
    $$tire.file
    TR_Front_Tires.til_wheel|pac1_7,ftire2_7,5213_7|1
    TR_Front_Tires.tir_wheel|pac1_7,ftire2_7,5213_7|1
    """
    admed_obj.edit_strs_data(str_cmd, [0,1])
    # admed_obj.updata()

    valuecmd = """
    $$car_bushing.k # Car衬套-刚度设置
    # 名称:选项:参数位置
    front_antiroll.bgl_antiroll_to_frame:t:0
    """
    admed_obj.edit_values_data(valuecmd,[10])
    edit_cmdlists = admed_obj.updata()
    
    # with open(admfd_obj.new_adm_path, 'r') as f:
    #     str1 = f.read()
    # with open(r'..\tests\car_adm_sim\temp\cuoban_v30_maintain_target.adm', 'r') as f:
    #     str2 = f.read()
    # assert str1 == str2


def test_admsim():

    # adm_path = r'D:\document\ADAMS\braking_brake.adm'
    # admfd_obj = AdmFileData(adm_path)
    # admfd_obj.updata_dir(r'..\tests\car_adm_sim')
    # return None

    # admfd_obj = test_AdmFileData()
    # adm_path  = admfd_obj.new_adm_path

    adm_path = r'..\tests\car_adm_sim\braking_brake.adm'
    

    sim_param = {'simtype':CAR, 'samplerate':None, 'simtime':None, 'step':None, 
        'version':'2017.2', 'simlimit':60}

    value_cmd = """
    $$car_spring.k_gain
    TR_Front_Suspension.nsl_ride_spring:255:0
    TR_Front_Suspension.nsr_ride_spring:255:0
    """
    edit_param1 = {
        'value_edit': {'value_cmd': value_cmd, 'list1d_value':[1.5]},
        'str_edit'  : {'str_cmd':None, 'list1d_str':None},
        'load_edit' : {'spline_ids': None, 'list2d': None, 'samplerate': None}
    }
    edit_param2 = {
        'value_edit': {'value_cmd': value_cmd, 'list1d_value':[2]},
        'str_edit'  : {'str_cmd':None, 'list1d_str':None},
        'load_edit' : {'spline_ids': None, 'list2d': None, 'samplerate': None}
    }

    admsim_obj = AdmSimControl(adm_path)
    admsim_obj.set_sub_dir('temp1')
    admsim_obj.set_sub_dir('temp2')
    admsim_obj.set_sub_dir('temp3')
    admsim_obj.set_sub_dir('temp4')
    admsim_obj.set_adm_edit('temp1', edit_param1)
    admsim_obj.set_adm_edit('temp2', edit_param2)
    admsim_obj.set_adm_edit('temp3', edit_param1)
    admsim_obj.set_adm_edit('temp4', edit_param2)

    admsim_obj.set_sim_param('temp1', sim_param)
    admsim_obj.set_sim_param('temp2', sim_param)
    admsim_obj.set_sim_param('temp3', sim_param)
    admsim_obj.set_sim_param('temp4', sim_param)

    # pprint.pprint(edit_param1)
    res_paths = admsim_obj.amd_sim_threading()
    pprint.pprint(res_paths)

    return None


def test_AdmResult():

    adm_path = r'..\tests\car_adm_sim\braking_brake.adm'
    admfd_obj = AdmFileData(adm_path)
    admfd_obj.updata_dir(r'..\tests\car_adm_sim\temp')
    adm_path = admfd_obj.new_adm_path
    # return None
    sim_param = {'simtype':CAR, 'samplerate':None, 'simtime':None, 'step':None, 
        'version':'2017.2', 'simlimit':60}

    value_cmd = """
    $$car_spring.k_gain
    TR_Front_Suspension.nsl_ride_spring:255:0
    TR_Front_Suspension.nsr_ride_spring:255:1
    TR_Rear_Suspension.nsl_ride_spring:255:2
    TR_Rear_Suspension.nsr_ride_spring:255:3
    """
    
    edit_param = {
        'value_edit': {'value_cmd': value_cmd, 'list1d_value':[1,1,1,1]},
        'str_edit'  : {'str_cmd':None, 'list1d_str':None},
        'load_edit' : {'spline_ids': None, 'list2d': None, 'samplerate': None}
    }

    params = {
        'block_size':{'u':128, 'l':128},
        'hz_range':[0,50],
        'docx_path':r'..\tests\car_adm_sim\temp\dmc_test.docx',
    }
    csv_path = params['docx_path'][:-4]+'csv'

    values_selects = [0, 1, 2, 3]
    values_gain    = [0.2, 0.2, 0.2, 0.2]
    strs_selects   = None
    req_params = {
        'reqs' : ['nsl_ride_spring_data', 'nsr_ride_spring_data', 'nsl_ride_spring_data', 'nsr_ride_spring_data', 'vas_steering_demand_data'],
        'comps': ['displacement_front', 'displacement_front', 'displacement_rear', 'displacement_rear', 'value'],
        'nrange':[3,None],
        'nchannel':None,
    }
    max_threading = 4
    is_str_Cal = False
    # =========================修改
    admparam_obj = AdmParam(edit_param)
    # admparam_obj.set_values_gain_2(values_selects, values_gain)
    admparam_obj.set_value_orthogonal(values_selects, values_gain)
    admparam_obj.set_strs_n(strs_selects, is_str_Cal)
    edit_params = admparam_obj.create_edit_params(base_name='m')

    # =========================计算
    admsim_obj = AdmSimControl(adm_path)
    for sub_name in edit_params:
        admsim_obj.set_sub_dir(sub_name)
        admsim_obj.set_adm_edit(sub_name, edit_params[sub_name])
        admsim_obj.set_sim_param(sub_name, sim_param)
    return None
    admsim_obj.amd_sim_threading(max_threading)
    res_paths = admsim_obj.res_paths

    # =========================res读取
    admres_obj = AdmResult()
    admres_obj.read_res_paths(res_paths, req_params)
    result_compare = admres_obj.create_pdf(edit_params, params, lower_name='m')
    admres_obj.parse_result_compare(csv_path)

    return None


if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    # test_AdmEditData()
    # test_admsim()

    test_AdmResult()