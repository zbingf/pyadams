"""
    python version : 3.7
    Adams version : 2017.2
    用途：
        Adm文件解析
    
    注： 
        1、 字符串编辑大写编辑
        2、 字典dic 关键词 为小写

    2020/11
"""
from pyadams import datacal

import math
import re
import copy
import pysnooper

import os.path
import logging
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)

# ===================================
# 子函数
strlower = lambda st1: re.sub(r'\s','',st1).lower()
strupper = lambda st1: re.sub(r'\s','',st1).upper()
list_gain = lambda list1,gain: [n*gain for n in list1]
list_loc = lambda list1,locs: [list1[n] for n in locs]
linear_spring_data = datacal.linear_spring_data
linear_single_spring_data = datacal.linear_single_spring_data
linear_damer_data = datacal.linear_damer_data
linear_spring_data = datacal.linear_spring_data

def values2list(values,locs): # 数值列表定位，含正负
    """
        values 列表数据 数值类型
        locs 对应列表位置， 可正可负
    """
    targets = []
    for loc in locs:
        if loc<0:
            targets.append(-values[abs(loc)])
        else:
            targets.append(values[loc])
    return targets


# ===================================
# 辨识模块

class AdmFile:
    """
        adm格式文件
        调用：AdmModel
        self.filepath 文本路径位置
        self.model 文本解析
    """
    def __init__(self,filepath):

        self.filepath = filepath
        self.file_read()
        self.filelist_cal()
        self.model = AdmModel(self.cmdlist,self.filelist) # adm 数据辨识

    def file_read(self): # adm文件读取
        """
            adm 文件命令读取
            输入 ： self.filepath
            输出 ： 
                self.filestr 文本字符串
                self.filelist  文本列表：每行为一项
        """

        filepath = self.filepath

        with open(filepath,'r') as f:
            filestr = f.read()

        filelist = filestr.split('\n')
        self.filestr = filestr
        self.filelist = filelist

    def filelist_cal(self): #adm文件字符串数据转化
        """
            针对 self.filelist 的数据处理
            输入 ： self.filelist
            输出 ： 
                self.cmdlist 命令组列表 二维数组
                    self.cmdlist[0]  单个完整命令数据
                        self.cmdlist[0][-1] 文本位置坐标信息(loc) [开头位置，结束位置]
        """

        filelist = self.filelist
        # 命令行检索
        isNote = False
        isFirstLine = False
        cmdlist = []
        oldline = []
        start,end = 0,0
        for loc,line in enumerate(filelist):
            line1 = line.lstrip()
            if line1: # 非空
                if line[0] != '!':
                    # 字符串非注释
                    isNote = False
                else:
                    isNote = True

                if line1[0] != ',':
                    # 命令为首行
                    isFirstLine = True
                else:
                    isFirstLine = False

                if not isNote:
                    """非注释行"""
                    if isFirstLine:
                        # 命令首行-开头
                        if 'list1' in vars():
                            # 参数存在
                            list1 += [[start,end]]
                            cmdlist.append(list1)

                        list1 = []
                        list1.append(oldline)
                        list1.append(line)
                        start = loc-1
                        end = loc
                    else:
                        end = loc
                        list1.append(line)

                oldline = line

        # num = 17
        # print(cmdlist[num])
        # print(filelist[cmdlist[num][-1][0]:cmdlist[num][-1][1]+1])
        self.cmdlist = cmdlist

        return cmdlist

    def updata(self):
        """
            更新数据
        """
        edit_cmdlists = []
        edit_objs = []
        obj_dic = {}
        n = 0
        for obj in self.model.all:
            if obj.isEdit:
                # 更新过的实例数据段
                edit_objs.append(obj)
                obj_dic[n] = obj.loc[0]
                n += 1
                edit_cmdlists.append(obj.cmdlist)
                # print(obj.cmdlist)
        
        # 根据文本档排序 以便于按顺序添加
        objlocs = sorted(obj_dic,key=lambda x :obj_dic[x]) 
        
        newlist = []
        start = 0
        for loc in objlocs:
            obj = edit_objs[loc]
            newlist += self.filelist[start:obj.loc[0]] 
            newlist += obj.cmdlist[:-1]
            start = obj.loc[1]+1

        newlist += self.filelist[start:] # 拼接剩余数据

        # 数据更新
        # self.filelist = newlist
        self.filestr = '\n'.join(newlist) # 不更新模型
        # self.model = AdmModel(self.filelist_cal(),self.filelist)

        return edit_cmdlists # 编辑过的adm模型数据

    def newfile(self,newfilepath=None):
        """
            文件创建
            newfilepath 默认 None , 即编辑原文件
        """
        if newfilepath == None:
            newfilepath = self.filepath

        with open(newfilepath,'w') as f :
            f.write(self.filestr)


class AdmCar(AdmFile): # 基于AdmFile扩展模型读取范围
    """
        在AdmFile基础上扩展解析范围
        用于car-adm模型
        对AdmModel数据进行再辨识
    """
    def __init__(self,filepath):
        super().__init__(filepath)
        
        self.car_spring = {}        # 弹簧解析实例，key为名称
        self.car_springnum = {}     # key为ID

        self.car_damper = {}        # 减振器解析实例，key为名称
        self.car_dampernum = {}     # key为ID

        self.car_bushing_objs = {}  # 临时存放
        self.car_bushing = {}       # 衬套解析实例，key为名称

        self.car_road = {}          # 路面路径实例，key为名称

        # 子函数
        self.isBushing = lambda name: sum([n in name for n in ['.bgl', '.bgr', '.bkl', '.bkr', '.bks', '.bgs']])

        self.sforce_read()
        self.spline_read()
        self.array_read()
        self.car_bushing_read()
        self.car_road_read()
        self.flex_read()

    def sforce_read(self):
        # sforce辨识
        for n in self.model.sforce:
            force_obj = self.model.sforce[n]
            if force_obj.isSpring:
                spline_id = force_obj.spline_id
                spline_obj = self.model.splinenum[spline_id]
                spring_obj = AdmSpring(force_obj,spline_obj)

                spring_id = force_obj.num
                spring_name = '.'.join(force_obj.name.split('.')[:-1]).lower()
                self.car_spring[spring_name] = spring_obj
                self.car_springnum[spring_id] = spring_obj

            if force_obj.isDamper:
                spline_id = force_obj.spline_id
                spline_obj = self.model.splinenum[spline_id]
                damper_obj = AdmDamper(force_obj,spline_obj)

                damper_id = force_obj.num
                damper_name = '.'.join(force_obj.name.split('.')[:-1]).lower()
                self.car_damper[damper_name] = damper_obj
                self.car_dampernum[damper_id] = damper_obj

        return True

    def spline_read(self):
        # spline 辨识
        spline_bushing_objs = {}
        for name in self.model.spline:
            spline_obj = self.model.spline[name]

            if self.isBushing(name):
                *bushing_name, bushing_type = name.split('.')
                bushing_name = '.'.join(bushing_name)
                if bushing_name in spline_bushing_objs:
                    spline_bushing_objs[bushing_name][bushing_type] = spline_obj
                else:
                    spline_objs = {}
                    spline_objs[bushing_type] = spline_obj
                    spline_bushing_objs[bushing_name] = spline_objs

        self.car_bushing_objs['spline'] = spline_bushing_objs

        return True

    def array_read(self):
        # array 辨识
        array_bushing_objs = {}
        for name in self.model.array:
            array_obj = self.model.array[name]
            if self.isBushing(name):
                *bushing_name, bushing_type = name.split('.')
                bushing_name = '.'.join(bushing_name)
                if bushing_name in array_bushing_objs:
                    array_bushing_objs[bushing_name][bushing_type] = array_obj
                else:
                    array_objs = {}
                    array_objs[bushing_type] = array_obj
                    array_bushing_objs[bushing_name] = array_objs

        self.car_bushing_objs['array'] = array_bushing_objs
        
        return True

    def flex_read(self): # 柔性体数据读取,返回柔性体名称
        # 历遍matrix
        # 读取后缀带 '.MTX' 的filename
        # 将数据存入 self.flex_mtxs 中

        objs = self.model.matrix
        mtx_filenames = []
        for name in objs:
            filename = objs[name].filename.upper()
            if '.MTX' in filename:
                mtx_filenames.append(filename)
        # print(mtx_filenames)
        self.flex_mtxs = list(set(mtx_filenames))

    def car_bushing_read(self):
        # car bushing 检索
        if self.car_bushing_objs['spline']: # 衬套数据存在
            names = list(self.car_bushing_objs['spline'].keys())
            for name in names:
                spline_objs = self.car_bushing_objs['spline'][name]
                array_objs = self.car_bushing_objs['array'][name]
                self.car_bushing[name] = AdmCarBushing(spline_objs,array_objs)

        return True

    def car_road_read(self): 
        # 路面路径检索
        car_road_objs = {}
        for name in self.model.string:
            # key为小写
            strline = self.model.string[name].strline
            if re.match(r'.*?\.rdf_file\s*\Z', name):
                # 调用AdmRoad
                car_road_objs[name] = AdmRoad(self.model.string[name])

        self.car_road = car_road_objs

    def set_car_roads(self):
        # 统一设置 路面路径
        for name in self.car_road:
            self.car_road[name].set_path(path)


