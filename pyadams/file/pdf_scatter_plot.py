"""
    pdf文件生成
    散点图生成

        csv_path0 : str
        csv_path1 : str
        ts_dic0 : {
            rms         : [float, float, ...]
            min         : [float, float, ...]
            max         : [float, float, ...]
            testname    : str
            chantitle   : [str, str, ...]
            samplerate  : [float, float, ...]
        }
        ts_dic1 : { ... }
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


def pdf_scatter_plot_csv(csv_path0, csv_path1, docx_path):

    logger = logging.getLogger('file.pdf_scatter_plot_path')
    xs, titles_x = csv2data(csv_path0, isTitle=True)
    ys, titles_y = csv2data(csv_path1, isTitle=True)

    del_file(csv_path0)
    logger.info(f'del : {csv_path0}')
    del_file(csv_path1)
    logger.info(f'del : {csv_path1}')

    return pdf_scatter_plot(xs, ys, titles_x, titles_y, docx_path)

    
def pdf_scatter_plot(xs, ys, titles_x, titles_y, docx_path):
    """
        输入数据:

        docx_path : str

        xs  :   [[float, float,...],[...]]
        ys  :   [[float, float,...],[...]]
        
        titles_x : [str, str, ...]
        titles_y : [str, str, ...]
    """

    logger = logging.getLogger('file.pdf_scatter_plot')
    # xs,titles_x = csv2data(csv_path0, isTitle=True)
    # ys,titles_y = csv2data(csv_path1, isTitle=True)

    figpaths_list = []
    for x, title_x in zip(xs, titles_x):
        fig_path = title_x
        figpaths = plot.scatter_ts_single([x]*len(titles_y), ys, [title_x]*len(titles_y), titles_y, 
            figpath=fig_path, nums=[1,1], isShow=False, size_gain=0.8, isGrid=True, 
            linewidths=0.5, scatter_s=15)
        figpaths_list.append(figpaths)

    logger.info(f'titles_x : {titles_x}')
    logger.info(f'titles_y : {titles_y}')
    logger.info(f'figpaths_list : {figpaths_list}')

    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------
    #   word 编写
    obj = office_docx.DataDocx(docx_path)
    obj.set_page_margin(x=1, y=1)
    for num, title_x in enumerate(titles_x):

        for loc in range(len(titles_y)):
            if divmod(loc, 2)[1] == 0 :
                obj.add_heading('X: '+title_x, level=0, size=15)

            obj.add_list_bullet('Y: '+titles_y[loc], size=12)
            
            # 散点图添加
            obj.add_docx_figure(figpaths_list[num][loc], width=16)
            
            # 另起一页
            if divmod(loc, 2)[1] == 1:
                obj.add_page_break()

        if divmod(len(titles_y), 2)[1] == 1 :
            if len(titles_x)-1 !=num:
                obj.add_page_break()

    obj.save()

    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------

    # 转存PDF
    logger.info('doc 2 pdf')
    pdf_path = office_docx.doc2pdf(docx_path)

    del_paths = []
    for figpaths in figpaths_list:
        del_paths += figpaths

    # 删除多余文档
    # del_paths += [csv_path0, csv_path1]
    for path in del_paths:
        del_file(path)
        logger.info(f'del : {path}')

    logger.info('End')

    return pdf_path




