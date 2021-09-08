"""
    力值计算程序
    2021.04.04

    分力计算
    合力计算
"""

from pyadams.file import result, file_edit
from pyadams.datacal import plot
DataModel = result.DataModel
DataModelPlot = result.DataModelPlot
dataobj = DataModel('post_force_load')

import os.path , copy
import csv
import xlwt
import xlsxwriter
import logging
# logging.basicConfig(level=logging.INFO)   # logging设置

FORCE_V = {0:'Fx',1:'Fy',2:'Fz',3:'Tx',4:'Ty',5:'Tz'} # {0:'X',1:'Y',2:'Z'}
abs_list = lambda list1: [abs(n) for n in list1]


# 实时读取res文件数据
def get_res_paths(res_paths, reqs, comps, n_start=5, n_end=None):
    """
        res_paths   list    多res路径

    """
    
    event_names = []
    force_data_list = []
    samplerates = []
    if isinstance(n_start, int): n_start = [n_start]*len(res_paths)
    if n_end == None or isinstance(n_end, int): n_end = [n_end]*len(res_paths)

    assert len(n_start)==len(res_paths), 'len(n_start) != len(res_paths)'
    assert len(n_end)==len(res_paths), 'len(n_end) != len(res_paths)'

    for loc_start, loc_end, res_path in zip(n_start, n_end, res_paths):
        res_name = os.path.basename(res_path)[:-4]
        event_names.append(res_name)
        dataobj.new_file(res_path, res_name)
        dataobj[res_name].set_reqs_comps(reqs, comps)
        dataobj[res_name].read_file_faster()
        force_data = dataobj[res_name].get_data()
        force_data = [ line[loc_start:loc_end] for line in force_data ] # 起始位置截断
        force_data_list.append(force_data)
        # 频域计算
        samplerate_mean = dataobj[res_name].get_samplerate(nlen=20, loc_start=4)
        samplerates.append(round(samplerate_mean))

    return force_data_list, event_names, samplerates

# 多个res文件数据拼接成一个时域
def extend_force_data(force_data_list): # 工况拼接
    """
        各工况数据 - 拼接
        force_datas = [[point1_event1],[point2_event1],...]
        force_data_list = [force_datas1,force_datas2,..]
    """
    force_datas = []
    for nline in range(len(force_data_list[0])):
        new_line = []
        event_locs = [] # 工况位置切分
        for force_data in force_data_list:
            # 拼接
            new_line.extend(force_data[nline])
            event_locs.append(len(new_line))

        force_datas.append(new_line)

    return force_datas, event_locs

# 根据时刻确认工况
def loc_name(event_locs,event_names,loc): # 工况名称定位
    # event_locs = [122,1334]
    # event_names = ['event1','event2']

    for event_loc,event_name in zip(event_locs,event_names):
        if loc>=event_loc:
            continue
        else:
            return event_name

# 获取指定位置数据
def get_force_step(force_datas, loc):
    # 获取指定位置数据
    return [line[loc] for line in force_datas]

# 时域数据输出
def csv_force_datas(res_paths, force_data_list, reqs, comps, samplerates):
    
    csv_paths = [res_path[:-4]+f'_{samplerate}Hz.csv' 
                for res_path,samplerate in zip(res_paths,samplerates)]

    for csv_path, data, samplerate in zip(csv_paths, force_data_list,samplerates):
        file_edit.data2csv(csv_path, data, reqs, comps)

    return True

# csv 转 excel 弃用
def csv2excel(workbook, csv_path, sheet_name): # 弃用
    """
        xlwt、csv 库

        csv文件读取 并转化为excel的表跟数据
        workbook    xlwt.Workbook 实例
        csv_path    目标csv文件路径
        sheet_name  目标表跟数据的sheet名称
    """
    if len(sheet_name)>31: # excel表格名称字符不能超31
        sheet_name = sheet_name[-31:]

    worksheet = workbook.add_sheet(sheet_name, cell_overwrite_ok=True)
    with open(csv_path, 'r') as f:
        rows = csv.reader(f)
        for irow, row in enumerate(rows):
            for icol, value in enumerate(row):
                try:
                    value = float(value)
                except:
                    pass
                
                if sheet_name == 'output_csv' and len(row)>=256:
                    # xls 格式, 避免列数超过256
                    worksheet.write(irow, icol, label=value)
                else:
                    worksheet.write(irow, icol, label=value)


    return workbook