class AdmModel:
    """
        adm 数据辨识模块
        存储各实例
        输入： cmdlist 命令组列表
        
        self.all 放置所有模块part/marker/join 实例
        
    """
    def __init__(self, cmdlist, filelist):
        self.cmdlist = cmdlist
        self.filelist = filelist

        self.part = {}
        self.partnum = {} # id 定位

        self.marker = {}
        self.markernum = {} 

        self.join = {}
        self.joinnum = {}

        self.spline = {}
        self.splinenum = {}

        self.variable = {}
        self.variablenum = {}

        self.bushing = {}
        self.bushingnum = {}

        self.sforce = {}
        self.sforcenum = {}

        self.array = {}
        self.arraynum = {}

        self.string = {}
        self.stringnum = {}

        self.matrix = {}
        self.matrixnum = {}

        self.flexbody ={}

        self.request = {}


        self.all = []
        self.read()

    def read(self):
        """
            辨识命令数据
        """
        for cmd in self.cmdlist[2:]:
            temp = cmd[0].split('=')
            if len(temp) > 1:
                # print(cmd[0])
                # print(cmd)
                # print(temp)
                name = temp[-1].split("'")[-2].lower()
                if 'PART' in cmd[1].upper():
                    self.part[name] = AdmPart(cmd)
                    self.partnum[self.part[name].num] = self.part[name]
                    self.all.append(self.part[name])

                elif 'SPLINE' in cmd[1].upper():
                    self.spline[name] = AdmSpline(cmd)
                    self.splinenum[self.spline[name].num] = self.spline[name]
                    self.all.append(self.spline[name])
                
                elif 'MARKER' in cmd[1].upper():
                    self.marker[name] = AdmMarker(cmd)
                    self.markernum[self.marker[name].num] = self.marker[name]
                    self.all.append(self.marker[name])
                
                elif 'BUSHING' in cmd[1].upper():
                    self.bushing[name] = AdmBushing(cmd)
                    self.bushingnum[self.bushing[name].num] = self.bushing[name]
                    self.all.append(self.bushing[name])

                elif 'SFORCE' in cmd[1].upper():
                    self.sforce[name] = AdmSforce(cmd)
                    self.sforcenum[self.sforce[name].num] = self.sforce[name]
                    self.all.append(self.sforce[name])
                
                elif 'ARRAY' in cmd[1].upper():
                    self.array[name] = AdmArray(cmd)
                    self.arraynum[self.array[name].num] = self.array[name]
                    self.all.append(self.array[name])

                elif 'VARIABLE' in cmd[1].upper():
                    self.variable[name] = AdmVariable(cmd)
                    self.variablenum[self.variable[name].num] = self.variable[name]
                    self.all.append(self.variable[name])
                
                elif 'STRING' in cmd[1].upper():
                    self.string[name] = AdmString(cmd)
                    self.stringnum[self.string[name].num] = self.string[name]
                    self.all.append(self.string[name])
                
                elif 'MATRIX' in cmd[1].upper():
                    cmd_copy = copy.deepcopy(cmd)
                    cmd_copy[-1][0] -= 1
                    newcmd = [ self.filelist[cmd_copy[-1][0]] ]
                    newcmd.extend(cmd_copy)
                    # 初始位置,后退一行
                    self.matrix[name] = AdmMatrix(newcmd)
                    self.matrixnum[self.matrix[name].num] = self.matrix[name]
                    self.all.append(self.matrix[name])

                elif 'FLEX_BODY' in cmd[1].upper():
                    self.flexbody[name] = AdmFlexBody(cmd)

                    self.all.append(self.flexbody[name])    

                elif 'REQUEST' in cmd[1].upper():
                    self.request[name] = AdmRequest(cmd)

                    self.all.append(self.request[name])

        #       else:
        #           return False
        # return True

    def get_req_comp(self,reqs,comps):
        """
            通过 reqs 和 comps 获取 id
            reqs    list    
            comps   list    
        """
        req_loc = []
        comp_loc = []
        for req,comp in zip(reqs,comps):
            # target = req+'.'+comp
            # print(req,comp)
            for name in  self.request.keys():
                req_name = self.request[name].req_name
                if req.lower() == req_name:
                    # print(req,name)
                    # print(name)
                    comp_dic = self.request[name].components
                    if comp in comp_dic.keys():
                        # print(comp_dic[comp])
                        req_loc.append(self.request[name].num)
                        comp_loc.append(comp_dic[comp])
                        # print(req,comp)
        # print(req_loc)
        # print(comp_loc)
        return req_loc,comp_loc


# ===================================Base
# 基础模块
class AdmCmd:
    """
        子模块辨识
        文本格式：
            !    adams_view_name='BUSHING_1'
            BUSHING/1
            , I = 65 # marker id i
            , J = 66 # marker id j
            , C = 0.3, 0.3, 0.3 # N/(mm/s)
            , K = 1.2, 1.2, 1.2 # N/mm
            , CT = 5200, 5200, 5200  # N*mm / (rad/s)
            , KT = 21000, 21000, 21000 # N*mm / rad
            , FORCE = 0,0,132412 # 预载
    """
    def __init__(self,cmdlist):
        self.cmdlist = cmdlist
        # 名称
        self.name = cmdlist[0].split('=')[-1].split("'")[-2]
        if '/' in cmdlist[1] and cmdlist[1][0]!='!':
            self.num = int(cmdlist[1].split('/')[-1])
        elif cmdlist[1][0]=='!':
            # MATRIX [1]为单位行
            if 'adams_view_units'.upper() in cmdlist[1][0].upper():
                "adams_view_units='no_units'"
                self.units = cmdlist[1][0].split('=')[-1].split('\'')[1]
            self.num = int(cmdlist[2].split('/')[-1])


        # 位置信息
        self.loc = cmdlist[-1] 
        # 是否编辑更新
        self.isEdit = False

        # 文本数据处理 lambda
        # 格式： , KT = 21000, 21000, 21000
        self.str2list = lambda line: [float(n) for n in line.split('=')[-1].split(',')]
        # 格式： , J = 66
        self.str2int = lambda line: int(line.split('=')[-1])
        # 格式： , MASS = 0.1
        self.str2float = lambda line: float(line.split('=')[-1])
        # 格式： , REULER = 120D,38.65980825D,245.7324904D
        self.str2list_deg = lambda line: [float(n[:-1]) for n in line.split('=')[-1].split(',')]
        # 格式:   , 1.0E+10
        self.str2list_extend = lambda line: [float(n) for n in line.split(',') if n]
        # , FUNCTION = 2.0*2500.0*IF(0.0:0,1.0,0.0)
        self.str2str_equal = lambda str1,str2 : ', {} = {}'.format(str1,str2)
        # 列表数据 等比例增益
        self.list_gain = lambda list1,gain: [n*gain for n in list1]

    def value2str(self,str1,value): # 数值转化字符串
        # 格式： , J = 66 或 , MASS = 0.1
        if value == int(value):
            value = int(value)

        return ', {} = {}'.format(str1,value)

    def list2str(self,str1,list1,r=''): # 数值组转化为字符串
        # 格式： , KT = 21000, 21000, 21000 或 , REULER = 120D, 38.65980825D, 245.7324904D
        # r为后缀设置如 D 
        for n in range(len(list1)):
            if list1[n] == int(list1[n]):
                list1[n] = int(list1[n])

        return ', {} = {}'.format(str1,','.join([str(n)+r for n in list1]))


class AdmSpline(AdmCmd): 
    """
        spline 辨识
        文本格式：
            !    adams_view_name='spline_1'
            SPLINE/1
            ,X = 1, 2, 3
            ,5,6,7,8
            ,9,10,11,12
            ,13,14,15
            ,Y = 1, 2, 3
            ,5,6,7,8
            ,9,10,11,12
            ,13,14,15       
    """
    def __init__(self,cmdlist):
        super().__init__(cmdlist)
        xStart = False
        yStart = False
        self.xlist = []
        self.ylist = []
        self.linear = False # 没有后缀 LINEAR_EXTRAPOLATE
        for line in cmdlist[:-1]:
            line1 = line.replace(' ','')
            if ',X='.lower() in line1.lower():
                # print(x)
                xStart = True
                yStart = False
                self.xlist += self.str2list(line)
                continue
            elif ',Y='.lower() in line1.lower():
                xStart = False
                yStart = True
                self.ylist += self.str2list(line)
                continue
            if xStart:
                self.xlist += [float(n) for n in line1.split(',') if n]
            if yStart:
                if line1 and 'LINEAR_EXTRAPOLATE' not in line1.upper():
                    # print(line1,'\n\n')
                    # print(line1.split(','))
                    self.ylist += [float(n) for n in line1.split(',') if n]
                if 'LINEAR_EXTRAPOLATE' in line1.upper():
                    self.linear = True
        
        # 用于3d曲线计数, y首位为计数, 故x个数基础上加1
        self.n_y = len(self.xlist)+1 

    def updata(self,xlist=None,ylist=None,x_gain=1,y_gain=1):
        """
            编辑命令
            
            x_gain  x数组缩放
            y_gain  y数值缩放
        """
        self.isEdit = True # 数据变更标示
        if xlist == None:
            xlist = self.xlist
            ylist = self.ylist
        if x_gain != 1:
            xlist = self.list_gain(xlist,x_gain)
        if y_gain != 1:
            ylist = self.list_gain(ylist,y_gain)

        newlist = [] # 新字符串组
        newlist += self.cmdlist[:2]
        newlist += self.value_change(xlist,'X')
        newlist += self.value_change(ylist,'Y')
        if self.linear:
            newlist.append(', LINEAR_EXTRAPOLATE')
        newlist.append(self.cmdlist[-1]) # 坐标添加
        self.cmdlist = newlist
        self.xlist = xlist
        self.ylist = ylist
        # print(newlist)
        # print(xlist)
        # print(newlist)
        return newlist

    def updata_3d(self, ylist=None, x_gain=1, y_gain=1):
        n_line = self.n_y
        self.isEdit = True
        if ylist == None:
            xlist = self.xlist
            ylist = self.ylist
        else:
            xlist = self.xlist

        if x_gain != 1:
            xlist = self.list_gain(xlist, x_gain)
        if y_gain != 1:
            ylist = self.list_gain(ylist, y_gain)

        self.num_yline = int(len(ylist)/n_line)

        newlist = []
        newlist += self.cmdlist[:2]
        newlist += [self.list2str('X',xlist,r=' ')]

        for n in range(self.num_yline):
            target_line = ylist[n*n_line:(n+1)*n_line]
            newlist += [self.list2str('Y',target_line,r=' ')]

        if self.linear:
            newlist.append(', LINEAR_EXTRAPOLATE')

        newlist.append(self.cmdlist[-1])
        self.cmdlist = newlist
        self.xlist = xlist
        self.ylist = ylist

        return newlist

    def get_x(self,y,kind=None):
        """
            数值or数组 输入
            插值拟合
        """
        from scipy import interpolate
        if kind == None:
            f = interpolate.interp1d(self.ylist,self.xlist)
        else:
            f = interpolate.interp1d(self.ylist,self.xlist,kind=kind)
        return f(y)

    def get_y(self,x,kind=None):
        """
            数值or数组 输入
            插值拟合
        """
        from scipy import interpolate
        if kind == None:
            f = interpolate.interp1d(self.xlist,self.ylist)
        else:
            f = interpolate.interp1d(self.xlist,self.ylist,kind=kind)
        return f(x)

    @staticmethod
    def value_change(xlist,str1='X'):
        """
            将数据转化为字符串组输出
            xlist 一维数据 list
            str1 开头 X 或 Y
        """
        newlist = []
        if len(xlist) <= 3 : # x数组长度小于3
            newlist.append(f',{str1} = '+', '.join([str(n) for n in xlist]))
        else: 
            newlist.append(f',{str1} = '+', '.join([str(n) for n in xlist[:3]]))
            nlen = len(xlist[3:])
            nlist = math.ceil(nlen/4)
            xlist1 = xlist[3:]
            for n in range(nlist):
                if n == nlist-1:
                    newlist.append(
                        ','+','.join([str(n) for n in xlist1[n*4:]])
                        )
                else:
                    newlist.append(
                        ','+','.join([str(n) for n in xlist1[n*4:(n+1)*4]])
                        )
            # print(newlist)
        return newlist

    
