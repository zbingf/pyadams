"""
    bdf Nastran有限元格式
    根据硬点数据,通道数据,直接生成bdf文件
    用于模态叠加计算
    2021/08/28
"""
import re
import os
import json
from pyadams.file import result
DataModel = result.DataModel


# 路面配置读取
set_path = os.path.join(os.path.dirname(__file__), 'bdf_transient_modal.json')
with open(set_path, 'r', encoding='utf-8') as f: bdf_set = json.load(f)

# # 初始值设置
# GRID_ID     = 99000000
# RBE2_ID     = 98000000
# # LOADCOL ID编号
# EIGRL_ID    = 11000
# TSTEP_ID    = 11100
# TABDMP1_ID  = 11200
# DLOAD_ID    = 11300
# TABLED1_ID  = 12000
# FORCE_ID    = 13000
# TLOAD1_ID   = 14000
# COMP_ID     = 15000

# 初始值设置
GRID_ID     = bdf_set['TRANSIENT_MODAL']['GRID_ID']
RBE2_ID     = bdf_set['TRANSIENT_MODAL']['RBE2_ID']
# LOADCOL ID编号
EIGRL_ID    = bdf_set['TRANSIENT_MODAL']['EIGRL_ID']
TSTEP_ID    = bdf_set['TRANSIENT_MODAL']['TSTEP_ID']
TABDMP1_ID  = bdf_set['TRANSIENT_MODAL']['TABDMP1_ID']
DLOAD_ID    = bdf_set['TRANSIENT_MODAL']['DLOAD_ID']
TABLED1_ID  = bdf_set['TRANSIENT_MODAL']['TABLED1_ID']
FORCE_ID    = bdf_set['TRANSIENT_MODAL']['FORCE_ID']
TLOAD1_ID   = bdf_set['TRANSIENT_MODAL']['TLOAD1_ID']
COMP_ID     = bdf_set['TRANSIENT_MODAL']['COMP_ID']
LOADSTEP_ID = bdf_set['TRANSIENT_MODAL']['LOADSTEP_ID']

HMNAME      = '$HMNAME'.ljust(8)
HWCOLOR     = '$HWCOLOR'.ljust(8)
HMMOVE      = '$HMMOVE'.ljust(8)
COMP        = 'COMP'.ljust(8)
LOADCOL     = 'LOADCOL'.ljust(8)
EMPTY       = ' '.ljust(8)
FORCE       = 'FORCE'.ljust(8)
MOMENT      = 'MOMENT'.ljust(8)
GRID        = 'GRID'.ljust(8)
TLOAD1      = 'TLOAD1'.ljust(8)
LOADSTEP    = 'LOADSTEP'.ljust(8)
VX          = '1.0,0.0,0.0'
VY          = '0.0,1.0,0.0'
VZ          = '0.0,0.0,1.0'
V_DIC       = {1:VX, 2:VY, 3:VZ}
FORCE_DIC   = {1:'Fx', 2:'Fy', 3:'Fz', 4:'Tx', 5:'Ty', 6:'Tz'}

# ----------------子函数---------------------
strint      = lambda value: str(value).rjust(8)
strlower    = lambda str1: re.sub(r'\s', '', str1).lower()
list_id     = lambda list1, init_n : [n+init_n+1 for n in range(len(list1))]

# 列表数据转化
def str_list_change(prefix, list1, nlen):
    """
        将数据转化为规则多行数据
        prefix 前缀
        list1   单列数据
        nlen    每行数据长度
    """
    isStart = True
    list_2  = []
    for loc, value in enumerate(list1):
        if divmod(loc, nlen)[1] == 0:
            if isStart:
                line, isStart = [value], False
                continue
            list_2.append(line)
            line = [value]
            continue
        line.append(value)
    list_2.append(line)

    strs = [prefix + ','.join([str(nid) for nid in line]) for line in list_2]

    return '\n'.join(strs)

# LOADCOL 开头
def loadcol_title_str(name, nid, color=5):
    """
        LOADCOL 开头
    """
    line1 = HMNAME+LOADCOL+EMPTY+strint(nid)+f'"{name}"'
    line2 = HWCOLOR+LOADCOL+EMPTY+strint(nid)+strint(color)
    return '\n'.join([line1, line2])

# LOADSTEP 开头
def loadstep_title_str(name, nid):
    """
        LOADSTEP 开头
    """
    line1 = HMNAME+LOADSTEP+EMPTY+strint(nid)+f'"{name}"'+f'8'.ljust(8)
    line2 = '$'
    return '\n'.join([line1, line2])

# -------------------------------------------
# GRID 创建
def create_grid_str(nid, x, y, z):

    return f'GRID,{nid},,{x},{y},{z}'