# csv 转 excel  xlsx
def csv2excel_xlsx(workbook, csv_path, sheet_name):
    """
        xlsxwriter、csv 库

        csv文件读取 并转化为excel的表跟数据
        workbook    xlwt.Workbook 实例
        csv_path    目标csv文件路径
        sheet_name  目标表跟数据的sheet名称
    """
    if len(sheet_name)>31: # excel表格名称字符不能超31
        sheet_name = sheet_name[-31:]

    worksheet = workbook.add_worksheet(name = sheet_name)
    with open(csv_path, 'r') as f:
        rows = csv.reader(f)
        for irow, row in enumerate(rows):
            for icol, value in enumerate(row):
                try:
                    value = float(value)
                except:
                    pass
                worksheet.write(irow, icol, value)

    return workbook

# 分力计算
def cal_force_component(force_datas, block_num, force_type):
    """
        分力计算定位

        输入:
        force_datas
            [[point1.x,...],[point1.y,...],[point1.z,...],....]
        block_num
            point 数量
        force_type
            3 或 6 (即是否带力矩数据)
        
        输出:
        force_abs_max_locs
            [499, 495, 864, 863, 394] 
        locs_to_points
            {499: ['P0.Fx', 'P0.Fy', 'P1.Fy', 'P2.Fx', 'P2.Fz'], 
            495: ['P0.Fz'], 
            864: ['P1.Fx', 'P2.Fy', 'P3.Fz'], 
            863: ['P1.Fz', 'P3.Fx'], 
            394: ['P3.Fy']}
    """
    force_abs_max_locs = []
    locs_to_points = {}
    for num in range(block_num):
        for v in range(3):
            f = force_datas[num*force_type+v]
            f_abs = abs_list(copy.deepcopy(f))
            f_abs_max_loc = f_abs.index(max(f_abs))
            # print(f_abs_max_loc)
            f_v = f'P{num+1}.{FORCE_V[v]}' # 位置与方向
            if f_abs_max_loc not in force_abs_max_locs:
                force_abs_max_locs.append(f_abs_max_loc)
                # print(f_abs_max_loc)
                locs_to_points[f_abs_max_loc] = [f_v]   
            else:
                locs_to_points[f_abs_max_loc].append(f_v) 

    return  force_abs_max_locs, locs_to_points

# 合力计算
def cal_force_combine(force_datas, block_num, force_type):
    """
        合力计算定位
        
        输入:
        force_datas
            [[point1.x,...],[point1.y,...],[point1.z,...],....]
        block_num
            point 数量
        force_type
            3 或 6 (即是否带力矩数据)
        
        输出:
        force_abs_max_locs
            [499, 495, 864, 863, 394] 
        locs_to_points
            {499: ['P0.Fx', 'P0.Fy', 'P1.Fy', 'P2.Fx', 'P2.Fz'], 
            495: ['P0.Fz'], 
            864: ['P1.Fx', 'P2.Fy', 'P3.Fz'], 
            863: ['P1.Fz', 'P3.Fx'], 
            394: ['P3.Fy']}
    """
    force_c_max_locs = []
    locs_to_points = {}
    for num in range(block_num):
        fx = force_datas[num*force_type+0]
        fy = force_datas[num*force_type+1]
        fz = force_datas[num*force_type+2]

        f_c = [(x**2+y**2+z**2)**0.5 for x,y,z in zip(fx,fy,fz)]
        f_c_max_loc = f_c.index(max(f_c))
        f_v = f'P{num+1}' # 位置与方向

        if f_c_max_loc not in force_c_max_locs:
            force_c_max_locs.append(f_c_max_loc)
            # print(f_abs_max_loc)
            locs_to_points[f_c_max_loc] = [f_v] 
        else:
            locs_to_points[f_c_max_loc].append(f_v) 

    return force_c_max_locs, locs_to_points

# 工况静态截取,指定位置
def cal_force_fixloc(force_data_list, locs):
    """
        静载
        指定位置输出
        locs_to_points: [499, 898]
        locs_to_points: {499: ['FixLoc-1'], 898: ['FixLoc-1']}
    """
    
    new_locs = []
    new_starts = []
    for num, datas in enumerate(force_data_list):
        if num == 0 :
            new_starts.append(0)
            new_starts.append( len(datas[0]) )
        else:
            new_starts.append( new_starts[num] + len(datas[0]) )    

        logging.info(f'time_len: {len(datas[0])}')

    logging.info( 'len_new_starts: {}'.format(len(new_starts)) )
    logging.info( f'new_starts: {new_starts}' )

    for num in range(len(force_data_list)):
        if locs[num] < 0:
            new_locs.append( new_starts[num] + len(force_data_list[num][0]) + locs[num] )
        else:
            new_locs.append( new_starts[num] + locs[num] )

    logging.info( 'len_new_locs: {}'.format(len(new_locs)) )
    logging.info( f'new_locs: {new_locs}' )

    force_abs_max_locs  = new_locs
    locs_to_points = {}
    for num in range(len(force_data_list)):
        locs_to_points[new_locs[num]] = [f'FixLoc{locs[num]}'] 

    logging.info( f'locs_to_points: {locs_to_points}' )

    return force_abs_max_locs, locs_to_points

