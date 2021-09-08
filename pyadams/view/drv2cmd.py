"""
    python version : 3.7
    Adams version 2017.2
    注明:
        2017.2 与 2019cmd命令有兼容问题
    用途：
        读取 femfat-lab 虚拟迭代生成的drv文件
        将数据转化为 cmd 控制命令加载
    主函数:
        drv2cmd
"""

from pyadams.file import result
DataModel = result.DataModel


SPLINE_EDIT = '''
data_element modify spline &
 spline=.{}.{} &
 x={} &
 y={} &
 linear_extrapolate=no &
 units=no_units &
 comments=""
'''

SPLINE_CREATE = '''
data_element create spline &
 spline=.{}.{} &
 x={} &
 y={} &
 linear_extrapolate=no &
 units=no_units &
 comments=""
'''

def cmd_spline_edit(model_name,spline_name,xlist,ylist):
    '''
        生成cmd命令
        编辑 adams 中的 spline曲线
    '''
    if model_name[0] == '.':
        model_name = model_name[1:]
    if spline_name[0] == '.':
        spline_name = spline_name[1:]
    xstr = translate_list(xlist)
    ystr = translate_list(ylist)
    str1 = SPLINE_EDIT.format(model_name,spline_name,xstr,ystr)
    return str1

def cmd_spline_create(model_name,spline_name,xlist,ylist):
    '''
        生成cmd命令
        创建 adams 中的 spline曲线
    '''
    if model_name[0] == '.':
        model_name = model_name[1:]
    if spline_name[0] == '.':
        spline_name = spline_name[1:]
    xstr = translate_list(xlist)
    ystr = translate_list(ylist)
    str1 = SPLINE_CREATE.format(model_name,spline_name,xstr,ystr)
    return str1

def translate_list(lines):
    str1 = ', '.join([str(n) for n in lines])
    return str1

def drv2cmd(cmdpath, model_name, drv_path, spline_names, reqs=None, comps=None, nrange=None, isEdit=True):
    """
        读取drv数据，转化并写成cmd加载数据

        cmdpath : 目标路径
        model_name ： 模型名称 包含.  例如： '.six_dof_rig_421'
        drv_path : drv文件路径 ， drv为femfat-lab 加载数据文件，格式rpc3
        spline_names : spline 名称列表

    """
    dataobj = DataModel('drv2cmd')
    dataobj.new_file(drv_path, 'drv')
    
    if dataobj.file_types['drv'] in ['res', 'rsp']:
        dataobj['drv'].set_reqs_comps(reqs, comps)
        
    dataobj['drv'].set_line_ranges(nrange)
    dataobj['drv'].read_file()
    
    data_list = dataobj['drv'].get_data()
    samplerate = dataobj['drv'].get_samplerate()

    # data_list , dic , name_channels = result.rsp_read(drv_path)
    if isEdit:
        cmd_spline_run = cmd_spline_edit
    else:
        cmd_spline_run = cmd_spline_create

    x = [n/samplerate for n in range(len(data_list[0]))]

    with open(cmdpath,'w') as f:
        for y, name in zip(data_list, spline_names):
            str1 = cmd_spline_run(model_name, name, x, y)
            f.write(str1)

    return None


# ======================================================================
# ======================================================================
# 测试

def test_drv2cmd_rpc():
    pass
    cmdpath = r'..\tests\view_drv2cmd\drv_rpc.cmd'
    model_name = '.MODEL_1'
    drv_path = r'..\tests\view_drv2cmd\test_drv2cmd.DRV'
    spline_names = ['spline_1','spline_2','spline_3']

    drv2cmd(cmdpath, model_name, drv_path, spline_names, reqs=None, comps=None, nrange=None)

    return None

def test_drv2cmd_res():
    pass
    cmdpath = r'..\tests\view_drv2cmd\drv_res.cmd'
    model_name = '.MODEL_1'
    drv_path = r'..\tests\file_result\break_brake.res'
    spline_names = ['spline_1','spline_2','spline_3']

    reqs = ['ACC_FL','ACC_FL','ACC_FL','ACC_FR','ACC_FR','ACC_FR']
    comps = ['X','Y','Z','X','Y','Z']
    nrange = [3, None]

    drv2cmd(cmdpath, model_name, drv_path, spline_names, reqs=reqs, comps=comps, nrange=nrange)


if __name__ == '__main__':

    # # 421 加载
    # cmdpath = r'D:\document\FEMFAT_LAB\dof6_421_flex\drv.cmd'
    # samplerate = 512
    # model_name = '.six_dof_rig_421'
    # drv_path = r'D:\document\FEMFAT_LAB\dof6_421_flex\cuoban_acc_1p5_50hz_8.DRV'
    # spline_names = ['spline_x','spline_y_f','spline_y_r','spline_z_fl','spline_z_fr','spline_z_rl','spline_z_rr']
    # drv2cmd(cmdpath,samplerate,model_name,drv_path,spline_names)

    # # mast台架加载
    # cmdpath = r'D:\document\FEMFAT_LAB\mast\drv.cmd'
    # samplerate = 512
    # model_name = '.six_dof_rig_stewart'
    # drv_path = r'D:\document\FEMFAT_LAB\mast\cuoban_acc_1p5_50hz_5.DRV'
    # spline_names = ['spline_1','spline_2','spline_3','spline_4','spline_5','spline_6']  
    # drv2cmd(cmdpath,samplerate,model_name,drv_path,spline_names)

    test_drv2cmd_rpc()
    test_drv2cmd_res()