# GRID 批量创建
def create_grid_str_list(nids, xs, ys, zs):

    strs = [create_grid_str(nid,x,y,z) for nid,x,y,z in zip(nids,xs,ys,zs)]
    return '\n'.join(strs)

# RBE2创建
def create_rbe2_str(rbe2_id, grid_id_tar, dof, grid_ids):
    """
        rbe2_id     rbe2的ID号
        grid_id_tar 目标点ID号
        dof         自由度     '123456'表示全约束
        grid_ids    各个连接点ID号 [1,2,...]
    """
    if isinstance(grid_ids, int):grid_ids = [grid_ids]
    
    if len(grid_ids)>2: 
        # 超过两个接点
        line1 = f'RBE2,{rbe2_id},{grid_id_tar},{dof},' + \
                ','.join([str(grid_id) for grid_id in grid_ids[:2]])
        
        line2 = str_list_change('+,', grid_ids[2:], 4)

        return '\n'.join([line1, line2])
    else:
        line1 = f'RBE2,{rbe2_id},{grid_id_tar},{dof},' + \
                ','.join([str(grid_id) for grid_id in grid_ids])

        return line1

# COMP 创建
def create_comp_str(comp_name, comp_id, color=5):
    """
        comp 创建
    """
    line1 = HMNAME+COMP+f' {comp_id} {comp_name}'
    line2 = HWCOLOR+COMP+f' {comp_id} {color}'

    return '\n'.join([line1, line2])

# COMP 单元ID添加
def create_comp_append_str(comp_id, ids):
    line1 = HMMOVE+strint(comp_id)
    line2 = str_list_change('$'.ljust(8), ids, 4)

    return '\n'.join([line1, line2])

# TABLED1 创建
def create_tabled1_str(tabled1_name, tabled1_id, times, values, 
                    color=4):
    """
    """
    line1 = loadcol_title_str(tabled1_name, tabled1_id, color)
    # line1 = HMNAME+LOADCOL+strint(tabled1_id)+f'"{tabled1_name}"'
    # line2 = HWCOLOR+LOADCOL+strint(tabled1_id)+strint(color)
    line3 = f'TABLED1,{tabled1_id},LINEAR,LINEAR'
    
    new_data = []
    for t,v in zip(times, values):
        new_data.extend([t,v])
    line4 = str_list_change('+,', new_data, 8)+',ENDT'

    return '\n'.join([line1, line3, line4])

# FORCE/MOMENT 单位加载
def create_force_unit_str(force_name, force_id, grid_id, v, 
                    color=4):
    """
    """
    line1 = loadcol_title_str(force_name, force_id, color)
    # line1 = HMNAME+LOADCOL+EMPTY+strint(force_id)+f'"{force_name}"'
    # line2 = HWCOLOR+LOADCOL+EMPTY+strint(force_id)+strint(color)
    if v<4:
        line3 = f'FORCE,{force_id},{grid_id},0,1.0,{V_DIC[v]}'
    else:
        line3 = f'MOMENT,{force_id},{grid_id},0,1.0,{V_DIC[v-3]}'

    return '\n'.join([line1, line3])

# TLOAD1 模块
def create_tload1_str(tload1_name, tload1_id, force_id, tabled1_id, 
                    color=5):
    """
    """
    line1 = loadcol_title_str(tload1_name, tload1_id, color)
    # line1 = HMNAME+LOADCOL+EMPTY+strint(force_id)+f'"{force_name}"'
    # line2 = HWCOLOR+LOADCOL+EMPTY+strint(force_id)+strint(color)
    line2 = f'TLOAD1,{tload1_id},{force_id},,LOAD,{tabled1_id}'

    return '\n'.join([line1, line2])

# DLOAD 模块
def create_dload_unit_str(dload_name, dload_id, tload1_ids, 
                        color=5):
    """

    """

    line1 = loadcol_title_str(dload_name, dload_id, color)
    if len(tload1_ids)>3:
        line2 = f'DLOAD,{dload_id},1.0,' +\
                ','.join(['1.0,'+str(nid) for nid in tload1_ids[:3]])
        
        new_strs = ['1.0,'+str(nid) for nid in tload1_ids[3:]]
        
        line2 += '\n'+str_list_change('+,', new_strs, 4)
    else:
        line2 = f'DLOAD,{dload_id},1.0,' +\
                ','.join(['1.0,'+str(nid) for nid in tload1_ids])

    return '\n'.join([line1, line2])

# TSTEP 模块
def create_tstep_one_str(tstep_name, tstep_id, step_len, step_size, 
                    color=5):
    """
    """
    line1 = loadcol_title_str(tstep_name, tstep_id, color)
    line2 = f'TSTEP,{tstep_id},{step_len},{step_size},1,,,,,'
    
    return '\n'.join([line1, line2])    

