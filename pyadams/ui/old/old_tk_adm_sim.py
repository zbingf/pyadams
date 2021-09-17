"""
	Adm模型仿真计算
	
	用于数值变更计算
	可进行多线程计算
	
	适用范围：
		1、View 模型仿真
		2、Car Ride&TILT 模型仿真
		3、Car Event 模型仿真
			Event仿真需要对adm文件加前缀，避免被覆盖：CAR_PREFIX = car_adm_sim_）

	2021.04.05
"""
from pyadams.call import admrun, threadingrun
from pyadams.file import admfile, result, file_edit, tkfile
from pyadams.datacal import tscal, freqcal, plot
from pyadams.view import drv2cmd
from pyadams.ui import tkui, tk_linear_regression, tk_reqcomp


# 第三方模块
import os, time, math, json, copy, re, threading, shutil
import matplotlib.pyplot as plt
import pysnooper


import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


# 函数赋予
DataModel = result.DataModel

linear_regression_ui = tk_linear_regression.linear_regression_ui

threading_car_files = threadingrun.threading_car_files
threading_sim_doe = threadingrun.threading_sim_doe

data2csv = file_edit.data2csv

TkUi = tkui.TkUi 							# TkUi 对象

# 字符串数据
PREFIX = 'view_sim_' 		# view类型计算,adm文件,前缀  view_adm_sim_
CAR_PREFIX = 'car_adm_sim_' 	# Car类型计算,adm文件, 前缀
TARGET_NAME = 'target' 			# 目标数据名称
CMDS_INIT = admfile.CMDS_INIT 	# AdmEdit模型,字符串命令格式
CMDS_STR_INIT = admfile.CMDS_STR_INIT


# ==========================================================
# request重组
def req_change(reqs,comps,isCommon=True): 
	"""
		reqs 	list 	request 
		comps 	list 	component
		isCommon bool 	是否批量设置

		批量设置表示，一个req对应一组comps
		可用于：
			六分力输出
	"""
	if isCommon: # request 批量设置
		new_reqs=[]
		for req in reqs:
			for n in range(len(comps)):
				new_reqs.append(req)
		new_comps = comps*len(reqs)
	else:
		new_reqs,new_comps = reqs,comps

	return new_reqs,new_comps


