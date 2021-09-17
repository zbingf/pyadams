'''
    python version : 3.7
    Adams version : 2017.2

    通过windows cmd 调用adams
    2021/03  更改程序终止方式, 使用psutil 进行终止 pid
    

'''
import os
import re
import sys
import subprocess
import psutil
import glob
import time

import os.path
import logging
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


ADAMS_VERSION='adams2017_2'
SIM_LIMIT_MINUTE = 60 # 仿真时限 min

# 定位bat路径
def bat_path_search(bat_name): 
    '''
        定位bat路径
        用于cmd调用
    '''
    # file_set_path = __file__[:-3]+'.set' # 文件路几个保存
    file_set_path = PY_FILE_NAME+'.set' # 文件路几个保存
    if os.path.exists(file_set_path):
        with open(file_set_path, 'r') as f:
            fullPath = f.read()
        if os.path.exists(fullPath):
            if re.search(r'\s',fullPath):
                fullPath = '\"'+fullPath+'\"'
            return fullPath

    fullPath=[]
    for npath in range(0,5):
        # 5级 文件夹搜索 adams放置路径
        for n in ['C','D','E','F','G','H','I','J']:
            locPath=r'\*'*npath
            searchPath=r'{}:{}\MSC.Software\*\*\bin\{}.bat'.format(n,locPath,bat_name)
            fullSearch=glob.glob(searchPath)
            if fullSearch:
                fullPath=fullSearch[0]
                break
        if fullPath:
            break
    # print(fullPath)

    if not fullPath: # 未找到文件
        import tkinter.filedialog
        fullPath = tkinter.filedialog.askopenfilename(filetypes = (('adams bat调用路径','bat'),))
        assert fullPath, 'error admas bat path'
        with open(file_set_path, 'w') as f:
            f.write(fullPath)

    # 路径如果存在空格, 批处理调用
    # 则需加上双引号
    if re.search(r'\s',fullPath):
        fullPath = '\"'+fullPath+'\"'

    return fullPath


# 通过判断 msg内容 来鉴别仿真是否完结
def is_sim_success(res_path, sim_minute): 
    ''' 
        通过判断 msg内容 来鉴别仿真是否完结
        res_path路径为Adams仿真路径
        sim_minute 为仿真允许时间，单位 分钟min
    '''
    msg_path = res_path[0:-3]+r'msg'
    n = 1
    isSuccess = False
    while True:
        try:
            # print('is calling')
            with open(msg_path, 'r') as msgObj:
                listStr = msgObj.readlines()
                for temp in listStr:
                    if 'finished' in temp.lower().replace(' ','')[:len('finished')]:
                        # print('is_sim_success call Finished')
                        isSuccess = True
                        break
            if isSuccess:
                break
        except:
            pass
        time.sleep(1)
        n += 1
        if n > sim_minute*60:
            logger.warning("进程计算超时, 停止计算")
            break
    return isSuccess


# 运行bat进行计算
def call_bat_sim(bat_path, res_path, simlimit=SIM_LIMIT_MINUTE):
    """
        subprocess.Popen 运行bat_path
        通过cmdlink.is_sim_success进行判定是否计算完成
    """

    msg_path = res_path[0:-3]+r'msg'
    try:
        os.remove(msg_path)
    except:
        pass

    proc = subprocess.Popen(bat_path)
    main_pid = proc.pid
    try:
        # 判定是否运行完毕，并结束进程
        if is_sim_success(res_path, simlimit):
            # 'msg' 信息到 finish即结束
            logger.info(f'“msg”信息检测到 finished 判定结束, 关闭子程序')
            logger.info(f'Res Path : {res_path}')
            try:
                # 防止计算过快
                p = psutil.Process(main_pid)
                p_childrens =p.children() 
                logger.info(f'计算程序: {p}')
                logger.info(f'计算子程序: {p_childrens}')
                for p_chr in p_childrens:
                    # print(cp.pid)
                    p_chr.kill()    
                proc.kill()
                logger.info(f'进程（id: {main_pid}）及子程序结束')
            except:
                logger.info('进程本身已经终止,返回res_path')
                return res_path

        return res_path
    except:
        # print('error in kiil_pid')
        logger.warning(f'仿真进程（id{main_pid}）有问题,res_path返回False')
    
    return False


# 调用adams模型 运行cmd文件
def cmd_file_send(cmd_path=None, mode='car', res_path=None, minutes=30): 
    """
        cmd文件发送
        mode 计算模式选择： 'car' 'view' ；默认'car'
        cmd_path cmd文件路径
        minutes 运行时常
    """
    bat_path = bat_path_search(ADAMS_VERSION)
    mode_dict = {
        'car': 'acar', 
        'view': 'aview'}

    if cmd_path == None: # 不运行cmd文件 测试用
        cmds = bat_path+f' {mode_dict[mode.lower()]} ru-st b exit'
        subprocess.call(cmds)
        return False
    else:
        if os.path.exists(cmd_path):
            # 文件存在
            cmds = bat_path+f' {mode_dict[mode.lower()]} ru-st b '+str(cmd_path)+' exit'
            if res_path == None:
                subprocess.call(cmds)
            else:
                # res路径存在
                call_bat_sim(cmds, res_path, simlimit=SIM_LIMIT_MINUTE)
            return True
        else:
            logger.error(f"文件不存在: {cmd_path}")
            return False


# 调用并运行cmd命令
def cmd_send(cmds, cmd_path=None, mode='car', savefile=False, res_path=None, minutes=30): 
    """
        cmds 命令行 字符串或列表格式
        cmd_path 目标存储文件路径
        mode 计算模式选择： 'car' 'view' ；默认'car'
        savefile 是否保存 cmd_path
        minutes 分析时长（分钟）限制 默认10分钟关闭
    """
    if cmd_path==None:
        cmd_path=os.getcwd()+'\\'+'temp.cmd'
    with open(cmd_path,'w') as f:
        if isinstance(cmds,list):
            for line in cmds:
                f.write(line)
        else:
            f.write(cmds)
    
    if cmd_file_send(cmd_path=cmd_path, mode=mode, res_path=res_path, minutes=minutes):
        if not savefile:
            # 不保存cmd文件
            os.remove(cmd_path)
        return True
    else:
        if not savefile:
            os.remove(cmd_path)
        return False

# -----------------------------------------
# 测试
def test_cmd_send():
    pass

    cmd_path = os.path.abspath(r'..\tests\call_cmdlink\test_view.cmd')
    os.chdir(os.path.dirname(cmd_path))
    cmd_send(f'file command read file_name="{cmd_path}"',mode='view')



if __name__ == '__main__':
    '''
        测试
    '''
    # print('adams_cmdlink')

    # test_cmd_send()

    pass

    print(bat_path_search('adams20191'))