# TABDMP1 模块 - 未完成
def create_tabdmp1_str(tabdmp1_name, tabdmp1_id, fs=None, ds=None, 
                    d_type='CRIT', color=5):
    """
    """
    line1 = loadcol_title_str(tabdmp1_name, tabdmp1_id, color)
    line2 = f'TABDMP1,{tabdmp1_id},{d_type}'
    line3 = '+,0.0,0.01,100.0,0.01,101,0.1,1000,0.1,'
    line4 = '+,1001,1,3000.0,1,ENDT'
    
    return '\n'.join([line1, line2, line3, line4])


# LOADSTEP 工况加载
LOADSTEP_TM = """
SUBCASE {:>8d}
LABEL   {}
ANALYSIS MTRAN
METHOD(STRUCTURE)           = {}
SDAMPING(STRUCTURE)         = {}
DLOAD                       = {}
TSTEP(TIME)                 = {}
SDISPLACEMENT(PUNCH,REAL)   = ALL
STRESS(OUTPUT2,MODAL)       = YES
"""
LOADSTEP_TM = """
SUBCASE,{:>8d}
LABEL,{}
ANALYSIS,MTRAN
METHOD(STRUCTURE)           = {}
SDAMPING(STRUCTURE)         = {}
DLOAD                       = {}
TSTEP(TIME)                 = {}
SDISPLACEMENT(PUNCH,REAL)   = ALL
STRESS(OUTPUT2,MODAL)       = YES
"""

def create_loadstep_tm_str(loadstep_name, loadstep_id, 
        eigrl_id, tabdmp1_id, dload_id, tstep_id):

    line1 = loadstep_title_str(loadstep_name, loadstep_id)
    line2 = LOADSTEP_TM.format(loadstep_id, 
        loadstep_name,
        eigrl_id, tabdmp1_id, dload_id, tstep_id)

    return '\n'.join([line1, line2, ])


# EIGRL 模块 - 未完成
def create_eigrl_str(eigrl_name, eigrl_id, color=5):
    """
    """
    line1 = loadcol_title_str(eigrl_name, eigrl_id, color)
    line2 = f'EIGRL,{eigrl_id},,,30,,,,,MASS'

    return '\n'.join([line1, line2])    


