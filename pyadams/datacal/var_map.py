"""
   灵敏度数据后处理评价

"""

import re
import os
import matplotlib.pyplot as plt
from pyadams import datacal
from pyadams.file import office_docx


# 极差分析
def create_pdf_range_analysis(data, str_input=None):

    fig_paths = data['result_fig_paths']
    docx_path = data['csv_path'][:-4]+'.docx'
    csv_name  = os.path.basename(data['csv_path'])

    obj = office_docx.DataDocx(docx_path)
    obj.set_page_margin(x=1.27, y=1.27)    

    page_one = {
        'title_main' : '灵敏度评价', 
        'title_minor': '----极差分析',
        'file_paths' : [csv_name],
    }
    obj.add_cover_page(page_one)
    obj.add_page_break()
    if str_input != None:
        obj.add_paragraph(str_input)
        obj.add_page_break()

    for fig_path in fig_paths:
        obj.add_docx_figure(fig_path, '极差分析-评估图', width=18)

    obj.save()
    pdf_path = office_docx.doc2pdf(docx_path)

    return pdf_path


# 计算结果图像化
def plot_var_color_map(data, str_type='range_analysis'):
    """
        彩图
    """
    fig_path = data['csv_path'][:-4]
    fig_path = os.path.abspath(fig_path)

    fig_paths = []
    for title in data['titles']:
        chr_data = data[title]
        res_name = chr_data['name_res']
        var_name = chr_data['name_var']
        result   = chr_data['result']
        plt.pcolor(result, cmap='jet')
        plt.colorbar(shrink=0.83)
        plt.title(title+'\n'+str_type)

        plt.rcParams['figure.figsize'] = [len(result[0])*0.15+5, len(res_name)*0.15+3]

        if var_name==None: var_name = [n for n in range(len(result[0]))]

        n_var = len(var_name)
        n_res = len(res_name)

        plt.xticks([v+0.5 for v in range(n_var)], labels=var_name)
        plt.yticks([v+0.5 for v in range(n_res)], labels=res_name)
        plt.tight_layout()

        path = fig_path+f'_{title}.png'
        plt.savefig(path)
        plt.close()
        fig_paths.append(path)

    data['result_fig_paths'] = fig_paths
    """
        { csv_path :  str ,
          result_fig_paths : [ str.. ],
          titles : [ str.. ],
          u_max_divide_l_max : { name_res : [ str.. ],
                                 name_var :  NoneType ,
                                 result : [[ float.. ]],
                                 title :  str },
          u_min_divide_l_min : { name_res : [ str.. ],
                                 name_var :  NoneType ,
                                 result : [[ float.. ]],
                                 title :  str },
          u_pdi_divide_l_pdi : { name_res : [ str.. ],
                                 name_var :  NoneType ,
                                 result : [[ float.. ]],
                                 title :  str },
          u_rms_divide_l_rms : { name_res : [ str.. ],
                                 name_var :  NoneType ,
                                 result : [[ float.. ]],
                                 title :  str }}
    """
    return data