# 数据拼接 - 字符串化
def str_force_datas(force_datas, point_names, 
    force_abs_max_locs, locs_to_points, locs_to_events, force_type):
    """
        输入:
        force_datas
            [[point1.x,...],[point1.y,...],[point1.z,...],....]
        
        point_names
            ['bkl_lca_front_force.rear', 'bkr_lca_front_force.rear', 
                'bkl_lca_front_force.front', 'bkr_lca_front_force.front'] 
        
        force_abs_max_locs
            [499, 495, 864, 863, 394] 
        
        locs_to_points
            {499: ['P0.Fx', 'P0.Fy', 'P1.Fy', 'P2.Fx', 'P2.Fz'], 
                495: ['P0.Fz'], 
                864: ['P1.Fx', 'P2.Fy', 'P3.Fz'], 
                863: ['P1.Fz', 'P3.Fx'], 
                394: ['P3.Fy']}
            
        locs_to_events:
            {499: 'GB_T_crc', 495: 'GB_T_crc', 864: 'GB_T_s', 
                863: 'GB_T_s', 394: 'GB_T_crc'}

        force_type
            3 或 6 (即是否带力矩数据)
    """
    # print(point_names, force_abs_max_locs, locs_to_points, locs_to_events, force_type)
    # print(point_names)
    n_round = 2
    # -------------------------------------------------
    # 数据转换 ---- 横向拼接
    csv_row = []
    for n in range(len(point_names)):
        line = []
        for loc in force_abs_max_locs:
            force_step = get_force_step(force_datas, loc)
            # print(force_step)
            line.extend(force_step[n*force_type : (n+1)*force_type])
            # print(len(force_step[n*force_type : (n+1)*force_type]))
            # break
        csv_row.append(line)

    title_names = ['_'.join(locs_to_points[loc])+'_'+ locs_to_events[loc]
                     for loc in force_abs_max_locs]
    str_csv_row_values = [','.join([str(round(value,n_round)) for value in line]) for line in csv_row]
    str_csv_row_title = ','.join([f'{name}'+','*(force_type-1) for name in title_names])
    str_csv_row = [str_csv_row_title] + str_csv_row_values
    # print(str_csv_row)

    # -------------------------------------------------
    # 数据转换 ---- 垂向拼接
    str_csv_column = []
    title_names = ['_'.join(locs_to_points[loc])+'_'+ locs_to_events[loc]
                     for loc in force_abs_max_locs]
    for loc, name in zip(force_abs_max_locs, title_names):
        force_step = get_force_step(force_datas, loc)

        if force_type==6:
            title = f'{name},Fx,Fy,Fz,Tx,Ty,Tz'
        else:
            title = f'{name},Fx,Fy,Fz'

        str_csv_column.append(title)

        for n in range(len(point_names)):
            line = force_step[n*force_type : (n+1)*force_type]
            str_line = f'{n+1}.'+point_names[n]+','+','.join([str(round(value,n_round)) for value in line])
            # break
            str_csv_column.append(str_line)

        str_csv_column.append('')

    # print('\n'.join(str_csv_column))
    # return str_csv_row, str_csv_column

    # 开头
    new_title_names = ['_'.join(locs_to_points[loc])+','+ locs_to_events[loc]
                     for loc in force_abs_max_locs]

    return '\n'.join(str_csv_row), '\n'.join(new_title_names)+'\n'*2+'\n'.join(str_csv_column)
    
def str_to_csv(params,isColumn=True):

    str_row = params['str_row']
    str_column = params['str_column']
    csv_path = params['csv_path']

    if isColumn:
        with open(csv_path, 'w') as f:
            f.write(str_column)

    else:
        with open(csv_path, 'w') as f:
            f.write(str_row)            