# 模态叠加前处理
class BdfTransientModalPre:
    """
        模态叠加前处理
    """

    def __init__(self, bdf_path, csv_path, rsp_path,
                nranges=None, channels=None):

        self.bdf_path   = bdf_path
        self.csv_path   = csv_path
        self.rsp_path   = rsp_path
        self.nranges    = nranges      # rsp截取范围
        self.channels   = channels     # rsp通道选取
        self.samplerate = None

        self.main_cal()
        self.bdf_write()
        
    def main_cal(self):
        """
            主计算
        """
        names, xs, ys, zs = self.csv_read()
        data              = self.rsp_read()
        samplerate        = self.samplerate

        grid_ids     = list_id(names, GRID_ID)
        grid_id_tar  = GRID_ID
        tabled1_ids  = list_id(data, TABLED1_ID)
        force_ids    = list_id(data, FORCE_ID)
        tload1_ids   = list_id(data, TLOAD1_ID)
        dload_id     = DLOAD_ID 
        rbe2_id      = RBE2_ID 
        rbe2_comp_id = COMP_ID 
        tstep_id     = TSTEP_ID
        tabdmp1_id   = TABDMP1_ID
        eigrl_id     = EIGRL_ID
        loadstep_id  = LOADSTEP_ID

        # 通道名称命名
        load_names = []
        for name in names:
            for n in range(1,7):
                load_names.append(name+'.'+FORCE_DIC[n])

        times = [n/samplerate for n in range(len(data[0]))]

        file_strs = []

        # ===========================
        # GRID
        # 坐标点-GRID-创建
        file_strs += [ create_grid_str(grid_id_tar, 0, 0, 0) ]
        file_strs += [ create_grid_str_list(grid_ids, xs, ys, zs) ]
        
        # ===========================
        # RBE2 comp
        # 创建存放RBE2的comp
        file_strs += [ create_comp_str('RBE2_to_del', rbe2_comp_id, color=2) ]
        # comp中添加rbe2单元
        file_strs += [ create_comp_append_str(rbe2_comp_id, [rbe2_id])]
        # 创建rbe2单元
        file_strs += [ create_rbe2_str(rbe2_id, grid_id_tar, '123456', grid_ids) ]
        
        # ===========================
        # TABLED1 创建
        for load_name, line, tabled1_id in zip(load_names, data, tabled1_ids):
            file_strs += [ create_tabled1_str('tabled1_'+load_name, tabled1_id, times, line, color=3) ]
        
        # ===========================
        # FORCE 创建
        for load_name, force_id, loc in zip(load_names, force_ids, range(len(load_names))):
            n, v = divmod(loc, 6)
            file_strs += [ create_force_unit_str('force_'+load_name, force_id, grid_ids[n], v+1, color=4) ]
        
        # ===========================
        # TLOAD 创建
        for load_name, tload1_id, force_id, tabled1_id in zip(load_names, tload1_ids, force_ids, tabled1_ids):
            file_strs += [ create_tload1_str('tload1_'+load_name, tload1_id, force_id, tabled1_id, color=5) ]

        # ===========================
        # DLOAD 创建
        file_strs += [ create_dload_unit_str('dload_sum', dload_id, tload1_ids, color=8) ]

        # ===========================
        # 
        step_len  = len(data[0])
        step_size = 1.0/samplerate
        file_strs += [ create_tstep_one_str('tstep_tm', tstep_id, step_len, step_size, color=8) ]
        file_strs += [ create_tabdmp1_str('tabdmp1_tm', tabdmp1_id, color=8) ]
        file_strs += [ create_eigrl_str('eigrl_tm', eigrl_id, color=8) ]

        file_strs += [ create_loadstep_tm_str("Train_cal", loadstep_id, 
            eigrl_id, tabdmp1_id, dload_id, tstep_id) ]

        self.file_strs = file_strs

        return file_strs

    def bdf_write(self):
        """
            写入bdf
        """
        with open(self.bdf_path, 'w') as f:
            f.write('\n\n'.join(self.file_strs))

        with open(self.bdf_path[:-3]+'fem', 'w') as f:
            f.write('\n\n'.join(self.file_strs))

        return None

    def rsp_read(self):
        """
            rsp 数据读取
        """
        rsp_path    = self.rsp_path
        nranges     = self.nranges
        channels    = self.channels

        dataobj = DataModel('BdfTransientModalPre')
        dataobj.new_file(rsp_path ,'rsp')
        dataobj['rsp'].set_select_channels(channels)
        dataobj['rsp'].set_line_ranges(nranges)

        dataobj['rsp'].read_file()
        data = dataobj['rsp'].get_data()
        name_channels = dataobj['rsp'].get_titles()
        
        self.samplerate = dataobj['rsp'].get_samplerate()
        self.data = data
        self.rsp_names = name_channels
        return data

    def csv_read(self):
        """
            csv文件读取
            格式:
                name1, x1, y1, z1
                name2, x2, y2, z2
                ...
            仅包含点名称及坐标
        """
        csv_path = self.csv_path

        with open(csv_path, 'r') as f:
            filestr = f.read()

        lines = [[value for value in strlower(line).split(',') if value] 
                    for line in filestr.split('\n')]
        names, xs, ys, zs = [], [], [], []
        for line in lines:
            if line:
                names.append(line[0])
                xs.append(line[1])
                ys.append(line[2])
                zs.append(line[3])

        return names, xs, ys, zs


# =====================================================
# =====================================================
# bdf_transient_modal 测试
# 模态叠加前处理

def test_bdf_transient_modal():

    bdf_path = r'..\tests\file_bdf_transient_modal\test.bdf'
    rsp_path = r'..\tests\file_bdf_transient_modal\test.rsp'
    csv_path = r'..\tests\file_bdf_transient_modal\hardpoint.csv'

    obj = BdfTransientModalPre(bdf_path, csv_path, rsp_path, 
        nranges=[None,20], channels=None)

    # 对比
    result_list = [round(n, 5) for n in obj.data[-1]]

    compare_list = [
        0.81995, 0.72578, 2.06302, -0.07918, -0.62367, -1.3904, 
        -0.13701, 0.6507, 1.3116, 0.66015, -0.69876, -1.24571, 
        -0.48094, 0.746, 1.22121, 0.72383, -0.71117, -0.88685, 
        -1.13409, 0.59967]

    assert result_list==compare_list, 'obj.data[-1]数据不匹配'

    return None


if __name__=='__main__':
    pass

    test_bdf_transient_modal()
    


"""

$HMNAME LOADCOL            10002"TABDMP1_1"
$HWCOLORLOADCOL            10002       6
TABDMP1,10002,CRIT
+,0.0,0.05,2000.0,0.05,,,,,


$HMNAME LOADCOL            10003"TSTEP_1"
$HWCOLORLOADCOL            10003       6
TSTEP,10003,60000,0.001,1,,,,,

$HMNAME LOADCOL            10004"EIGRL_1"
$HWCOLORLOADCOL            10004       6
EIGRL,10004,,,10,,,,,MASS


$HMNAME LOADSTEP               1"Train_cal"       8
$
SUBCASE        10005
LABEL Train_cal
ANALYSIS MTRAN
METHOD(STRUCTURE) =    10004
SDAMPING(STRUCTURE) =    10002
DLOAD =    10001
TSTEP(TIME) =    10003
SDISPLACEMENT(PUNCH,REAL) = ALL
STRESS(OUTPUT2,MODAL) = YES


"""