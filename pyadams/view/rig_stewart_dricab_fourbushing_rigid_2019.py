# -*- coding: utf-8 -*-
'''
	结构：
		1、stewart 台架 6自由度振动
		2、4悬置结构
		3、刚性体!!!!
	
	version: adams 2019
	version: python 3.6
	edit time: 2020/9/20
	注：不能输出中文
'''
import os
import sys
import json
import re
import os.path
import shutil
import math
try:
	import Adams
except:
	pass

def stewart_create(model_name,center_point,parameter):
	"""
		stewart 台架创建
		model_name	:	模型名称

	"""
	print('-'*50+'\nstart\n'+'-'*50)

	viewobj = Viewmodel(model_name) # 类实例
	model_obj = viewobj.model # adams 模型实例

	# parameter
	# 参数设置
	upper_length = parameter['upper_length'] # 上端三角形 端点到中心距离
	lower_length = parameter['lower_length']	# 下端三角形	端点到中心距离
	height = parameter['height'] # 台架高度
	upper_ratio = parameter['upper_ratio'] # 上加载点位置比例 0.45
	lower_ratio = parameter['lower_ratio'] # 下加载点位置比例 0.05

	# 等边三角形 数据转化
	lower_center = [center_point[0],center_point[1],center_point[2]-height]
	upper_center = center_point
	point_1 = [-3.0**0.5/3.0*2,0,0]
	point_2 = [3.0**0.5/3.0,1.0,0]
	point_3 = [3.0**0.5/3.0,-1.0,0]
	gain_init = 3.0**0.5/3.0*2.0
	lower_1 = sum_point(gain_point(point_1,lower_length/gain_init),lower_center)
	lower_2 = sum_point(gain_point(point_2,lower_length/gain_init),lower_center)
	lower_3 = sum_point(gain_point(point_3,lower_length/gain_init),lower_center)
	upper_1 = sum_point(gain_point(point_1,upper_length/gain_init),upper_center)
	upper_2 = sum_point(gain_point(point_2,upper_length/gain_init),upper_center)
	upper_3 = sum_point(gain_point(point_3,upper_length/gain_init),upper_center)

	# 地面
	ground = model_obj.Parts['ground']

	# 创建硬点
	# 硬点名称
	hardpoint_names = ['upper','lower','lower_1','lower_2',
		'lower_3','upper_1','upper_2','upper_3'] 
	# 硬点坐标
	hardpoints = [upper_center,lower_center,lower_1,lower_2,
		lower_3,upper_1,upper_2,upper_3] 
	for name,loc1 in zip(hardpoint_names,hardpoints):
		viewobj.createHardpoint(name,loc1)


	# part create
	# names
	names = ['upper','lower',
		'upper_rod_1','upper_rod_2','upper_rod_3','upper_rod_4','upper_rod_5','upper_rod_6',
		'lower_rod_1','lower_rod_2','lower_rod_3','lower_rod_4','lower_rod_5','lower_rod_6']
	for name in names:
		viewobj.createRigidBody(name)

	# 上台架中心
	viewobj.marker['upper'].location = upper_center
	# 下台架中心
	viewobj.marker['lower'].location = lower_center

	loc_on_line(viewobj.marker['upper_rod_1'],viewobj.hardpoint['upper_1'],viewobj.hardpoint['upper_2'],upper_ratio)
	loc_on_line(viewobj.marker['upper_rod_2'],viewobj.hardpoint['upper_2'],viewobj.hardpoint['upper_1'],upper_ratio)
	loc_on_line(viewobj.marker['upper_rod_3'],viewobj.hardpoint['upper_2'],viewobj.hardpoint['upper_3'],upper_ratio)
	loc_on_line(viewobj.marker['upper_rod_4'],viewobj.hardpoint['upper_3'],viewobj.hardpoint['upper_2'],upper_ratio)
	loc_on_line(viewobj.marker['upper_rod_5'],viewobj.hardpoint['upper_3'],viewobj.hardpoint['upper_1'],upper_ratio)
	loc_on_line(viewobj.marker['upper_rod_6'],viewobj.hardpoint['upper_1'],viewobj.hardpoint['upper_3'],upper_ratio)
	
	loc_on_line(viewobj.marker['lower_rod_1'],viewobj.hardpoint['lower_1'],viewobj.hardpoint['lower_2'],lower_ratio)
	loc_on_line(viewobj.marker['lower_rod_2'],viewobj.hardpoint['lower_2'],viewobj.hardpoint['lower_1'],lower_ratio)
	loc_on_line(viewobj.marker['lower_rod_3'],viewobj.hardpoint['lower_2'],viewobj.hardpoint['lower_3'],lower_ratio)
	loc_on_line(viewobj.marker['lower_rod_4'],viewobj.hardpoint['lower_3'],viewobj.hardpoint['lower_2'],lower_ratio)
	loc_on_line(viewobj.marker['lower_rod_5'],viewobj.hardpoint['lower_3'],viewobj.hardpoint['lower_1'],lower_ratio)
	loc_on_line(viewobj.marker['lower_rod_6'],viewobj.hardpoint['lower_1'],viewobj.hardpoint['lower_3'],lower_ratio)

	# mark 方向调整
	ori_two_mark( viewobj.marker['upper_rod_1'],viewobj.marker['lower_rod_1'] )
	ori_two_mark( viewobj.marker['upper_rod_2'],viewobj.marker['lower_rod_2'] )
	ori_two_mark( viewobj.marker['upper_rod_3'],viewobj.marker['lower_rod_3'] )
	ori_two_mark( viewobj.marker['upper_rod_4'],viewobj.marker['lower_rod_4'] )
	ori_two_mark( viewobj.marker['upper_rod_5'],viewobj.marker['lower_rod_5'] )
	ori_two_mark( viewobj.marker['upper_rod_6'],viewobj.marker['lower_rod_6'] )

	# constraint 约束创建
	for n in range(1,7):
		# 创建台架 - 下端加载点 - 铰接副
		viewobj.spherical['lower_'+str(n)] = spherical_create(
			model_obj,
			viewobj.part['lower_rod_'+str(n)],
			viewobj.part['lower'],
			viewobj.marker['lower_rod_'+str(n)],
			'join_spher_lower_'+str(n) )
		# 创建台架 - 上端加载点 - 铰接副
		viewobj.spherical['upper_'+str(n)] = spherical_create(
			model_obj,
			viewobj.part['upper_rod_'+str(n)],
			viewobj.part['upper'],
			viewobj.marker['upper_rod_'+str(n)],
			'join_spher_upper_'+str(n) )
		# 创建 加载杆件间的 滑动副
		viewobj.translational['rod_'+str(n)] = translational_center_create(
			model_obj,
			viewobj.part['upper_rod_'+str(n)],
			viewobj.part['lower_rod_'+str(n)],
			viewobj.marker['upper_rod_'+str(n)],
			viewobj.marker['lower_rod_'+str(n)],
			'join_trans_rod_'+str(n) )

	# 固定副 
	viewobj.fixed['lower'] = fixed_create(
		model_obj,
		viewobj.part['lower'],
		ground,
		viewobj.marker['lower'],
		'join_fixed_lower')


	# geometry 几何创建
	# 杆件几何参数
	rod_radius = 50 # 加载杆件 半径 mm 不影响计算
	rod_length = height/1.5 # 加载杆件 长度 mm 不影响计算

	for n in range(1,7):
		model_obj.Parts['part_upper_rod_'+str(n)].Geometries.createCylinder(name= 'geo_upper_rod_'+str(n), 
			center_marker = model_obj.Parts['part_upper_rod_'+str(n)].Markers['mar_upper_rod_'+str(n)] ,
			length = rod_length, radius = rod_radius) 
		model_obj.Parts['part_lower_rod_'+str(n)].Geometries.createCylinder(name= 'geo_lower_rod_'+str(n), 
		 	center_marker = model_obj.Parts['part_lower_rod_'+str(n)].Markers['mar_lower_rod_'+str(n)] ,
		 	length = rod_length, radius = rod_radius) 

	upper_loc = [upper_1,upper_2,upper_3]
	lower_loc = [lower_1,lower_2,lower_3]
	
	upper_marks = [viewobj.createMarker('upper_'+str(n),'upper',upper_loc[n-1]) for n in range(1,4)]
	lower_marks = [viewobj.createMarker('lower_'+str(n),'lower',lower_loc[n-1]) for n in range(1,4)]


	viewobj.part['upper'].Geometries.createPlate(name= 'gem_plate_upper', markers = upper_marks, radius = 100, width = 10) 
	viewobj.part['lower'].Geometries.createPlate(name= 'gem_plate_lower', markers = lower_marks, radius = 100, width = 10) 

	for n in range(1,7):
		# create spline
		viewobj.spline[str(n)] = model_obj.DataElements.createSpline(name = 'spline_'+str(n) ,adams_id = n, 
			x=[float(value)/10 for value in range(100)], y = [math.sin(float(value))*100 for value in range(100)]) 
	
		# create motion
		viewobj.motionT[str(n)] = model_obj.Constraints.createMotionT(name = 'motion_'+str(n), joint_name='join_trans_rod_'+str(n))
		viewobj.motionT[str(n)].function = 'AKISPL(time,0,spline_{}, 0)'.format(n)


	# create adm output 输出adm
	# cmds_run(CMD_ADM_CREATE,'#model_name',model_name)

	print('-'*50+'\nend\n'+'-'*50)
	return viewobj