# ----------------------
# 单次分析计算模块-主要计算模块
def simcal(params): # adm仿真计算
	"""
		1、仿真计算
		2、对比数据

		params 为字典 dict 格式,至少包含以下:
		params = {
		'values' 		# 变量  列表一维 
		'samplerate'  	# 采样频率 
		'adm_path' 		# adm模型路径 str
		'drv_path' 		# drv 加载路径 str
		'isTsPlot' 		# 是否作时域图 boole

		'target_path' 	# 目标路径
		'target_req' 	# 目标 request 列表
		'target_comp' 	# 目标 comps	 列表	 
		'isTarCommon'	# 目标 req&comp是否批量设置
		'isLoad'		# 是否加载spline
		'isMultiSim'	# 是否进行批量计算
		'target_range'	# 目标数据阶段范围
		'res_range'		# 仿真数据阶段范围

		'isOutput' 		# 是否到处数据 csv格式 boole
		'isOutCommon'	# csv输出 req&comp是否批量设置
		'output_req' 	# csv输出 request 列表 
		'output_comp'	# csv输出 comp 列表 
		
		'spline_id' 	# 加载 spline id 列表[整数]
		'values_cmd'	# 
		
		'isAdams2019' 	# ADAMS计算版本 Ture 2019 False 2017.2
		
		'isHzPlot' 		# 
		'isReading' 	# 直接调用,不读取
		'isResDebug' 	# 直接读取,不计算
		'read_target_path' 	# 
		'loading_type'	# 后处理读取方式
		'isNotDelData' 	# 

		'nums_plot' 	# list [2,3] 	图片显示行列数
		'hz_range' 		# list [0,50] 	psd计算截取范围
		'ylabels' 		# list 	y坐标轴标示
		'block_size'  	# list 	psd计算设置，块尺寸	

		strs_cmd 		# str 	字符串变量具体设置
		strlocs			# list 	字符串变量位置
		strnums 		# list 	字符串各变量位置的个数 

		}
	"""
	values 		= params['values']
	samplerate 	= params['samplerate']
	adm_path 	= params['adm_path']
	drv_path 	= params['drv_path']
	isTsPlot 		= params['isTsPlot']
	target_path = params['target_path']
	target_req 	= params['target_req']	
	target_comp = params['target_comp']	
	isTarCommon = params['isTarCommon']
	isLoad 		= params['isLoad']
	isMultiSim	= params['isMultiSim']
	target_range= params['target_range']
	res_range 	= params['res_range']
	isOutput 	= params['isOutput']
	isOutCommon = params['isOutCommon']
	output_req 	= params['output_req']
	output_comp = params['output_comp']
	spline_id 	= params['spline_id']
	values_cmd 	= params['values_cmd']
	isAdams2019 = params['isAdams2019']
	isHzPlot 	= params['isHzPlot']
	isReading 	= params['isReading']					
	isResDebug 	= params['isResDebug'] 					
	read_target_path 	= params['read_target_path']
	loading_type 		= params['loading_type']		
	isNotDelData 		= params['isNotDelData'] 		
	nums_plot 	= params['nums_plot']
	hz_range 	= params['hz_range']
	ylabels 	= params['ylabels']
	block_size 	= params['block_size'] 	# list 	psd计算设置，块尺寸

	strs_cmd 	= params['strs_cmd'] 	# str 	字符串变量具体设置
	strlocs 	= params['strlocs'] 	# list 	字符串变量位置
	strnums 	= params['strnums'] 	# list 	字符串各变量位置的个数 

	res_channel = params['res_channel'] 	# [0,1,2,3,4,5] 通道截取
	target_channel = params['target_channel'] # [0,1,2,3,4,5] 通道截取

	sim_type = params['sim_type']

	legend = params['legend']


	# 版本选择
	adams_version = '2019' if isAdams2019 else '2017.2'

	# -----------------------
	# 判定adm类型，以便进行不同方式的调用
	# car 或者 view
	# 生成 adm_sim_path
	filedir, name = os.path.split(adm_path) # 分解adm路径
	if sim_type == 3:
		# Car 模型计算
		# 创建新的文件夹
		filedir, name = os.path.split(adm_path)
		adm_sim_path = os.path.join(filedir, name.split(CAR_PREFIX)[-1] )

	else:
		# view模型
		# view模型 计算，在原有adm_path 基础上加前缀及后缀
		filedir, name = os.path.split(adm_path)
		adm_sim_path = file_edit.rename_filepath( os.path.join(filedir, PREFIX+name) )
		

	# -----------------------

	# -----------------------
	# adm编辑模块
	# 根据AdmEdit解析及更改
	# 判断是否进行台架spline加载
	admobj = admfile.AdmCar(adm_path)  # AdmCar实例
	if values:# 数值变量
		# 若values不为空则，不对数据进行更改
		editobj = admfile.AdmEdit(admobj)	# 编辑Adm文件
		admobj 	= editobj.edit(values_cmd,values)
	
	if strlocs: # 字符串变量
		str_loc_dic = {}
		for num,loc in enumerate(strlocs):
			str_loc_dic[num] = loc
			# 	num 变量编号 	loc 变量所指向的字符串位置
			# eg : [8] = 1  变量编号8 的 第1个字符串
		editobj.read_str(strs_cmd)
		admobj 	= editobj.edit_str(str_loc_dic)

	if isLoad: # 判断台架是否加载
		DataModel('drv',drv_path)
		drv_data = DataModel.get_data('drv')
		xlist = [n/samplerate[1] for n in range(len(drv_data[0]))] # 目标信号的采样频率,生成上的时间
		for num,nid in enumerate(spline_id):
			admobj.model.splinenum[nid].updata(xlist,drv_data[num])
	
	admobj.updata() 				# 模型更新
	admobj.newfile(adm_sim_path) 	# 生成新adm仿真文件
	# -----------------------

	# -----------------------
	# 对比目标数据读取
	data_model_read(TARGET_NAME, target_path, target_req, target_comp, 
		loading_type, isTarCommon, admobj, isNotDelData, isReading=True)

	DataModel.channels[TARGET_NAME] = target_channel
	DataModel.nranges[TARGET_NAME] = target_range
	target_data = DataModel.get_data(TARGET_NAME)
	# -----------------------

	# -----------------------
	# Adm调用计算

	# DataModel.names 名称设置
	if not isMultiSim: # DataModel 名称
		res_name = 'single'
	else:
		num = sum([1 for name in DataModel.names if 'multi_'==name[:6]])
		res_name = f'multi_{num}'
		if name not in DataModel.names: # 是否读取过
			DataModel.names.append(res_name)
		else:
			logger.warning(f'DataModel.names 中已存在{name},数据读取进行覆盖')

	# Adm仿真-后台调用计算
	if isResDebug or isReading: # 读取已有res文件不进行计算, 直接调用也不用计算
		res_path = read_target_path 	# 直接调用
	else:
		# 根据sim_type，判定adm不同运行模式
		if sim_type == 3: # 整车 Event计算
			if isMultiSim: # 多线程计算
				DataModel.n_threading += 1
				# 重新定义 amd_sim_path  , 复制到子目录
				adm_sim_path,_ = threading_car_files(adm_sim_path, DataModel.n_threading)
			else:
				# 单个计算
				filedir, name = os.path.split(adm_sim_path)
				base_name = '.'.join(name.split('.')[:-1])
				new_filedir = os.path.join(filedir,base_name)
				# 文件夹重命名,加后缀
				new_filedir, num = file_edit.rename_filedir(new_filedir)
				# 创建文件夹
				# file_edit.create_dir(new_filedir)
				# 复制文件到文件夹
				adm_sim_path,_ = threading_car_files(adm_sim_path, num, base_name)

			res_path = admrun.admrun_car(adm_sim_path, version=adams_version)		

		else: # view 运行
			if isLoad: # drv加载
				# 仿真时常根据加载定义
				sim_time = int(len(drv_data[0])/samplerate[0])
			else: # 根据target数据定义
				sim_time = len(target_data[0])/samplerate[0]
			res_path = admrun.admrun(adm_sim_path, sim_time, samplerate[0], version=adams_version)
	# -----------------------

	# -----------------------
	# 仿真数据读取 res
	data_model_read(res_name, res_path, target_req, target_comp, 
		loading_type, isTarCommon, admobj, isNotDelData, isReading)

	DataModel.values[res_name] = values
	DataModel.nranges[res_name] = res_range
	DataModel.channels[res_name] = res_channel
	res_data = DataModel.get_data(res_name)
	# -----------------------

	# -----------------------
	# output 数据导出
	# output 与res文件共用数值截取范围
	if isOutput : 	# csv-数据输出
		reqs_out, comps_out = req_change(output_req, output_comp, isCommon=isOutCommon)
		if loading_type==3:
			reqs_out, comps_out = admobj.model.get_req_comp(reqs_out,comps_out)
		# 读取文件
		output_data = DataModel.data_range(
			DataModel.objs[res_name].data_request_get(reqs_out, comps_out, isSave=False),
			DataModel.nranges[res_name],)

		csv_path = adm_sim_path[:-3]+'csv'
		reqs_out, comps_out = req_change(output_req, output_comp, isCommon=isOutCommon) # 重新拼接，避免req的数值标题
		data2csv(csv_path, output_data, reqs_out, comps_out)
	# -----------------------

	# -----------------------
	# 图像显示
	# if isTsPlot: # 图片输出
	if not ylabels or ylabels==None:
		ylabels=None
	else:
		if target_channel and target_channel != None:
			ylabels = [ylabels[n] for n in target_channel]
	plot.plot_ts_hz(res_data, target_data, samplerate, 
		isShow=True,isHzPlot=isHzPlot,isTsPlot=isTsPlot,
		nums=nums_plot,block_size=block_size,
		ylabels=ylabels, hz_range=hz_range, figpath=res_path[:-4],legend=legend.reverse() )

	# -----------------------

	# -----------------------
	# 文本当存储
	compare_dic = DataModel.compare(res_name, TARGET_NAME)
	target_reqs1, target_comps1 = req_change(target_req, target_comp, isCommon=isTarCommon)
	single_res(adm_sim_path+'.txt', target_reqs1, target_comps1, values, compare_dic)
	# -----------------------

	# -----------------------
	# 释放内存
	if not isNotDelData:
		DataModel.del_data_full(res_name)
		DataModel.del_data_full(TARGET_NAME)
	# -----------------------

	# 返回对比文件
	return compare_dic

