"""
    检查对车架的力，参考坐标是否接地
    adm读取
    仅仅适用于 request force 数据获取
"""

import re
from pyadams.file import admfile

import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


class ReferenceMarkCHeck:

    def __init__(self, adm_path):

        self.adm_obj = admfile.AdmCar(adm_path)


    def reference_mark_check(self, target_str='to_frame_force', target_part_name='ground'):
        """
            reqyest 参考坐标判定
        """
        car_obj = self.adm_obj
        target_str = re.sub(r'\s', '', target_str).lower()
        target_part_name = re.sub(r'\s', '', target_part_name).lower()

        adm_obj = car_obj.model
        if target_part_name not in adm_obj.part.keys():
            return '参考坐标所属部件全称 错误！！！'

        reqs = adm_obj.request.keys()
        reqs_true = []
        reqs_warning = []

        for req in reqs:
            if target_str in req:
                for line in adm_obj.request[req].cmdlist[:-1]:
                    line = re.sub(r'\s', '', line).upper()
                    if ',RM=' in line:
                        marker_num = int(line.split('=')[-1])
                        part_num = adm_obj.markernum[marker_num].part
                        str_line = req+': RM = ' + adm_obj.partnum[part_num].name
                        if part_num == adm_obj.part[target_part_name].num:
                            reqs_warning.append(str_line)
                        else:
                            reqs_true.append(str_line)

                    re_obj = re.match(r',\w+=\w+\(\d+,\d+,(\d+)\)',line)
                    re_obj2 = re.match(r',\w+=\w+\(\d+,\d+\)',line)
                    if re_obj:
                        ', F4 = FZ(82,108,82)'
                        marker_num = int(re_obj.group(1))
                        part_num = adm_obj.markernum[marker_num].part
                        # print()
                        str_line = req+': RM = ' + adm_obj.partnum[part_num].name +'  '+ line
                        if part_num == adm_obj.part[target_part_name].num:
                            reqs_warning.append(str_line)
                        else:
                            reqs_true.append(str_line)

                    if re_obj2:
                        ', F4 = FZ(82,108)'
                        str_line = req+': RM = 未设定参考坐标' +'  '+ line
                        # print(re_obj2.groups())
                        reqs_warning.append(str_line)

        if reqs_warning:
            strs_warning = '警告: \n' + '\n'.join(reqs_warning)
        else:
            strs_warning = '警告: \n' + '未搜寻到问题\n'

        strs_true = '其他目标项:\n' + '\n'.join(reqs_true)

        return strs_warning + '\n\n' + strs_true        


def test_ReferenceMarkCHeck():
    
    adm_path = r'..\tests\car_reqeust_check\CAR_brake_brake.adm'
    obj = ReferenceMarkCHeck(os.path.abspath(adm_path))
    res_str = obj.reference_mark_check('L_UCA', 'ground')
    print(res_str)


if __name__ == '__main__':

    test_ReferenceMarkCHeck()