"""
    用户关联计算模块
    基于已有计算数据(PDI伪损伤数据)进行处理
        数据格式:
        pdi_dic = {
            slope       : [float, float, ...]  # 长度为通道数 # 非必要数据
            rms         : [float, float, ...]  # 长度为通道数 # 非必要数据
            intercept   : [float, float, ...]  # 长度为通道数 # 非必要数据
            min         : [float, float, ...]  # 长度为通道数 # 非必要数据
            max         : [float, float, ...]  # 长度为通道数 # 非必要数据
            damage      : [float, float, ...]  # 长度为通道数 !!!!!!!!!!!!!
            testname    : str                  # 非必要数据
            chantitle   : [str, str, ...]      # 长度为通道数 !!!!!!!!!!!!!
            samplerate  : [float, float, ...]  # 长度为通道数 # 非必要数据
            block_size  : int                  # 非必要数据
            hz_range    : [float, float]       # 非必要数据
        }
    算法: 使用粒子群算法(PSO)
"""

import tkinter.filedialog
import os
import json
import matplotlib.pyplot as plt
import logging
# logging.basicConfig(level=logging.INFO)   # logging设置
logger = logging.getLogger('cal_road_correlation')

import pyadams.datacal.optimization_pso as pso


class RoadCorrelation:
    """
            用于用户关联
    """
    def __init__(self):
        """
            
        """
        self.data = {}
        self.channel_weight = None

    def read_target_pdi_path(self, paths=None):
        """
            目标工况读取解析
        """
        if paths == None:
            tkobj = tkinter.Tk()
            tkobj.withdraw()
            target_paths = tkinter.filedialog.askopenfilenames(
                filetypes=(('目标PDI数据', '*.json'),),
                title="目标PDI数据-json文件")
            logger.info('target_paths: [\'{}\']'.format('\',\''.join(target_paths)))
        else:
            target_paths = paths

        target_data, target_keys = self.read_pdi_jsons(target_paths)

        # 目标工况伪损伤累加-用于优化计算
        target_pdi = []
        n_channel_damage = len(target_data[target_keys[0]]['damage'])
        for n in range(n_channel_damage):
            s = 0
            for key in target_keys:
                s += target_data[key]['damage'][n]
            target_pdi.append(s)

        # 累加前 - 各工况数据
        target_pdi_singles = []
        for key in target_keys:
            damage = target_data[key]['damage']
            target_pdi_singles.append(damage)

        target_channel_names = target_data[target_keys[0]]['chantitle']

        self.target_data            = target_data
        self.target_keys            = target_keys
        self.target_channel_names   = target_channel_names
        self.target_pdi             = target_pdi
        self.target_pdi_singles     = target_pdi_singles
        self.target_dir = os.path.dirname(target_paths[0]) # 路径

        return None

    def read_base_pdi_paths(self, paths=None):
        """
            基础工况读取解析
        """
        if paths == None:
            tkobj = tkinter.Tk()
            tkobj.withdraw()
            base_paths = tkinter.filedialog.askopenfilenames(
                filetypes=(('各工况PDI数据', '*.json'),),
                title="基础工况PDI数据-json文件")
            logger.info('base_paths: [\'{}\']'.format('\',\''.join(base_paths)))
        else:
            base_paths = paths

        base_data, base_keys = self.read_pdi_jsons(base_paths)

        base_pdi = []
        for base_key in base_keys:
            damage = base_data[base_key]['damage']
            base_pdi.append(damage)

        self.base_data  = base_data
        self.base_keys  = base_keys
        self.base_channel_names = base_data[base_keys[0]]['chantitle']
        self.base_pdi = base_pdi

        return None

    def base_pdi_csv_write(self, csv_path=None, isOpen=True):
        """
            基础 damage
        """
        if csv_path == None:
            csv_path = 'base_pdi.csv'
            csv_path = os.path.join(self.target_dir, csv_path)

        RoadCorrelation.pdi_data_csv_write(csv_path, 
            channle_names=self.base_channel_names,
            file_names=self.base_keys,
            data_pdis=self.base_pdi
            )

        if isOpen:
            os.system(csv_path)

        return csv_path

    def target_pdi_csv_write(self, csv_path=None, isOpen=True):
        """
            目标工况 damage 显示
        """
        if csv_path == None:
            csv_path = 'target_pdi.csv'
            csv_path = os.path.join(self.target_dir, csv_path)

        RoadCorrelation.pdi_data_csv_write(csv_path, 
            channle_names=self.target_channel_names,
            file_names=self.target_keys,
            data_pdis=self.target_pdi_singles
            )

        if isOpen:
            os.system(csv_path)

        return csv_path

    def func_csv_write(self, x, csv_path=None, isOpen=True):
        """
            计算结果输出
        """
        if csv_path == None:
            csv_path = 'func_csv.csv'
            csv_path = os.path.join(self.target_dir, csv_path)

        result, pdi_rels = RoadCorrelation.cal_func(x, self.base_pdi, self.target_pdi, 
            self.channel_weight, isShow=True)
        channel_names = self.base_channel_names
        with open(csv_path, 'w') as f:

            base_title = ','.join(self.base_keys)
            target_title = ','.join(self.target_keys)
            x_str = ','.join([str(value) for value in x])

            f.write(f',,工况,{base_title}\n')
            f.write(f',,配比,{x_str}\n')
            f.write(f',,结果,{result},{target_title}\n')

            f.write('channel_name,relative_pdi\n')
            for channel_name, pdi_rel in zip(channel_names, pdi_rels):
                f.write(f'{channel_name},{pdi_rel},\n')

        with open(csv_path, 'r') as f:
            func_csv_str = f.read()

        logger.info(f'\nfunc_csv_str:{func_csv_str}')

        if isOpen:
            os.popen(csv_path)

        return None

    def set_lb(self, lb):

        if not isinstance(lb, list):
            lb = [lb for name in self.base_keys]
        
        self.lb = lb
        return lb

    def set_ub(self, ub):

        if not isinstance(ub, list):
            ub = [ub for name in self.base_keys]
        
        self.ub = ub
        return ub

    def set_channel_weight(self, channel_weight):
        # 通道权重
        if not isinstance(channel_weight, list):
            channel_weight = [channel_weight for n in self.target_pdi]
        
        self.channel_weight = channel_weight
        return channel_weight

    @staticmethod
    def read_pdi_jsons(paths):
        if isinstance(paths, str):
            paths = [paths]
        data_dic = {}
        keys = []
        for path in paths:
            with open(path, 'r') as f:
                dic1 = json.load(f)
            key = os.path.basename(path)[:-5]
            keys.append(key)
            data_dic[key] = dic1

        return data_dic, keys

    @staticmethod
    def pdi_data_csv_write(csv_path, channle_names, file_names, data_pdis):
        """
            csv_path        str             目标存储路径
            channle_names   [str, str,..]   各通道名称
            file_names      [str, str,..]   各工况名称名
            data_pdis       [[chan1,chan2,chan3], [chan1,chan2, ]] 数据存储
        """
        n_file = len(file_names)
        n_channel = len(channle_names)

        with open(csv_path, 'w') as f:
            title = ','.join(file_names)
            f.write(f'channel,{title}\n')
            
            for n, channel_name in enumerate(channle_names):
                f.write(channel_name+',')
                list1 = [str(data_pdis[num][n]) for num in range(n_file)]
                f.write(','.join(list1))
                f.write('\n')

        return csv_path

    @staticmethod
    def cal_func(x, base_pdi, target_pdi, channel_weight=None, isShow=False):
        """
            目标计算函数
        """
        cal_ts = []
        tar_ts = target_pdi

        if channel_weight==None:
            # 各通道权重
            channel_weight = [1 for n in tar_ts]

        for loc_chan in range(len(target_pdi)):

            s = 0
            for loc_x, value in enumerate(x):
                s += value * base_pdi[loc_x][loc_chan]

            cal_ts.append(s)

        pdi_rels = []
        for cal_t, tar_t in zip(cal_ts, tar_ts):
            pdi_rel = cal_t / tar_t
            pdi_rels.append(pdi_rel)

        result = 0
        for pdi_rel, gain in zip(pdi_rels, channel_weight):
            if pdi_rel < 0.5:
                result += ((1-pdi_rel)*gain*2)**2
            elif pdi_rel > 2:
                result += ((1-pdi_rel)*gain*2)**2
            else:
                result += ((1-pdi_rel)*gain)**2

        # result = sum( [((1-pdi_rel)*gain)**2 for pdi_rel, gain in zip(pdi_rels, channel_weight)] )
        if isShow:
            # print(f'result:{result}')
            # print('PDI')
            # [print(value) for value in pdi_rels]
            return result, pdi_rels

        return result

    @staticmethod
    def cal_pso(obj, isShow=True):
        """
            粒子群计算
        """
        

        func = RoadCorrelation.cal_func
        lb = obj.lb
        ub = obj.ub
        g, fg, g_record, fg_record = pso.pso(func, lb, ub, 
            ieqcons=[], f_ieqcons=None, 
            args=(obj.base_pdi, obj.target_pdi, obj.channel_weight), kwargs={}, 
            swarmsize=200, omega=0.5, phip=0.5, phig=0.5, maxiter=100, 
            minstep=1e-8, minfunc=1e-8, debug=False, processes=1,
            particle_output=False)

        
        
        
        plt.rcParams['savefig.dpi'] = 500
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        size_gain = 0.6
        linewidth = 1
        plt.rcParams['figure.figsize'] = [16*size_gain, 9*size_gain]    # 尺寸

        fig = plt.figure(1)
        plt.subplot(211)
        plt.plot(list(range(len(g_record))), g_record)
        plt.xlabel('迭代次数')
        plt.ylabel('配比')
        plt.legend(obj.base_keys)
        plt.subplot(212)
        plt.plot(list(range(len(fg_record))), fg_record)
        plt.xlabel('迭代次数')
        plt.ylabel('目标值')
        plt.tight_layout()
        
        fig_path = os.path.join(obj.target_dir, 'result.png')
        fig.savefig(fig_path)
        if isShow:
            plt.show()
        
        fig.clf()   

        logger.info(f'fig_path:{fig_path}')

        return g, fg, obj


def test_RoadCorrelation():
    # 
    base_paths = ['../tests/car_cal_road_correlation/accel_gs_pdi_1.json','../tests/car_cal_road_correlation/accel_gs_pdi_2.json']
    target_paths = ['../tests/car_cal_road_correlation/accel_gs_pdi_full.json']
    # base_paths = None
    # target_paths = None
    base_paths = [os.path.abspath(path) for path in base_paths]
    target_paths = [os.path.abspath(path) for path in target_paths]

    obj = RoadCorrelation()
    obj.read_base_pdi_paths(base_paths)
    obj.read_target_pdi_path(target_paths)
    obj.set_lb(0)
    obj.set_ub(10)
    obj.set_channel_weight(1)
    base_csv_path = obj.base_pdi_csv_write(isOpen=False)
    target_csv_path = obj.target_pdi_csv_write(isOpen=False)
    g, fg, obj = RoadCorrelation.cal_pso(obj, isShow=False)
    func_csv_path = obj.func_csv_write(g, isOpen=False)
        


if __name__ == '__main__':
    # 
    test_RoadCorrelation()