class AdmPart(AdmCmd):
    """
        Part 辨识
        文本格式：
            !    adams_view_name='part_lower_rod_3'
            PART/12
            , MASS = 0.1
            , CM = 52
            , IP = 0.1, 0.1, 0.1
    """
    def __init__(self,cmdlist):
        super().__init__(cmdlist)

        for line in cmdlist[:-1]:
            line1 = line.replace(' ','')
            if ',MASS=' in line1:
                self.mass = self.str2float(line)
            if ',CM=' in line1:
                self.cm = self.str2int(line)
            if ',IP=' in line1:
                # print(line1)
                self.ip = self.str2list(line)

    def updata(self):
        self.isEdit = True
        newlist = []
        newlist += self.cmdlist[:2]
        newlist += [self.value2str('MASS',self.mass)]
        newlist += [self.value2str('CM',self.cm)]
        newlist += [self.list2str('IP',self.ip)]
        newlist.append(self.cmdlist[-1])

        # print(newlist)

        self.cmdlist = newlist
        return newlist


class AdmMarker(AdmCmd):
    """
        marker 辨识

        文本格式：
            !                       adams_view_name='mar_lower_rod_1'
            MARKER/46
            , PART = 10
            , QP = -1202.146997, 75, -1250
            , REULER = 120D, 38.65980825D, 245.7324904D
    """
    def __init__(self,cmdlist):
        super().__init__(cmdlist)
        # 方向默认为 0,0,0
        self.ori = [0,0,0]
        for line in cmdlist[:-1]:
            line1 = line.replace(' ','')
            if 'PART' in line1:
                self.part = self.str2int(line)
            if 'QP' in line1:
                self.location = self.str2list(line)
            if 'REULER' in line1 and 'D' in line1:
                self.ori = self.str2list_deg(line1)

    def updata(self):
        self.isEdit = True
        newlist = []
        newlist += self.cmdlist[:2]
        newlist += [self.value2str('PART',self.part)]
        newlist += [self.list2str('QP',self.location)]
        newlist += [self.list2str('REULER',self.ori,'D')]
        newlist.append(self.cmdlist[-1])
        
        self.cmdlist = newlist
        return newlist


class AdmBushing(AdmCmd):
    """
        view模型
        buhing 衬套数据编辑
        文本格式：
            !    adams_view_name='BUSHING_1'
            BUSHING/1
            , I = 65 # marker id i
            , J = 66 # marker id j
            , C = 0.3, 0.3, 0.3 # N/(mm/s)
            , K = 1.2, 1.2, 1.2 # N/mm
            , CT = 5200, 5200, 5200  # N*mm / (rad/s)
            , KT = 21000, 21000, 21000 # N*mm / rad
            , FORCE = 0,0,132412 # 预载
    """
    def __init__(self,cmdlist):
        super().__init__(cmdlist)
        # 初始化设置
        self.c = [0,0,0]
        self.k = [0,0,0]
        self.ct = [0,0,0]
        self.kt = [0,0,0]
        self.force = [0,0,0]
        for line in cmdlist[:-1]:
            line1 = line.replace(' ','')
            if ',I=' in line1 and ',' in line1:
                self.i = self.str2int(line)
            if ',J=' in line1 and ',' in line1:
                self.j = self.str2int(line)
            if ',C=' in line1:
                self.c = self.str2list(line)
            if ',K=' in line1 and ',' in line1:
                self.k = self.str2list(line)
            if ',CT=' in line1 and ',' in line1:
                self.ct = self.str2list(line)
            if ',KT=' in line1 and ',' in line1:
                self.kt = self.str2list(line)
            if ',FORCE=' in line1 and ',' in line1:
                self.force = self.str2list(line)

    def updata(self):
        self.isEdit = True
        newlist = []
        newlist += self.cmdlist[:2]
        newlist += [self.value2str('I',self.i)]
        newlist += [self.value2str('J',self.j)] 
        newlist += [self.list2str('C',self.c)]
        newlist += [self.list2str('K',self.k)]
        newlist += [self.list2str('CT',self.ct)]
        newlist += [self.list2str('KT',self.kt)]
        newlist += [self.list2str('FORCE',self.force)]
        newlist.append(self.cmdlist[-1])
        
        self.cmdlist = newlist
        return newlist


class AdmSforce_old(AdmCmd):
    """
        !     adams_view_name='SPRING_1.sforce'
        SFORCE/1
        , TRANSLATIONAL
        , I = 75
        , J = 76
        , FUNCTION =  - 4.0E-04*(dm(75,76)-482.1825380496)
        , - 1.0E-04*vr(75,76)
        , + 0.0
    """
    def __init__(self,cmdlist):
        super().__init__(cmdlist)
        # 初始化设置
        # 初始化设置
        self.k = 0 # 刚度
        self.c = 0 # 阻尼
        self.preload = 0 # 预载
        # linec = False
        self.is_cal = True
        try:
            for line in cmdlist[:-1]:
                line1 = line.replace(' ','')
                if ',FUNCTION=' in line1 :
                    self.k = float(line1.split('=')[-1].split('*')[0])
                    linec = True
                    continue
                # if linec:
                if 'vr' in line1.lower():
                    self.c = float(line1.split('*')[0].split('-')[-1])
                    continue
                    # linec = False
                if '+' in line1.lower():
                    self.preload = float(line1.split('+')[-1])
                    continue
        except:
            print('\n'+'*'*50)
            print('SForce Read False')
            print(cmdlist)
            print('\n'+'*'*50)
            self.is_cal = False # 不计算
    
    def updata(self):
        if self.is_cal:
            self.isEdit = True
            cmdlist = self.cmdlist
            # linec = False
            for n,line in enumerate(cmdlist[:-1]):
                line1 = line.replace(' ','')
                if ',FUNCTION=' in line1:
                    # 刚度
                    # line.split('=')
                    newline = ',FUNCTION = {} *'.format(self.k) + ''.join(line1.split('*')[1:])
                    cmdlist[n] = newline
                    continue
                    # linec = True
                # if linec:
                if 'vr' in line1.lower():
                    # 阻尼
                    newline = ',-'+str(self.c)+'*'+line1.split('*')[-1]
                    cmdlist[n] = newline
                    continue
                    # linec = False
                if '+' in line1.lower():
                    # 预载
                    newline = ', + '+str(self.preload)
                    cmdlist[n] = newline
                    continue

            # print(cmdlist)
            self.cmdlist = cmdlist
            return cmdlist
        return False


class AdmPoint(AdmCmd):
    """
        暂未使用
    """
    def __init__(self,cmdlist):
        super().__init__(cmdlist)
        pass


class AdmArray(AdmCmd): # Array 数据编译
    
    def __init__(self,cmdlist):
        super().__init__(cmdlist)
        self.size = 0
        self.numbers = []
        self.get_loc = {}
        self.variables = []

        for n, line in enumerate(cmdlist[:-1]):
            line1 = line.replace(' ','').upper()
            if ',SIZE=' in line1:
                self.size = self.str2int(line1)
                self.get_loc[n] = 'size'

            elif ',NUMBERS=' in line1:
                self.numbers = self.str2list(line1)
                self.get_loc[n] = 'numbers'

            elif ',VARIABLES=' in line1:
                self.variables = self.str2list(line1)
                self.get_loc[n] = 'variables'

            elif re.match(r',-?\+?\d.*',line1):
                temp = self.str2list_extend(line1)
                if len(self.numbers)>0:
                    self.numbers += temp
                    self.get_loc[n] = None
                elif len(self.variables)>0:
                    self.variables += temp
                    self.get_loc[n] = None
                    
        str1 = '\nAdmArray 的 ARRAY数据读取有误\n{}'.format('\n'.join(cmdlist[:-1]))
        assert len(self.numbers)==self.size or len(self.variables)==self.size ,str1
        # print(cmdlist)
        # self.updata()

    # @pysnooper.snoop(prefix='Array-updata ->',watch=(),depth=1)
    def updata(self):
        """
            编辑命令
        """
        self.isEdit = True
        n_edit = self.get_loc.keys()
        newlist = []
        for n,line in enumerate(self.cmdlist[:-1]):
            if n in n_edit:
                var = self.get_loc[n]
                if var == 'size':
                    newlist += [self.value2str('SIZE',self.size)]

                elif var == 'variables':
                    newlist += [self.list2str('VARIABLES',self.variables)]

                elif var == 'numbers':
                    newlist += [self.list2str('NUMBERS',self.numbers)]

                elif var == None:
                    pass
                else:
                    newlist.append(line)
            else:
                newlist.append(line)
        newlist.append(self.cmdlist[-1])
        self.cmdlist = newlist
        # print(newlist)
        return newlist


