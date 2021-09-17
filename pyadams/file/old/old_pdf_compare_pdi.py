"""
    pdf文件生成
    对比数据

        csv_path0 : str
        csv_path1 : str
        pdi_dic0 : {
            slope       : [float, float, ...]   len通道数
            rms         : [float, float, ...]   len通道数
            intercept   : [float, float, ...]   len通道数
            min         : [float, float, ...]   len通道数
            max         : [float, float, ...]   len通道数
            damage      : [float, float, ...]   len通道数
            testname    : str
            chantitle   : [str, str, ...]       len通道数
            samplerate  : [float, float, ...]   len通道数
            block_size  : int
            hz_range    : [0, 50]
        }
        pdi_dic1 : { ... }

"""
import logging
import sys
import json
import re
import os
import copy
from pyadams import datacal
from pyadams.datacal import plot
from pyadams.file import office_docx, file_edit

# logging.basicConfig(level=logging.INFO)

csv2data = file_edit.csv2data
del_file = file_edit.del_file
value2str_list2 = datacal.value2str_list2

# 读取csv数据, 对比 PDI , 生成pdf文件
def pdf_compare_pdi_csv(csv_path0, csv_path1, pdi_dic0, pdi_dic1, docx_path, fig_path):
    """
        csv_path0 : str
        csv_path1 : str
    """

    logger = logging.getLogger('file.pdf_compare_pdi_csv')

    data0, titles0 = csv2data(csv_path0, isTitle=True)
    data1, titles1 = csv2data(csv_path1, isTitle=True)

    logger.info('csv_path0 : {}'.format(csv_path0))
    logger.info('csv_path1 : {}'.format(csv_path1))
    logger.info('titles0 : {}'.format(titles0))
    logger.info('titles1 : {}'.format(titles1))


    pdf_path = pdf_compare_pdi(data0, data1, titles0, titles1, pdi_dic0, pdi_dic1, docx_path, fig_path)

    del_file(csv_path0)
    logger.info(f'del : {csv_path0}')
    del_file(csv_path1)
    logger.info(f'del : {csv_path1}')

    return pdf_path

