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


ADAMS_VERSION = 'adams2017_2'
SIM_LIMIT_MINUTE = 360 # 仿真时限 min


# 定位bat路径
def bat_path_search(bat_name): 
    '''
        定位bat路径
        用于cmd调用
    '''
    
    # --------------------------
    # 现有索引
    # file_set_path = __file__[:-3]+'.set' 
    file_set_path = PY_FILE_NAME+'.set' # 路径索引存储路径
    if os.path.exists(file_set_path):
        with open(file_set_path, 'r') as f:
            fullPath = f.read()

        if os.path.exists(fullPath):
            if re.search(r'\s',fullPath):
                fullPath = '\"'+fullPath+'\"'
            return fullPath

    # --------------------------
    # 重建检索
    fullPath = []
    for npath in range(0,5):
        # 5级 文件夹搜索 adams放置路径
        for n in ['C','D','E','F','G']: # ,'H','I','J'
            locPath = r'\*' * npath
            searchPath = r'{}:{}\MSC.Software\*\*\bin\{}.bat'.format(n,locPath,bat_name)
            fullSearch = glob.glob(searchPath)
            if fullSearch:
                fullPath = fullSearch[0]
                break
        if fullPath:
            break
    # print(fullPath)

    # --------------------------
    # 未找到文件, 手动索引
    if not fullPath: 
        import tkinter.filedialog
        fullPath = tkinter.filedialog.askopenfilename(filetypes = (('adams bat调用路径','bat'),))
        assert fullPath, 'error admas bat path'
        with open(file_set_path, 'w') as f:
            f.write(fullPath)

    # 路径如果存在空格, 批处理调用
    # 则需加上双引号
    if re.search(r'\s',fullPath):
        fullPath = '\"'+fullPath+'\"'

    return fullPath # 字符串


# 检索 View_ana_xxxx.log
def search_log_ana(res_path):

    target_dir = os.path.dirname(res_path)
    log_paths = []
    for file_name in os.listdir(target_dir):
        # log文件
        if re.match('view_ana_\d+\.log', file_name.lower()):
            file_path = os.path.join(target_dir, file_name)
            log_paths.append(file_path)

    return log_paths


# 
def search_target_log_ana_id(res_path):

    target_paths = []
    log_paths = search_log_ana(res_path)
    res_name = os.path.basename(res_path)[:-4].lower()
    for log_path in log_paths:
        with open(log_path, 'r') as f:
            log_str = f.read().lower()

        if re.search('\sout={}\s'.format(res_name), log_str):
            target_paths.append(log_path)
            # print(log_path)

    target_ids = []
    for target_path in target_paths:
        target_id = int(re.match('.*view_ana_(\d+)\.log', target_path.lower()).group(1))

        if is_pid_exist(target_id) and \
            get_pid_name(target_id)=='aview.exe':
            
            target_ids.append(target_id)

    return target_ids


# 进程是否存在
def is_pid_exist(p_id):
    if p_id in psutil.pids():
        return True
    else:
        return False


# 根据进程ID获取进程名称
def get_pid_name(p_id):
    return psutil.Process(p_id).name()