class AdmSforce(AdmCmd):
    """
        !     adams_view_name='SPRING_1.sforce'
        SFORCE/1
        , TRANSLATIONAL
        , I = 75
        , J = 76
        , FUNCTION =  - 4.0E-04*(dm(75,76)-482.1825380496)
        , - 1.0E-04*vr(75,76)
        , + 0.0
    """
    def __init__(self,cmdlist):
        super().__init__(cmdlist)
        self.get_loc = {}
        self.str_fun = ''

        for n,line in enumerate(cmdlist[:-1]):
            line1 = line.replace(' ','').upper()
            if ',FUNCTION=' in line1:
                self.str_fun = line1.split('=')[-1]
                self.get_loc[n] = 'FUNCTION'
                fun_start = True
            elif re.match(r'\A,',line1):
                if len(self.get_loc)>0:
                    self.str_fun += line1[1:]
                    self.get_loc[n] = None

        self.isLinear = self.re_linear()
        self.isSpring = self.re_spring()
        self.isDamper = self.re_damper()
        self.isBumpstop = self.re_bumpstop()
        self.isReboundstop = self.re_reboundstop()
        # print([self.isLinear,self.isSpring,self.isDamper])

        # print(self.isLinear)
        # self.updata()

    def updata(self): # 更新文件
        self.isEdit = True
        n_edit = self.get_loc.keys()
        newlist = []
        new_str_fun = ''

        if self.isLinear: # 线性
            # '-0.46*(DM(1,2)-770.1298591796)-0.11*VR(1,2)+-10.086'
            new_str_fun += f'-{self.k}*({self.dm_str}-{self.init_len})-{self.c}*{self.vr_str}+{self.preload}'
        elif self.isSpring: # car spring 模式
            # '1.0*akispl(299.7342371-dm(221,589),0,329)'
            new_str_fun += f'{self.gain}*AKISPL({self.init_len}-{self.dm_str},{self.akispl_num},{self.spline_id})'
            # print(new_str_fun)

        # print(new_str_fun)
        for n,line in enumerate(self.cmdlist[:-1]):
            if n in n_edit:
                var = self.get_loc[n]
                if var == 'FUNCTION':
                    if new_str_fun:
                        newlist += [self.str2str_equal('FUNCTION',new_str_fun)]
                    else: # function 未变更
                        newlist += [self.str2str_equal('FUNCTION',self.str_fun)]
                elif var == None:
                    pass
                else:
                    newlist.append(line)
            else:
                newlist.append(line)
        newlist.append(self.cmdlist[-1])
        self.str_fun = new_str_fun
        self.cmdlist = newlist
        # print(newlist)
        return newlist
        
    def re_linear(self): # 线性解析
        """
            线性解析
            包含 ：
                刚度
                阻尼
                预载
            格式：-0.46*(DM(1,2)-770.1298591796)-0.11*VR(1,2)+-10.086
        """
        line = self.str_fun
        # print(self.str_fun)
        re1 = re.search(r'-(\d+\.?\d*)\*\((DM\(\d+,\d+\))-(\d+\.?\d*)\)',line)
        # 刚度辨识
        if re1:
            self.k = float(re1.group(1))
            self.dm_str = re1.group(2)
            self.init_len = float(re1.group(3))
            str1 = re1.group(0)
            line = ''.join(line.split(str1))

        re2 = re.search(r'-(\d+\.?\d*)\*(VR\(\d+,\d+\))',line)
        # 阻尼辨识
        if re2:
            self.c = float(re2.group(1))
            self.vr_str = re2.group(2)
            str2 = re2.group(0)
            line = ''.join(line.split(str2))

        # re3 = re.search(r'(\+|-)+(\d+\.?\d*)\Z',line)
        re3 = re.search(r'(\+|-)+(\d+\.?\d*[Ee]?\+?-?\d*)\Z',line)  # 包含科学计数 20210329
        # 预载辨识
        if re1 and re2 and re3:
            self.preload = float(re3.group(1)+re3.group(2))
            return True

        return False

    def re_spring(self): # car spring 辨识
        '1.0*akispl(299.7342371-dm(221,589),0,329)'

        line = self.str_fun
        re1 = re.search(r'\A(\d+\.?\d*)?\*?AKISPL\((\d+\.?\d*)-(DM\(\d+,\d+\)),(\d+),(\d+)\)\Z',line)
        if re1:
            if '.NSL' in self.name.upper() or '.NSR' in self.name.upper():
                # print(re1)
                self.gain = float(re1.group(1)) if re1.group(1)!=None else 1
                self.init_len = float(re1.group(2))
                self.dm_str = re1.group(3)
                self.akispl_num = int(re1.group(4))
                self.spline_id = int(re1.group(5))
                # print(re1.groups())
                # print(self.name)
                return True
        return False

    def re_damper(self): # car damper 辨识
        'step(vr(528,577), -1e-4, 1.0, 1e-4, 1.0)*akispl(vr(528,577),0,330)'

        line = self.str_fun
        str1 = r'\ASTEP\((VR\(\d+,\d+\)),.*?\)\*AKISPL\((VR\(\d+,\d+\)),\d+,(\d+)\)\Z'
        re1 = re.search(str1,line)
        if re1:
            if '.DAL' in self.name.upper() or '.DAR' in self.name.upper():
                self.spline_id = int(re1.group(3))
                # print(re1.group())
                # print(re1.groups())
                # print(self.name)
                return True
        return False

    def re_bumpstop(self): # 缓冲块
        
        line = self.str_fun
        '1.0*AKISPL(varval(127),0,736)'
        str1 = r'\A(\d+\.?\d*)\*AKISPL\((VARVAL\(\d+\)),\d+,(\d+)\)\Z'
        '1.0*AKISPL(MAX(0,451.4684741-DM(925,872)),0,736)'
        str2 = r'\A(\d+\.?\d*)\*AKISPL\((MAX\(\d+,DM\(\d+,\d+\)-(\d+\.?\d*)\)),\d+,(\d+)\)\Z'
        '-1.0*1.0*AKISPL(MAX(0,DM(925,872)-451.4684741),0,736)'
        str3 = r'\A-(\d+\.?\d*)\*(\d+\.?\d*)\*AKISPL\((MAX\(\d+,DM\(\d+,\d+\)-(\d+\.?\d*)\)),\d+,(\d+)\)\Z'
        for strn in [str1,str2,str3]:
            ren = re.search(strn,line)
            if ren:
                if '.BUL' in self.name.upper() or '.BUR' in self.name.upper():
                    self.spline_id = int(ren.groups()[-1])
                    # print(self.name)
                    return True
        return False

    def re_reboundstop(self): # 缓冲块
                
        line = self.str_fun
        '-1.0*1.0*AKISPL(varval(130),0,742)'
        str1 = r'\A-(\d+\.?\d*)\*(\d+\.?\d*)\*AKISPL\((VARVAL\(\d+\)),\d+,(\d+)\)\Z'
        '-1.0*1.0*AKISPL(MAX(0,DM(939,884)-571.4684741),0,742)'
        str2 = r'\A-(\d+\.?\d*)\*(\d+\.?\d*)\*AKISPL\((MAX\(\d+,DM\(\d+,\d+\)-(\d+\.?\d*)\)),\d+,(\d+)\)\Z'
        '1.0*AKISPL(MAX(0,571.4684741-DM(939,884)),0,742)'
        str3 = r'\A(\d+\.?\d*)\*AKISPL\((MAX\(\d+,(\d+\.?\d*)-DM\(\d+,\d+\)\)),\d+,(\d+)\)\Z'
        for strn in [str1,str2,str3]:
            ren = re.search(strn,line)
            if ren:
                if '.REL' in self.name.upper() or '.RER' in self.name.upper():
                    self.spline_id = int(ren.groups()[-1])
                    # print(self.name)
                    return True
        return False


class AdmVariable(AdmCmd):
    """
    !        adams_view_name='TR_Rear_Suspension.bul_jounce_stop.penetration'
    VARIABLE/125
    , FUNCTION = max(0, 535.4462508 - dm(867, 916))

    !tire x velocity
    !              adams_view_name='TR_Front_Tires.til_wheel.u_belt_vx'
    VARIABLE/151
    , FUNCTION = USER(906, 1, 1017, 1000, 1000)\
    , ROUTINE = abgTire::var906

    """
    def __init__(self,cmdlist):
        super().__init__(cmdlist)
        self.get_loc = {}
        fun_start = False
        rou_start = False
        self.str_fun = ''
        self.srt_rou = ''
        for n,line in enumerate(cmdlist[:-1]):
            line1 = line.replace(' ','').upper()
            if ',FUNCTION=' in line1:
                self.str_fun = line1.split('=')[-1]
                self.get_loc[n] = 'FUNCTION'
                # print(line1)
                fun_start = True
            elif re.match(r'\A,',line1) and fun_start and ',ROUTINE=' not in line1:
                # print(line1)
                if len(self.get_loc)>0:
                    self.str_fun += line1[1:]
                    self.get_loc[n] = None
            elif ',ROUTINE=' in line1:
                self.srt_rou = line1.split('=')[-1]
                self.get_loc[n] = 'ROUTINE'
                # print(line1)
                fun_start = False
                rou_start = True
            elif re.match(r'\A,',line1) and rou_start and ',FUNCTION=' not in line1:
                self.srt_rou += line1[1:]
                self.get_loc[n] = None

        # print('\n')
        # print('*'*50)
        # print(self.str_fun)
        # print(self.srt_rou)
        # print('*'*50)
        # print('\n')

    def updata(self):
        """暂不进行更改"""
        pass


class AdmString(AdmCmd):
    """
        字符串庶读取
        单行读取
        格式：
            !              adams_view_name='TR_Front_Tires.tir_wheel.tpf_file'
            STRING/103
            , STRING =mdids://For_FEMFAT_LAB/tires.tbl/TR_front_pac89.tir

        self.strline    字符串数据
    """
    def __init__(self,cmdlist):
        super().__init__(cmdlist)
        
        self.strline = ''
        self.get_loc = {}
        for n, line in enumerate(cmdlist[:-1]):
            line1 = line.replace(' ','').upper()
            if ',STRING=' in line1:
                self.strline = line1.split('=')[-1]
                self.get_loc[n] = 'strline'
        
        #       print(line1)
        # print(self.strline)

    def updata(self):
        """
            更新
        """
        self.isEdit = True
        n_edit = self.get_loc.keys()
        newlist = []
        for n,line in enumerate(self.cmdlist[:-1]):
            if n in n_edit:
                var = self.get_loc[n]
                if var == 'strline':
                    newlist += [self.str2str_equal('STRING',self.strline)]
                elif var == None:
                    pass
                else:
                    newlist.append(line)
            else:
                newlist.append(line)

        newlist.append(self.cmdlist[-1])
        self.cmdlist = newlist

        return newlist