# ------------ 后处理 ------------
# @pysnooper.snoop()
def multi_res(csv_path, dic1, values, reqs, comps): # 多进程计算后处理
	"""
		csv_path 	文件路径
		dic1 	DataMode.compares 	后处理数据
		values 	DataMode.values  	后处理数值
		reqs 	DataMode.reqs 			
		comps 	DataMode.comps 		
	"""
	for n in range(len(reqs)):
		reqs[n] = str(reqs[n])
		comps[n] = str(comps[n])

	listgain = lambda list1,gain : [n*gain for n in list1]
	listsubt = lambda list1,a : [n-a for n in list1]
	listround = lambda list1,n: [round(v,n) for v in list1] 	# 数值列表数据，四舍五入
	list2str = lambda list1: ','.join([str(n) for n in list1]) 	# 逗号拼接字符串

	# 列表-删除
	def list_division(list1, list2):
		result = []
		for n1,n2 in zip(list1,list2):
			n1 = round(n1,2) + 0.01
			n2 = round(n2,2) + 0.01
			result.append(n1/n2)

		return result

	compares, names = {}, []
	for name in values:
		if 'multi_' in name: # 仿真名称
			names.append(name)
			compares[name] = dic1[(name,'target')]

	keys = list(compares[names[0]].keys())
	keys.reverse()
	names.sort()

	xs, ys = [], []
	nlen = len(keys)
	for name in names: # 
		v = values[name]
		xs.append(v)
		xlen = len(v)
		ytemp = []
		for key in keys:
			c = compares[name][key]
			ylen = len(c)
			ytemp.extend(c)

		ys.append(ytemp)

	# csv path 文件路径
	f = open(csv_path, 'w') # 写入
	# 原始数据
	f.write('原数据对比\n')
	title1 = ','*(xlen-1) + ',' + ','.join([key+','*(ylen-1) for key in keys])
	f.write(title1+'\n')
	title2 = ','.join([f'变量{n}' for n in range(xlen)]) + ',' +\
		','.join([','.join([f'{reqs[n]}.{comps[n]}' for n in range(ylen)]) for n1 in range(nlen)])
		# 
	# print(ylen)
	# print(len(reqs))
	f.write(title2+'\n')

	for x,y in zip(xs,ys):
		# list1 = []
		# list1.extend(x)
		# list1.extend(y)
		list1 = x+y
		list1 = listround(list1,3)
		f.write(list2str(list1)+'\n')

	# 百分比数据
	f.write('\n'*2)
	f.write('百分比\n')
	f.write(title1+'\n')
	f.write(title2+'\n')
	# print(xs,ys)
	for x,y in zip(xs,ys):
		# list1 = []
		# print(x,y)
		# print(x,xs[0])
		# print(list_division(x, xs[0]))
		# print(listgain(list_division(x, xs[0]), 100))
		# print(listsubt(listgain(list_division(x, xs[0]), 100), 100))
		new_x = listsubt(listgain(list_division(x, xs[0]), 100), 100)
		new_y = listsubt(listgain(list_division(y, ys[0]), 100), 100)
		# list1.extend(new_x)
		# list1.extend(new_y)
		# print(list1)
		list1 = new_x+new_y
		list1 = listround(list1,3)

		f.write(list2str(list1)+'\n')
	
	f.close() #关闭文件

	y_names = [n1+'.'+n2 for n1,n2 in zip(reqs, comps)]

	return xs, ys, y_names, keys


