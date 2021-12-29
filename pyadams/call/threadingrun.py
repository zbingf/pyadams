"""
    多线程计算模块
    ADAMS支持多进程计算, 故适用多线程运行adm文件, 即可实现;

    2021.12 : 增加注释
"""

import threading
import copy, os, time, shutil, re
import os.path
import logging
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


# =========================================
# =========================================


# 数值列表数据，四舍五入
listround = lambda list1, n: [round(v,n) for v in list1]

# 保留非空格数据并转为小写
strcal = lambda str1: re.sub(r'\s','',str1).lower() 

# 多线程初始设置,设置线程上限, 默认设置
threadmax = threading.BoundedSemaphore(4)   

# Car模型，在进行多线程计算前，进行文件复制
def threading_car_files(sim_path, n, prefix='thread'): 
    """
        在sim_path基础上复制文件到prefix前缀名称的文件夹内

        参数:
            sim_path :  adm模型路径
            n : 第n次threading调用
            在 sim_path 路径下创建新的子文件夹: thread_n
            复制相关文件：
                acf、bat、xml、mtx
    """
    old_dir = os.path.dirname(sim_path)              # 旧路径
    new_dir = os.path.join(old_dir, f'{prefix}_{n}') # 新路径
    try:
        os.mkdir(new_dir)
        logger.info(f'创建文件夹: {new_dir}')
    except:
        logger.info(f'文件夹创建失败, 先移除文件夹, 再重新创建: {new_dir}')
        shutil.rmtree(new_dir)
        os.mkdir(new_dir)

    # 
    # 文件复制
    acf_path  = sim_path[:-3]+'acf'
    bat_path  = sim_path[:-3]+'bat'
    xml_path  = sim_path[:-3]+'xml'
    old_paths = [sim_path, acf_path, bat_path, xml_path] # 复制目标
    new_paths = []
    for path in old_paths:
        new_path = os.path.join(new_dir, os.path.basename(path))
        new_paths.append(new_path)
        try:
            shutil.copy(path,new_path)
        except:
            logger.warning(f'threading_car_files: 文件：{path} 不存在，无法复制到目标路径')

    new_sim_path = new_paths[0]

    # ==========================================
    # 柔性体文件复制
    # 注明：Adams 2019 与 2017.2 生成的 柔性体文件不一样
    # 输入 old_dir 、 new_sim_path
    # adm文件读取
    with open(new_sim_path, 'r') as f:
        lines = f.readlines()
    # 柔性体mtxs文件查找
    mtxs = []
    for line in lines:
        line = strcal(line)
        re1 = re.match(r',file=(.*\.mtx)\Z', line)
        if re1:
            mtxs.append(re1.group(1))
    # 柔性体文件复制
    mtx_names = set(mtxs)
    for name in mtx_names:
        old_path = os.path.join(old_dir, name)
        shutil.copy(old_path, new_dir)
    # ==========================================


    return new_sim_path, new_dir



# 灵敏度-多线程计算
def threading_sim_doe(func, params, sim_range=0.1, simlen=4, dtime=5, threadmax=threadmax): 
    """
        调用 thread 库，进行多线程计算

        单一变量更改试验设计
        func    目标计算函数
        params      dict    func的参数输入
        sim_range   float   目标参数调整比例
        simlen      int     同时计算数量
        dtime       float   多进程调用-间隔时间 单位：秒

        其中：params['values'] 目标参数 格式：list 例如：[1, 1, 1, 1]
        
        注：      
        1、 多线程设置提前定义，设置多线程数上限
            threadmax = threading.BoundedSemaphore(4)   
        2、 func 函数结尾需要释放线程 
            threadmax.release()
    """
    nround = 3
    params['values'] = listround(params['values'], nround) # 去小数

    threads = []
    thread = threading.Thread(target=func, args=(params,))
    thread.start()
    threads.append(thread)
    threadmax.acquire()
    target_para = copy.deepcopy(params['values'])

    for num,value in enumerate(target_para):
        new_params = copy.deepcopy(params)
        
        time.sleep(dtime)
        listtemp = copy.deepcopy(params['values'])
        listtemp[num] = params['values'][num] * (1+sim_range)
        # print(new_params['values'])
        new_params['values'] = listround(listtemp, nround)
        thread = threading.Thread(target=func, args=(new_params, ))
        thread.start()
        threads.append(thread)
        threadmax.acquire()

        time.sleep(dtime)
        listtemp = copy.deepcopy(params['values'])
        listtemp[num] = params['values'][num] * (1-sim_range)
        new_params['values'] = listround(listtemp, nround)
        thread = threading.Thread(target=func, args=(new_params, ))
        thread.start()
        threads.append(thread)
        threadmax.acquire()
    
    while threads:
        threads.pop().join()

    return True

# 装饰目标函数
def threading_func(func, threadmax=threadmax):
    # 多进程计算调用函数
    # 装饰
    def new_func(*args, **kwargs):
        result = func(*args,**kwargs)
        threadmax.release()
        return result

    return new_func


if __name__ == '__main__':
    pass