# def fourbushing_rigid(viewobj,):


if __name__ == "__main__":
	# 在本界面运行
	print('rig_stewart is running as  __main__')
	if '__file__' in locals().keys():
		print(__file__)
		cmd_str = 'file python read file_name="{}"'.format(__file__)
		sys.path.append(r'..')
		import call.tcp_link as tcp_link
		tcp_link.cmd_send(cmd_str)
		# print(locals())

	else:
		# ADAMS View 中运行
		sys.path.append(r'D:\github\pycae\pyadams\view')
		from view_fun import *

		# 模型名称
		model_name = 'six_dof_rig_stewart'
		# 台架参数
		center_point = [400,0,250]
		parameter = {
			'upper_length':1732,
			'lower_length':1732,
			'height':1500,
			'upper_ratio':0.45 ,
			'lower_ratio':0.05,
		}
		lower_marker_names = ['FL','FR','RL','RR']
		lower_marker_locs = [
			[100.0, -400.0, 250.0],
			[100.0, 400.0, 250.0],
			[700.0, -400.0, 250.0],
			[700.0, 400.0, 250.0],
			]
		# 悬置上端参数
		upper_marker_names = ['FL_U','FR_U','RL_U','RR_U']
		upper_marker_locs = [
			[115.0, -400.0, 320.0],
			[103.0, 390.0, 300.0],
			[745.0, -426.0, 277.0],
			[699.0, 387.0, 322.0],
			]
		upper_mass = {
			'name':'point_mass',
			'mass':114,
			'loc':[510.0, 150.0, 600.0],
			'ip':[1e6,1e6,1e6],
		}
		# 悬置设置 
		bushing_marker_names = ['FL_B','FR_B','RL_B','RR_B']
		bushing_marker_locs = [
			[100.0, -400.0, 250.0],
			[100.0, 400.0, 250.0],
			[700.0, -400.0, 250.0],
			[700.0, 400.0, 250.0],
			]
		fl_bushing = {
			'k':[10,10,10],
			'tk':[8.2030474844E+04,8.2030474844E+04,8.2030474844E+04],
			'd':[1,1,1],
			'td':[2.0943951024E+04,2.0943951024E+04,2.0943951024E+04],
		}
		fr_bushing = {
			'k':[20,20,20],
			'tk':[8.2030474844E+04,8.2030474844E+04,8.2030474844E+04],
			'd':[2,2,2],
			'td':[2.0943951024E+04,2.0943951024E+04,2.0943951024E+04],
		}
		rl_bushing = {
			'k':[30,30,30],
			'tk':[8.2030474844E+04,8.2030474844E+04,8.2030474844E+04],
			'd':[3,3,3],
			'td':[2.0943951024E+04,2.0943951024E+04,2.0943951024E+04],
		}
		rr_bushing = {
			'k':[40,40,40],
			'tk':[8.2030474844E+04,8.2030474844E+04,8.2030474844E+04],
			'd':[4,4,4],
			'td':[2.0943951024E+04,2.0943951024E+04,2.0943951024E+04],
		}


		# 台架创建
		viewobj = stewart_create(model_name,center_point,parameter)
		for name,loc1 in zip(lower_marker_names,lower_marker_locs):
			viewobj.createMarker(name,'upper',loc1)
			viewobj.createRequestAcc(name,name)

		for name,loc1 in zip(bushing_marker_names,bushing_marker_locs):
			viewobj.createMarker(name,'upper',loc1)
			viewobj.createRequestAcc(name,name)

		# 创建 part
		part_name = upper_mass['name']
		viewobj.createRigidBody(part_name)
		viewobj.marker[part_name].location = upper_mass['loc']
		viewobj.part[part_name].mass = upper_mass['mass']
		viewobj.part[part_name].ixx = upper_mass['ip'][0]
		viewobj.part[part_name].iyy = upper_mass['ip'][1]
		viewobj.part[part_name].izz = upper_mass['ip'][2]

		for name,loc1 in zip(upper_marker_names,upper_marker_locs):
			viewobj.createMarker(name,part_name,loc1)
			viewobj.createRequestAcc(name,name)

		# 创建衬套连接
		viewobj.createBushing('upper',part_name,
			'FL_B',fl_bushing['k'],
			fl_bushing['tk'],
			'FL_bus')
		viewobj.bushing['FL_bus'].damping = fl_bushing['d']
		viewobj.bushing['FL_bus'].tdamping = fl_bushing['td']

		viewobj.createBushing('upper',part_name,
			'FR_B',fr_bushing['k'],
			fr_bushing['tk'],
			'FR_bus')
		viewobj.bushing['FR_bus'].damping = fr_bushing['d']
		viewobj.bushing['FR_bus'].tdamping = fr_bushing['td']

		viewobj.createBushing('upper',part_name,
			'RL_B',rl_bushing['k'],
			rl_bushing['tk'],
			'RL_bus')
		viewobj.bushing['RL_bus'].damping = rl_bushing['d']
		viewobj.bushing['RL_bus'].tdamping = rl_bushing['td']

		viewobj.createBushing('upper',part_name,
			'RR_B',rr_bushing['k'],
			rr_bushing['tk'],
			'RR_bus')
		viewobj.bushing['RR_bus'].damping = rr_bushing['d']
		viewobj.bushing['RR_bus'].tdamping = rr_bushing['td']

		