class AdmRequest(AdmCmd): # 用于req文件
    """
        用于req文件获取

        当前仅作为读取
        !               adams_view_name='testrig.steering_motion_demands'
        REQUEST/2
        , TITLE = Steering Demands
        , COMMENT = Steering Demands steering_angle/steering_rack_disp
        , CUNITS = "no_units", "angle", "length", "no_units", "no_units", "no_units"
        , "no_units", "no_units"
        , CNAMES = "", "steering_angle", "steering_rack_disp", "", "", "", "", ""
        , RESULTS_NAME = driver_demands
        , F2 = AZ(87,205)\
        , F3 = DZ(80,99,99)
    """
    def __init__(self,cmdlist):
        super().__init__(cmdlist)
        
        self.components = {}
        self.get_loc = {}
        isCNames = False
        comps_list = []
        for n, line in enumerate(cmdlist[:-1]):
            line1 = line.replace(' ','').upper()
            if ',CNAMES=' in line1:
                self.get_loc[n] = 'CNAMES'
                # print(line1)
                isCNames = True
                comps_list = line1.split('=')[-1].split(',')
                continue

            elif ',RESULTS_NAME=' in line1:
                self.get_loc[n] = 'RESULTS_NAME'
                self.req_name = line1.split('=')[-1].lower()

            elif '=' in line1:
                isCNames = False
                continue

            if isCNames and ','==line1[0]:
                comps_list.extend( line1.split(',')[1:] )
                continue

        for n2,line2 in enumerate(comps_list):
            for line3 in line2.split('"'):
                if line3:
                    if n2 > 3:
                        self.components[line3.lower()] = n2-1 # 用于req文件获取
                    else:
                        self.components[line3.lower()] = n2

                # self.components = 
                
        # print(self.components)


class AdmMatrix(AdmCmd): # 包含柔性体文件数据
    """
    注: Matrix 开头多一行单位备注 !!!!!!
    !              adams_view_name='front_antiroll.fbs_antiroll_R_MODE'
    !              adams_view_units='no_units'
    MATRIX/10
    , FILE = front_antiroll_fbs_antiroll.mtx
    , NAME = R_MODE
    """
    def __init__(self,cmdlist):
        super().__init__(cmdlist)
        # print(self.name)
        self.filename = ''
        self.martix_name = ''
        self.get_loc = {}
        for n, line in enumerate(cmdlist[:-1]):
            line1 = line.replace(' ','').upper()
            if ',FILE=' in line1:
                self.filename = line1.split('=')[-1]
                self.get_loc[n] = 'filename'
            if ',NAME=' in line1:
                self.martix_name = line1.split('=')[-1]
                self.get_loc[n] = 'martix_name'

        # print(cmdlist)
        # try:
        #   print(self.units)
        # except:
        #   pass
        # print(self.name)
        # print(self.martix_name)

    def updata(self):

        self.isEdit = True
        n_edit = self.get_loc.keys()
        newlist = []
        for n,line in enumerate(self.cmdlist[:-1]):
            if n in n_edit:
                var = self.get_loc[n]
                if var == 'filename':
                    newlist += [self.str2str_equal('FILE',self.filename)]
                if var == 'martix_name':
                    newlist += [self.str2str_equal('NAME',self.martix_name)]
                elif var == None:
                    pass
                else:
                    newlist.append(line)
            else:
                newlist.append(line)

        newlist.append(self.cmdlist[-1])
        self.cmdlist = newlist

        return newlist


class AdmFlexBody(AdmCmd):
    """
    !                 adams_view_name='front_antiroll.fbs_antiroll'
    FLEX_BODY/1
    , MATRICES = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
    # cratio 也可为公式输入
    , CRATIO = 0.2\
    , MNF_FILE = mdids://For_loadcal/flex_bodys.tbl/antiroll_20209_mnf2.mnf
    """
    def __init__(self, cmdlist):
        super().__init__(cmdlist)
        self.mnf_file = ''
        self.cratio = None # 模态阻尼
        self.get_loc = {}
        for n, line in enumerate(cmdlist[:-1]):
            line1 = strupper(line)
            if ',MNF_FILE=' in line1:
                self.mnf_file = line.split('=')[-1]
                self.get_loc[n] = 'mnf_file'
            if ',CRATIO=' in line1:
                # print(line1)
                self.cratio = line.split('=')[-1][:-1]
                self.get_loc[n] = 'cratio'

        # print(self.mnf_file)
        # print(self.cratio)
        # print(self.cmdlist)

    def set_cratio(self,value): # 设置阻尼
        # , CRATIO = 0.2\
        # value 可以为字符串
        self.cratio = '{}'.format(value)
        self.updata()
        # cratio = self.cratio
        # if isinstance(cratio,str): # 字符串
        #   newstr = re.sub(r'\s','',cratio).lower()[:-1] 
        #   try:
        #       cratio = float(newstr)
        #   except:
        return None

    def set_cratio_gain(self,value): # 设置阻尼增益
        # , CRATIO = gain*varstr \
        self.cratio = f'{value}*'+self.cratio
        self.updata()

    # @pysnooper.snoop()
    def updata(self):

        self.isEdit = True
        n_edit = self.get_loc.keys() # 被读取到的数据
        newlist = []
        for n,line in enumerate(self.cmdlist[:-1]):
            if n in n_edit:
                var = self.get_loc[n]
                if var == 'mnf_file':
                    newlist += [self.str2str_equal('MNF_FILE',self.mnf_file)]
                    continue
                if var == 'cratio':
                    newlist += [self.str2str_equal('CRATIO',self.cratio)+'\\']
                elif var == None:
                    pass
                else:
                    newlist.append(line)
            else:
                newlist.append(line)
        # print(newlist)
        newlist.append(self.cmdlist[-1])
        self.cmdlist = newlist

        return newlist

# ===================================Car

class AdmRoad: # 路面路径解析
    """
        路面路径解析
    """
    def __init__(self,string_obj):

        self.string_obj = string_obj
        self.name = string_obj.name
        self.path = string_obj.strline

    def set_path(self,path):
        
        self.path = path
        self.string_obj.strline = path
        self.string_obj.updata()


class AdmSpring: # 弹簧编辑
    
    def __init__(self,force_obj,spline_obj):
        self.force_obj = force_obj
        self.spline_obj = spline_obj
        self.name = '.'.join(spline_obj.name.split('.')[:-1]).lower()

    # @pysnooper.snoop(prefix='Spring-set_k_gain -->',watch=('self.force_obj.init_len','self.spline_obj.ylist'))
    def set_k_gain(self,design_length,gain):
        # design_length 设计状态的长度
        # gain 增益比例

        # 弹簧刚度更改
        dx = self.force_obj.init_len - design_length
        preload = self.spline_obj.get_y(abs(dx))
        # print(self.spline_obj.ylist)
        self.spline_obj.updata(x_gain=1/gain) # 调整位移数据,避免指定预载下,调整弹簧刚度超出插值范围
        # print(self.spline_obj.ylist)
        new_dx = self.spline_obj.get_x(preload)
        # print(self.force_obj.name)
        assert dx > 0 , '输入的弹簧设计状态长度(design_length) 有误'

        self.force_obj.init_len = new_dx + design_length
        self.force_obj.updata() # 更新
        # self.spline_obj.updata()
        # print(dx,new_dx)
        return True

    # @pysnooper.snoop()
    def set_k_linear(self,design_length,k,ymax,num):
        # 定义线性弹簧刚度
        # design_length 设计状态的长度
        # k 弹簧刚度
        # ymax 弹簧载荷范围
        # num 单侧样点数
        
        dx = self.force_obj.init_len - design_length
        preload = self.spline_obj.get_y(abs(dx))
        # print(self.spline_obj.ylist)
        xlist,ylist = linear_spring_data(k,ymax,num)
        self.spline_obj.updata(xlist=xlist,ylist=ylist)
        # print(self.spline_obj.ylist)
        new_dx = self.spline_obj.get_x(preload)

        self.force_obj.init_len = new_dx + design_length
        self.force_obj.updata() # 更新

        return True
    
    # @pysnooper.snoop()
    def set_single_k_linear(self,design_length,k,ymax,num):
        # 定义线性弹簧刚度 ， 单项设置
        # design_length 设计状态的长度
        # k 弹簧刚度
        # ymax 弹簧载荷范围
        # num 单侧样点数

        dx = self.force_obj.init_len - design_length
        preload = self.spline_obj.get_y(abs(dx))
        # print(self.spline_obj.ylist)
        xlist,ylist = linear_single_spring_data(k,ymax,num)
        self.spline_obj.updata(xlist=xlist,ylist=ylist)
        # print(self.spline_obj.ylist)
        new_dx = self.spline_obj.get_x(preload)

        self.force_obj.init_len = new_dx + design_length
        self.force_obj.updata() # 更新

        return True


class AdmDamper: # 减振器编辑
    
    def __init__(self,force_obj,spline_obj):
        self.force_obj = force_obj
        self.spline_obj = spline_obj
        self.name = '.'.join(spline_obj.name.split('.')[:-1]).lower()

    # @pysnooper.snoop(prefix='Damper-set_c_gain ->',watch=('self.spline_obj.ylist'))
    def set_c_gain(self,gain):
        # 对阻尼进行增益
        self.spline_obj.updata(y_gain=gain)

        return True

    # @pysnooper.snoop(watch=('self.spline_obj.xlist','self.spline_obj.ylist'))
    def set_c_linear(self,c_p,vmax,num,c_n=None):
        # 线性阻尼
        xlist,ylist = linear_damer_data(c_p,vmax,num,c_n=c_n)
        xs = self.spline_obj.xlist
        ys = self.spline_obj.ylist
        if xs[0]*ys[0] < 0:
            ylist = [-n for n in ylist]
        self.spline_obj.updata(xlist,ylist)

        return True


