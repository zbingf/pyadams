"""
    datacal 用于数据处理
    
"""
import pysnooper
import copy
import pprint


# ========================================================
# xlist  ylist
# 数据生成 

# @pysnooper.snoop()
def linear_data(x_range, y_range, num): # 线性数据生成
    """
        x_range : [start,end]
        y_range : [start,end]
        num : 数量
    """
    dx = x_range[1]-x_range[0]
    dy = y_range[1]-y_range[0]

    new_num = num-1

    xlist = [dx/new_num*n+x_range[0] for n in range(new_num)] + [x_range[1]] 
    ylist = [dy/new_num*n+y_range[0] for n in range(new_num)] + [y_range[1]]

    # print(dx,dy)
    # print(xlist)
    # print(ylist)
    assert len(xlist)==num , 'error'

    return xlist,ylist

# @pysnooper.snoop()
def linear_spring_data(k, ymax, num): # 弹簧刚度数据生成
    # k 刚度
    # ymax 力值最大值
    # num 单边数据长度
    # 需过0值

    ymax = abs(ymax)
    xmax = ymax/k
    x1,y1 = linear_data([-xmax,0],[-ymax,0],num)
    x2,y2 = linear_data([0,xmax],[0,ymax],num)

    return x1+x2[1:] , y1+y2[1:] 

# @pysnooper.snoop()
def linear_damer_data(c_p, vmax, num, c_n=None): # 减震器 阻尼数据生成
    # c_p   拉伸阻尼
    # vmax  速度最大值
    # num   单边数据长度
    # c_n   压缩阻尼
    if c_n == None:
        c_n = c_p

    x1,y1 = linear_data([-vmax,0],[-vmax*c_n,0],num)
    x2,y2 = linear_data([0,vmax],[0,vmax*c_p],num)

    return x1+x2[1:] , y1+y2[1:] 

# @pysnooper.snoop()
def linear_single_spring_data(k, ymax, num): # 弹簧刚度数据生成
    # 负值范围为 0值
    # k 刚度
    # ymax 力值最大值
    # num 单边数据长度
    # 需过0值

    ymax = abs(ymax)
    xmax = ymax/k
    x1,y1 = linear_data([-xmax,0],[0,0],num)
    x2,y2 = linear_data([0,xmax],[0,ymax],num)

    return x1+x2[1:] , y1+y2[1:] 


# ========================================================
# xlist  ylist
# 数据编辑 

def sorted_xy(xlist, ylist): # x_list 排序, y_list跟隨
    '''从小到大排序'''
    dic1 = {x:y for x,y in zip(xlist,ylist)}
    # 排序
    x = sorted(dic1, key=lambda x:dic1[x], reverse=True)
    y = [dic1[xn] for xn in x]
    return x,y


# ========================================================
# list1d 一位数据
# 数据处理

# 一维数据-数值转化
def value2str_list1(line, nlen=2): # 二维数据转为字符串
    """
        data    二维数据
        nlen    小数位数
        转化float数据, 保留nlen位小数
        若数据过小, 使用科学计数
    """

    new_line = []
    for value in line:
        if isinstance(value,float):
            if abs(value) < 10**(-(nlen+1)):
                temp = '{' + ':.{}e'.format(nlen) + '}' # 科学计数
                # '{:.2e}'.format(133) 科学计数格式
                value = temp.format(value)
            else:
                value = round(value,nlen)
        new_line.append(str(value))

    return new_line


# ========================================================
# list2d 二维数据 
# 数据处理

# 二维list数据 行列转换
def list2_change_rc(list2d):
    # 行列转换
    new_list2d = []
    for n in range(len(list2d[0])):
        new_line = []
        for line in list2d:
            new_line.append(line[n])

        new_list2d.append(new_line)

    return new_list2d

# 二维数据-数值转化
def value2str_list2(data, nlen=2): # 二维数据转为字符串
    """
        data    二维数据
        nlen    小数位数
        转化float数据, 保留nlen位小数
        若数据过小, 使用科学计数
    """
    new_data = []
    for line in data:
        new_line = []
        for value in line:
            if isinstance(value,float):
                if abs(value) < 10**(-(nlen+1)):
                    temp = '{' + ':.{}e'.format(nlen) + '}' # 科学计数
                    # '{:.2e}'.format(133) 科学计数格式
                    value = temp.format(value)
                else:
                    value = round(value,nlen)
            new_line.append(str(value))
        new_data.append(new_line)

    return new_data


# ========================================================
# 数据结构查看

def view_data_type(data): # 查看数据结构
    """
        列表和字典处理
        暂不支持numpy
    """
    # import pprint
    # import copy
    data = copy.copy(data)
    if isinstance(data, dict):
        # 字典
        for key in data:
            if isinstance(data[key], dict) or isinstance(data[key], list):
                # 字典 or 列表
                data[key] = view_data_type(data[key])
            else:
                n_type = type(data[key])
                n_type = f'{n_type}'.split("'")[1]
                data[key] = f'{n_type}'

        return data

    else:
        # 列表
        new_data = []
        current_type = []
        for value in data:
            n_type = type(value)
            n_type = f'{n_type}'.split("'")[1]

            if isinstance(value, list) or isinstance(value, dict): 
                # 列表 or 字典
                if n_type not in current_type:
                    current_type.append(n_type)
                    new_data.append(view_data_type(value))
            else:
                # 
                if n_type not in current_type:
                    current_type.append(n_type)
                    new_data.append(f'{n_type}..')

        return new_data
    


def str_view_data_type(data):  # 字符串化数据结构
    """
        列表和字典处理
        暂不支持numpy
    """
    str_output_data = pprint.pformat(view_data_type(data)).replace("'", ' ')
    return str_output_data

def test_str_view_data_type():

    data = [['test','asd'], {'test':[1,2,3,1.1,[1,2,3,4,1.1]]}]
    print(str_view_data_type(data))
    print(data)


if __name__ == '__main__':

    linear_data([1,10],[2,20],21)

    linear_spring_data(100,20000,11)

    linear_damer_data(10,520,11,1)

    linear_single_spring_data(100,20000,11)

    # import matplotlib.pyplot as plt
    # plt.plot(*linear_damer_data(10,520,11,1))
    # plt.plot(*linear_single_spring_data(100,20000,11))
    # plt.show()

    test_str_view_data_type()


    