# 用途: 数据生成
def pdf_compare_pdi(data0, data1, titles0, titles1, pdi_dic0, pdi_dic1, docx_path, fig_path):
    """
        输入数据:

        pdi_dic0 : {
            slope       : [float, float, ...]   PDI斜率
            rms         : [float, float, ...]   
            intercept   : [float, float, ...]   PDI截距
            min         : [float, float, ...]
            max         : [float, float, ...]
            damage      : [float, float, ...]   伪损伤
            testname    : str                   文件名称
            chantitle   : [str, str, ...]       Y轴通道名称
            samplerate  : [float, float, ...]   采样频率
            block_size  : int                   频域: 块尺寸
            hz_range    : [0, 50]               频域: 频率截取范围
        }
        pdi_dic1 : { ... }

        用途: 数据对比,生成PDI
    """
    logger = logging.getLogger('file.pdf_compare_pdi')

    block_size  = [pdi_dic0['block_size'],pdi_dic1['block_size']]
    hz_range    = pdi_dic0['hz_range']

    # data0,titles0 = csv2data(csv_path0, isTitle=True)
    # data1,titles1 = csv2data(csv_path1, isTitle=True)

    logger.info('pdi_dic0 : {}'.format(pdi_dic0))
    logger.info('pdi_dic1 : {}'.format(pdi_dic1))
    logger.info('docx_path : {}'.format(docx_path))
    logger.info('fig_path : {}'.format(fig_path))
    logger.info('len(data0) : {}'.format(len(data0)))
    logger.info('len(data1) : {}'.format(len(data1)))
    logger.info('len(data0[0]) : {}'.format(len(data0[0])))
    logger.info('len(data1[0]) : {}'.format(len(data1[0])))
    
    fig_paths = plot.plot_ts_hz(data0, data1, samplerate=[pdi_dic0['samplerate'][0], pdi_dic1['samplerate'][0]], 
        block_size=block_size,
        res_x=None, target_x=None, ylabels=None, xlabel=None,
        nums=[1,1], figpath=fig_path, isShow=None, isHzPlot=True, isTsPlot=True, 
        hz_range=hz_range, legend=[pdi_dic0['testname'], pdi_dic1['testname']], size_gain=0.6)

    line_hz_set = f'\tPSD 设置 :\n\t\thz_range [{hz_range[0]},{hz_range[1]}] , block_size [{block_size[0]},{block_size[1]}]'

    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------
    #   word 编写
    obj = office_docx.DataDocx(docx_path)

    line_title = 'A({}) vs. B({}) '
    title = line_title.format(pdi_dic0['testname'], pdi_dic1['testname'])

    obj.add_heading(title, level=0, size=20)
    obj.add_heading('数据对比', level=1, size=15)

    list_title = ['chantitle','damage','max','min','rms']

    # 汇总表格
    list_compare = []
    for loc in range(len(pdi_dic1['chantitle'])):
        # 表格
        list_0  = copy.deepcopy(list_title)
        list_1  = [pdi_dic0[key][loc] for key in list_title]
        list_2  = [pdi_dic1[key][loc] for key in list_title]
        list_3  = ['A / B']

        for value_a, value_b in zip(list_1[1:], list_2[1:]):
            if value_b == 0:
                logger.warning(f'denominator is zero : value add 0.01 , {value_a} / {value_b}')
                # list_3.append( (value_a+0.01) / (value_b+0.01) )
                list_3.append('None')
            else:
                list_3.append( value_a / value_b )
        list_compare.append(list_3)

    for loc in range(len(list_compare)):
        list_compare[loc][0] = pdi_dic0['chantitle'][loc]

    obj.add_table(f'相对比例-汇总 A/B', value2str_list2([list_title]+list_compare,3))
    obj.add_page_break()

    for loc in range(len(pdi_dic1['chantitle'])):
        
        obj.add_list_bullet('A : '+pdi_dic0['chantitle'][loc], size=14)
        # 时域图
        obj.add_docx_figure(fig_paths[loc], f'时域图 {loc+1}', width=17)
        # 频域图
        obj.add_docx_figure(fig_paths[loc+len(pdi_dic1['chantitle'])], f'频域图 {loc+1}', width=17)
        # 另起一页
        obj.add_page_break()
        # 注释
        obj.add_paragraph(
            '设置:'
            )
        line_pdi_set = '\t{} :\n\t\tsamplerate 采样频率 {} Hz\n\t\tPDI设置: slope斜率 {} , intercept截距 {}'
        obj.add_paragraph(
            line_pdi_set.format(pdi_dic0['chantitle'][loc],pdi_dic0['samplerate'][loc],pdi_dic0['slope'][loc],pdi_dic0['intercept'][loc])
            )
        obj.add_paragraph(
            line_pdi_set.format(pdi_dic1['chantitle'][loc],pdi_dic1['samplerate'][loc],pdi_dic1['slope'][loc],pdi_dic1['intercept'][loc])
            )
        obj.add_paragraph(line_hz_set)

        # 表格
        list_0  = copy.deepcopy(list_title)
        list_1  = [pdi_dic0[key][loc] for key in list_title]
        list_2  = [pdi_dic1[key][loc] for key in list_title]
        list_1[0] = 'A:'+list_1[0]
        list_2[0] = 'B:'+list_2[0]
        list_3  = ['A / B']
        for value_a, value_b in zip(list_1[1:], list_2[1:]):
            if value_b == 0:
                logger.warning(f'denominator is zero : value add 0.01 , {value_a} / {value_b}')
                # list_3.append( (value_a+0.01) / (value_b+0.01) )
                list_3.append('None')
            else:
                list_3.append( value_a / value_b )

        str_list    = [list_0, list_1, list_2, list_3]
        
        obj.add_table(f'表格{loc+1}', value2str_list2(str_list,3))

        # 另起一页
        obj.add_page_break()

    obj.save()

    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------

    # 转存PDF
    office_docx.doc2pdf(docx_path)
    # os.popen(docx_path[:-4]+'pdf')

    # 删除多余文档
    # del_paths = fig_paths+[csv_path0, csv_path1]
    del_paths = fig_paths
    for path in del_paths:
        del_file(path)
        logger.info(f'del : {path}')

    
    pdf_path = docx_path[:-4]+'pdf'

    logger.info(f'Return path : {pdf_path}')
    logger.info('End')

    return pdf_path

    