from pyadams import datacal
from pyadams.datacal import plot, tscal
from pyadams.file import file_edit, office_docx

import re, math, sys, os, struct, abc, copy, time
import logging, os.path

# ==============================
# logging日志配置
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)
# ==============================


# ==============================
# 子函数
str_lower_strip = lambda str1: re.sub(r'\s','',str1).lower() # 去空格,小写化
list2_change_rc = datacal.list2_change_rc
value2str_list2 = datacal.value2str_list2
cal_max         = tscal.cal_max
cal_min         = tscal.cal_min
cal_pdi         = tscal.cal_pdi
cal_rms         = tscal.cal_rms
cal_rainflow_pdi= tscal.cal_rainflow_pdi
# ==============================


# ==============================

class ReusltData(abc.ABC):

    def __init__(self): 
        self.name            = None
        self.file_path       = None
        self.data_original   = None
        self.select_channels = None
        self.line_ranges     = None
        self.titles          = None
        self.samplerate      = None
        self.data_func       = None

    @abc.abstractmethod
    def read_file(self): pass  # 读取文件

    @abc.abstractmethod
    def get_samplerate(self): return self.samplerate # 采样频率获取

    def get_data(self): # 获取数据

        # ==============================
        select_channels = self.select_channels
        line_ranges     = self.line_ranges
        data_original   = self.data_original
        data_func       = self.data_func
        # ==============================
        new_data = []
        if line_ranges==None: line_ranges = [None, None]
        if select_channels==None: select_channels = list(range(len(data_original)))

        assert isinstance(line_ranges, list)
        assert isinstance(select_channels, list)

        # for n, line in enumerate(data_original):
        #     if n in select_channels:
        #         new_data.append(line[line_ranges[0] : line_ranges[1]])

        for n in select_channels: # 通道截取
            assert n<len(data_original), 'channels selected is error' # 通道截取错误
            new_data.append(data_original[n][ line_ranges[0] : line_ranges[1] ])

        # ==============================
        self.line_ranges    = line_ranges
        # self.data_original  = data_original
        # ==============================
        if data_func != None: # 函数编辑
            new_data = copy.deepcopy(new_data)
            new_data = data_func(new_data)

        return new_data

    def set_data_func(self, func=None): self.data_func = func

    def set_select_channels(self, list1d): # 通道截取
        self.select_channels = list1d
        return None

    def set_line_ranges(self, list1d): # 数据截取区间
        self.line_ranges = list1d
        return None

    def get_select_channels(self, list1d): return self.select_channels

    def get_line_ranges(self): return self.line_ranges

    def get_titles(self): 
        # ==============================
        select_channels = self.select_channels
        titles = self.titles
        # ==============================
        if select_channels == None:
            return titles
        else:
            return [titles[n] for n in select_channels]

    def save_csv_data(self, file_path, data=None):  # 数据转存位CsvFile
        """ 数据保存到csv文件中"""

        # ==============================
        if data == None:
            data   = copy.copy(self.get_data())
        else:
            data   = copy.copy(data)

        titles     = copy.copy(self.get_titles())
        samplerate = self.get_samplerate()
        # ==============================

        time_line = [ n / samplerate for n in range(len(data[0])) ]
        data.insert(0, time_line)
        titles.insert(0, 'time(s)')

        f = open(file_path, 'w')
        f.write(','.join(titles) + '\n')
        for row in range(len(data[0])):
            for col in range(len(data)):
                f.write(str(data[col][row]) + ',')
            f.write('\n')

        f.close()

        return None


class ResFile(ReusltData):

    def __init__(self, file_path, name=None): 
        super().__init__()
        self.file_path = file_path
        self.name      = name
        self.data_full = None

    def read_file(self, isReload=True): 
        # ==============================
        file_path = self.file_path
        # ==============================

        if not isReload:
            self._set_request_data()
            logger.warning(f'ResFile: {self.name} do not reload!!!')
            return None

        fileid = open(file_path,'r')
        data = []
        data_str = []
        n = 0
        while True:
            line=fileid.readline().lower()
            if '<stepmap' in line:
                n=1
            if r'</stepmap>' in line:
                data_str.append(line)
                n=0
                break
            if n==1:
                data_str.append(line)
        self.data_str=data_str
        while  True:
            line=fileid.readline().lower()
            if '<step' in line:
                data_n=[]
                while True:
                    line2=fileid.readline().lower()
                    if '</step>' in line2:
                        break
                    d1=line2.replace('\n','')
                    d2=d1.split(' ')
                    data_n.extend(d2)
                data.append(data_n)
            if '</analysis>' in line:
                break
        fileid.close()

        self._requestId = self.data_title_parse(data_str)
        self.data_full  = data
        self._set_request_data()

        return None

    def get_samplerate(self, nlen=20, loc_start=5):

        # ==============================
        file_path = self.file_path
        # ==============================

        f = open(file_path, 'r')
        data = []
        while True:
            line = f.readline().lower()
            if r'</stepmap>' in line:
                break
        
        cur_loc = 0
        while True:
            line = f.readline().lower()
            data_n = []
            if '<step' in line:
                data_n=[]
                while True:
                    line2 = f.readline().lower()
                    if '</step>' in line2:
                        break
                    d1 = line2.replace('\n','')
                    d2 = d1.split(' ')
                    data_n.extend(d2)
                data.append(data_n)
            cur_loc += 1
            if nlen < cur_loc: # 完成计数，结束读取
                break
            if '</analysis>' in line:
                break
        f.close()

        simTime = []
        for n in range(loc_start, len(data[:])):
            simTime.append(float(data[n][0]))

        samplerates = []
        for n in range(len(simTime)-1):
            delta = simTime[n+1] - simTime[n]
            samplerates.append(1.0 / delta)

        samplerate_mean = sum(samplerates) / len(samplerates)

        # ==============================
        self.samplerate = samplerate_mean
        # ==============================

        return samplerate_mean

    def _set_request_data(self): 
        
        # ==============================
        data        = self.data_full
        requestId   = self._requestId
        reqs        = self.reqs
        comps       = self.comps
        # ==============================

        dataId, dataOut, names = [], [], []
        isAllRead = True
        for n in range(0,len(reqs)):
            keyName = str_lower_strip(reqs[n])+'.'+str_lower_strip(comps[n])
            names.append(keyName)
            try:
                dataId.append(requestId[keyName])
            except:
                # logger.warning('reqs.comps error: {}\n'.format(keyName))
                logger.error(f'{key_name} not in requestId')
                isAllRead = False

        assert isAllRead , 'ResFile读取失败,未完全完成读取,终止'

        for n in dataId:
            n1=n-1
            temp=[]
            for n2 in range(len(data[:])): # 不考虑首位数据
                temp.append(float(data[n2][n1]))
            dataOut.append(temp)

        # ==============================
        self.data_original = dataOut
        # ==============================

        return None

    def read_file_faster(self): 

        # ==============================
        file_path = self.file_path
        reqs      = self.reqs
        comps     = self.comps
        # ==============================


        getlist = lambda data,list1: [data[n-1] for n in list1]

        fileid = open(file_path,'r')
        id_list, data, data_str, n = [], [], [], 0
        while True:
            line = fileid.readline().lower()
            if '<stepmap' in line:
                n=1
            if r'</stepmap>' in line:
                data_str.append(line)
                n=0
                break
            if n==1:
                data_str.append(line)

        requestId = self.data_title_parse(data_str) # 开头数据解析

        for req, comp in zip(self.reqs, self.comps):
            key_name = str_lower_strip(req)+'.'+str_lower_strip(comp)
            if key_name not in requestId:
                logger.error(f'{key_name} not in requestId')
            id_list.append(requestId[key_name])

        while True:
            line=fileid.readline().lower()
            if '<step' in line:
                data_n=[]
                while True:
                    line2=fileid.readline().lower()
                    if '</step>' in line2:
                        break
                    d1=line2.replace('\n','')
                    d2=d1.split(' ')
                    data_n.extend(d2)
                data.append(getlist(data_n, id_list))
            if '</analysis>' in line:
                break
        fileid.close()

        new_data = []
        for n in range(len(data[0])):
            new_line = []
            for line in data:
                new_line.append(float(line[n]))
            new_data.append(new_line)

        # ==============================
        self.data_original = new_data
        # ==============================

        return None

    def set_reqs_comps(self, reqs, comps): 

        titles = []
        for req, comp in zip(reqs, comps):
            titles.append(str(req)+'.'+str(comp))

        # ==============================
        self.reqs   = reqs
        self.comps  = comps
        self.titles = titles
        # ==============================

        return None

    @staticmethod
    def data_title_parse(data_str): 

        reg=r'^<entityname="(.*?)"(.*)entity="(\S*)"(.*)enttype="\S*"(.*)>'
        reg2=r'^<componentname="(.*?)".*id="(\d*)"(?:.*)/>'
        
        n=0
        requestId=dict()
        for line in data_str:
            line = str_lower_strip(line) #去所有空格并转为小写

            a=re.match(reg,line)
            b=re.match(reg2,line)
            if a:
                entityName=a.group(1)
                n = 1
            if b and (n==1):
                componentName=b.group(1)
                locId=b.group(2)
                requestId[entityName+'.'+componentName]=int(locId)
            if r'</entity>' in line: # 结束
                # print(line)
                n=0
                entityName=''

        return requestId