# 计算主函数
def post_force_load(res_paths, reqs, comps, force_type, csv_path, isShow=True, isComponent=True, locs=None, n_start=5, n_end=None):
    """
        res_paths
            ['as.res',...]
        reqs
            ['','',...]
        comps
            ['','',...]
        force_type
            3 或 6 (即是否带力矩数据)
        csv_path
            存储路径
        isShow
            是否显示时域数据
        isComponent
            是否进行分力计算
            True    分力计算
            False   合力计算
        locs 静载,指定位置
            静力计算,每个文件指定一个位置
            None or [-1,-1,....]
    """

    # --------------------------
    # 点- 名称命名
    # reqs, comps
    # print(reqs, comps)
    new_comps = []
    for comp in comps:
        temp = comp.split('_') 
        if len(temp)>1:
            new_comps.append(temp[-1])
        else:
            new_comps.append('')

    point_names = []
    for req, comp in zip(reqs, new_comps):
        str1 = req+'.'+comp
        if str1 not in point_names:
            point_names.append(str1)
    # print(point_names)

    # --------------------------
    # 数据读取
    if isinstance(res_paths, str):
        res_paths  = [res_paths]
    # res读取
    force_data_list, event_names, samplerates = get_res_paths(res_paths, reqs, comps, n_start, n_end)
    # 时域数据导出
    csv_force_datas(res_paths, force_data_list, reqs, comps, samplerates)

    # --------------------------
    # 合理性判定
    block_num, block_c =divmod(len(force_data_list[0]), force_type)
    if block_c != 0:
        logging.error(f' 通道数不对 目标点:{block_num} 有额外通道数:{block_c}')
        raise Exception("通道数不对")

    if len(point_names) != block_num :
        logging.error(f' force_type:{force_type} point_names:{len(point_names)} 目标点数:{block_num}')
        raise Exception("force_type 与 通道数不符")

    # --------------------------
    # 单文件计算
    res_singles = {}
    for datas, event_name, res_path, num in zip(force_data_list, event_names, res_paths, range(len(res_paths))):
        res_singles[event_name] = {}
        # res_singles[event_name]['force_datas'] = datas

        # 静力计算,每个文件指定一个位置
        if locs != None: 
            res_singles[event_name]['force_abs_max_locs'] = [locs[num]]
            res_singles[event_name]['locs_to_points'] = { locs[num]:[f'FixLoc{locs[num]}'] }

        # 分力计算
        elif isComponent: 
            res_singles[event_name]['force_abs_max_locs'], res_singles[event_name]['locs_to_points'] = \
                cal_force_component(datas, block_num, force_type)
        
        # 合力计算
        else: 
            res_singles[event_name]['force_abs_max_locs'], res_singles[event_name]['locs_to_points'] = \
                cal_force_combine(datas, block_num, force_type)

        res_singles[event_name]['locs_to_events'] = {}
        for key in res_singles[event_name]['locs_to_points'].keys():
            res_singles[event_name]['locs_to_events'][key] = event_name

        # print(res_singles[event_name])
        res_singles[event_name]['res_path'] = res_path
        res_singles[event_name]['csv_path'] = res_path[:-4] + '_cal.csv'
        res_singles[event_name]['str_row'], res_singles[event_name]['str_column'] = str_force_datas(datas,
            point_names, res_singles[event_name]['force_abs_max_locs'], res_singles[event_name]['locs_to_points'], 
            res_singles[event_name]['locs_to_events'], force_type)

        # print(res_singles[event_name])

    # --------------------------
    # 合并时域数据 - 计算
    # 数据拼接
    force_datas, event_locs = extend_force_data(force_data_list)
    if locs != None: 
        # 静力计算,每个文件指定一个位置
        force_abs_max_locs, locs_to_points = cal_force_fixloc(force_data_list, locs)
    elif isComponent:
        # 分力计算
        force_abs_max_locs, locs_to_points = cal_force_component(force_datas, block_num, force_type)
    else:
        # 合力计算
        force_abs_max_locs, locs_to_points = cal_force_combine(force_datas, block_num, force_type)

    # print(force_abs_max_locs, locs_to_points)
    # 时刻对应事件
    locs_to_events = {}
    for loc in force_abs_max_locs:
        locs_to_events[loc] = loc_name(event_locs,event_names,loc)

    # logging.info( f'locs_to_events: {locs_to_events}' )
    # logging.info( f'{force_data_list[0][0][-1]}')
    # logging.info( f'{force_datas[0][new_locs[0]]}')
    # logging.info( f'{force_data_list[1][0][-1]}')
    # logging.info( f'{force_datas[0][new_locs[1]]}')
    # logging.info( f'locs_to_points : {locs_to_points}')

    # 数据转换
    res_multi = {}
    res_multi['str_row'], res_multi['str_column'] = str_force_datas(force_datas, point_names, 
        force_abs_max_locs, locs_to_points, locs_to_events, force_type)
    res_multi['csv_path'] = csv_path

    # --------------------------
    str_to_csv(res_multi, isColumn=False)
    res_multi['csv_path'] += '_row'
    str_to_csv(res_multi, isColumn=True)

    for event_name in event_names:
        str_to_csv(res_singles[event_name], isColumn=True)

    
    # # 文件保存 - xls
    # workbook = xlwt.Workbook(encoding='utf-8')
    # for event_name in event_names:
    #   csv2excel(workbook,res_singles[event_name]['csv_path'],event_name)
    #   file_edit.del_file(res_singles[event_name]['csv_path'])
    # csv2excel(workbook,res_multi['csv_path'],'multi_cal')
    # file_edit.del_file(res_multi['csv_path'])
    # workbook.save(csv_path[:-3]+'xls')


    # 文件保存 - xlsx
    workbook = xlsxwriter.Workbook(filename=csv_path[:-3]+'xlsx')
    for event_name in event_names:
        csv2excel_xlsx(workbook, res_singles[event_name]['csv_path'], event_name)
        file_edit.del_file(res_singles[event_name]['csv_path'])
    # 垂向数据汇总
    csv2excel_xlsx(workbook, res_multi['csv_path'], 'multi_cal')
    file_edit.del_file(res_multi['csv_path'])
    # csv格式横向
    csv2excel_xlsx(workbook, res_multi['csv_path'][:-4], 'csv')
    file_edit.del_file(res_multi['csv_path'][:-4])
    # print(res_multi['csv_path'][:-4])
    workbook.close()

    # --------------------------
    # 图片显示
    # res_paths, reqs, comps, force_type, point_names, force_datas
    # isShow = True

    ylabels = [req+'.'+comp for req,comp in zip(reqs,comps)]
    y_data, y_labels = [], []
    for num in range(len(point_names)):
        for n in range(3):
            y_data.append(force_datas[num*force_type+n])
            y_labels.append(reqs[num*force_type+n]+'.'+FORCE_V[n])

    dirname = os.path.dirname(res_paths[0])
    figure_path = os.path.join(dirname, 'figure_force')
    # 作图
    figobj = plot.FigPlot()
    figobj.set_figure(nums=[2,3], size_gain=0.6, figsize='25:9')
    figobj.plot_ts(y_data)
    figobj.set_ylabel(y_labels, 'ts')
    figobj.set_xlabel(['loc']*len(y_labels), 'ts')
    figobj.updata('ts')
    # figobj.tight_layout()
    figobj.save(figure_path)
    if isShow:
        figobj.show()
    # plot.plot_ts_hz_single(y_data, samplerate=1, block_size=None,
    #   res_x=None, ylabels=y_labels, xlabels=['loc']*len(y_labels),
    #   nums=None, figpath=figure_path, isShow=isShow, isHzPlot=False, isTsPlot=True,
    #   hz_range=None, isGrid=False, size_gain=1)
    

    return None