# csv数据读取
def _res_csv_read(csv_path):
    """
    文档数据格式:
        u_max_divide_l_max,nsl_ride_spring_data.displacement_front,nsr_ride_spring_data.displacement_front,nsl_ride_spring_data.displacement_rear,nsr_ride_spring_data.displacement_rear
        m_vs_m,1.0,1.0,1.0,1.0
        v_L_L_L_L_vs_m,1.001567524734563,1.0019102142237435,1.0545728306980793,1.0562186775988174
        v_L_M_U_M_vs_m,1.0022776654405814,0.9994754333656689,0.9694153073560976,0.9931504432213962
        v_L_U_M_U_vs_m,0.9989618250573638,1.0002282143905923,0.9761896202774214,0.9768771560140493
        v_M_L_U_U_vs_m,1.000565629157024,1.0011180043627521,0.9675396602426782,0.9598782121120047
        v_M_M_M_L_vs_m,1.0015610619447795,0.9984262627953194,1.0149190501662178,1.0419578556605928
        v_M_U_L_M_vs_m,0.9979629539619961,1.0005794805476076,1.020818656280937,1.0131593480604988
        v_U_L_M_M_vs_m,0.9998577663578688,1.0008727187519666,1.0062657645374853,0.9914525960066898
        v_U_M_L_U_vs_m,0.9974147586471581,1.0026704818966155,1.0270856054867046,0.983294690274134
        v_U_U_U_L_vs_m,1.00151718442514,0.9968851001032271,0.9847568425102922,1.0198343601459379

        u_min_divide_l_min,nsl_ride_spring_data.displacement_front,nsr_ride_spring_data.displacement_front,nsl_ride_spring_data.displacement_rear,nsr_ride_spring_data.displacement_rear
        m_vs_m,1.0,1.0,1.0,1.0
        v_L_L_L_L_vs_m,0.966815527731033,0.9229235218257456,0.9917132899438547,0.9920814588416245
        v_L_M_U_M_vs_m,0.9761145261075754,0.9977412534710892,1.004177490321742,1.0007929476674857
        v_L_U_M_U_vs_m,0.9893519899054266,1.006740194241634,1.0013700161216033,1.003513110469214
        v_M_L_U_U_vs_m,0.9960477276023564,0.9820581728669036,1.0045348949668886,1.0048840367018388
        v_M_M_M_L_vs_m,0.981610483941413,1.0018728751259725,0.9984188188850682,0.9941773238801882
        v_M_U_L_M_vs_m,1.0053800940303423,0.9780596640934223,0.9942220723178593,0.998117232634845
        v_U_L_M_M_vs_m,1.0095640389903993,0.98453438438158,0.9995987778791431,1.000404450256821
        v_U_M_L_U_vs_m,1.0179697556440055,0.9820256638080801,0.9953141110807245,1.0024412289036855
        v_U_U_U_L_vs_m,0.9968908563905192,1.0206317823792561,1.0025149085594716,0.9959302176634979

    """

    with open(csv_path, 'r') as f: 
        file_str = f.read()

    data_ress, titles, new_lines = [], [], []
    name_ress, data_vars = [], []
    for line in file_str.split('\n'):
        if not line: continue
        line = [value for value in line.split(',') if value]
        if not line: continue
        
        try:
            temp    = float(line[1]) # 判定是否为标题(必须有字符串)
            isStart = False
            if line[0][0] == 's': continue # 首字母为s, 非目标对象!!
        except:
            isStart = True

        if isStart: # 标题行
            name_ress.append(line[1:])
            if new_lines != []:
                data_ress.append(new_lines)
                data_vars.append(y)
            new_lines, y = [], []
            titles.append(line[0])
        else: # 非标题行
            y.append(line[0])
            new_lines.append(line[1:])
    
    if new_lines: # 最后一行增补
        data_ress.append(new_lines)
        data_vars.append(y)

    # data_ress, data_vars, name_ress, titles
    # print(data_ress, data_vars, name_ress, titles)
    
    return data_ress, data_vars, name_ress, titles


# 
def data_change_amdsim(data_ress, data_vars, name_ress, titles):

    data = {}
    for n, block in enumerate(data_ress):
        d1 = {}
        new_data_vars = []
        for n1, data_var in enumerate(data_vars[n]):
            if data_var:
                if n1 == 0: # 首位为 
                    new_data_var = ['M']
                else:
                    new_data_var = [value for value in data_var.split('vs')[0].split('_')[1:] if value]

                if new_data_var: new_data_vars.append(new_data_var)

        new_data_vars[0] = new_data_vars[0]*len(new_data_vars[-1])
        block = [[float(value) for value in line] for line in block]
        d1['data_var'] = new_data_vars        # 2D list  变量 配置
        d1['name_res'] = name_ress[n]       # 2D list  结果 行x, 目标名称
        d1['title']    = titles[n]          # 模块名称
        d1['data_res']    = block              # 2D list  结果数据,先行后列 
        data[titles[n]]= d1                 
    """
        { 
          u_max_divide_l_max : { data_res : [[ float.. ]],
                                 data_var : [[ str.. ]],
                                 name_res : [ str.. ],
                                 title :  str },
          u_min_divide_l_min : { data_res : [[ float.. ]],
                                 data_var : [[ str.. ]],
                                 name_res : [ str.. ],
                                 title :  str },
          u_pdi_divide_l_pdi : { data_res : [[ float.. ]],
                                 data_var : [[ str.. ]],
                                 name_res : [ str.. ],
                                 title :  str },
          u_rms_divide_l_rms : { data_res : [[ float.. ]],
                                 data_var : [[ str.. ]],
                                 name_res : [ str.. ],
                                 title :  str }
        }
    """
    return data