class ReqFile(ReusltData):

    def __init__(self, file_path, name=None):
        super().__init__()
        self.file_path = file_path
        self.name      = name
        self.data_full = None

    def read_file(self, isReload=True): 

        # ==============================
        file_path = self.file_path
        # ==============================
        
        if not isReload:
            self._set_request_data()
            logger.warning(f'ReqFile: {self.name} do not reload!!!')
            return None

        f = open(file_path,'r')
        # 开头解析
        title = []
        for n in range(3):
            title.append(f.readline())
        num,temp,gain = [line for line in title[2].split(' ') if line]
        num,gain = int(num),float(gain)

        # 索引解析
        n = 0
        loc_dic = {}
        num_dic = {}
        while True:
            line = f.readline()
            line2 = re.sub(r'\s','',line)
            if re.search(r'\D+',line2) == None:
                n += 1
                temp = [int(n) for n in re.split(r'\s',line) if n]
                num_dic[n] = temp
                loc_dic[temp[0]] = n
            else:
                continue
            if n == num:
                break
        # 数据解析
        ts,vs = [],[]
        is_start = False
        while True:
            line = f.readline()
            if not line:
                break
            temp = []
            temp = [float(n) for n in re.split(r'\s',line) if n]

            if len(temp) == 1:
                if is_start:
                    vs.append(v)
                    ts.append(temp[0])
                    v = []
                else:
                    is_start,v = True,[]
            else:
                v.extend(temp)

        f.close()

        # ==============================
        self.data_full = vs
        self.times = ts
        self.loc_dic = loc_dic
        self.num_dic = num_dic
        # ==============================
        self._set_request_data()

        return None

    def get_samplerate(self):
        # ==============================        
        list1 = self.times
        # ==============================
        nlen = len(list1)
        if nlen<10:
            cal_len = nlen
        else:
            cal_len = 10

        samplerate = 1 / (sum([list1[n+1]-list1[n] for n in range(cal_len-1)]) / (cal_len-1) )

        # ==============================
        self.samplerate = samplerate
        # ==============================
        return samplerate

    def _set_request_data(self): 
        # ==============================
        data_full = self.data_full
        loc_dic   = self.loc_dic
        nlocs     = self.nlocs
        nums      = self.nums
        # ==============================

        for n in range(len(nlocs)): # 将数据转化为
            # assert nlocs[n]==int(nlocs[n]), f'req数据读取，reqs中数据为非整数'
            # assert nums[n]==int(nums[n]), f'req数据读取，comps中数据为非整数'
            nlocs[n] = int(nlocs[n])
            nums[n] = int(nums[n])

        lines = [ [] for n in nlocs ]
        for line in data_full:
            for n in range(len(nlocs)):
                loc = nlocs[n]
                num = nums[n]
                new_loc = (loc_dic[loc]-1)*6
                lines[n].append(line[new_loc+num-1])
        
        names = [f'{loc}.{num}' for loc,num in zip(nlocs,nums)]

        # ==============================
        self.data_original = lines
        self.titles        = names
        # ==============================

        return None


    def set_reqs_comps(self, reqs, comps):

        titles = []
        for req, comp in zip(reqs, comps):
            titles.append(str(req)+'.'+str(comp))

        # ==============================
        self.nlocs  = reqs
        self.nums   = comps
        self.titles = titles
        # ==============================
        return None


class NumDataFile(ReusltData):

    def __init__(self, file_path, name=None): 
        super().__init__()
        self.file_path = file_path
        self.name      = name

    def read_file(self): 
        # ==============================
        file_path = self.file_path
        # ==============================

        file = open(file_path, 'r')
        data, titlelist = [], []
        isdata_start = False
        lines_temp = []
        while True:    
            line = file.readline()     #这里可以进行逻辑处理     file2.write('"'+line[:s]+'"'+",")  
            if not line: break  # 空
            isdata=True
            # num=0
            if re.match('\s*[ABCDE]+.*',line): # 标题注释
                # print(line)
                if '.' in line:
                    isdata_start = False
                    titlelist.append(line.replace('\n',''))
                else:
                    isdata_start = True
                continue

            value_strs = [float(value) for value in re.split('\s',line) if value]
            if value_strs:
                # 是数据段且非空数据行
                if isdata_start:
                    isdata_start = False
                    if lines_temp:
                        data.extend(list2_change_rc(lines_temp))
                        lines_temp = []
                    lines_temp = []
                lines_temp.append(value_strs)

        data.extend(list2_change_rc(lines_temp))

        file.close()

        titlelist = [title[4:] for title in titlelist]

        # ==============================
        self.data_original = data
        self.titles        = titlelist
        # ==============================

        return None

    def get_samplerate(self): return self.samplerate

    def set_reqs_comps(self, reqs, comps): return None