def single_res(filepath, reqs, comps, values, compare_dic): # 单词后处理数据转化为字符串
	"""
		filepath 存储路径
		reqs 	list
		comps 	list 
		values 	list 一组
		compare_dic dict 结果数据

		主要输出：
			pdi 及 drms 数据输出
	"""
	# print('\n\n\n')
	# print(compare_dic)
	pdi,drms = compare_dic['pdi'],compare_dic['drms']
	for n in range(len(reqs)):
		reqs[n] = str(reqs[n])
		comps[n] = str(comps[n])

	floats2str = lambda list1:','+','.join([str(n) for n in list1])
	# 字符串转化
	title = [req+'_'+comp for req,comp in zip(reqs,comps)]
	title_str = ','+','.join(title)
	pdi_str = floats2str(compare_dic['pdi'])
	drms_str = floats2str(compare_dic['drms'])
	rms_str = floats2str(compare_dic['rms'])
	max_str = floats2str(compare_dic['max'])
	min_str = floats2str(compare_dic['min'])
	rain_pdi_str = floats2str(compare_dic['rain_pdi'])

	result_str = '\n'.join([',title'+title_str, 'pdi'+pdi_str, 'drms'+drms_str,
		'max'+max_str,'min'+min_str, 'rain_pdi'+rain_pdi_str])
	print(result_str)

	# 计算结果记录
	with open(filepath,'w') as f:
		f.write(','.join([str(n) for n in values]))
		f.write('\n')
		f.write(result_str)

	return result_str

