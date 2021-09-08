"""
    1 文件处理
    2 变量存储
    3 csv文件处理
    
"""
import re
import os
import logging
import os.path
import glob

# ======================================================================
# 文件处理
# ======================================================================

# 删除文件夹内制定文件
def file_remove_pt(path, prefix=None, file_type=None): 
    '''
        仅仅删除文件夹内的文件，不删除子文件夹
        path 文件夹路径
        prefix 文件前缀
        file_type 文件后缀,类型
        示例：
            file_remove_pt(path,'sim_','adm')

            file_remove_pt(cal_path, prefix=None, file_type='bak') # 删除文件夹内整个带bak后缀的文件

    '''
    path_rems = []

    for line in os.listdir(path):
        # print(os.listdir(path))
        if file_type!=None and file_type.lower() == line[-len(file_type):].lower() or file_type==None:
            if prefix!=None and prefix.lower() == line[:len(prefix)].lower() or prefix==None:
                path_rems.append(line)

    for line in path_rems:
        target = os.path.join(path, line)
        if os.path.isfile(target):
            os.remove(target)
        # print(target)
    return True

# 删除文件夹内指定文件
def file_remove(path,prefix,suffix=None): 
    '''
        仅仅删除文件夹内的文件，不删除子文件夹
        path 文件夹路径
        prefix 文件前缀
        suffix 文件后缀
        示例：
            file_remove(path,'sim_','.adm')
    '''
    list1 = []
    if suffix==None:
        str1 = f'\A{prefix}.*'
    else:
        str1 = f'\A{prefix}.*{suffix}'
    # str1 = '{}.*{}'.format(prefix,suffix)
    for line in os.listdir(path):
        # print(os.listdir(path))
        if re.match(str1, line):
            list1.append(line)

    for line in list1:
        target = os.path.join(path,line)
        os.remove(target)
        # print(target)
    return True

# 删除指定文件
def del_file(filepath): 
    try:
        os.remove(filepath)
        return True
    except:
        return False

# 判断文件是否存在
def is_file_exist(filepath):
    # 判断文件是否存在
    return os.path.exists(filepath)

# 重命名 文件名，避免重名
def rename_filepath(filepath):
    # 重命名 文件名
    if is_file_exist(filepath):
        pass
        n = 0
        while True:
            filedir, name = os.path.split(filepath)
            print(filedir,name)
            base_name = '.'.join(name.split('.')[:-1])
            file_type = name.split('.')[-1]
            new_filepath = os.path.join(filedir,base_name+f'_{n}.'+file_type)
            n += 1
            if not is_file_exist(new_filepath):
                break
        return new_filepath
    else:
        return filepath

# 重名文件夹名称，避免重名
def rename_filedir(filedir):
    # 重命名 文件夹名
    # 直接加后缀！！！！！
    n = -1
    while True:
        n += 1
        new_filedir = os.path.join(filedir+f'_{n}')
        if not is_file_exist(new_filedir):
            break
    return new_filedir,n

# 创建文件夹
def create_dir(filedir):
    # 创建文件夹
    try:
        os.mkdir(filedir)
    except:
        logging.warning(f'文件已存在,不进行创建:{filedir}')
        pass
    return None

# 获取文件大小
def get_file_size(file_path, size_type='mb'):
    # 获取文件大小
    fsize = os.path.getsize(file_path)
    if size_type.lower() == 'mb':
        fsize = fsize / float(1024 * 1024)
    elif size_type.lower() == 'gb':
        fsize = fsize / float(1024 * 1024 * 1024)


    return round(fsize, 2)


# 检索指定路径的文件
def file_search(path, prefix, suffix): 
    '''
        仅仅删除文件夹内的文件，不删除子文件夹
        path 文件夹路径
        prefix 文件前缀
        suffix 文件后缀
        示例：
            file_remove(path,'sim_','.adm')
    '''
    filepaths = []

    list1 = []
    str1 = '{}.*{}'.format(prefix,suffix)
    for line in os.listdir(path):
        # print(os.listdir(path))
        if re.match(str1, line):
            list1.append(line)

    for line in list1:
        target = os.path.join(path,line)
        # os.remove(target)
        filepaths.append(target)
        # print(target)
    return filepaths

def file_search_glob(filedir, filename, n_subpath=5, isOneFile=True):
    """
        文件存放目录
        filedir     文件存放目录
        n_subpath 文件夹层级数 , 1为仅检索主目录
        isOneFile 只输出一个符合的文件路径
    """
    for n in range(n_subpath):
        c = '*\\'
        path = os.path.join(os.path.abspath(filedir), 
            c*n+filename)
        paths = glob.glob(path)
        if paths:
            if isOneFile:
                return paths[0]
    return paths