class RpcFile(ReusltData):

    def __init__(self, file_path, name=None): 
        super().__init__()
        self.file_path = file_path
        self.name      = name
        self.title_dic = None

    def read_file(self): 
        # ==============================
        file_path = self.file_path
        # ==============================

        file_path = os.path.abspath(file_path)
        # 判定文件是否存在
        if not(os.path.isfile(file_path)): 
            print('RPC File " %s " Not Found' %file_path)
            return
        
        # 读取开头数据
        file   = open(file_path,'rb')
        r = file.read(512)

        num =  len(r)//128
        dic    = {}
        for i in range(num):
            s = i*128
            e = s + 32
            key = r[s:e]
            key = key.replace(b'\x00',b'').decode()
            if key != '' : 
                v = e+96
                value = r[e:v]
                value = value.replace(b'\x00',b'').decode()
                dic[key] = value

        numHeader = int(dic['NUM_HEADER_BLOCKS'])

        r = file.read(512*(numHeader-1))
        num = len(r)//128 
        for i in range(num):
            s = i*128
            e = s + 32
            key = r[s:e]
            key = key.replace(b'\x00',b'').decode()
            if key != '' : 
                v = e+96
                value = r[e:v]
                value = value.replace(b'\x00',b'').decode()
                dic[key] = value

        # 开头数据解析
        # print(dic)
        # 通道数
        n_channel = int(dic['CHANNELS']) 
        # 通道名称
        name_channels = [ dic['DESC.CHAN_{}'.format(n+1)] for n in range(n_channel)]
        # print(name_channels)
        # SCALE 系数
        scales = [ float(dic['SCALE.CHAN_{}'.format(n+1)]) for n in range(n_channel)]
        # print(scales)
        # frame数
        n_frame = int(dic['FRAMES'])
        frame = int(dic['PTS_PER_FRAME'])
        n_half_frame = int(dic['HALF_FRAMES'])
        n_frame += n_half_frame
        # print(n_half_frame)
        # group
        group = int(dic['PTS_PER_GROUP'])
        n_group = max(1, int(frame*n_frame//group))
        # print(frame*n_frame,group,n_group)
        if frame*n_frame > n_group*group:
            n_group +=1

        # 数据段读取并解析
        data_list = [ [] for n in range(n_channel) ]

        for n_g in range(n_group):
            for num in range(n_channel):
                cal_n = group
                if n_g == n_group-1:
                    # 最后一段数据读取 , 并不一定完整解析
                    if frame*n_frame < group*n_group:
                        cal_n = frame*n_frame - group*(n_group-1)

                r = file.read(group*2)
                data_raw = struct.unpack('h'*int(group),r)
                for n,temp1 in zip(data_raw,range(cal_n)):
                    data_list[num].append(n*scales[num])

        # data_list 各同道数据

        # 关闭文档
        file.close()

        # ==============================
        self.data_original = data_list
        self.title_dic     = dic
        self.titles        = name_channels
        self.samplerate    = 1 / float(dic['DELTA_T'])
        # ==============================

        return None

    def get_samplerate(self): return self.samplerate

    def set_reqs_comps(self, reqs, comps): return None


class CsvFile(ReusltData):

    def __init__(self, file_path, name=None): 
        super().__init__()
        
        self.name          = name
        self.file_path     = file_path
        self.data_original = None
        self.times         = None
        self.titles        = None
        self.samplerate    = None


    def read_file(self): 

        # ==============================
        file_path = self.file_path
        # ==============================

        with open(file_path,'r') as f:
            filestr = f.read()
        
        list1 = []
        isTitle = True
        for loc, line in enumerate(filestr.split('\n')):
            
            if isTitle: # 开头读取
                titles = line.split(',')
                isTitle = False
                continue

            line = str_lower_strip(line)
            if line:
                line = [float(value) for value in line.split(',') if value]
                list1.append(line)

        new_list1 = []
        for n0 in range(len(list1[0])):
            line = []
            for n1 in range(len(list1)):
                line.append(list1[n1][n0])
            new_list1.append(line)

        # ==============================
        self.data_original = new_list1[1:]
        self.titles        = titles[1:]
        self.times         = new_list1[0]
        # ==============================

        return None

    def get_samplerate(self): 
        
        # ==============================
        list1 = self.times
        # ==============================

        nlen = len(list1)
        if nlen<10:
            cal_len = nlen
        else:
            cal_len = 10

        samplerate = 1 / (sum([list1[n+1]-list1[n] for n in range(cal_len-1)]) / (cal_len-1) )

        # ==============================
        self.samplerate = samplerate
        # ==============================

        return samplerate

    def set_reqs_comps(self, reqs, comps): return None


# ==============================
# ==============================

class DataModel:

    model_names = []
    models      = {}

    def __init__(self, name):

        if name not in DataModel.model_names:
            DataModel.model_names.append(name)
            DataModel.models[name] = self
            self.names      = []
            self.objs       = {}
            self.file_types = {}
            self.others     = {}
        else:
            self.names      = DataModel.models[name].names
            self.objs       = DataModel.models[name].objs
            self.file_types = DataModel.models[name].file_types
            self.others     = DataModel.models[name].others
            logger.warning(f'DataModel["{name}"] is exists, using old data.')

    def __getitem__(self, k): return self.objs[k]

    def new_file(self, file_path, name):

        assert os.path.exists(file_path)
        # assert not name in self.objs
        if name in self.objs: logger.warning(f'DataModel.new_file: {name} is exists')

        # ==============================
        file_types = self.file_types
        # ==============================

        file_type = file_path[-4:].lower()
        if file_type == '.res':
            class_cal = ResFile
            file_types[name] = 'res'
        elif file_type == '.req':
            class_cal = ReqFile
            file_types[name] = 'req'
        elif file_type in ['.drv', '.rsp']:
            class_cal = RpcFile
            file_types[name] = 'rpc'
        elif file_type == '.csv':
            class_cal = CsvFile
            file_types[name] = 'csv'
        else:
            class_cal = NumDataFile
            file_types[name] = 'num'

        # if file_path == None: # 仅存放数据
        #     class_cal = DataOnly
        #     file_types[name] = None

        # ==============================
        self.objs[name] = class_cal(file_path, name)
        if name not in self.names:
            self.names.append(name)
        # ==============================

        return None

    def get_samplerate(self, name):

        return self.objs[name].get_samplerate()


    # def join_data(self, names):
    #     # 数拼接
    #     pass
    #     key = tuple(names)
    #     self.objs[key] = 


class DataModelPlotAndPdf(abc.ABC):

    def __init__(self):
        self.fig_paths      = {} # {key:{'ts':[],'hz':[]}, }
        self.pdf_paths      = {} # {key:r'',}
        self.docx_paths     = {} # {key:r'',}

    @abc.abstractmethod
    def result_save(self): pass

    @abc.abstractmethod
    def result_read(self): pass

    @abc.abstractmethod
    def create_figure(self): pass

    @abc.abstractmethod
    def create_pdf(self): pass

    @abc.abstractmethod
    def run(self): pass

    @abc.abstractmethod
    def set_key(self): pass

    def remove_result_files(self, result_key):
        """删除所有生成的文件"""
        self.remove_figure_files(result_key)

        docx_path = self.docx_paths[result_key]
        pdf_path  = self.pdf_paths[result_key]
        os.remove(pdf_path)
        os.remove(docx_path)
        logger.info(f'remove file: {pdf_path}')
        logger.info(f'remove file: {docx_path}')

        return None

    def remove_figure_files(self, result_key):
        """删除对应的图像文件"""
        paths = self.recursive_figure_files(self.fig_paths[result_key], [])
        for path in paths:
            os.remove(os.path.abspath(path))
            logger.info(f'remove file: {path}')
        return None

    @staticmethod
    def recursive_figure_files(file_path_dic, file_paths, key_name='ts'):
        """删除对应的图像文件"""
        if key_name in file_path_dic:
            for figtype in file_path_dic:
                for path in file_path_dic[figtype]:
                    file_paths.append(path)
        else:
            for key in file_path_dic:
                temp_path = []
                file_paths.extend(DataModelPlotAndPdf.recursive_figure_files(file_path_dic[key], temp_path, key_name))

        return file_paths


class DataModelCompare(DataModelPlotAndPdf):

    def __init__(self, data_obj=None):
        super().__init__()
        self.obj            = data_obj
        self.result_compare = {}

    def compare(self, name_u, name_l):

        # ==============================
        result_key = f'{name_u}_vs_{name_l}'
        result = {}
        obj = self.obj
        u_obj = self.obj[name_u]
        l_obj = self.obj[name_l]

        # ==============================
        data_u = u_obj.get_data()
        data_l = l_obj.get_data()

        u_max, l_max = cal_max(data_u), cal_max(data_l)
        u_min, l_min = cal_min(data_u), cal_min(data_l)
        u_rms, l_rms = cal_rms(data_u), cal_rms(data_l)
        u_pdi, l_pdi = cal_rainflow_pdi(data_u), cal_rainflow_pdi(data_l)

        # ==============================
        # result定义
        result['u_name'] = name_u
        result['u_path'] = u_obj.file_path
        result['u_samplerate'] = obj.get_samplerate(name_u)
        result['u_title'] = u_obj.get_titles()
        result['u_max'] = u_max
        result['u_min'] = u_min
        result['u_pdi'] = u_pdi
        result['u_rms'] = u_rms
        result['data_u'] = data_u

        result['l_name'] = name_l
        result['l_path'] = l_obj.file_path
        result['l_samplerate'] = obj.get_samplerate(name_l)
        result['l_title'] = l_obj.get_titles()
        result['l_max'] = l_max
        result['l_min'] = l_min
        result['l_pdi'] = l_pdi
        result['l_rms'] = l_rms
        result['data_l'] = data_l

        result['u_max_divide_l_max'] = [None if l==0 else u/l for u,l in zip(u_max, l_max)]
        result['u_min_divide_l_min'] = [None if l==0 else u/l for u,l in zip(u_min, l_min)]
        result['u_pdi_divide_l_pdi'] = [None if l==0 else u/l for u,l in zip(u_pdi, l_pdi)]
        result['u_rms_divide_l_rms'] = [None if l==0 else u/l for u,l in zip(u_rms, l_rms)]

        result['u_slope'] = -5
        result['l_slope'] = -5
        result['u_intercept'] = 5000
        result['l_intercept'] = 5000

        # ==============================
        self.result_compare[result_key] = result
        # ==============================

        return result

    def result_save(self, file_path):

        file_edit.var_save(file_path, self.result_compare)
        return None

    def result_read(self, file_path):

        self.result_compare = file_edit.var_read(file_path)
        return None

    def create_figure(self, result_key, params):
        """
            创建图像 - 调用 FigPlotRealTime
            
            result_key : self.result_compare的key

            params = {
                'block_size': {'u':128, 'l':128},   # 频域计算块尺寸
                'hz_range'  : [0, 50],              # 频域截取
                'docx_path' : docx路径 str,          
                'fig_path'  : 图像路径 str,
                'str_input' : str,                  # 用于pdf创建时的额外输入, 可无
            }
        """

        # ==============================
        result_compare = self.result_compare
        result = result_compare[result_key]
        block_size = params['block_size']
        hz_range = params['hz_range']
        fig_path = params['fig_path']
        # ==============================
        
        # 图像生成
        fig_obj = plot.FigPlotRealTime(fig_path)
        fig_obj.set_figure(nums=[1,1], figsize='16:9')

        fig_obj.set_legend([result['u_name'], result['l_name']], 'ts')
        fig_obj.set_legend([result['u_name'], result['l_name']], 'hz')
        fig_obj.set_ylabel(result['u_title'], 'ts')
        fig_obj.set_ylabel(result['u_title'], 'hz')
        fig_obj.set_xlabel('time(s)', 'ts')
        fig_obj.set_xlabel('Hz', 'hz')

        time_line_u  = [ n / result['u_samplerate'] for n in range(len(result['data_u'][0])) ]
        time_line_us = [time_line_u] * len(result['data_u'])

        time_line_l  = [ n / result['l_samplerate'] for n in range(len(result['data_l'][0])) ]
        time_line_ls = [time_line_l] * len(result['data_l'])

        fig_obj.plot_ts(
            [result['data_u'], result['data_l']],
            [time_line_us, time_line_ls], 
            linetypes = ['b', 'r--'],
            )

        fig_obj.plot_hz(
            [result['data_u'], result['data_l']], 
            samplerates = [result['u_samplerate'], result['l_samplerate']], 
            block_sizes = [block_size['u'], block_size['l']], 
            hz_range    = hz_range, 
            linetypes   = ['b', 'r--']
            )

        fig_paths = fig_obj.fig_paths

        # ==============================
        self.fig_paths[result_key] = fig_paths
        # ==============================

        return fig_paths

    def create_figure_ts(self, result_key, params):
        """
            创建图像 - 调用 FigPlotRealTime
            
            result_key : self.result_compare的key

            params = {
                'block_size': {'u':128, 'l':128},   # 频域计算块尺寸
                'hz_range'  : [0, 50],              # 频域截取
                'docx_path' : docx路径 str,          
                'fig_path'  : 图像路径 str,
                'str_input' : str,                  # 用于pdf创建时的额外输入, 可无
                'nums'      : [int,int]             # 图片排列
            }   
        """

        # ==============================
        result_compare = self.result_compare
        result         = result_compare[result_key]
        block_size     = params['block_size']
        hz_range       = params['hz_range']
        fig_path       = params['fig_path']
        nums           = params['nums']
        # ==============================
        
        # 图像生成
        fig_obj = plot.FigPlotRealTime(fig_path)
        size = 16
        figsize = '{}:{}'.format(size, size/nums[1]*nums[0]*0.65)
        fig_obj.set_figure(nums=nums, figsize=figsize)

        fig_obj.set_legend([result['u_name'], result['l_name']], 'ts')
        fig_obj.set_ylabel(result['u_title'], 'ts')
        fig_obj.set_xlabel('time(s)', 'ts')

        time_line_u  = [ n / result['u_samplerate'] for n in range(len(result['data_u'][0])) ]
        time_line_us = [time_line_u] * len(result['data_u'])

        time_line_l  = [ n / result['l_samplerate'] for n in range(len(result['data_l'][0])) ]
        time_line_ls = [time_line_l] * len(result['data_l'])

        fig_obj.plot_ts(
            [result['data_u'], result['data_l']],
            [time_line_us, time_line_ls], 
            linetypes = ['b', 'r--'],
            )

        fig_paths = fig_obj.fig_paths
        # ==============================
        self.fig_paths[result_key] = fig_paths
        # ==============================

        return fig_paths

    def create_figure_1(self, result_key, params):
        """
            创建图像 - 调用 FigPlot
            
            result_key : self.result_compare的key

            params = {
                'block_size': {'u':128, 'l':128},   # 频域计算块尺寸
                'hz_range'  : [0, 50],              # 频域截取
                'docx_path' : docx路径 str,          
                'fig_path'  : 图像路径 str,
                'str_input' : str,                  # 用于pdf创建时的额外输入, 可无
            }
        """

        # ==============================
        result_compare = self.result_compare
        result = result_compare[result_key]
        block_size = params['block_size']
        hz_range = params['hz_range']
        fig_path = params['fig_path']
        # ==============================
        
        # 图像生成
        fig_obj = plot.FigPlot()
        fig_obj.set_figure(nums=[1,1])
        time_line_u = [ n / result['u_samplerate'] for n in range(len(result['data_u'][0])) ]
        fig_obj.plot_ts(result['data_u'],time_line_u, linetype='b')
        time_line_l = [ n / result['l_samplerate'] for n in range(len(result['data_l'][0])) ]
        fig_obj.plot_ts(result['data_l'],time_line_l, linetype='r--')

        fig_obj.plot_hz(result['data_u'], samplerate=result['u_samplerate'], 
            block_size=block_size['u'], hz_range=hz_range, linetype='b')

        fig_obj.plot_hz(result['data_l'], samplerate=result['l_samplerate'], 
            block_size=block_size['l'], hz_range=hz_range, linetype='r--')

        fig_obj.set_legend([result['u_name'], result['l_name']], 'ts')
        fig_obj.set_legend([result['u_name'], result['l_name']], 'hz')
        fig_obj.set_ylabel(result['u_title'], 'ts')
        fig_obj.set_ylabel(result['u_title'], 'hz')
        fig_obj.set_xlabel('time(s)', 'ts')
        fig_obj.set_xlabel('Hz', 'hz')
        fig_obj.updata('hz')
        fig_obj.updata('ts')

        fig_paths = fig_obj.save(fig_path)

        # ==============================
        self.fig_paths[result_key] = fig_paths
        # ==============================

        return fig_paths

    def create_pdf(self, result_key, params):
        """
            创建pdf文件

            result_key : self.result_compare的key

            params = {
                'block_size': {'u':128, 'l':128},   # 频域计算块尺寸
                'hz_range'  : [0, 50],              # 频域截取
                'docx_path' : docx路径 str,          
                'fig_path'  : 图像路径 str,
                'str_input' : str,                  # 用于pdf创建时的额外输入, 可无
            }
        """

        # ==============================
        fig_paths = self.fig_paths[result_key]
        result_compare = self.result_compare
        result = result_compare[result_key]

        block_size = params['block_size']
        hz_range   = params['hz_range']
        docx_path  = params['docx_path']
        # ==============================

        line_hz_set = '\tPSD 设置 :\n\t\thz_range [{},{}] ; block_size A:{} B:{}'
        line_hz_set = line_hz_set.format(*hz_range, block_size['u'], block_size['l'])

        obj = office_docx.DataDocx(docx_path)  # word编写
        obj.set_page_margin(x=1.27, y=1.27)

        self.str_pdf_title(obj, result)
        obj.add_page_break()  # 另起一页     

        line_title = 'A({}) vs. B({}) '
        title = line_title.format(
            os.path.basename(result['u_path']) + '|' + result['u_name'],
            os.path.basename(result['l_path']) + '|' + result['l_name'])

        obj.add_heading(title, level=0, size=20)

        # ==============================
        # 时间显示
        str_time = time.strftime('%Y.%m.%d - %H:%M:%S', time.localtime(time.time()))
        obj.add_paragraph('创建时间:' + str_time)  # 注释

        # ==============================
        # 额外输入
        if 'str_input' in params:
            obj.add_paragraph(params['str_input'])
            obj.add_page_break()

        # ==============================
        # 数据对比
        obj.add_heading('数据对比', level=1, size=15)

        list_title = ['chantitle','pdi','max','min','rms']

        # ==============================
        # 汇总表格
        list_compare = [
            result['u_pdi_divide_l_pdi'],
            result['u_max_divide_l_max'],
            result['u_min_divide_l_min'],
            result['u_rms_divide_l_rms'],
        ]
        list_compare = list2_change_rc(list_compare)
        
        for n, line in enumerate(list_compare):
            line.insert(0, 'A:{}'.format(result['u_title'][n])) 

        obj.add_table(f'相对比例-汇总 A/B', value2str_list2([list_title]+list_compare,3))
        obj.add_page_break()
        # ==============================

        for loc in range(len(result['u_title'])):
            
            obj.add_list_bullet('A : '+result['u_title'][loc], size=12)
            obj.add_list_bullet('B : '+result['l_title'][loc], size=12)
            obj.add_docx_figure(fig_paths['ts'][loc], f'时域图 {loc+1}', width=17)  # 时域图
            obj.add_docx_figure(fig_paths['hz'][loc], f'PSD图 {loc+1}', width=17)  # 频域图
            obj.add_page_break()   # 另起一页
            
            obj.add_paragraph('设置:')  # 注释
            line_pdi_set = '\t{} :\n\t\tsamplerate 采样频率 {} Hz\n\t\tPDI设置: slope斜率 {} , intercept截距 {}'
            obj.add_paragraph(
                line_pdi_set.format(result['u_title'][loc],result['u_samplerate'],result['u_slope'],result['u_intercept'])
                )
            obj.add_paragraph(
                line_pdi_set.format(result['l_title'][loc],result['l_samplerate'],result['l_slope'],result['l_intercept'])
                )
            obj.add_paragraph(line_hz_set)

            # 表格
            list_0  = copy.deepcopy(list_title)
            temp_list = [ list_0,
                ['A'+result['u_title'][loc], result['u_pdi'][loc], result['u_max'][loc], result['u_min'][loc], result['u_rms'][loc]],
                ['B'+result['l_title'][loc], result['l_pdi'][loc], result['l_max'][loc], result['l_min'][loc], result['l_rms'][loc]],
            ]
            obj.add_table(f'表格{loc+1}', value2str_list2(temp_list, 3))

            obj.add_page_break()  # 另起一页

        obj.save()

        self.pdf_paths[result_key] = office_docx.doc2pdf(docx_path)
        self.docx_paths[result_key] = docx_path

        return self.pdf_paths[result_key]

    def create_pdf_ts(self, result_key, params):
        """
            创建pdf文件

            result_key : self.result_compare的key

            params = {
                'block_size': {'u':128, 'l':128},   # 频域计算块尺寸
                'hz_range'  : [0, 50],              # 频域截取
                'docx_path' : docx路径 str,          
                'fig_path'  : 图像路径 str,
                'str_input' : str,                  # 用于pdf创建时的额外输入, 可无
                'nums'      : [int,int]             # 图片排列
            }
        """

        # ==============================
        fig_paths = self.fig_paths[result_key]
        result_compare = self.result_compare
        result = result_compare[result_key]

        block_size = params['block_size']
        hz_range   = params['hz_range']
        docx_path  = params['docx_path']
        nums           = params['nums']
        # ==============================
        obj = office_docx.DataDocx(docx_path)  # word编写
        obj.set_page_margin(x=1.27, y=1.27)

        self.str_pdf_title(obj, result)
        obj.add_page_break()  # 另起一页     

        line_title = 'A({}) vs. B({}) '
        title = line_title.format(
            os.path.basename(result['u_path']) + '|' + result['u_name'],
            os.path.basename(result['l_path']) + '|' + result['l_name'])

        obj.add_heading(title, level=0, size=20)
        # ==============================
        # 时间显示
        str_time = time.strftime('%Y.%m.%d - %H:%M:%S', time.localtime(time.time()))
        obj.add_paragraph('创建时间:' + str_time)  # 注释
        # ==============================
        # 额外输入
        if 'str_input' in params:
            obj.add_paragraph(params['str_input'])
            obj.add_page_break()
        # ==============================
        # 数据对比
        obj.add_heading('数据对比', level=1, size=15)
        list_title = ['chantitle','pdi','max','min','rms']
        # ==============================
        # 汇总表格
        list_compare = [
            result['u_pdi_divide_l_pdi'],
            result['u_max_divide_l_max'],
            result['u_min_divide_l_min'],
            result['u_rms_divide_l_rms'],
        ]
        list_compare = list2_change_rc(list_compare)
        
        for n, line in enumerate(list_compare):
            line.insert(0, 'A:{}'.format(result['u_title'][n])) 

        obj.add_table(f'相对比例-汇总 A/B', value2str_list2([list_title]+list_compare,3))
        obj.add_page_break()
        # ==============================
        n_axis   = 1
        max_axis = nums[0] * nums[1]
        for loc in range(len(result['u_title'])):
            a_str = f'{n_axis} A : '+result['u_title'][loc]
            # b_str = f'{n_axis} B : '+result['l_title'][loc]
            b_str = 'B : '+result['l_title'][loc]
            obj.add_list_bullet(a_str + ' ; '+  b_str, size=10)
            # obj.add_list_bullet(, size=10)
            fig_loc, temp_n = divmod(loc, max_axis)
            n_axis += 1
            if temp_n == max_axis-1:
                obj.add_docx_figure(fig_paths['ts'][fig_loc], f'时域图 {fig_loc+1}', width=18)  # 时域图
                obj.add_page_break()   # 另起一页
                n_axis = 1
        if temp_n != max_axis-1:
            obj.add_docx_figure(fig_paths['ts'][fig_loc], f'时域图 {fig_loc+1}', width=18)  # 时域图

        obj.save()

        self.pdf_paths[result_key] = office_docx.doc2pdf(docx_path)
        self.docx_paths[result_key] = docx_path

        return self.pdf_paths[result_key] 

    def create_pdf_middle(self, result_key, params):
        """
            创建pdf文件

            result_key : self.result_compare的key

            params = {
                'block_size': {'u':128, 'l':128},   # 频域计算块尺寸
                'hz_range'  : [0, 50],              # 频域截取
                'docx_path' : docx路径 str,          
                'fig_path'  : 图像路径 str,
                'str_input' : str,                  # 用于pdf创建时的额外输入, 可无
            }
        """

        # ==============================
        fig_paths = self.fig_paths[result_key]
        result_compare = self.result_compare
        result = result_compare[result_key]

        block_size = params['block_size']
        hz_range   = params['hz_range']
        docx_path  = params['docx_path']
        # ==============================

        line_hz_set = '\tPSD 设置 :\n\t\thz_range [{},{}] ; block_size A:{} B:{}'
        line_hz_set = line_hz_set.format(*hz_range, block_size['u'], block_size['l'])

        obj = office_docx.DataDocx(docx_path)  # word编写
        obj.set_page_margin(x=1.27, y=1.27)

        self.str_pdf_title(obj, result)
        obj.add_page_break()  # 另起一页     

        line_title = 'A({}) vs. B({}) '
        title = line_title.format(
            os.path.basename(result['u_path']) + '|' + result['u_name'],
            os.path.basename(result['l_path']) + '|' + result['l_name'])

        obj.add_heading(title, level=0, size=20)

        # ==============================
        # 时间显示
        str_time = time.strftime('%Y.%m.%d - %H:%M:%S', time.localtime(time.time()))
        obj.add_paragraph('创建时间:' + str_time)  # 注释

        # ==============================
        # 额外输入
        if 'str_input' in params:
            obj.add_paragraph(params['str_input'])
            obj.add_page_break()

        # ==============================
        # 数据对比
        obj.add_heading('数据对比', level=1, size=15)

        list_title = ['chantitle','pdi','max','min','rms']

        # ==============================
        # 汇总表格
        list_compare = [
            result['u_pdi_divide_l_pdi'],
            result['u_max_divide_l_max'],
            result['u_min_divide_l_min'],
            result['u_rms_divide_l_rms'],
        ]
        list_compare = list2_change_rc(list_compare)
        
        for n, line in enumerate(list_compare):
            line.insert(0, 'A:{}'.format(result['u_title'][n])) 

        obj.add_table(f'相对比例-汇总 A/B', value2str_list2([list_title]+list_compare,3))
        obj.add_page_break()


        # ==============================
        obj.add_paragraph('设置:')  # 注释
        line_pdi_set = '\t{} :\n\t\tsamplerate 采样频率 {} Hz\n\t\tPDI设置: slope斜率 {} , intercept截距 {}'
        obj.add_paragraph(
            line_pdi_set.format('A File', result['u_samplerate'], result['u_slope'], result['u_intercept'])
            )
        obj.add_paragraph(
            line_pdi_set.format('B File', result['l_samplerate'], result['l_slope'], result['l_intercept'])
            )
        obj.add_paragraph(line_hz_set)

        for loc in range(len(result['u_title'])):
            # 表格
            list_0  = copy.deepcopy(list_title)
            temp_list = [ list_0,
                ['A'+result['u_title'][loc], result['u_pdi'][loc], result['u_max'][loc], result['u_min'][loc], result['u_rms'][loc]],
                ['B'+result['l_title'][loc], result['l_pdi'][loc], result['l_max'][loc], result['l_min'][loc], result['l_rms'][loc]],
            ]
            obj.add_table(f'通道 {loc+1}', value2str_list2(temp_list, 3))

        obj.add_page_break()  # 另起一页


        # ==============================        
        for loc in range(len(result['u_title'])):
            
            obj.add_list_bullet('A : '+result['u_title'][loc], size=12)
            obj.add_list_bullet('B : '+result['l_title'][loc], size=12)
            obj.add_docx_figure(fig_paths['ts'][loc], f'时域图 {loc+1}', width=17)  # 时域图
            obj.add_docx_figure(fig_paths['hz'][loc], f'PSD图  {loc+1}', width=17)  # 频域图
            if loc != (len(result['u_title'])-1):
                obj.add_page_break()   # 另起一页

        obj.save()

        self.pdf_paths[result_key] = office_docx.doc2pdf(docx_path)
        self.docx_paths[result_key] = docx_path

        return self.pdf_paths[result_key]

    def run(self, name_u, name_l, params, pdfType=1):
        """
            运行生成pdf文件

            name_u : DataModel类实例的 objs属性的 key, 分子名称
            name_l : DataModel类实例的 objs属性的 key, 分母名称

            params = {
                'block_size': {'u':1024, 'l':1023},
                'hz_range'  : [0, 50],
                'docx_path' : r'',
                'fig_path'  : r'',
                'str_input' : str,                  # 用于pdf创建时的额外输入, 可无
            }
        """
        # ==============================
        result_compare = self.result_compare
        # result_key     = f'{name_u}_vs_{name_l}'
        result_key     = self.set_key(name_u, name_l)
        # ==============================
        if result_key in result_compare:
            result = result_compare[result_key]
        else:
            result = self.compare(name_u, name_l)

        if pdfType == 1:
            self.create_figure(result_key, params)
            pdf_path = self.create_pdf(result_key, params)
        elif pdfType == 2:
            self.create_figure_ts(result_key, params)
            pdf_path = self.create_pdf_ts(result_key, params)
        elif pdfType == 3:
            self.create_figure(result_key, params)
            pdf_path = self.create_pdf_middle(result_key, params)


        return pdf_path

    def set_key(self, name_u, name_l):
        """生成key"""
        return f'{name_u}_vs_{name_l}'

    def str_pdf_title(self, docx_obj, result): # 创建文档开头

        # str_time = time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time()))
        str_time = time.strftime('%Y.%m.%d %H:%M', time.localtime(time.time()))

        docx_obj.add_heading('\n'*2, level=1, size=20)
        docx_obj.add_heading('数据对比评估', level=1, size=40, align='center')
        docx_obj.add_heading('--A vs. B', level=1, size=25, align='right')
        docx_obj.add_heading('\n'*1, level=1, size=20)
                
        docx_obj.add_heading('A File: '+os.path.basename(result['u_path']), level=1, size=15, align='center')
        docx_obj.add_heading('B File: '+os.path.basename(result['l_path']), level=1, size=15, align='center')
        docx_obj.add_heading('\n'*5, level=1, size=20)

        docx_obj.add_list_bullet('创建时间:'+str_time, size=15)
        docx_obj.add_list_bullet('自动生成', size=15)

        return None        


class DataModelPlot(DataModelPlotAndPdf):

    def __init__(self, data_obj=None):
        super().__init__()
        self.obj       = data_obj
        self.results   = {}

    def ts_data_change(self, name):

        # ==============================
        obj = self.obj
        data_obj = self.obj[name]
        # ==============================
        result = {}
        data = data_obj.get_data()
        d_max = cal_max(data)
        d_min = cal_min(data)
        d_rms = cal_rms(data)

        result['name'] = name
        result['path'] = data_obj.file_path
        result['samplerate'] = obj.get_samplerate(name)
        result['title'] = data_obj.get_titles()
        result['max'] = d_max
        result['min'] = d_min
        result['rms'] = d_rms
        result['data'] = data
        result['slope'] = -5
        result['intercept'] = 5000

        # ==============================
        self.results[name] = result
        # ==============================

        return result

    def result_save(self, file_path):

        file_edit.var_save(file_path, self.results)
        return None

    def result_read(self, file_path):

        self.results = file_edit.var_read(file_path)
        return None

    def create_figure(self, name, params):

        # ==============================
        result     = self.results[name]
        block_size = params['block_size']
        hz_range   = params['hz_range']
        fig_path   = params['fig_path']
        # ==============================
        
        # 图像生成
        fig_obj = plot.FigPlotRealTime(fig_path)  # 即时生成图像数据,减少内存占用
        fig_obj.set_figure(nums=[1,1], figsize='16:9')
        fig_obj.set_legend([result['name']], 'ts')
        fig_obj.set_legend([result['name']], 'hz')
        fig_obj.set_ylabel(result['title'], 'ts')
        fig_obj.set_ylabel(result['title'], 'hz')
        fig_obj.set_xlabel('time(s)', 'ts')
        fig_obj.set_xlabel('Hz', 'hz')

        time_line  = [ n / result['samplerate'] for n in range(len(result['data'][0])) ]
        time_lines = [time_line] * len(result['data'])

        fig_obj.plot_ts([result['data']], [time_lines], linetypes=['b'])

        fig_obj.plot_hz([result['data']], samplerates=[result['samplerate']], 
            block_sizes=[block_size], hz_range=hz_range, linetypes=['b'])

        fig_paths = fig_obj.fig_paths
        # ==============================
        self.fig_paths[name] = fig_paths
        # ==============================
        return fig_paths

    def create_figure_ts(self, name, params):
        """
            仅生成时域数据
        """
        # ==============================
        result     = self.results[name]
        block_size = params['block_size']
        hz_range   = params['hz_range']
        fig_path   = params['fig_path']
        nums       = params['nums']
        # ==============================
        
        # 图像生成
        fig_obj = plot.FigPlotRealTime(fig_path)  # 即时生成图像数据,减少内存占用
        fig_size = 16
        figsize = '{}:{}'.format(fig_size, fig_size/nums[1]*nums[0]*0.65)
        fig_obj.set_figure(nums=nums, figsize=figsize)
        fig_obj.set_legend([result['name']], 'ts')
        fig_obj.set_ylabel(result['title'], 'ts')
        fig_obj.set_xlabel('time(s)', 'ts')

        time_line  = [ n / result['samplerate'] for n in range(len(result['data'][0])) ]
        time_lines = [time_line] * len(result['data'])

        fig_obj.plot_ts([result['data']], [time_lines], linetypes=['b'])

        fig_paths = fig_obj.fig_paths
        # ==============================
        self.fig_paths[name] = fig_paths
        # ==============================
        return fig_paths

    def create_figure_1(self, name, params):

        # ==============================
        result     = self.results[name]
        block_size = params['block_size']
        hz_range   = params['hz_range']
        fig_path   = params['fig_path']
        # ==============================
        
        # 图像生成
        fig_obj = plot.FigPlot()
        fig_obj.set_figure(nums=[1,1])
        time_line = [ n / result['samplerate'] for n in range(len(result['data'][0])) ]
        fig_obj.plot_ts(result['data'],time_line, linetype='b')

        fig_obj.plot_hz(result['data'], samplerate=result['samplerate'], 
            block_size=block_size, hz_range=hz_range, linetype='b')

        fig_obj.set_legend([result['name']], 'ts')
        fig_obj.set_legend([result['name']], 'hz')
        fig_obj.set_ylabel(result['title'], 'ts')
        fig_obj.set_ylabel(result['title'], 'hz')
        fig_obj.set_xlabel('time(s)', 'ts')
        fig_obj.set_xlabel('Hz', 'hz')
        fig_obj.updata('hz')
        fig_obj.updata('ts')

        fig_paths = fig_obj.save(fig_path)

        # ==============================
        self.fig_paths[name] = fig_paths
        # ==============================

        return fig_paths

    def create_pdf(self, name, params):

        # ==============================
        result_key = self.set_key(name)
        fig_paths = self.fig_paths[result_key]
        result = self.results[result_key]
        
        block_size = params['block_size']
        hz_range   = params['hz_range']
        docx_path  = params['docx_path']
        # ==============================

        line_hz_set = '\tPSD 设置 :\n\t\thz_range [{},{}] ; block_size {} '
        line_hz_set = line_hz_set.format(*hz_range, block_size)

        obj = office_docx.DataDocx(docx_path)  # word编写
        obj.set_page_margin(x=1.27, y=1.27)
        line_title = 'A({})'
        title = line_title.format(os.path.basename(result['path'])+'|'+result['name'])


        obj.add_heading(title, level=0, size=20)
        obj.add_heading('数据对比', level=1, size=15)

        list_title = ['chantitle','max','min','rms']
        # ==============================
        # 汇总表格
        list_compare = [result['max'], result['min'], result['rms'],]
        list_compare = list2_change_rc(list_compare)
        for n, line in enumerate(list_compare):
            line.insert(0, result['title'][n])

        obj.add_table(f'汇总', value2str_list2([list_title]+list_compare,3))
        obj.add_page_break()
        # ==============================

        for loc in range(len(result['title'])):
            obj.add_list_bullet('channel : '+result['title'][loc], size=15)
            obj.add_docx_figure(fig_paths['ts'][loc], f'时域图 {loc+1}', width=15)  # 时域图
            obj.add_docx_figure(fig_paths['hz'][loc], f'频域图 {loc+1}', width=15)  # 频域图
            line_set = '采样频率: {} Hz ; block_size: {};'.format(result['samplerate'], block_size)
            obj.add_paragraph(line_set)  # 注释
            obj.add_page_break()  # 另起一页

        obj.save()

        self.pdf_paths[result_key] = office_docx.doc2pdf(docx_path)
        self.docx_paths[result_key] = docx_path

        return self.pdf_paths[result_key]

    def create_pdf_ts(self, name, params):

        # ==============================
        result_key = self.set_key(name)
        fig_paths = self.fig_paths[result_key]
        result = self.results[result_key]
        
        block_size = params['block_size']
        hz_range   = params['hz_range']
        docx_path  = params['docx_path']
        nums       = params['nums']
        # ==============================
        obj = office_docx.DataDocx(docx_path)  # word编写
        obj.set_page_margin(x=1.27, y=1.27)
        line_title = 'A({})'
        title = line_title.format(os.path.basename(result['path'])+'|'+result['name'])

        obj.add_heading(title, level=0, size=20)
        obj.add_heading('数据对比', level=1, size=15)

        list_title = ['chantitle','max','min','rms']
        # ==============================
        # 汇总表格
        list_compare = [result['max'], result['min'], result['rms'],]
        list_compare = list2_change_rc(list_compare)
        for n, line in enumerate(list_compare):
            line.insert(0, result['title'][n])

        obj.add_table(f'汇总', value2str_list2([list_title]+list_compare,3))
        obj.add_page_break()
        # ==============================
        n_axis   = 1
        max_axis = nums[0] * nums[1]
        for loc in range(len(result['title'])):
            obj.add_list_bullet(f'{n_axis} fig : '+result['title'][loc], size=10)
            fig_loc, temp_n = divmod(loc, max_axis)
            n_axis += 1
            if temp_n == max_axis-1:
                obj.add_docx_figure(fig_paths['ts'][fig_loc], f'时域图 {fig_loc+1}', width=18)  # 时域图
                obj.add_page_break()   # 另起一页
                n_axis = 1
        if temp_n != max_axis-1:
            obj.add_docx_figure(fig_paths['ts'][fig_loc], f'时域图 {fig_loc+1}', width=18)  # 时域图

        obj.save()

        self.pdf_paths[result_key] = office_docx.doc2pdf(docx_path)
        self.docx_paths[result_key] = docx_path

        return self.pdf_paths[result_key]

    def run(self, name, params, pdfType=1):
        """
            params = {
                'block_size': 1024,
                'hz_range'  : [0, 50],
                'docx_path' : r'',
                'fig_path'  : r'',
            }
        """
        # ==============================
        reuslt = self.results[name] if name in self.results else self.ts_data_change(name)
        # ==============================
        if pdfType == 1:
            self.create_figure(name, params)
            pdf_path = self.create_pdf(name, params)
        elif pdfType == 2:
            self.create_figure_ts(name, params)
            pdf_path = self.create_pdf_ts(name, params)

        return pdf_path

    def set_key(self, name): return name


class DataModelScatter(DataModelPlotAndPdf):

    def __init__(self, data_obj=None):
        super().__init__()
        self.obj       = data_obj
        self.results   = {}
        self.cors      = {}  # 相关系数

    def ts_data_change(self, name, xchannels, ychannels=None): # results 赋值

        # ==============================
        obj = self.obj
        data_obj = self.obj[name]
        # ==============================
        result = {}
        result_key = self.set_key(name, xchannels)

        data_obj.set_select_channels(xchannels)
        result['data_x'] = data_obj.get_data()
        result['titles_x'] = data_obj.get_titles()

        data_obj.set_select_channels(ychannels)
        result['data_y'] = data_obj.get_data()
        result['titles_y'] = data_obj.get_titles()

        self.results[result_key] = result

        return result

    def result_save(self): pass

    def result_read(self): pass

    def create_figure(self, name, params):

        xchannels = params['xchannels']
        ychannels = params['ychannels']
        fig_path  = params['fig_path']

        result_key = self.set_key(name, xchannels)
        result = self.results[result_key]

        data_x   = result['data_x']
        data_y   = result['data_y']
        titles_x = result['titles_x']
        titles_y = result['titles_y']

        nums = params['nums'] if 'nums' in params else [3,2]

        n = 0
        fig_paths = {}    
        for line_x, title_x in zip(data_x, titles_x):

            fig_obj = plot.FigPlotRealTime(fig_path+f'_{title_x}')  # 即时生成图像数据,减少内存占用
            fig_size = 16  # 16
            figsize = '{}:{}'.format(fig_size, fig_size/nums[1]*nums[0]*0.65)
            fig_obj.set_figure(nums=nums, figsize=figsize)
            fig_obj.set_xlabel(title_x, 'ts')
            fig_obj.set_ylabel(titles_y, 'ts')
            fig_obj.set_legend([result_key[0]], 'ts')
            fig_obj.plot_ts(
                [data_y], 
                [[line_x]*len(data_y)], 
                linetypes=['b'],
                plottype='scatter')

            cors = [self.xy_correlation(line_x, line_y) for line_y in data_y]
            self.cors[title_x] = cors
            # print(cors)

            fig_paths[title_x] = fig_obj.fig_paths

        self.fig_paths[result_key] = fig_paths 

        return fig_paths

    def create_figure_1(self, name, params):

        xchannels = params['xchannels']
        ychannels = params['ychannels']
        fig_path  = params['fig_path']

        result_key = self.set_key(name, xchannels)
        result = self.results[result_key]

        data_x   = result['data_x']
        data_y   = result['data_y']
        titles_x = result['titles_x']
        titles_y = result['titles_y']

        nums = params['nums'] if 'nums' in params else [2,2]

        n = 0
        fig_paths = {}    
        for line_x, title_x in zip(data_x, titles_x):

            fig_obj = plot.FigPlot()
            fig_obj.set_figure(nums=nums)
            fig_obj.plot_ts(data_y, line_x, linetype='b',plottype='scatter')
            fig_obj.set_xlabel(title_x, 'ts')
            fig_obj.set_ylabel(titles_y, 'ts')
            fig_obj.updata('ts')
            # fig_obj.show()
            fig_paths[title_x] = fig_obj.save(fig_path+f'_{title_x}')

        self.fig_paths[result_key] = fig_paths 

        return fig_paths # {key:{'ts':[],hz':[]}}

    def create_pdf(self, name, params):
        """
            self.fig_paths 
                {'ACC_FL.X': {'ts': ['../dms_test_ACC_FL.X_ts_0.png', '../dms_test_ACC_FL.X_ts_1.png'], 'hz': []}, 
                'ACC_FL.Y': {'ts': ['../dms_test_ACC_FL.Y_ts_0.png', '../dms_test_ACC_FL.Y_ts_1.png'], 'hz': []}}
        """
        xchannels = params['xchannels']
        result_key = self.set_key(name, xchannels)

        fig_paths = self.fig_paths[result_key]
        docx_path = params['docx_path']

        nums = params['nums'] if 'nums' in params else [3,2]
        # nums   = params['nums']
        n_nums = nums[0] * nums[1]

        obj = office_docx.DataDocx(docx_path)  # word编写
        obj.set_page_margin(x=1.27, y=1.27)

        self.str_pdf_title(name, obj, fig_paths)
        obj.add_page_break()  # 另起一页     

        for key in fig_paths:
            for n, path in enumerate(fig_paths[key]['ts']):
                
                result = self.results[result_key]
                titles_y = result['titles_y']

                obj.add_heading(key, level=1, size=15)
                # Y轴标题
                for n1 in range(n*n_nums, n*n_nums+n_nums):
                    if n1 >= len(titles_y):
                        break
                    cor = self.cors[key][n1] # 相关系数
                    obj.add_list_bullet(f'{n1} : {titles_y[n1]:65}  皮尔逊相关系数: {cor:0.2f}', size=10)

                # if divmod(n,2)[-1]==0:
                #     obj.add_heading(key, level=1, size=15)

                obj.add_docx_figure(path, f'散点图{n} {key}', width=19)  # 时域图
                obj.add_page_break()  # 另起一页    

                # if divmod(n,2)[-1]==1:
                #     obj.add_page_break()  # 另起一页        
            
            # if divmod(n,2)[-1]==0:
            #     obj.add_page_break()  # 另起一页
        obj.save() # 保存
        
        self.pdf_paths[result_key] = office_docx.doc2pdf(docx_path)
        self.docx_paths[result_key] = docx_path

        return self.pdf_paths[result_key]

    def str_pdf_title(self, name, docx_obj, fig_paths): # 创建文档开头

        # str_time = time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time()))
        str_time = time.strftime('%Y.%m.%d %H:%M', time.localtime(time.time()))

        file_path = self.obj[name].file_path

        file_name = os.path.basename(file_path)
        docx_obj.add_heading('\n'*2, level=1, size=20)
        docx_obj.add_heading('数据相关性评估', level=1, size=40, align='center')
        docx_obj.add_heading('--散点图对比', level=1, size=25, align='right')
        docx_obj.add_heading('\n'*1, level=1, size=20)
        # docx_obj.add_heading('目标文件:'+file_name, level=1, size=15, align='right')
        docx_obj.add_heading('File: '+file_name, level=1, size=15, align='center')
        for key in fig_paths:
            docx_obj.add_heading('X: '+key, level=1, size=15, align='center')

        docx_obj.add_heading('\n'*5, level=1, size=20)
        # docx_obj.add_list_bullet('目标文件:'+file_name, size=15)
        docx_obj.add_list_bullet('创建时间:'+str_time, size=15)
        docx_obj.add_list_bullet('自动生成', size=15)

        return None        

    def run(self, name, params):
        """
            params = {
                'docx_path' : r'./dms_test.docx',
                'fig_path'  : r'./dms_test',
                'xchannels' : [0,1],
                'ychannels' : None,
                'nums'      : [2,2]
        }
        """

        xchannels = params['xchannels']
        ychannels = params['ychannels']
        docx_path = params['docx_path'][:-5] + '_x{}_{}.docx'
        pdf_paths = []
        for xchannel in xchannels:
            
            params['fig_path']  = params['docx_path'][:-5]
            params['xchannels'] = [xchannel]
            key = self.set_key(name, [xchannel])

            result = self.results[key] if key in self.results else self.ts_data_change(name, [xchannel], ychannels)
            params['docx_path'] = docx_path.format(xchannel, result['titles_x'][0])

            fig_paths = self.create_figure(name, params)
            pdf_path  = self.create_pdf(name, params)
            pdf_paths.append(pdf_path)

        params['xchannels'] = xchannels

        return pdf_paths

    def set_key(self, name, xchannels):  return (name, tuple(xchannels))

    @staticmethod
    def xy_correlation(xline, yline): # 皮尔逊相关系数
        from scipy.stats import pearsonr
        r, p = pearsonr(xline, yline)
        # print(r)
        return r


# ==============================
# ==============================
# 测试
def test_CsvFile():

    csv_path = r'..\tests\file_result\break_brake.csv'
    data_obj = DataModel('test')
    data_obj.new_file(csv_path, 'csv')
    data_obj['csv'].read_file()
    data_obj['csv'].set_select_channels([0,1,2])
    data_obj['csv'].set_line_ranges([0,10])
    data = data_obj['csv'].get_data()
    print(data)

    return None

def test_ResFile():

    res_path = r'..\tests\file_result\break_brake.res'

    # obj = ResFile(res_path, 'res')

    data_obj = DataModel('test')
    data_obj.new_file(res_path, 'res')
    data_obj['res'].set_reqs_comps(
        ['ACC_FL','ACC_FL','ACC_FL','ACC_FR','ACC_FR','ACC_FR'],
        ['X','Y','Z','X','Y','Z'],
        )
    # data_obj['res'].read_file()
    data_obj['res'].read_file_faster()
    data_obj['res'].set_select_channels([0,1,2])
    data_obj['res'].set_line_ranges([3,30])
    
    data_obj['res'].get_samplerate()
    data = data_obj['res'].get_data()
    titles = data_obj['res'].get_titles()
    print(data)

    csv_path = r'..\tests\file_result\break_brake.csv'
    data_obj['res'].save_csv_data(csv_path)

    return None

def test_NumDataFile():

    file_path = r'..\tests\file_result\num_brake_brake.txt'
    data_obj = DataModel('test')
    data_obj.new_file(file_path, 'num')
    data_obj['num'].read_file()
    data_obj['num'].set_select_channels([0,1,2])
    data_obj['num'].set_line_ranges([2,30])

    data = data_obj['num'].get_data()
    titles = data_obj['num'].get_titles()
    print(data)
    print(titles)

    return None

def test_RspFile():

    file_path = r'..\tests\file_result\rpc3.rsp'
    data_obj = DataModel('test')
    data_obj.new_file(file_path, 'rpc')
    data_obj['rpc'].read_file()
    data_obj['rpc'].set_select_channels([0,1,2])
    data_obj['rpc'].set_line_ranges([2,10])

    data = data_obj['rpc'].get_data()
    titles = data_obj['rpc'].get_titles()
    samplerate = data_obj['rpc'].get_samplerate()
    # print(data)
    # print(titles)
    # print(samplerate)

    assert data == [[-7.6039368087969e-14, -5.76823893273381e-13, 6.478707775979984e-13, -1.0701836990158599e-13, -1.424778058618005e-13, -4.576443449738875e-13, 5.157619764754665e-13, 7.547611350953959e-13], [1.92020746365668e-14, -5.449416353756716e-13, -1.590792562563853e-13, 4.33702030584526e-14, -8.82302222525009e-14, -1.114051399173229e-13, 1.6975627189482114e-12, -1.719909960982147e-13], [2.0630193422913488, -0.07917972926812084, -0.6236742239329072, -1.390401085230892, -0.13700549813696325, 0.6506973773585427, 1.3115993021645282, 0.6601460324024713]]
    assert titles == ['.six_dof_rig_stewart.Last_Run.FL.U2', '.six_dof_rig_stewart.Last_Run.FL.U3', '.six_dof_rig_stewart.Last_Run.FL.U4']
    assert round(samplerate, 3) == round(10.0, 3)

    return None

def test_ReqFile():

    file_path = r'..\tests\file_result\Car_Sim_brake.req'
    data_obj = DataModel('test')
    data_obj.new_file(file_path, 'req')
    data_obj['req'].set_reqs_comps(
        ['213','213','213'],
        ['1', '2', '3'])
    '''
        chassis_displacements, chassis_displacements, chassis_displacements
        longitudinal, lateral, vertical
    '''
    data_obj['req'].read_file()
    data_obj['req'].set_select_channels([0,1,2])
    data_obj['req'].set_line_ranges([0,10])

    data = data_obj['req'].get_data()
    titles = data_obj['req'].get_titles()
    samplerate = data_obj['req'].get_samplerate()

    # print(data)
    # print(titles)
    # print(samplerate)

    assert data == [[-1500.0, -1467.45, -1434.9, -1402.34, -1369.79, -1337.24, -1304.69, -1272.14, -1239.58, -1207.03], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [436.543, 436.543, 436.543, 436.543, 436.543, 436.543, 436.543, 436.543, 436.543, 436.543]]
    assert titles == ['213.1', '213.2', '213.3']
    assert round(samplerate, 3) == round(511.9986892833554, 3)

    return None

def test_DataModelCompare():

    params = {
            'block_size': {'u':128, 'l':128},
            'hz_range'  : [0, 50],
            'docx_path' : r'..\tests\file_result\dmc_test.docx',
            'fig_path'  : r'..\tests\file_result\dmc_test',
        }
    res_path = r'..\tests\file_result\break_brake.res'
    data_obj = DataModel('test')
    data_obj.new_file(res_path, 'res')
    data_obj['res'].set_reqs_comps(
        ['ACC_FL','ACC_FL','ACC_FL','ACC_FR','ACC_FR','ACC_FR'],
        ['X','Y','Z','X','Y','Z'],
        )
    data_obj['res'].read_file()
    dmc_obj = DataModelCompare(data_obj)
    pdf_path = dmc_obj.run('res', 'res', params)
    print(pdf_path)
    os.popen(pdf_path)
    time.sleep(1)
    dmc_obj.remove_result_files(dmc_obj.set_key('res', 'res'))

    return None

def test_DataModelCompare_2():

    params = {
            'block_size': {'u':128, 'l':128},
            'hz_range'  : [0, 50],
            'docx_path' : r'..\tests\file_result\dmc_test.docx',
            'fig_path'  : r'..\tests\file_result\dmc_test',
            'nums'      : [3,2]
        }
    res_path = r'..\tests\file_result\break_brake.res'
    data_obj = DataModel('test')
    data_obj.new_file(res_path, 'res')
    data_obj['res'].set_reqs_comps(
        ['ACC_FL','ACC_FL','ACC_FL','ACC_FR','ACC_FR','ACC_FR'],
        ['X','Y','Z','X','Y','Z'],
        )
    data_obj['res'].read_file()
    dmc_obj = DataModelCompare(data_obj)
    pdf_path = dmc_obj.run('res', 'res', params, pdfType=2)
    print(pdf_path)
    os.popen(pdf_path)
    time.sleep(1)
    dmc_obj.remove_result_files(dmc_obj.set_key('res', 'res'))

    return None

def test_DataModelCompare_3():

    params = {
            'block_size': {'u':128, 'l':128},
            'hz_range'  : [0, 50],
            'docx_path' : r'..\tests\file_result\dmc_test.docx',
            'fig_path'  : r'..\tests\file_result\dmc_test',
        }
    res_path = r'..\tests\file_result\break_brake.res'
    data_obj = DataModel('test')
    data_obj.new_file(res_path, 'res')
    data_obj['res'].set_reqs_comps(
        ['ACC_FL','ACC_FL','ACC_FL','ACC_FR','ACC_FR','ACC_FR'],
        ['X','Y','Z','X','Y','Z'],
        )
    data_obj['res'].read_file()
    dmc_obj = DataModelCompare(data_obj)
    pdf_path = dmc_obj.run('res', 'res', params, pdfType=3)
    print(pdf_path)
    os.popen(pdf_path)
    time.sleep(1)
    dmc_obj.remove_result_files(dmc_obj.set_key('res', 'res'))

    return None


def test_DataModelPlot():

    params = {
            'block_size': 128,
            'hz_range'  : [0, 50],
            'docx_path' : r'..\tests\file_result\dmp_test.docx',
            'fig_path'  : r'..\tests\file_result\dmp_test',
        }
    res_path = r'..\tests\file_result\break_brake.res'
    data_obj = DataModel('test')
    data_obj.new_file(res_path, 'res')
    data_obj['res'].set_reqs_comps(
        ['ACC_FL','ACC_FL','ACC_FL','ACC_FR','ACC_FR','ACC_FR'],
        ['X','Y','Z','X','Y','Z'],
        )
    data_obj['res'].read_file()

    dmp_obj = DataModelPlot(data_obj)
    pdf_path = dmp_obj.run('res', params)
    print(pdf_path)
    os.popen(pdf_path)
    time.sleep(1)
    dmp_obj.remove_result_files(dmp_obj.set_key('res'))

    return None

def test_DataModelPlot_2():

    params = {
            'block_size': 128,
            'hz_range'  : [0, 50],
            'docx_path' : r'..\tests\file_result\dmp_test.docx',
            'fig_path'  : r'..\tests\file_result\dmp_test',
            'nums'      : [3,2],
        }
    res_path = r'..\tests\file_result\break_brake.res'
    data_obj = DataModel('test')
    data_obj.new_file(res_path, 'res')
    data_obj['res'].set_reqs_comps(
        ['ACC_FL','ACC_FL','ACC_FL','ACC_FR','ACC_FR','ACC_FR'],
        ['X','Y','Z','X','Y','Z'],
        )
    data_obj['res'].read_file()

    def test_data_cal(data):
        return [[value for value in line] for line in data]

    data_obj['res'].set_data_func(test_data_cal)

    dmp_obj = DataModelPlot(data_obj)
    pdf_path = dmp_obj.run('res', params, pdfType=2)
    print(pdf_path)
    os.popen(pdf_path)
    time.sleep(1)
    dmp_obj.remove_result_files(dmp_obj.set_key('res'))

    return None

def test_DataModelScatter():

    params = {
            'docx_path' : r'..\tests\file_result\dms_test.docx',
            'fig_path'  : r'..\tests\file_result\dms_test',
            'xchannels' : [0,1],
            'ychannels' : None,
            'nums'      : [3,2],
        }
    res_path = r'..\tests\file_result\break_brake.res'
    data_obj = DataModel('test')
    data_obj.new_file(res_path, 'res')
    data_obj['res'].set_reqs_comps(
        ['ACC_FL','ACC_FL','ACC_FL','ACC_FR','ACC_FR','ACC_FR'],
        ['X','Y','Z','X','Y','Z'],
        )
    data_obj['res'].read_file()

    dms_obj = DataModelScatter(data_obj)
    pdf_paths = dms_obj.run('res', params)
    for pdf_path in pdf_paths:
        print(pdf_path)
        os.popen(pdf_path)
    time.sleep(1)
    for xchannel in params['xchannels']:
        dms_obj.remove_result_files(dms_obj.set_key('res', [xchannel]))

    return None


if __name__ == '__main__':
    pass

    # test_ResFile()
    # test_CsvFile()
    # test_NumDataFile()
    # test_RspFile()
    # test_ReqFile()

    # test_DataModelCompare()
    # test_DataModelCompare_2()
    test_DataModelCompare_3()
    # test_DataModelPlot()
    # test_DataModelPlot_2()
    # test_DataModelScatter()