# 终止进程
def kill_pid(p_id):
    return psutil.Process(p_id).kill()



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
def call_bat_sim(bat_path, res_path, simlimit=SIM_LIMIT_MINUTE, true_res_path=None):
    """
        subprocess.Popen 运行bat_path
        通过cmdlink.is_sim_success进行判定是否计算完成
        
        res_path 实际上用于.msg的查找(一般.res与.msg文件名一致)
        true_res_path 实际res路径(用于.res与.msg文件名不一致的情况)
    """
    if true_res_path==None: true_res_path = res_path

    msg_path = res_path[0:-3]+r'msg'
    try:
        os.remove(msg_path)
    except:
        pass

    run_dir = os.path.dirname(res_path)
    proc = subprocess.Popen(bat_path, cwd=run_dir)

    main_pid = proc.pid
    logger.info(f"bat_path: {bat_path} ;\n 运行路径: {run_dir} ;\n main_pid: {main_pid}")

    try:
        # 判定是否运行完毕，并结束进程
        if is_sim_success(res_path, simlimit):

            # 'msg' 信息到 finish即结束
            logger.info(f'“msg”信息检测到 finished 判定结束, 关闭子程序')
            logger.info(f'ResPath : {res_path}')

            try:
                # 防止计算过快
                p = psutil.Process(main_pid)
                p_childrens = p.children() 
                logger.info(f'计算程序: {p}')
                logger.info(f'计算子程序: {p_childrens}')

                # 子进程关闭
                for p_chr in p_childrens:
                    # print(cp.pid)
                    p_chr.kill()

                # 主进程关闭
                proc.kill()
                logger.info(f'进程（id: {main_pid}）及子程序结束')

                # 2021.12.29新增 
                # 2017.1 ADAMS view 程序
                aview_ids = search_target_log_ana_id(true_res_path)
                for aview_id in aview_ids:
                    kill_pid(aview_id)
                    logger.info(f'进程（aview_id: {aview_id}）结束')

            except:
                logger.info(f'进程本身已经终止,返回res_path: {res_path}')
                return res_path

        return res_path
    except:
        # print('error in kiil_pid')
        logger.warning(f'仿真进程（id{main_pid}）有问题,res_path返回False')
    
    return False


# 调用adams模型 运行cmd文件
def cmd_file_send(cmd_path=None, mode='car', 
        res_path=None, minutes=SIM_LIMIT_MINUTE, true_res_path=None): 
    """
        cmd文件发送
        mode 计算模式选择： 'car' 'view' ；默认'car'
        cmd_path cmd文件路径
        minutes 运行时常限制
    """
    bat_path = bat_path_search(ADAMS_VERSION)
    if bat_path[0] == bat_path[-1] == "\"" or \
        bat_path[0] == bat_path[-1] == "\'" :
        bat_path = bat_path[1:-1]

    mode_dict = {
        'car': 'acar', 
        'view': 'aview'}

    if cmd_path == None: # 不运行cmd文件 测试用
        cmds = f'"{bat_path}" {mode_dict[mode.lower()]} ru-st b exit'
        subprocess.call(cmds)
        return False
    else:
        if os.path.exists(cmd_path):
            # 文件存在
            cmd_path = os.path.abspath(cmd_path) # 文件校正
            # 调用命名生成
            cmds = f'"{bat_path}" {mode_dict[mode.lower()]} ru-st b "{cmd_path}" exit'
            if res_path == None:
                # res路径为空, 直接调用命令
                subprocess.call(cmds)
            else:
                # res路径不为空, 将cmds命令保存文bat文件 
                # 创建bat_path 并通过 call_bat_sim 调用计算
                # 2021.12.29
                cmd_bat_path = cmd_path[:-3]+'bat'
                with open(cmd_bat_path, 'w') as f: f.write(cmds)
                # 
                call_bat_sim(cmd_bat_path, res_path, simlimit=minutes, true_res_path=true_res_path)

            return True
        else:
            logger.error(f"文件不存在: {cmd_path}")
            return False


# 调用并运行cmd命令
def cmd_send(cmds, cmd_path=None, mode='car', 
        savefile=False, res_path=None, 
        minutes=SIM_LIMIT_MINUTE, true_res_path=None): 
    """
        cmds 命令行 字符串或列表格式
        cmd_path 目标存储文件路径
        mode 计算模式选择： 'car' 'view' ；默认'car'
        savefile 是否保存 cmd_path
        minutes 分析时长（分钟）限制 默认10分钟关闭
    """
    if cmd_path==None:
        cmd_path = os.path.join(os.getcwd(), 'temp.cmd')
        # cmd_path=os.getcwd()+'\\'+'temp.cmd'

    with open(cmd_path, 'w') as f:
        if isinstance(cmds, list):
            for line in cmds:
                f.write(line)
        else:
            f.write(cmds)
    
    if cmd_file_send(cmd_path=cmd_path, mode=mode, res_path=res_path, 
            minutes=minutes, true_res_path=true_res_path):
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