# ------------ run_cal 主程序 ------------ 
def run_cal(params):

	if params['loading_type']==3:
		admobj = admfile.AdmCar(params['adm_path'])
	else:
		admobj = None
	data_model_read(TARGET_NAME, params['target_path'], params['target_req'], params['target_comp'], 
		params['loading_type'], params['isTarCommon'], admobj, isNotDelData=False, isReading=True)
	DataModel.channels[TARGET_NAME] = params['target_channel']

	DataModel.target_req, DataModel.target_comp = req_change(params['target_req'], params['target_comp'], 
		isCommon=params['isTarCommon'])


	if params['isMultiSim']: # 多进程计算
		'多进程计算'
		assert params['values'] , 'values 数据为空，终止多线程计算'
		t_start = time.time()
		# 多线程灵计算
		new_func = threadingrun.threading_func(simcal)
		threading_sim_doe(new_func, params, sim_range=params['var_range'])
		# 数据保存
		data = {
			'compares':DataModel.compares,
			'values':DataModel.values,
			'target_req':DataModel.target_req,
			'target_comp':DataModel.target_comp,
			'paths':DataModel.paths,
			'result_compares':DataModel.result_compares,
		}
		file_edit.var_save(params['adm_path'][:-4], {'DataModel':data})
		# 分析时长计时
		t_end = time.time()-t_start
		logger.info( ('\n'+ '*'*50)*2 + '\n' +\
			f'计算所用时间 : {round(t_end)} s ' +\
			('\n'+ '*'*50)*2 )

		# 后处理数据输出
		xs, ys, y_names, keys = multi_res(params['csv_path'], DataModel.compares,
			DataModel.values, DataModel.target_req, DataModel.target_comp)
		
		# 灵敏度分析
		linear_regression_ui(xs[0], xs, ys, y_names=y_names, y_repeats=keys)

	else: # 单个计算
		'当个计算'
		t_start = time.time()
		simcal(params) 	# 运算
		t_end = time.time()-t_start

		logger.info( ('\n'+ '*'*50)*2 + '\n' +\
			f'计算所用时间 : {round(t_end)} s ' +\
			('\n'+ '*'*50)*2 )

		# 数据保存
		data = {
			'compares':DataModel.compares,
			'values':DataModel.values,
			'target_req':DataModel.target_req,
			'target_comp':DataModel.target_comp,
			'paths':DataModel.paths,
			'result_compares':DataModel.result_compares,
		}
		file_edit.var_save(params['adm_path'][:-4], {'DataModel':data})

# ------------ 模型读取 ------------
def data_model_read(target_name, target_path, target_req, target_comp, 
	loading_type, isTarCommon, admobj, isNotDelData, isReading):
	"""
		logding_type 加载类型  1 req读取 ; 2 res读取 ; 3 adm输入,req读取
		isTarCommon 	req和comps批量组合
		admobj 		AdmCar的实例
		isNotDelData 保留完整数据
		isReading 	直接调用
	"""

	# DataModel 读取数据
	target_reqs, target_comps = req_change(target_req, target_comp, isCommon=isTarCommon)
	if target_path[-3:].lower() in ['res','req']:
		if loading_type==1:
			# req读取
			new_target_path = target_path[:-3]+'req'
		elif loading_type==2:
			# res读取
			new_target_path = target_path[:-3]+'res'
		elif loading_type==3:
			# res的request输入, req读取
			new_target_path = target_path[:-3]+'req'
			target_reqs, target_comps = admobj.model.get_req_comp(target_reqs, target_comps)
	else:
		new_target_path = target_path

	# if not isReading:
	# 	# 重新调用,以便于request重新设置
	# 	DataModel(target_name, new_target_path, target_reqs, target_comps) # 数据读取

	if target_name not in DataModel.names or isNotDelData or not isReading: 
		# target若已经读取则不再进行读取 or 数据完整无删除,进行读取 or 重新调用
		try:
			DataModel(target_name, new_target_path, target_reqs, target_comps)
		except:
			# print(target_name,new_target_path,target_reqs,target_comps)
			logger.info(f'"{target_name}" : 切换成res读取')
			target_reqs, target_comps = req_change(target_req, target_comp,
				isCommon=isTarCommon)
			DataModel(target_name, target_path[:-3]+'res', target_reqs, target_comps)

