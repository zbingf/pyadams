"""
	运行测试
	adm 运行
"""

import sys
import os

# 索引 pyadams 父目录
cae_path = os.path.dirname(os.path.abspath('..'))
sys.path.append(cae_path)

import pyadams.call.admrun as admrun
import pyadams.file.admfile as admfile
import pyadams.file.result as result
import pyadams.datacal.tscal as tscal
import pyadams.view.drv2cmd as drv2cmd


simtime = 10
samplerate = 512
n_start = 1027


reqs = []
for req in ['fl','FL_U','fr','FR_U','rl','RL_U','rr','RR_U']:
	for n in range(3):
		reqs.append(req)
comps = ['u2','u3','u4']*8



adm_path = os.path.join(cae_path,r'pyadams\code_test\six_dof_rig_stewart.adm')
rsp_path = os.path.join(cae_path,r'pyadams\code_test\adm\t5p99s_512Hz_1p5_50Hz.rsp')
drv_path = os.path.join(cae_path,r'pyadams\code_test\adm\t5p99s_512Hz_1p5_50Hz_7.DRV')

run_adm_path = os.path.join(cae_path,r'pyadams\code_test\adm\temp.adm')


# 目标数据读取
data,_,_ = result.rsp_read(rsp_path)

# 变更
admobj = admfile.AdmFile(adm_path)

# admobj.model.bushing['bus_fl_bus'].c = [1,1,1]
# admobj.model.bushing['bus_fr_bus'].c = [1,1,1]
# admobj.model.bushing['bus_rl_bus'].c = [1,1,1]
# admobj.model.bushing['bus_rr_bus'].c = [1,1,1]

admobj.model.bushing['bus_fl_bus'].ct = [1,1,1]  # N*mm / rad
admobj.model.bushing['bus_fr_bus'].ct = [1,1,1]
admobj.model.bushing['bus_rl_bus'].ct = [1,1,1]
admobj.model.bushing['bus_rr_bus'].ct = [1,1,1]
# admobj.model.bushing['bus_fl_bus'].k = [20,20,20]
# admobj.model.bushing['bus_fr_bus'].k = [20,20,20]
# admobj.model.bushing['bus_rl_bus'].k = [20,20,20]
# admobj.model.bushing['bus_rr_bus'].k = [20,20,20]

admobj.model.bushing['bus_fl_bus'].updata()
admobj.model.bushing['bus_fr_bus'].updata()
admobj.model.bushing['bus_rl_bus'].updata()
admobj.model.bushing['bus_rr_bus'].updata()



# admobj.model.part['part_point_mass'].mass = 114*0.95
# admobj.model.part['part_point_mass'].updata()
# print(dir(admobj.model.part['part_point_mass']))


admobj.updata()
admobj.newfile(run_adm_path)
respath = admrun.admrun(run_adm_path,simtime,samplerate)
resobj2 = result.ResFile(respath)
data2 = resobj2.data_request_get(reqs,comps)


nlen = len(data[0])
for line in data2:
	del line[:n_start]
	del line[nlen:]


# 数据对比
pdi = tscal.cal_pdi_relative(data2,data)
rms = tscal.cal_rms_delta_percent(data2,data)
# rms_percent = tscal.cal_rms_percent(data2,data)

pdi_str = ','.join([str(value) for value in pdi])
rms_str = ','.join([str(value) for value in rms])
# rms_percent_str = ','.join([str(value) for value in rms_percent])
print('\n'*2)
print(pdi_str)
print('\n'*2)
print(rms_str)
print('\n'*2)
# print(rms_percent_str)
# print('\n'*2)



# # 作图
# import matplotlib.pyplot as plt

# fig1 = plt.figure(1)
# for n in range(12):
# 	ax1 = fig1.add_subplot(4,3,n+1)
# 	ax1.plot(data[n],linewidth=0.5)
# 	ax1.plot(data2[n],linewidth=0.5)

# fig2 = plt.figure(2)
# for n in range(12,24):
# 	ax1 = fig2.add_subplot(4,3,n+1-12)
# 	ax1.plot(data[n],linewidth=0.5)
# 	ax1.plot(data2[n],linewidth=0.5)

# plt.show()