class AdmCarBushing: # 衬套数据编辑

    def __init__(self,spline_objs,array_objs):
        self.name = '.'.join(spline_objs['tx_spline'].name.split('.')[:-1]).lower()

        self.num_dic = {'preload':6,'damper':4}

        self.spline_objs = spline_objs
        self.array_objs = array_objs

        self.tx_k = spline_objs['tx_spline']
        self.ty_k = spline_objs['ty_spline']
        self.tz_k = spline_objs['tz_spline']
        self.rx_k = spline_objs['rx_spline']
        self.ry_k = spline_objs['ry_spline']
        self.rz_k = spline_objs['rz_spline']

        self.tx_a = array_objs['tx_data_array']
        self.ty_a = array_objs['ty_data_array']
        self.tz_a = array_objs['tz_data_array']

        self.rx_a = array_objs['rx_data_array']
        self.ry_a = array_objs['ry_data_array']
        self.rz_a = array_objs['rz_data_array']

        self.array_dic = {'preload':[],'damper':[],}
        
    def get_c(self): # 获取衬套阻尼数据

        array_names = ['tx_data_array','ty_data_array','tz_data_array',
            'rx_data_array','ry_data_array','rz_data_array']
        # self.array_dic['damper'] = 
        cs = []
        for name in array_names:
            cs.append(self.array_objs[name].numbers[self.num_dic['damper']])

        self.array_dic['damper'] = cs
        return cs

    # @pysnooper.snoop(prefix='Bushing-set_array ->',watch=())
    def set_array(self,locs,values,edit_type):  # 预载、阻尼调整
        """
            # 预载、阻尼调整
            locs 编辑范围
                tx , ty , tz, rx , ry , rz  
            values  数值
            edit_type   编辑类型
                damper , preload
        """
        # edit_type = edit_type.lower().replace(' ','')
        if type(locs) == str:
            locs = [strlower(locs)]
        if type(values) != list:
            values = [values]

        edit_type = strlower(edit_type)

        if edit_type == 'preload':
            num = self.num_dic['preload'] # 弹簧预载位置
        elif edit_type == 'damper':
            num = self.num_dic['damper']  # 减振器预载位置

        for loc,value in zip(locs,values):
            str1 = 'AdmBushing 模块 array 编辑范围应为：tx,ty,tz,rx,ry,rz'
            assert loc in ['tx','ty','tz','rx','ry','rz'] , str1

            if loc == 'tx':
                self.tx_a.numbers[num] = value
                self.tx_a.updata() 
            elif loc == 'ty':
                self.ty_a.numbers[num] = value
                self.ty_a.updata()
            elif loc == 'tz':
                self.tz_a.numbers[num] = value
                self.tz_a.updata()
            elif loc == 'rx':
                self.rx_a.numbers[num] = value
                self.rx_a.updata()
            elif loc == 'ry':
                self.ry_a.numbers[num] = value
                self.ry_a.updata()
            elif loc == 'rz':
                self.rz_a.numbers[num] = value
                self.rz_a.updata()

    # @pysnooper.snoop()
    def set_c_gain(self,gain=1,edit_type='all'): # 阻尼增益
        """
            阻尼增益 编辑
            edit_type 类型
                t , r , all , tx,ty,tz,rx,ry,rz , ['tx','ty']
        """
        dic1 = {'tx':0,'ty':1,'tz':2,'rx':3,'ry':4,'rz':5}
        
        if type(edit_type) == list and len(edit_type)==1:
            edit_type = edit_type[0]

        if type(edit_type) == str:
            edit_type = strlower(edit_type)

        if edit_type == 't':
            ts = ['tx','ty','tz']
            locs = [0,1,2]
        elif edit_type == 'r':
            ts = ['rx','ry','rz']
            locs = [3,4,5]
        elif edit_type == 'all':
            ts = ['tx','ty','tz','rx','ry','rz']
            locs = list(range(6))
        elif type(edit_type) == str:
            ts = [edit_type]
            locs = [dic1[edit_type]]
        elif type(edit_type) == list:
            ts = edit_type
            locs = [dic1[n] for n in edit_type]

        cs = self.get_c()

        values = list_loc(cs,locs)
        self.set_array(ts,list_gain(values,gain),'damper')
        new_cs = self.get_c()
        # print(cs)
        # print(new_cs)

    # @pysnooper.snoop()
    def set_k_gain(self,gain=1,edit_type='all'): # 刚度增益
        """
            刚度增益 编辑
            edit_type 类型
                t , r , all , tx,ty,tz,rx,ry,rz , ['tx','ty']
        """
        dic_obj = {'tx':self.tx_k,'ty':self.ty_k,'tz':self.tz_k,
            'rx':self.rx_k,'ry':self.ry_k,'rz':self.rz_k}
        
        if type(edit_type) == list and len(edit_type)==1:
            edit_type = edit_type[0]
        
        if type(edit_type) == str:
            edit_type = strlower(edit_type)

        if edit_type == 't':
            ts = ['tx','ty','tz']
        elif edit_type == 'r':
            ts = ['rx','ry','rz']
        elif edit_type == 'all':
            ts = ['tx','ty','tz','rx','ry','rz']
        elif type(edit_type) == str:
            ts = [edit_type]
        elif type(edit_type) == list:
            ts = edit_type

        for t in ts:
            ylist = dic_obj[t].ylist
            dic_obj[t].updata(y_gain=gain)
            new_ylist = dic_obj[t].ylist
            # print(t)
            # print(ylist)
            # print(new_ylist)

    # @pysnooper.snoop()
    def set_k(self,k,edit_type='all',num=11,ymax=None): # 线性刚度设置
        """
            k   float ,刚度数值
            edit_type   类型
                t , r , all , tx,ty,tz,rx,ry,rz , ['tx','ty']
            num int 单边刚度数据-数组长度 
        """
        # 指定刚度（位移刚度&旋转刚度）
        dic_obj = {'tx':self.tx_k,'ty':self.ty_k,'tz':self.tz_k,
            'rx':self.rx_k,'ry':self.ry_k,'rz':self.rz_k}
        
        if type(edit_type) == list and len(edit_type)==1:
            edit_type = edit_type[0]

        if type(edit_type) == str:
            edit_type = strlower(edit_type)

        if edit_type == 't':
            ts = ['tx','ty','tz']
        elif edit_type == 'r':
            ts = ['rx','ry','rz']
        elif edit_type == 'all':
            ts = ['tx','ty','tz','rx','ry','rz']
        elif type(edit_type) == str:
            ts = [edit_type]
        elif type(edit_type) == list:
            ts = edit_type

        for t in ts:
            xlist = dic_obj[t].xlist
            ylist = dic_obj[t].ylist
            if ymax == None:
                ymax = max( abs(min(ylist)), max(ylist) )
            new_xlist,new_ylist = linear_spring_data(k,ymax,num)
            # print(new_xlist, new_ylist)
            dic_obj[t].updata(xlist=new_xlist, ylist=new_ylist) # spline 更新
            # print(id(dic_obj[t]))
            # print(dic_obj[t].xlist, dic_obj[t].ylist, dic_obj[t].cmdlist)
            # print(dic_obj[t].isEdit)

    def set_c(self,c,edit_type='all'): # 阻尼设置
        """
            c   float ,阻尼数值
            edit_type   类型
                t , r , all , tx,ty,tz,rx,ry,rz , ['tx','ty']
        """
        if type(edit_type) == list and len(edit_type)==1:
            edit_type = edit_type[0]

        if type(edit_type) == str:
            edit_type = strlower(edit_type)

        if edit_type == 't':
            ts = ['tx','ty','tz']
        elif edit_type == 'r':
            ts = ['rx','ry','rz']
        elif edit_type == 'all':
            ts = ['tx','ty','tz','rx','ry','rz']
        elif type(edit_type) == str:
            ts = [edit_type]
        elif type(edit_type) == list:
            ts = edit_type

        self.set_array(locs=ts,values=[c]*len(ts),edit_type='damper')


class AdmFlex: # 柔性体文件辨识
    def __init__(self,matrix_obj):
        matrix_obj.filename
        pass