# ================================================
# 测试模块

def test_post_force_load():

    # --------------------------
    # 输入数据
    force_type = 6
    res_paths = [r'..\tests\file_result\GB_T_crc.res',
        r'..\tests\file_result\GB_T_s.res']
    reqs = ['bkl_lca_front_force']*6 + ['bkr_lca_front_force']*6 +\
        ['bkl_lca_front_force']*6 + ['bkr_lca_front_force']*6
    comps = [
        'fx_front','fy_front','fz_front','tx_front','ty_front','tz_front',
        'fx_front','fy_front','fz_front','tx_front','ty_front','tz_front',
        'fx_rear','fy_rear','fz_rear','tx_rear','ty_rear','tz_rear',
        'fx_rear','fy_rear','fz_rear','tx_rear','ty_rear','tz_rear',
    ]
    csv_path = r'..\tests\car_post_force_load\multi_cal.csv'

    isComponent = True
    isShow = True

    # post_force_load(res_paths, reqs, comps, force_type, csv_path, isShow=isShow, isComponent=isComponent)
    post_force_load(res_paths, reqs, comps, force_type, csv_path, isShow=isShow, isComponent=isComponent, locs=[-1,-1], 
        n_start=5, n_end=None)

    # dmp_obj = DataModelPlot(dataobj)
    # dmp_obj.run()


if __name__=='__main__':

    pass
    test_post_force_load()