# ======================================================================
# 变量存储
# ======================================================================

# 变量保存，保存为文档
def var_save(path,dict1):
    """
        保存变量数据
        path 变量存储路径
        dict1 字典格式，目标变量
    """
    import shelve
    from contextlib import closing
    with closing(shelve.open(path,'c')) as shelf:
        for var in dict1:
            shelf[var] = dict1[var]

# 变量读取，读取文档
def var_read(path):
    """
        读取变量存储数据
        path 目标数据路径
        字典格式导出
    """
    import shelve
    from contextlib import closing
    dict1 = {}
    with closing(shelve.open(path,'r')) as shelf:
        for name in shelf.keys():
            dict1[name] = shelf[name]

    return dict1


# 字典格式，元组为key（全为字符串），数据保存
def dict_tuplekey_save(dic1, path, str1='.compare.'): 
    """
        dic1 : 字典，存储目标
        path : 路劲
        str1 : 元祖字符串间隔
        字典数据保存
        key为元组格式
        通过将元组转化为字符串数据，通过str1拼接
    """
    import json
    new_dic1 = {}
    for name in dic1:
        new_name = str1.join(name)
        new_dic1[new_name] = dic1[name]
    with open(path, 'w') as f:
        json.dump(new_dic1,f)

    return True

# 读取json，
def dict_tuplekey_load(path, str1='.compare.'): 
    """ 
        读取json文件，将字典key转化为元组tuple格式
        path 文件路径
        str1 分割关键字符
    """
    import json
    
    with open(path, 'r') as f:
        values = json.load(f)
    new_values = {}
    for name in values:
        new_name = tuple(name.split(str1))
        new_values[new_name] = values[name]

    return new_values,values

# ======================================================================


# ======================================================================
# CSV文件
# ======================================================================

# 数据转CSV
def data2csv(csv_path,data,reqs=None,comps=None): # 数据导出为csv格式
    """
        csv_path    目标csv路径
        data    list(list)      二维数组
        reqs    list            一位数组（标题前缀）
        comps   list            一维数组（标题后缀）
        example:
            req.comp    req.comp
            1.1         1.1
            1.1         1.1
    """
    # drv_path[:-3]+'csv'
    if reqs == None :
        reqs = ['n' for n in range(len(data))]
    if comps == None :
        comps = ['n' for n in range(len(data))]

    f = open(csv_path,'w')
    f.write(
        ','.join(['{}.{}'.format(a,b) for a,b in zip(reqs,comps)])
        )
    f.write('\n')
    for n in range(len(data[0])):
        for loc in range(len(data)):
            f.write(str(data[loc][n]))
            f.write(',')
        f.write('\n')
    f.close()

    return True

# CSV读取
def csv2data(csv_path,isTitle=True): 
    """
        csv_path    目标csv路径
        isTitle

        data    list(list)      二维数组
    """
    strlower = lambda st1: re.sub(r'\s','',st1).lower()
    f = open(csv_path,'r')
    with open(csv_path,'r') as f:
        filestr = f.read()
    
    if not isTitle:
        titles = None

    list1 = []
    for loc, line in enumerate(filestr.split('\n')):
        
        if isTitle:
            titles = line.split(',')
            isTitle = False
            continue

        line = strlower(line)
        if line:
            line = [float(value) for value in line.split(',') if value]
            list1.append(line)

    new_list1 = []
    for n0 in range(len(list1[0])):
        line = []
        for n1 in range(len(list1)):
            line.append(list1[n1][n0])
        new_list1.append(line)

    return new_list1,titles

# CSV文件 行列转换, 要求行列数一致
def csv_str_reshape(csv_str):
    """
        CSV 格式文件行列调换
    """
    strs = [line.split(',') for line in csv_str.split('\n') if line]
    new_strs = []
    for n1 in range(len(strs[0])):
        line = []
        for n2 in range(len(strs)):
            line.append(strs[n2][n1])
        new_strs.append(','.join(line))

    return '\n'.join(new_strs)

# CSV文件 行列转换
def csv_file_reshape(csv_path,new_csv_path=None):
    """
        csv_path 目标文件路径
        new_csv_path 新生成文件路径
    """
    with open(csv_path, 'r') as f:
        file_str = f.read()

    new_csv_path = csv_path if new_csv_path==None else new_csv_path

    with open(new_csv_path, 'w') as f:
        f.write( csv_str_reshape(file_str) )

    return None

# ======================================================================