# 
def cal_range_analysis_3var(data, titles, csv_path): # 方差分析计算
    
    list_select = lambda list1, tarstr, list2: [v2 for v1, v2 in zip(list1, list2) if v1.upper()==tarstr.upper()]
    average     = lambda list1: sum(list1)/len(list1)
    
    for title in titles:
        d1       = data[title]
        data_var = d1['data_var']
        data_res = d1['data_res']
        name_res = d1['name_res']

        data_var_vertical = [[line[n] for line in data_var] for n in range(len(data_var[0]))]

        data[title]['result_r'] = {}
        for res_n in range(len(name_res)):
            # print(data_res)
            data_res_n = [line[res_n] for line in data_res]
            Rs = []
            for line in data_var_vertical:
                # print(data_res_n)
                ave_l = average(list_select(line, 'L', data_res_n))
                ave_m = average(list_select(line, 'M', data_res_n))
                ave_u = average(list_select(line, 'U', data_res_n))
                aves  = [ave_l, ave_m, ave_u]
                r     = max(aves) - min(aves)
                Rs.append(r)

                data[title]['result_r'][name_res[res_n]] = Rs


    # print(datacal.str_view_data_type(data))

    f = open(csv_path, 'w')
    data_r = {}
    for title in titles:
        f.write(title+'\n')
        data_r[title] = {}
        data_r[title]['result'] = []
        for key in data[title]['name_res']:
            str1 = ','.join([f'{v:0.4f}' for v in data[title]['result_r'][key]])
            line = key+','+str1
            f.write(line+'\n')

            data_r[title]['result'].append(data[title]['result_r'][key])
        f.write('\n\n')

        data_r[title]['name_res'] = data[title]['name_res']
        data_r[title]['name_var'] = None
        data_r[title]['title']    = title
    data_r['csv_path']        = csv_path
    data_r['titles']          = titles

    f.close()

    # print(datacal.str_view_data_type(data_r))
    """
    { csv_path :  str ,
      titles : [ str.. ],
      u_max_divide_l_max : { name_res : [ str.. ],
                             name_var :  NoneType ,
                             result : [[ float.. ]],
                             title :  str },
      u_min_divide_l_min : { name_res : [ str.. ],
                             name_var :  NoneType ,
                             result : [[ float.. ]],
                             title :  str },
      u_pdi_divide_l_pdi : { name_res : [ str.. ],
                             name_var :  NoneType ,
                             result : [[ float.. ]],
                             title :  str },
      u_rms_divide_l_rms : { name_res : [ str.. ],
                             name_var :  NoneType ,
                             result : [[ float.. ]],
                             title :  str }}
    """
    return data_r


# 
def cal_var_color_map(csv_path, str_input=None): # 主函数

    csv_path = os.path.abspath(csv_path)

    data_ress, data_vars, name_ress, titles = _res_csv_read(csv_path)
    data = data_change_amdsim(data_ress, data_vars, name_ress, titles)

    # print(datacal.str_view_data_type(data))
    data_r = cal_range_analysis_3var(data, titles, csv_path[:-4]+'_range_analysis.csv')
    # print(datacal.str_view_data_type(data_r))
    data_r = plot_var_color_map(data_r, str_type='range_analysis')
    # print(datacal.str_view_data_type(data_r))

    pdf_path = create_pdf_range_analysis(data_r, str_input)

    return pdf_path


# ================================

def test_cal_var_color_map():
    csv_path = r'..\tests\datacal_var_map\test_tk_adm_sim.csv'

    pdf_path = cal_var_color_map(csv_path)
    os.popen(pdf_path)

    # csv_path = os.path.abspath(csv_path)

    # data_ress, data_vars, name_ress, titles = _res_csv_read(csv_path)
    # data = data_change_amdsim(data_ress, data_vars, name_ress, titles)

    # # print(datacal.str_view_data_type(data))
    # data_r = cal_range_analysis_3var(data, titles, csv_path[:-4]+'_range_analysis.csv')
    
    # fig_path = csv_path[:-4]
    # fig_paths = plot_var_color_map(fig_path, data_r, str_type='range_analysis')
    # print(fig_paths)




if __name__=='__main__':
    pass

    test_cal_var_color_map()