# ===================================
class AdmEdit: # values_cmd 字符串解析
    """
    格式
        $$marker.location # 坐标更改  
        # 名称:参数位置1,参数位置2,参数位置3
        # fl:0,1,-2

        $$bushing.k # 线性衬套-位移刚度更改
        # 名称:参数位置1,2,3
        # bus_fl_bus:1,-2,3

        $$bushing.c # 线性衬套-位移阻尼更改
        # 名称:参数位置1,2,3
        # bus_fl_bus:1,-2,3

        $$bushing.kt # 线性衬套-扭转刚度更改
        # 名称:参数位置1,2,3
        # bus_fl_bus:1,-2,3

        $$bushing.ct # 线性衬套-扭转阻尼更改
        # 名称:参数位置1,2,3
        # bus_fl_bus:1,-2,3

        $$bushing.force # 线性衬套-衬套预载更改
        # 名称:参数位置1,2,3
        # bus_fl_bus:1,-2,3

        $$sforce.k # 刚度设置
        # 名称:参数位置
        # SPRING_1.sforce:4

        $$sforce.c # 阻尼设置
        # 名称:参数位置
        # eg: name:1
        # SPRING_1.sforce:5

        $$car_bushing.k_gain # Car衬套-刚度增益
        # 名称:选项:参数位置
        tr_steering.bkl_rack_housing_bushing:tx,ty,tz:6

        $$car_bushing.c_gain # Car衬套-阻尼增益
        # 名称:选项:参数位置
        tr_steering.bkl_rack_housing_bushing:tx:7

        $$car_bushing.k  # Car衬套-线性刚度定义
        # 名称:选项:参数位置
        tr_steering.bkl_rack_housing_bushing:tx,ty,tz:8

        $$car_bushing.c  # Car衬套-线性阻尼定义
        # 名称:选项:参数位置
        tr_steering.bkl_rack_housing_bushing:all:9
        
        $$car_spring.k_gain # Car弹簧-刚度增益
        # 名称:设计长度:参数位置
        tr_front_suspension.nsl_ride_spring:244:10

        $$car_spring.k_linear # car弹簧-刚度定义
        # 名称:设计长度:参数位置
        tr_front_suspension.nsl_ride_spring:244:11

        $$car_damper.c_gain # car减振器-阻尼增益
        # 名称:参数位置
        tr_front_suspension.dal_ride_damper:5

        $$car_damper.c_linear # car减振器-阻尼定义 
        # 名称:参数变量-拉伸阻尼:参数变量-压缩阻尼
        TR_Rear_Suspension.dal_ride_damper:10:1
        tr_front_suspension.dal_ride_damper:10:1
    """
    def __init__(self,admobj): # AdmFile\AdmCar 的实例
        self.obj = admobj

    # @pysnooper.snoop()
    def edit(self,strcmd,values):

        blocks = [] # 类型段落
        for line1 in strcmd.split('$$') :
            list1 = []
            for line2 in [n for n in line1.split('\n') if n]:
                line3 = line2.split('#')[0] # 去注释
                line3 = re.sub(r'\s','',line3) # 去空格
                line3 = line3.replace(';','')
                if line3:
                    list1.append(line3.lower())

            if list1:
                blocks.append(list1)

        for block in blocks:
            if len(block) < 2 :
                continue
            titlename = block[0]
            lines = block[1:]
            if 'marker.location' == titlename:
                'fl:0,1,2'
                for line in lines:
                    name,temp = line.split(':')
                    locs = [int(n) for n in temp.split(',') if n]
                    # print(self.obj.model.marker[name].location)
                    self.obj.model.marker[name].location=values2list(values,locs)
                    # print(self.obj.model.marker[name].location)
                    self.obj.model.marker[name].updata()
                continue

            if 'bushing.k' == titlename:
                for line in lines:
                    name,temp = line.split(':')
                    locs = [int(n) for n in temp.split(',') if n]
                    # print(self.obj.model.bushing[name].k)
                    self.obj.model.bushing[name].k=values2list(values,locs)
                    # print(self.obj.model.bushing[name].k)
                    self.obj.model.bushing[name].updata()
                continue

            if 'bushing.c' == titlename:
                for line in lines:
                    name,temp = line.split(':')
                    locs = [int(n) for n in temp.split(',') if n]
                    # print(self.obj.model.bushing[name].c)
                    self.obj.model.bushing[name].c=values2list(values,locs)
                    # print(self.obj.model.bushing[name].c)
                    self.obj.model.bushing[name].updata()
                continue

            if 'bushing.kt' == titlename:
                for line in lines:
                    name,temp = line.split(':')
                    locs = [int(n) for n in temp.split(',') if n]
                    # print(self.obj.model.bushing[name].kt)
                    self.obj.model.bushing[name].kt=values2list(values,locs)
                    # print(self.obj.model.bushing[name].kt)
                    self.obj.model.bushing[name].updata()
                continue

            if 'bushing.ct' == titlename:
                for line in lines:
                    name,temp = line.split(':')
                    locs = [int(n) for n in temp.split(',') if n]
                    # print(self.obj.model.bushing[name].ct)
                    self.obj.model.bushing[name].ct=values2list(values,locs)
                    # print(self.obj.model.bushing[name].ct)
                    self.obj.model.bushing[name].updata()
                continue

            if 'bushing.force' == titlename:
                for line in lines:
                    name,temp = line.split(':')
                    locs = [int(n) for n in temp.split(',') if n]
                    # print(self.obj.model.bushing[name].force)
                    self.obj.model.bushing[name].force=values2list(values,locs)
                    # print(self.obj.model.bushing[name].force)
                    self.obj.model.bushing[name].updata()
                continue

            if 'sforce.k' == titlename:
                'SPRING_1.sforce:5'
                for line in lines:
                    name,temp = line.split(':')
                    locs = [int(n) for n in temp.split(',') if n]
                    assert len(locs)==1 ,f'sforce.k 输入数据有误 : {line}'
                    # print(self.obj.model.sforce[name].k)
                    self.obj.model.sforce[name].k=values2list(values,locs)[0]
                    # print(self.obj.model.sforce[name].k)
                    self.obj.model.sforce[name].updata()
                continue

            if 'sforce.c' == titlename:
                'SPRING_1.sforce:5'
                for line in lines:
                    name,temp = line.split(':')
                    locs = [int(n) for n in temp.split(',') if n]
                    assert len(locs)==1 ,f'sforce.c 输入数据有误 : {line}'
                    # print(self.obj.model.sforce[name].c)
                    self.obj.model.sforce[name].c=values2list(values,locs)[0]
                    # print(self.obj.model.sforce[name].c)
                    self.obj.model.sforce[name].updata()
                continue

            if 'car_bushing.k_gain' == titlename:
                'tr_steering.bkl_rack_housing_bushing:tx,ty,tz:6'
                for line in lines:
                    name,types,temp = line.split(':')
                    types = [n for n in types.split(',') if n]

                    locs = [int(n) for n in temp.split(',') if n]
                    assert len(locs)==1 ,f'car_bushing.k_gain 输入数据有误 : {line}'
                    gain = float(values2list(values,locs)[0])

                    # print(self.obj.car_bushing[name].tx_k.ylist)
                    self.obj.car_bushing[name].set_k_gain(gain=gain,edit_type=types)
                    # print(self.obj.car_bushing[name].tx_k.ylist)
                continue

            if 'car_bushing.c_gain' == titlename:
                'tr_steering.bkl_rack_housing_bushing:tx,ty,tz:6'
                for line in lines:
                    name,types,temp = line.split(':')
                    types = [n for n in types.split(',') if n]

                    locs = [int(n) for n in temp.split(',') if n]
                    assert len(locs)==1 ,f'car_bushing.c_gain 输入数据有误 : {line}'
                    gain = float(values2list(values,locs)[0])
                    
                    # print(self.obj.car_bushing[name].get_c())
                    self.obj.car_bushing[name].set_c_gain(gain=gain,edit_type=types)
                    # print(self.obj.car_bushing[name].get_c())
                continue

            if 'car_bushing.k' == titlename:
                'tr_steering.bkl_rack_housing_bushing:tx,ty,tz:6'

                for line in lines:
                    name,types,temp = line.split(':')
                    types = [n for n in types.split(',') if n]

                    locs = [int(n) for n in temp.split(',') if n]
                    assert len(locs)==1 ,f'car_bushing.k 输入数据有误 : {line}'
                    k = float(values2list(values,locs)[0])
                    
                    # print(self.obj.car_bushing[name].tx_k.xlist)
                    self.obj.car_bushing[name].set_k(k=k,edit_type=types)
                    # print(self.obj.car_bushing[name].tx_k.xlist)
                continue

            if 'car_bushing.c' == titlename:
                'tr_steering.bkl_rack_housing_bushing:tx,ty,tz:6'
                for line in lines:
                    name,types,temp = line.split(':')
                    types = [n for n in types.split(',') if n]
                    locs = [int(n) for n in temp.split(',') if n]
                    assert len(locs)==1 ,f'car_bushing.c 输入数据有误 : {line}'
                    c = float(values2list(values,locs)[0])
                    
                    # print(self.obj.car_bushing[name].get_c())
                    self.obj.car_bushing[name].set_c(c=c,edit_type=types)
                    # print(self.obj.car_bushing[name].get_c())
                continue

            if 'car_spring.k_gain' == titlename:
                'tr_front_suspension.nsl_ride_spring:244:10'
                for line in lines:
                    name,str_length,gain_num = line.split(':')
                    design_length = float(str_length)
                    # print(gain_num)
                    gain = float(values[int(gain_num)])

                    # print(self.obj.car_spring[name].spline_obj.ylist)
                    self.obj.car_spring[name].set_k_gain(design_length=design_length,
                        gain=gain)
                    # print(self.obj.car_spring[name].spline_obj.ylist)
                continue

            if 'car_spring.k_linear' == titlename:
                'tr_front_suspension.nsl_ride_spring:244:10'
                for line in lines:
                    name,str_length,k_num = line.split(':')
                    design_length = float(str_length)
                    k = float(values[int(k_num)])

                    # print(self.obj.car_spring[name].spline_obj.ylist)
                    self.obj.car_spring[name].set_single_k_linear(design_length=design_length,
                        k=k,ymax=1e5,num=21)
                    # print(self.obj.car_spring[name].spline_obj.ylist)
                continue
            if 'car_damper.c_gain' == titlename:
                'tr_front_suspension.dal_ride_damper:5'
                for line in lines:
                    name, gain_num = line.split(':')
                    gain = float(values[int(gain_num)])

                    # print(self.obj.car_damper[name].spline_obj.ylist)
                    self.obj.car_damper[name].set_c_gain(gain=gain)
                    # print(self.obj.car_damper[name].spline_obj.ylist)
                continue

            if 'car_damper.c_linear' == titlename: 
                'tr_front_suspension.dal_ride_damper:13:1'
                for line in lines:
                    name, c_p_num, c_n_num = line.split(':')
                    c_p = float(values[int(c_p_num)]) # 拉伸阻尼
                    c_n = float(values[int(c_n_num)]) # 压缩阻尼

                    # print(self.obj.car_damper[name].spline_obj.ylist)
                    self.obj.car_damper[name].set_c_linear(c_p=c_p,vmax=1000,num=21,c_n=c_n)
                    # print(self.obj.car_damper[name].spline_obj.ylist)
                continue
            
            if 'flex_body_cratio.c_gain' == titlename: # 模态阻尼数值增益
                'front_antiroll.fbs_antiroll:5'
                pass
                for line in lines:
                    name, gain_num = line.split(':')
                    gain = float(values[int(gain_num)])
                    self.obj.model.flexbody[name].set_cratio_gain(gain)
                    
                continue

            if 'flex_body_cratio.c' == titlename: # 模态阻尼数值赋予
                'front_antiroll.fbs_antiroll:5'
                for line in lines:
                    name, gain_num = line.split(':')
                    value = float(values[int(gain_num)])
                    self.obj.model.flexbody[name].set_cratio(value)

                continue

        return self.obj

    def edit_str(self,locs): # 字符串变量编辑
        """
            修改 admobj
            locs    dict    {7:0, 8:0}
            #   num 变量编号    loc 变量所指向的字符串位置
            # eg : [8] = 1  变量编号8 的 第1个字符串
        """
        for loc in locs.keys():
            # 每个变更范围(变量序列号),单独计算
            loc = int(loc)
            for str_target in self.str_dic[loc]:
                # 同一变更范围的不同变更对象修改
                name = str_target['name']
                if str_target['type'] == 'tire.road':
                    self.obj.model.string[name+'.rpf_file'].strline = str_target['strs'][locs[loc]]
                    self.obj.model.string[name+'.rpf_file'].updata()

                if str_target['type'] == 'tire.file':
                    self.obj.model.string[name+'.tpf_file'].strline = str_target['strs'][locs[loc]]
                    self.obj.model.string[name+'.tpf_file'].updata()

                if str_target['type'] == 'flex_body_cratio.c':
                    # print(str_target['strs'][locs[loc]])
                    # print(str_target)
                    self.obj.model.flexbody[name].set_cratio( str_target['strs'][locs[loc]] )

        return self.obj

    def read_str(self, strcmd, str_split='|'): # 字符串解析
        """
            字符串类型变量读取，获取变量名称及变量
            strcmd str
                $$tire.road 
                TR_Front_Tires.til_wheel:road1,road2,road3:7 
                TR_Front_Tires.tir_wheel:road1,road2,road3:7 
                TR_Rear_Tires.til_wheel:road1,road2,road3:8
        """
        blocks = self.strcmd_cal(strcmd)
        self.str_dic = {}
        for block in blocks:
            if len(block) < 2:
                continue
            titlename = block[0]
            lines = block[1:]
            for line in lines:
                name, varline, num = line.split(str_split)
                num = int(num)
                # strs = [n for n in varline.split(',') if n]
                strs = self.line_strvar_split(varline)
                if num in self.str_dic:
                    self.str_dic[num].append({'type':titlename, 'name':name, 'strs':strs})
                else:
                    self.str_dic[num] = [{'type':titlename, 'name':name, 'strs':strs}]
        
        # print(self.str_dic)
        return self.str_dic

    @staticmethod
    def strcmd_cal(strcmd): # 字符串变量初始数据解析
        blocks = [] # 类型段落
        for line1 in strcmd.split('$$'):
            list1 = []
            for line2 in [n for n in line1.split('\n') if n]:
                line3 = line2.split('#')[0]
                line3 = re.sub(r'\s','',line3)
                line3 = line3.replace(';','')
                if line3:
                    list1.append(line3.lower())

            if list1:
                blocks.append(list1)

        return blocks

    @staticmethod
    def line_strvar_split(strline): # 字符串变量拆分
        """
            字符串行变量拆分
            案例:
        'road1_7,road2_7,road3_7'
        '"STEP(FXFREQ,60,0.05,80,0.8)","2*STEP(FXFREQ,60,0.05,80,0.8)","3*STEP(FXFREQ,60,0.05,80,0.8)"'
        '0.2,"2*STEP(FXFREQ,60,0.05,80,0.8)",0.2,"3*STEP(FXFREQ,60,0.05,80,0.8)"'
        """
        strline = re.sub(r'\s','',strline)
        if '"' in strline: # 带有逗号的字符串
            var_line = re.sub(r'".+?"','',strline)
            var_strs = re.findall(r'"(.+?)"',strline)
            str_list = []
            str_loc = 0
            for var in var_line.split(','):
                if var:
                    str_list.append(var)
                else:
                    str_list.append(var_strs[str_loc])
                    str_loc += 1
            return str_list

        str_list = [n for n in strline.split(',') if n]
        return str_list