# ----------------------
# UI模块
class AdmSimUi(TkUi):
	"""
		AdmSim 主程序
	"""
	def __init__(self,title):

		super().__init__(title)
		str_label = '-'*40

		self.frame_entry({
			'frame':'values', 'var_name':'values', 'label_text':'变量(列表)',
			'label_width':15, 'entry_width':30,
			})

		self.frame_entry({
			'frame' : 'var_range', 'var_name':'var_range', 'label_text' : '变量调整比例范围',
			'label_width' : 15, 'entry_width' : 30,
			})

		self.frame_entry({
			'frame':'var_range','var_name':'samplerate','label_text':'采样频率 Hz',
			'label_width':15,'entry_width':30,
			})

		self.frame_loadpath({
			'frame':'adm_path', 'var_name':'adm_path', 'path_name':'adm file',
			'path_type':'.adm', 'button_name':'adm load',
			'button_width':15, 'entry_width':30,
			})

		self.frame_radiobuttons({
			'frame':'sim_type',
			'var_name':'sim_type',
			'texts':['view', 'car四立柱ride', 'car整车Event'],
			})

		self.frame_loadpath({
			'frame':'drv_path', 'var_name':'drv_path', 'path_name':'drv file',
			'path_type':'.drv', 'button_name':'drv load',
			'button_width':15, 'entry_width':30,
			})

		self.frame_check_entry({
			'frame':'drv_path', 'check_text':'spline ID', 'check_var':'isLoad',
			'entry_var':'spline_id', 'entry_width':30,
			})

		self.frame_radiobuttons({
			'frame':'loading_type',
			'var_name':'loading_type',
			'texts':['req读取方式', 'res读取方式', '通过adm读取req'],
			})

		self.frame_check_entry({
			'frame':'isResDebug', 'check_text':'不计算直接读取：', 
			'check_var':'isResDebug', 'entry_var':'read_target_path',
			'entry_width':30,
			})

		self.frame_entry({
			'frame':'channel_set', 'var_name':'res_channel', 'label_text':'仿真-通道截取',
			'label_width':15, 'entry_width':30,
			})
		self.frame_entry({
			'frame':'channel_set', 'var_name':'target_channel', 'label_text':'目标-通道截取',
			'label_width':15, 'entry_width':30,
			})

		self.frame_label_only({'label_text':f'{str_label}后处理-读取设置{str_label}','label_width':50})

		self.frame_loadpath({
			'frame':'target_path','var_name':'target_path', 
			'path_name':'target file', 'path_type':'*.*',
			'button_name':'目标数据加载',
			'button_width':15, 'entry_width':30,
			})
		
		self.frame_entry({
			'frame':'target_req', 'var_name':'target_req', 'label_text':'仿真&目标 req',
			'label_width':15, 'entry_width':30,
			})

		self.frame_entry({
			'frame':'target_comp', 'var_name':'target_comp', 'label_text':'仿真&目标 comp',
			'label_width':15, 'entry_width':30,
			})

		self.frame_checkbutton({
			'frame':'target_comp', 'var_name':'isTarCommon', 'check_text':'目标Req是否批量组合',
			})

		self.frame_entry({
			'frame':'ranges', 'var_name':'res_range', 'label_text':'仿真-数据截取',
			'label_width':15, 'entry_width':30,
			})

		self.frame_entry({
			'frame':'ranges',	'var_name':'target_range', 'label_text':'目标-数据截取',
			'label_width':15, 'entry_width':30,
			})
		
		self.frame_label_only({'label_text':f'{str_label}output 时域数据 导出设置{str_label}','label_width':50})

		self.frame_entry({
			'frame':'output_req', 'var_name':'output_req', 'label_text':'Output Req',
			'label_width':15, 'entry_width':30,
			})

		self.frame_entry({
			'frame':'output_comp','var_name':'output_comp','label_text':'Output Comp',
			'label_width':15,'entry_width':30,
			})

		self.frame_checkbutton({
			'frame':'output_req', 'var_name':'isOutput', 'check_text':'Output 是否输出数据',
			})

		self.frame_checkbutton({
			'frame':'output_comp', 'var_name':'isOutCommon', 'check_text':'Output Req 是否批量组合 ',
			})

		self.frame_button({
			'frame':'reqcomp_ui',
			'button_name':'reqs comps 辅助生成',
			'button_width':30,
			'func':self.fun_reqcomp_ui,
			})

		self.frame_label_only({'label_text':f'{str_label}计算设置{str_label}','label_width':50})

		self.frame_checkbuttons({
			'frame' : 'checks2',
			'vars' : ['isMultiSim','isAdams2019','isNotDelData', 'isReading'],
			'check_texts' : ['是否批量计算','ADAMS版本是否是：2019','保留完整数据', '直接调用不再读取'],
			})
		
		self.frame_savepath({
			'frame' : 'csv_path', 'var_name':'csv_path', 'path_name' : 'csv file',
			'path_type' : '.csv', 'button_name' : '批量计算 csv',
			'button_width' : 15, 'entry_width' : 30,
			})

		self.frame_label_only({'label_text':f'{str_label}作图设置{str_label}','label_width':50})

		self.frame_checkbuttons({
			'frame' : 'plot1',
			'vars' : ['isTsPlot','isHzPlot',],
			'check_texts' : ['是否作时域图','是否作频域图'],
			})
		
		self.frame_entry({
			'frame':'plot1', 'var_name':'nums_plot', 'label_text':'|nums_plot|',
			'label_width':9, 'entry_width':10,
			})

		self.frame_entry({
			'frame':'plot1', 'var_name':'block_size', 'label_text':'|block_size|',
			'label_width':9, 'entry_width':10,
			})

		self.frame_entry({
			'frame':'plot1', 'var_name':'hz_range', 'label_text':'|Hz_range|',
			'label_width':9, 'entry_width':10,
			})
		
		self.frame_entry({
			'frame':'plot3', 'var_name':'ylabels', 'label_text':'ylabels',
			'label_width':15, 'entry_width':20,		
			})
		self.frame_entry({
			'frame':'plot3', 'var_name':'legend', 'label_text':'legend',
			'label_width':15, 'entry_width':10,		
			})
		
		
		self.frame_buttons_RWR({
			'frame' : 'rrw',
			'button_run_name' : '运行',
			'button_write_name' : '保存',
			'button_read_name' : '读取',
			'button_width' : 15,
			'func_run' : self.fun_run,
			})

		self.frame_note()

		self.frame_label_only({'label_text':f'{str_label}数值变量编辑{str_label}','label_width':50})

		self.frame_button({
			'frame':'values_cmd', 
			'button_name':'数值变量编辑', 'button_width':15,
			'func':self.fun_values_cmd_set,
			})
		self.frame_text_lines({
			'frame':'values_cmd',
			'text_name':'values_cmd',
			'text_width':80, 'text_height':2,
			})
	

		self.frame_label_only({'label_text':f'{str_label}字符串变量编辑{str_label}','label_width':50})
		
		self.frame_entry({
			'frame':'strlocs', 'var_name':'strlocs', 'label_text':'字符串变量位置',
			'label_width':15, 'entry_width':20,
			})
		self.frame_entry({
			'frame':'strlocs', 'var_name':'strnums', 'label_text':'字符串各变量位置的个数',
			'label_width':20, 'entry_width':20,
			})

		self.frame_button({
			'frame':'strs_cmd', 
			'button_name':'字符串变量编辑', 'button_width':15,
			'func':self.fun_strs_cmd_set,
			})
		self.frame_text_lines({
			'frame':'strs_cmd',
			'text_name':'strs_cmd',
			'text_width':80, 'text_height':2,
			})

		self.frame_button({
			'frame':'file_remove',
			'button_name':'删除adm路径生成的文件',
			'button_width':30,
			'func':self.fun_file_remove,
			})
		
		self.frame_entry({
			'frame':'file_remove', 'var_name':'file_prefix', 'label_text':'前缀',
			'label_width':10, 'entry_width':15,		
			})

		self.frame_entry({
			'frame':'file_remove', 'var_name':'file_postfix', 'label_text':'后缀',
			'label_width':10, 'entry_width':15,		
			})

		self.frame_button({
			'frame':'pycmd', 
			'button_name':'py字符串命令编辑', 'button_width':15,
			'func':self.fun_pycmd_set,
			})
		self.frame_text_lines({
			'frame':'pycmd', 'text_name':'pycmd', 'text_width':80,'text_height':2,
			})

		self.frame_button({
			'frame':'fun_pycmd', 'button_name':'Py命令运行', 'button_width':30,
			'func':self.fun_pycmd,
			})


		# 初始化设置
		self.set_text('values_cmd',CMDS_INIT)
		self.set_text('strs_cmd',CMDS_STR_INIT)
		self.vars['target_channel'].set('None')
		self.vars['res_channel'].set('None')
		self.vars['block_size'].set('1024,1024')
		self.vars['nums_plot'].set('2,3')
		self.vars['hz_range'].set('0,50')
		self.vars['spline_id'].set('1,2,3,4')
		self.vars['res_range'].set('None,None')
		self.vars['target_range'].set('None,None')
		self.vars['samplerate'].set('256,256')
		self.vars['file_prefix'].set(PREFIX)
		self.vars['file_postfix'].set('None')
		self.vars['legend'].set('对比目标,仿真')
		# self.run()

	def fun_run(self):
		"""
			运行按钮调用函数
			主程序
		"""
		# 获取界面数据
		params = self.get_vars_and_texts()
		logger.info(f'params数据:\n{params}\n')

		# 非空 且 非列表格式, 将数据转化为列表
		if not isinstance(params['values'], list) and params['values']: params['values'] = [params['values'],]
		if not isinstance(params['target_req'], list): params['target_req'] = [params['target_req']]
		if not isinstance(params['target_comp'], list): params['target_comp'] = [params['target_comp']]
		if not params['isReading']: DataModel.set_init() # 若不是直接调用,则进行初始化

		run_cal(params)

		return True

	def fun_file_remove(self):
		"""
			移除数据
			删除adm_path同路径文件夹内数据
		"""
		params = self.get_vars_and_texts()
		if tkfile.ask('确认-是否删除'):
			try:
				adm_path = params['adm_path']			# adm路径
				if not adm_path:
					self.print('adm_path无-未删除')
					return False
				file_prefix = params['file_prefix']		# 前缀
				file_postfix = params['file_postfix']	# 后缀
				# print(file_prefix, file_postfix, type(file_postfix))
				path = os.path.dirname(adm_path)
				file_edit.file_remove(path, prefix=file_prefix, suffix=file_postfix)
				self.print('文件删除完成')
			except:
				self.print('文件删除失败！！！')
		else:
			self.print('未删除')

	def fun_pycmd(self):
		"""
			python命令运算
		"""
		cmd = self.get_text('pycmd')
		exec(cmd)

	def fun_reqcomp_ui(self):

		tk_reqcomp.ReqComTxtUi('ReqsComps').run()

	def fun_values_cmd_set(self):
		# adm数值变量编辑
		text_data = self.get_text('values_cmd')

		obj1 = tkui.TextUi('adm数值变量编辑', text=text_data, label_text='Text')
		obj1.run()
		self.set_text('values_cmd', obj1.text_data)
		del obj1
		# self.set_text('values_cmd', text_data)

	def fun_strs_cmd_set(self):
		# adm字符串变量编辑
		text_data = self.get_text('strs_cmd')
		obj1 = tkui.TextUi('adm字符串变量编辑', text=text_data, label_text='Text')
		obj1.run()
		self.set_text('strs_cmd', obj1.text_data)
		del obj1
		
	def fun_pycmd_set(self):
		# py字符串命令编辑
		text_data = self.get_text('pycmd')
		obj1 = tkui.TextUi('py字符串命令编辑', text=text_data, label_text='Text')
		obj1.run()
		self.set_text('pycmd', obj1.text_data)
		del obj1

if __name__ == '__main__':
	

	logging.basicConfig(level=logging.INFO)
	logger.info('start AdmSimUi')
	
	obj = AdmSimUi('AdmSimUi').run()
	
	# obj.run()

	# # multi_res 测试
	# var_path = r'D:/document/ADAMS/AdmCarSim'
	# dic1 = file_edit.var_save(var_path)['DataModel']
	# # print(dic1)
	# csv_path = var_path+'.csv'
	# xs, ys, y_names, keys = multi_res(csv_path, dic1['compares'],
	# 			dic1['values'], dic1['target_req'], dic1['target_comp'])
	# # print(dic1['target_req'])
	# import os
	# os.popen(csv_path)

	# # 多元线性回归GUI测试
	# linear_regression_ui(xs[0],xs,ys)
	


