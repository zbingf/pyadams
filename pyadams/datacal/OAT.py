# encoding: utf-8
"""
    正交试验设计模块
"""
from itertools import groupby
from collections import OrderedDict
import os


def dataSplit(data):
    ds = []
    mb = [sum([k for m, k in data['mk'] if m <= 10]), sum([k for m, k in data['mk'] if m > 10])]
    for i in data['data']:
        if mb[1] == 0:
            ds.append([int(d) for d in i])
        elif mb[0] == 0:
            ds.append([int(i[n * 2:(n + 1) * 2]) for n in range(mb[1])])
        else:
            part_1 = [int(j) for j in i[:mb[0]]]
            part_2 = [int(i[mb[0]:][n * 2:(n + 1) * 2]) for n in range(mb[1])]
            ds.append(part_1 + part_2)
    return ds


class OAT(object):
    def __init__(self, OAFile=os.path.split(os.path.realpath(__file__))[0] + '/data/ts723_Designs.txt'):
        """
        初始化解析构造正交表对象，数据来源：http://support.sas.com/techsup/technote/ts723_Designs.txt
        """
        self.data = {}

        # 解析正交表文件数据
        with open(OAFile, ) as f:
            # 定义临时变量
            key = ''
            value = []
            pos = 0

            for i in f:
                i = i.strip()
                if 'n=' in i:
                    if key and value:
                        self.data[key] = dict(pos=pos,
                                              n=int(key.split('n=')[1].strip()),
                                              mk=[[int(mk.split('^')[0]), int(mk.split('^')[1])] for mk in key.split('n=')[0].strip().split(' ')],
                                              data=value)
                    key = ' '.join([k for k in i.split(' ') if k])
                    value = []
                    pos += 1
                elif i:
                    value.append(i)

            self.data[key] = dict(pos=pos,
                                  n=int(key.split('n=')[1].strip()),
                                  mk=[[int(mk.split('^')[0]), int(mk.split('^')[1])]for mk in key.split('n=')[0].strip().split(' ')],
                                  data=value)
        self.data = sorted(self.data.items(), key=lambda i: i[1]['pos'])

    def get(self, mk):
        """
        传入参数：mk列表，如[(2,3)],[(5,5),(2,1)]

        1. 计算m,n,k
        m=max(m1,m2,m3,…)
        k=(k1+k2+k3+…)
        n=k1*(m1-1)+k2*(m2-1)+…kx*x-1)+1

       2. 查询正交表
        这里简单处理，只返回满足>=m,n,k条件的n最小数据，未做复杂的数组包含校验
        """
        mk = sorted(mk, key=lambda i: i[0])

        m = max([i[0] for i in mk])
        k = sum([i[1] for i in mk])
        n = sum([i[1] * (i[0] - 1) for i in mk]) + 1
        query_key = ' '.join(['^'.join([str(j) for j in i]) for i in mk])

        for data in self.data:
            # 先查询是否有完全匹配的正交表数据
            if query_key in data[0]:
                return dataSplit(data[1])
            # 否则返回满足>=m,n,k条件的n最小数据
            elif data[1]['n'] >= n and data[1]['mk'][0][0] >= m and data[1]['mk'][0][1] >= k:
                return dataSplit(data[1])
        # 无结果
        return None

    def genSets(self, params, mode=0, num=1):
        """
        传入测试参数OrderedDict，调用正交表生成测试集
        mode:用例裁剪模式，取值0,1
            0 宽松模式，只裁剪重复测试集
            1 严格模式，除裁剪重复测试集外，还裁剪含None测试集(num为允许None测试集最大数目)
        """
        sets = []
        mk = [(k, len(list(v)))for k, v in groupby(params.items(), key=lambda x:len(x[1]))]
        data = self.get(mk)
        for d in data:
            # 根据正则表结果生成测试集
            q = OrderedDict()
            for index, (k, v) in zip(d, params.items()):
                try:
                    q[k] = v[index]
                except IndexError:
                    # 参数取值超出范围时，取None
                    q[k] = None
            if q not in sets:
                if mode == 0:
                    sets.append(q)
                elif mode == 1 and (len(list(filter(lambda v: v is None, q.values())))) <= num:
                    # 测试集裁剪,去除重复及含None测试集
                    sets.append(q)
        return sets


def cal_oat(var_tuples):

    oat = OAT()

    n_var = len(var_tuples)
    n_cal = len(var_tuples[0][1])
    cal_tuples = []
    for n in range(n_var):
        cal_tuples.append((n, list(range(n_cal))))
    
    od = OrderedDict(cal_tuples)
    od_res = oat.genSets(od, mode=0)
    # 参数确认
    keys = []
    results = {}
    for line in od_res:
        new_line = []
        for n in line:
            if line[n]==None:
                new_line.append(1)
            else:
                new_line.append(line[n])

        str1 = '_'.join([str(value) for value in new_line])
        keys.append(str1)

        list1 = [var_tuples[loc][1][value] for loc, value in enumerate(new_line)]
        results[str1] = list1

    return keys, results


if __name__ == "__main__":
    oat = OAT()
    case1 = OrderedDict([('K1', [0, 1]),
                         ('K2', [0, 1]),
                         ('K3', [0, 1])])

    case2 = OrderedDict([('A', ['A1', 'A2', 'A3']),
                         ('B', ['B1', 'B2', 'B3', 'B4']),
                         ('C', ['C1', 'C2', 'C3']),
                         ('D', ['D1', 'D2'])])

    case3 = OrderedDict([(u'对比度', [u'正常', u'极低', u'低', u'高', u'极高']),
                         (u'色彩效果', [u'无', u'黑白', u'棕褐色', u'负片', u'水绿色']),
                         (u'感光度', [u'自动', 100, 200, 400, 800]),
                         (u'白平衡', [u'自动', u'白炽光', u'日光', u'荧光', u'阴光']),
                         (u'照片大小', ['5M', '3M', '2M', '1M', 'VGA']),
                         (u'闪光模式', [u'开', u'关'])])

    case4 = OrderedDict([('A', ['A1', 'A2', 'A3', 'A4', 'A5', 'A6']),
                         ('B', ['B1']),
                         ('C', ['C1'])])

    # # 默认mode=0，宽松模式，只裁剪重复测试集（测试用例参数值可能为None）
    # print (json.dumps(oat.genSets(case1)))
    # print (json.dumps(oat.genSets(case2)))
    # print (json.dumps(oat.genSets(case3), ensure_ascii=False))
    # print (json.dumps(oat.genSets(case4)))

    # # mode=1，严格模式，除裁剪重复测试集外，还裁剪含None测试集(num为允许None测试集最大数目)
    # print (json.dumps(oat.genSets(case4, mode=1, num=0)))
    # print (json.dumps(oat.genSets(case4, mode=1, num=1)))
    # print (json.dumps(oat.genSets(case4, mode=1, num=2)))
    # print (json.dumps(oat.genSets(case4, mode=1, num=3)))

    var_tuples = [
        (0,[10,11,32,43]),
        (1,[20,21,32,43]),
        (2,[30,31,32,43]),
        (3,[40,41,32,43]),
        (4,[50,51,32,43]),
    ]
    print(cal_oat(var_tuples))
    