CMDS_INIT = """# 数值变量
$$marker.location # 坐标更改  
# 名称:参数位置1,参数位置2,参数位置3
# fl:0,1,-2

$$bushing.k # 线性衬套-位移刚度更改
# 名称:参数位置1,2,3
# bus_fl_bus:1,-2,3

$$bushing.c # 线性衬套-位移阻尼更改
# 名称:参数位置1,2,3
# bus_fl_bus:1,-2,3

$$bushing.kt # 线性衬套-扭转刚度更改
# 名称:参数位置1,2,3
# bus_fl_bus:1,-2,3

$$bushing.ct # 线性衬套-扭转阻尼更改
# 名称:参数位置1,2,3
# bus_fl_bus:1,-2,3

$$bushing.force # 线性衬套-衬套预载更改
# 名称:参数位置1,2,3
# bus_fl_bus:1,-2,3

$$sforce.k # 刚度设置
# 名称:参数位置
# SPRING_1.sforce:4

$$sforce.c # 阻尼设置
# 名称:参数位置
# eg: name:1
# SPRING_1.sforce:5

$$car_bushing.k_gain # Car衬套-刚度增益
# 名称:选项:参数位置
# tr_steering.bkl_rack_housing_bushing:tx,ty,tz:6

$$car_bushing.c_gain # Car衬套-阻尼增益
# 名称:选项:参数位置
# tr_steering.bkl_rack_housing_bushing:tx:7

$$car_bushing.k  # Car衬套-线性刚度定义
# 名称:选项:参数位置
# tr_steering.bkl_rack_housing_bushing:tx,ty,tz:8

$$car_bushing.c  # Car衬套-线性阻尼定义
# 名称:选项:参数位置
# tr_steering.bkl_rack_housing_bushing:all:9

$$car_spring.k_gain # Car弹簧-刚度增益
# 名称:设计长度:参数位置
# tr_front_suspension.nsl_ride_spring:244:10

$$car_spring.k_linear # car弹簧-刚度定义
# 名称:设计长度:参数位置
# tr_front_suspension.nsl_ride_spring:244:11

$$car_damper.c_gain # car减振器-阻尼增益
# 名称:参数位置
# tr_front_suspension.dal_ride_damper:5

$$car_damper.c_linear # car减振器-阻尼定义 
# 名称:参数变量-拉伸阻尼:参数变量-压缩阻尼
# TR_Rear_Suspension.dal_ride_damper:10:1
# tr_front_suspension.dal_ride_damper:10:1

$$flex_body_cratio.c_gain # flex_body模态阻尼增益
# 'front_antiroll.fbs_antiroll:5'

$$flex_body_cratio.c # flex_body模态阻尼数值
# 'front_antiroll.fbs_antiroll:5'
"""

CMDS_STR_INIT = """# 字符串变量
$$tire.road 
# TR_Front_Tires.til_wheel:road1_7,road2_7,road3_7:0 
# TR_Front_Tires.tir_wheel:road1_7,road2_7,road3_7:0 
# TR_Rear_Tires.til_wheel:road1,road2_8,road3:1

$$tire.file
# TR_Front_Tires.til_wheel:pac1_7,ftire2_7,5213_7:0 

$$flex_body_cratio.c
# front_antiroll.fbs_antiroll:0.3,"STEP(FXFREQ,60,0.05,80,0.8)",0.5:1
"""




if __name__ == '__main__':
    test_key1 = lambda obj : obj[ list(obj.keys())[0] ] # 测试用获取字典内容

    # filepath = r'D:\document\FEMFAT_LAB\mast\six_dof_rig_stewart.adm'
    # filepath = r'D:\document\FEMFAT_LAB\dof6_421_flex\six_dof_rig_421.adm'
    # filepath = r"..\code_test\test.adm"
    # filepath2 = r"..\code_test\test2.adm"
    
    # admobj = AdmFile(filepath)

    # admobj.model.splinenum[1].updata([1,2,3,5,6,7,8,9,10,11,12,13,14,15],
    #   [1,2,3,5,6,7,8,9,10,11,12,13,14,15])
    # admobj.model.part['part_upper_rod_5'].updata()

    # # part
    # admobj.model.partnum[8].mass = 999
    # admobj.model.partnum[8].updata()
    # print(admobj.model.partnum[8].ip)
    # print([obj.name for obj in admobj.model.all if obj.isEdit])
    
    # # for obj in admobj.model.marker.values(): print([obj.name,obj.loc,obj.ori])
    
    # # marker
    # admobj.model.markernum[37].location=[1,1,1]
    # admobj.model.markernum[37].updata()
    
    # # bushing
    # print(admobj.model.bushingnum[1].c)
    # admobj.model.bushingnum[1].c=[10,10,10]
    # admobj.model.bushingnum[1].k=[10,10,10]
    # admobj.model.bushingnum[1].updata()
    
    
    # # sforce
    # # print(admobj.model.sforcenum.keys())
    # print(admobj.model.sforcenum[1].k)
    # print(admobj.model.sforcenum[1].c)
    # admobj.model.sforcenum[1].c = 10
    # admobj.model.sforcenum[1].preload = -110
    # # admobj.model.sforcenum[1].k = 1000
    # admobj.model.sforcenum[1].updata()
    
    # # print(admobj.model.bushingnum.keys())
    # # print(admobj.model.markernum[37].cmdlist)
    
    # admobj.updata()
    # admobj.newfile(filepath2)
    
    # car adm解析
    # filepath = r"..\code_test\carmodel.adm"
    filepath = r"..\tests\file_admfile\adm_car_withFlex.adm"
    admobj = AdmCar(filepath)

    test_key1(admobj.car_bushing).set_array('tx',123.456,'damper')
    test_key1(admobj.car_bushing).set_c_gain(gain=1.2)
    test_key1(admobj.car_bushing).set_c_gain(gain=10,edit_type='tx')
    test_key1(admobj.car_bushing).set_c_gain(gain=10,edit_type='tz')
    test_key1(admobj.car_bushing).set_c_gain(gain=10,edit_type=['tz','ty'])
    test_key1(admobj.car_bushing).set_k_gain(gain=10,edit_type='tx')
    test_key1(admobj.car_bushing).set_k_gain(gain=10,edit_type=['tz','ty'])
    test_key1(admobj.car_bushing).set_k_gain(gain=10,edit_type='t')
    test_key1(admobj.car_bushing).set_k(k=100,edit_type='t')
    test_key1(admobj.car_spring).set_k_gain(244,3)
    # print(admobj.car_spring.keys())
    test_key1(admobj.car_spring).set_k_linear(244,100,20000,11)
    test_key1(admobj.car_spring).set_single_k_linear(244,100,20000,11)
    test_key1(admobj.car_damper).set_c_gain(2) 
    test_key1(admobj.car_damper).set_c_linear(10,520,11,1) 
    test_key1(admobj.model.flexbody).set_cratio(0.3)
    admobj.updata()
    admobj.newfile(r'..\tests\file_admfile\cartest.adm')
    # print(admobj.flex_mtxs)
    # print(test_key1(admobj.car_bushing).name)
    # print(test_key1(admobj.car_spring).name)
    # print(test_key1(admobj.car_damper).name)
    
    # print(admobj.model.request.keys())
    admobj.model.get_req_comp(['steering_force_demands'.lower()],['steering_torque'])
    # filepath = r"..\code_test\test.adm"
    # admobj = AdmCar(filepath)
    # editobj = AdmEdit(admobj)
    # editobj.edit(test_str,[0.1,1.1,2.1,3.1,4.1,5.1,6.1,7.1,8.1,9.1,10.1,11.1])

    
    strcmd = """
    $$tire.road 
    TR_Front_Tires.til_wheel|road1_7,road2_7,road3_7|0 
    TR_Front_Tires.tir_wheel|road1_7,road2_7,road3_7|0 
    TR_Rear_Tires.til_wheel|road1,road2_8,road3|1
    $$tire.file
    TR_Front_Tires.til_wheel|pac1_7,ftire2_7,5213_7|0 
    $$flex_body_cratio.c
    front_antiroll.fbs_antiroll|0.3,"STEP(FXFREQ,60,0.05,80,0.8)",0.5|1
    """
    
    # filepath = r'D:\document\ADAMS\MDI_Demo_Vehicle_temp.adm'
    admobj = AdmCar(filepath)
    editobj = AdmEdit(admobj)
    editobj.read_str(strcmd)
    # print(editobj.str_dic)
    editobj.edit_str({0:2, 1:1})
    # test_key1(admobj.model.flexbody).set_cratio(0.3)
    # test_key1(admobj.model.flexbody).set_cratio_gain(0.3)
    admobj.updata()
    admobj.newfile(r'..\tests\file_admfile\cartest2.adm')
    
    