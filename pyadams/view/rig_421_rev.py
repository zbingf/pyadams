# -*- coding: utf-8 -*-
'''
	for ADAMS 2017.2
	six dof rig
	创建 六自由度台架 
	421加载 ： 4个Z向加载、 2个Y向加载 、 1个Z向加载
	台架拆分两半
	
	适用于 python 2.7
	修改时间 2020/7/8

	调用view_fun 模块

'''
import os
import sys
import json
import re
import os.path
import shutil
import math
import random

try:
	import Adams
except:
	pass


# --------------------------------------------
def dof_six_421_felx_create(model_name,center_point,bushing_stifness,parameter,viewobj=None):
	'''
		421振动台架创建
		model_name 模型名称
		center_point 台架中点位置 [x,y,z]
		bushing_stifness 衬套刚度 [x,y,z,tx,ty,tz]
		parameter 参数 dict 
			x_length 		台架X向宽度 mm
			y_length 		台架Y向宽度 mm
			x_load_length 	X向加载 长度 mm
			y_load_length 	Y向加载 长度 mm
			z_load_length 	台架高度 即 Z加载长度 mm
			y_load_dis 		Y向加载点 间距 mm

		输出：Viewmodel类 实例
	'''
	print('-'*20+'start'+'-'*20)
	if viewobj == None:
		viewobj = Viewmodel(model_name)
	
	model_obj = viewobj.model

	# parameter 参数设置 台架参数
	x_length = parameter['x_length']	 # 台架X向宽度 
	y_length = parameter['y_length'] # 台架Y向宽度
	x_load_length = parameter['x_load_length'] # X向加载 长度 mm
	y_load_length = parameter['y_load_length'] # Y向加载 长度 mm
	z_load_length = parameter['z_load_length'] # 台架高度 即 Z加载长度 mm
	y_load_dis = parameter['y_load_dis'] # Y向加载点 间距 mm

	# 硬点坐标
	# center_point = [0,0,0]
	center_point_lower = [center_point[0],center_point[1],-z_load_length]
	point_z_fl_1 = [center_point[0]-x_length/2,center_point[1]-y_length/2,center_point[2]]
	point_z_fr_1 = [center_point[0]-x_length/2,center_point[1]+y_length/2,center_point[2]]
	point_z_rl_1 = [center_point[0]+x_length/2,center_point[1]-y_length/2,center_point[2]]
	point_z_rr_1 = [center_point[0]+x_length/2,center_point[1]+y_length/2,center_point[2]]

	point_z_fl_2 = [center_point[0]-x_length/2,center_point[1]-y_length/2,center_point[2]-z_load_length]
	point_z_fr_2 = [center_point[0]-x_length/2,center_point[1]+y_length/2,center_point[2]-z_load_length]
	point_z_rl_2 = [center_point[0]+x_length/2,center_point[1]-y_length/2,center_point[2]-z_load_length]
	point_z_rr_2 = [center_point[0]+x_length/2,center_point[1]+y_length/2,center_point[2]-z_load_length]

	point_x_1 = [center_point[0]-x_length/2,center_point[1],center_point[2]]
	point_x_2 = [center_point[0]-x_length/2-x_load_length,center_point[1],center_point[2]]

	point_y_f_1 = [center_point[0]-y_load_dis/2,center_point[1]-y_length/2,center_point[2]]
	point_y_r_1 = [center_point[0]+y_load_dis/2,center_point[1]-y_length/2,center_point[2]]

	point_y_f_2 = [center_point[0]-y_load_dis/2,center_point[1]-y_length/2-y_load_length,center_point[2]]
	point_y_r_2 = [center_point[0]+y_load_dis/2,center_point[1]-y_length/2-y_load_length,center_point[2]]


	# 创建地面
	ground = model_obj.Parts['ground']

	# hardpoint create
	hp_names = ['z_fl_1','z_fr_1','z_rl_1','z_rr_1',
		'z_fl_2','z_fr_2','z_rl_2','z_rr_2',
		'x_1','x_2','y_f_1','y_r_1','y_f_2','y_r_2',
		'center_point_lower','center_point']

	hardpoints = [point_z_fl_1,point_z_fr_1,point_z_rl_1,point_z_rr_1,
		point_z_fl_2,point_z_fr_2,point_z_rl_2,point_z_rr_2,
		point_x_1,point_x_2,point_y_f_1,point_y_r_1,point_y_f_2,point_y_r_2,center_point_lower,center_point]
	
	for name,loc1 in zip(hp_names,hardpoints):
		viewobj.createHardpoint(name,loc1)

	# part create

	# names
	names = ['upper_1','upper_2','lower',
		'z_fl_1','z_fr_1','z_rl_1','z_rr_1','y_f_1','y_r_1','x_1',
		'z_fl_2','z_fr_2','z_rl_2','z_rr_2','y_f_2','y_r_2','x_2']

	for name in names:
		viewobj.createRigidBody(name)

	# mark 位置调整
	viewobj.marker['upper_1'].location = center_point
	viewobj.marker['upper_2'].location = center_point
	viewobj.marker['lower'].location = center_point_lower

	loc_on_line(viewobj.marker['z_fl_1'],viewobj.hardpoint['z_fl_1'],viewobj.hardpoint['z_fl_2'],0)
	loc_on_line(viewobj.marker['z_fl_2'],viewobj.hardpoint['z_fl_2'],viewobj.hardpoint['z_fl_1'],0)

	loc_on_line(viewobj.marker['z_fr_1'],viewobj.hardpoint['z_fr_1'],viewobj.hardpoint['z_fr_2'],0)
	loc_on_line(viewobj.marker['z_fr_2'],viewobj.hardpoint['z_fr_2'],viewobj.hardpoint['z_fr_1'],0)

	loc_on_line(viewobj.marker['z_rl_1'],viewobj.hardpoint['z_rl_1'],viewobj.hardpoint['z_rl_2'],0)
	loc_on_line(viewobj.marker['z_rl_2'],viewobj.hardpoint['z_rl_2'],viewobj.hardpoint['z_rl_1'],0)

	loc_on_line(viewobj.marker['z_rr_1'],viewobj.hardpoint['z_rr_1'],viewobj.hardpoint['z_rr_2'],0)
	loc_on_line(viewobj.marker['z_rr_2'],viewobj.hardpoint['z_rr_2'],viewobj.hardpoint['z_rr_1'],0)

	loc_on_line(viewobj.marker['y_f_1'],viewobj.hardpoint['y_f_1'],viewobj.hardpoint['y_f_2'],0)
	loc_on_line(viewobj.marker['y_f_2'],viewobj.hardpoint['y_f_2'],viewobj.hardpoint['y_f_1'],0)

	loc_on_line(viewobj.marker['y_r_1'],viewobj.hardpoint['y_r_1'],viewobj.hardpoint['y_r_2'],0)
	loc_on_line(viewobj.marker['y_r_2'],viewobj.hardpoint['y_r_2'],viewobj.hardpoint['y_r_1'],0)

	loc_on_line(viewobj.marker['x_1'],viewobj.hardpoint['x_1'],viewobj.hardpoint['x_2'],0)
	loc_on_line(viewobj.marker['x_2'],viewobj.hardpoint['x_2'],viewobj.hardpoint['x_1'],0)


	# mark 方向调整
	ori_two_mark( viewobj.hardpoint['z_fl_1'],viewobj.hardpoint['z_fl_2'] )
	ori_two_mark( viewobj.hardpoint['z_fr_1'],viewobj.hardpoint['z_fr_2'] )
	ori_two_mark( viewobj.hardpoint['z_rl_1'],viewobj.hardpoint['z_rl_2'] )
	ori_two_mark( viewobj.hardpoint['z_rr_1'],viewobj.hardpoint['z_rr_2'] )

	ori_two_mark( viewobj.hardpoint['y_f_1'],viewobj.hardpoint['y_f_2'] )
	ori_two_mark( viewobj.hardpoint['y_r_1'],viewobj.hardpoint['y_r_2'] )

	ori_two_mark( viewobj.hardpoint['x_1'],viewobj.hardpoint['x_2'] )


	# constraint 约束设置
	# 台架上端
	# 左前
	viewobj.bushing['z_fl_1'] = bushing_create(model_obj,viewobj.part['z_fl_1'],viewobj.part['upper_1'],
		viewobj.part['z_fl_1'].Markers['mar_z_fl_1'],
		bushing_stifness[0:3],bushing_stifness[3:6],
		'bushing_z_fl_1')
	# 右前
	viewobj.bushing['z_fr_1'] = bushing_create(model_obj,viewobj.part['z_fr_1'],viewobj.part['upper_2'],
		viewobj.part['z_fr_1'].Markers['mar_z_fr_1'],
		bushing_stifness[0:3],bushing_stifness[3:6],
		'bushing_z_fr_1')
	# 左后
	viewobj.bushing['z_rl_1'] = bushing_create(model_obj,viewobj.part['z_rl_1'],viewobj.part['upper_1'],
		viewobj.part['z_rl_1'].Markers['mar_z_rl_1'],
		bushing_stifness[0:3],bushing_stifness[3:6],
		'bushing_z_rl_1')
	# 右后
	viewobj.bushing['z_rr_1'] = bushing_create(model_obj,viewobj.part['z_rr_1'],viewobj.part['upper_2'],
		viewobj.part['z_rr_1'].Markers['mar_z_rr_1'],
		bushing_stifness[0:3],bushing_stifness[3:6],
		'bushing_z_rr_1')

	# 台架拆分-衬套 ---------------------------------------------------------------------------------------------
	viewobj.bushing['z_middle'] = bushing_create(model_obj,viewobj.part['upper_1'],viewobj.part['upper_2'],
		viewobj.marker['upper_1'],
		[1e5,1e5,1e5],[1e8,1e7,1e8],
		'bushing_z_middle')

	viewobj.revolute['z_middle'] = viewobj.createRevolute('z_middle','upper_1','upper_2',
		location=center_point,orientation=[0,90,0])

	# 左侧
	viewobj.spherical['y_f_1'] = spherical_create(model_obj,viewobj.part['y_f_1'],viewobj.part['upper_1'],
		viewobj.part['y_f_1'].Markers['mar_y_f_1'],'join_spher_y_f_1')

	viewobj.spherical['y_r_1'] = spherical_create(model_obj,viewobj.part['y_r_1'],viewobj.part['upper_1'],
		viewobj.part['y_r_1'].Markers['mar_y_r_1'],'join_spher_y_r_1')

	viewobj.spherical['x_1'] = spherical_create(model_obj,viewobj.part['x_1'],viewobj.part['upper_1'],
		viewobj.part['x_1'].Markers['mar_x_1'],'join_spher_x_1')

	# 台架底部
	viewobj.spherical['z_fl_2'] = spherical_create(model_obj,viewobj.part['z_fl_2'],viewobj.part['lower'],
		viewobj.part['z_fl_2'].Markers['mar_z_fl_2'],'join_spher_z_fl_2')
	
	viewobj.spherical['z_fr_2'] = spherical_create(model_obj,viewobj.part['z_fr_2'],viewobj.part['lower'],
		viewobj.part['z_fr_2'].Markers['mar_z_fr_2'],'join_spher_z_fr_2')

	viewobj.spherical['z_rl_2'] = spherical_create(model_obj,viewobj.part['z_rl_2'],viewobj.part['lower'],
		viewobj.part['z_rl_2'].Markers['mar_z_rl_2'],'join_spher_z_rl_2')

	viewobj.spherical['z_rr_2'] = spherical_create(model_obj,viewobj.part['z_rr_2'],viewobj.part['lower'],
		viewobj.part['z_rr_2'].Markers['mar_z_rr_2'],'join_spher_z_rr_2')

	viewobj.spherical['y_f_2'] = spherical_create(model_obj,viewobj.part['y_f_2'],viewobj.part['lower'],
		viewobj.part['y_f_2'].Markers['mar_y_f_2'],'join_spher_y_f_2')

	viewobj.spherical['y_r_2'] = spherical_create(model_obj,viewobj.part['y_r_2'],viewobj.part['lower'],
		viewobj.part['y_r_2'].Markers['mar_y_r_2'],'join_spher_y_r_2')

	viewobj.spherical['x_2'] = spherical_create(model_obj,viewobj.part['x_2'],viewobj.part['lower'],
		viewobj.part['x_2'].Markers['mar_x_2'],'join_spher_x_2')


	viewobj.translational['z_fl'] = translational_center_create(model_obj,viewobj.part['z_fl_1'],
		viewobj.part['z_fl_2'],
		viewobj.part['z_fl_1'].Markers['mar_z_fl_1'],
		viewobj.part['z_fl_2'].Markers['mar_z_fl_2'],
		'join_trans_z_fl')
	viewobj.translational['z_fr'] = translational_center_create(model_obj,viewobj.part['z_fr_1'],
		viewobj.part['z_fr_2'],
		viewobj.part['z_fr_1'].Markers['mar_z_fr_1'],
		viewobj.part['z_fr_2'].Markers['mar_z_fr_2'],
		'join_trans_z_fr')
	viewobj.translational['z_rl'] = translational_center_create(model_obj,viewobj.part['z_rl_1'],
		viewobj.part['z_rl_2'],
		viewobj.part['z_rl_1'].Markers['mar_z_rl_1'],
		viewobj.part['z_rl_2'].Markers['mar_z_rl_2'],
		'join_trans_z_rl')
	viewobj.translational['z_rr'] = translational_center_create(model_obj,viewobj.part['z_rr_1'],
		viewobj.part['z_rr_2'],
		viewobj.part['z_rr_1'].Markers['mar_z_rr_1'],
		viewobj.part['z_rr_2'].Markers['mar_z_rr_2'],
		'join_trans_z_rr')
	viewobj.translational['y_f'] = translational_center_create(model_obj,viewobj.part['y_f_1'],
		viewobj.part['y_f_2'],
		viewobj.part['y_f_1'].Markers['mar_y_f_1'],
		viewobj.part['y_f_2'].Markers['mar_y_f_2'],
		'join_trans_y_f')
	viewobj.translational['y_r'] = translational_center_create(model_obj,viewobj.part['y_r_1'],
		viewobj.part['y_r_2'],
		viewobj.part['y_r_1'].Markers['mar_y_r_1'],
		viewobj.part['y_r_2'].Markers['mar_y_r_2'],
		'join_trans_y_r')
	viewobj.translational['x'] = translational_center_create(model_obj,viewobj.part['x_1'],
		viewobj.part['x_2'],
		viewobj.part['x_1'].Markers['mar_x_1'],
		viewobj.part['x_2'].Markers['mar_x_2'],
		'join_trans_x')

	viewobj.fixed['lower'] = fixed_create(model_obj,viewobj.part['lower'],ground,
			viewobj.part['lower'].Markers['mar_lower'],'join_fixed_lower')



	# geometry 创建几何

	# for n in range(1,7):
	# 	viewobj.part['upper_rod_'+str(n)].Geometries.createCylinder(name= 'geo_upper_rod_'+str(n), 
	# 		center_marker = viewobj.part['upper_rod_'+str(n)].Markers['mar_upper_rod_'+str(n)] ,
	# 		length = rod_length, radius = rod_radius) 
	# 	viewobj.part['lower_rod_'+str(n)].Geometries.createCylinder(name= 'geo_lower_rod_'+str(n), 
	# 	 	center_marker = viewobj.part['lower_rod_'+str(n)].Markers['mar_lower_rod_'+str(n)] ,
	# 	 	length = rod_length, radius = rod_radius) 

	# upper_loc = [upper_1,upper_2,upper_3]
	# lower_loc = [lower_1,lower_2,lower_3]
	
	# upper_marks = [ viewobj.part['upper'].Markers.create(name = 'mar_upper_'+str(n) , location = upper_loc[n-1]) for n in range(1,4)]
	# lower_marks = [ viewobj.part['lower'].Markers.create(name = 'mar_lower_'+str(n) , location = lower_loc[n-1]) for n in range(1,4)]

	upper_loc = [point_z_fl_1,point_z_fr_1,point_z_rl_1,point_z_rr_1]
	upper_left_marks = [ viewobj.part['upper_1'].Markers.create(name = 'mar_upper_1_'+str(n) , location = upper_loc[n]) for n in [0,2] ]
	upper_left_marks.append(viewobj.marker['upper_1'])
	upper_right_marks = [ viewobj.part['upper_2'].Markers.create(name = 'mar_upper_2_'+str(n) , location = upper_loc[n]) for n in [1,3] ]
	upper_right_marks.append(viewobj.marker['upper_2'])
	viewobj.part['upper_1'].Geometries.createPlate(name= 'gem_plate_upper_1', markers = upper_left_marks, radius = 100, width = 10) 
	viewobj.part['upper_2'].Geometries.createPlate(name= 'gem_plate_upper_2', markers = upper_right_marks, radius = 100, width = 10) 
	# viewobj.part['lower'].Geometries.createPlate(name= 'gem_plate_lower', markers = lower_marks, radius = 100, width = 10) 

	# # create spline and motion
	spline_name = ['x','y_f','y_r','z_fl','z_fr','z_rl','z_rr']
	for n in range(1,8):
		name = spline_name[n-1]
		# 创建spline
		# y = [ random.random()*10 for n1 in range(100) ]
		# y[0] = 0
		y = [math.sin(float(n1))*5 for n1 in range(100)]
		viewobj.spline[name] = model_obj.DataElements.createSpline(name = 'spline_'+ name,adams_id = n, 
			x=[float(n)/20 for n in range(100)], y = y) 

		# 创建加载
		viewobj.motionT[name] = model_obj.Constraints.createMotionT(name = 'motion_'+name, joint_name='join_trans_'+name)
		viewobj.motionT[name].function = 'AKISPL(time,0,.{}.spline_{}, 0)'.format(model_name,name)

	# measure 

	# solve set
	cmds_run(CMD_SOLVE,'#model_name',model_name)

	# create adm output
	# cmds_run(CMD_ADM_CREATE,'#model_name',model_name)

	print('-'*50+'\nend\n'+'-'*50)

	return viewobj


if __name__ == "__main__":
	# 在本界面运行
	cmd_str = 'file python read file_name="{}"'.format(__file__)

	sys.path.append(r'..')
	import call.tcplink as tcplink
	tcplink.cmd_send(cmd_str)

else:
	sys.path.append(r'D:\github\pycae\pyadams\view')
	from view_fun import *

	# run in adams 2017.2
	# 衬套
	bushing_stifness = [30000,30000,30000,0,0,0]
	# 中点
	center_point = [400,0,250]
	# 模型名称
	model_name = 'six_dof_rig_421'
	# 台架模型
	parameter = {
		'x_length':600, # 台架X向宽度 
		'y_length':800,# 台架Y向宽度
		'x_load_length':1500, # X向加载 长度 mm
		'y_load_length':1500, # Y向加载 长度 mm
		'z_load_length':1500, # 台架高度 即 Z加载长度 mm
		'y_load_dis':600, # Y向加载点 间距 mm
	}

	# 在view中运行
	viewobj = dof_six_421_felx_create(model_name,center_point,bushing_stifness,parameter)

	# # 柔性体
	# flexname = 'test' # 柔性体部件名称
	# filepath = r'D:\document\ADAMS\con_rod.mnf'  # 柔性体路径
	# flexobj = viewobj.createFlexbody(flexname,filepath)  # 创建柔性体

	# # 创建衬套 台架与柔性体相接
	# flex_names = ['flex_bus_1','flex_bus_2','flex_bus_3','flex_bus_4']  
	# node_ids = [1,2,3,4]
	# for name,node_id in zip(flex_names,node_ids):
	# 	viewobj.createMarkerFlex(name,flexname,node_id)
	# 	# viewobj.set_flex_marker_node(name,flexname,node_id)
	# 	viewobj.bushing_flex_create(flexname,'upper',name,[1000,1000,1000],[0,0,0],'bushing_'+name,node_id)

	# # flex 加速度测量点 创建
	# request_markernames = ['acc1','acc2','acc3']
	# request_node_id = [10,11,12]
	# for name,node_id in zip(request_markernames,request_node_id):
	# 	viewobj.createMarkerFlex(name,flexname,node_id)
	# 	viewobj.createRequestAcc(name,name)

	# rigid 部件测量
	viewobj.createMarker('upper_acc1','upper_1')
	viewobj.marker['upper_acc1'].location = [100.0, -400.0, 250.0]
	viewobj.createRequestAcc('upper_acc1','upper_acc1')
	viewobj.createMarker('upper_acc2','upper_2')
	viewobj.marker['upper_acc2'].location = [100.0, 400.0, 250.0]
	viewobj.createRequestAcc('upper_acc2','upper_acc2')
	viewobj.createMarker('upper_acc3','upper_1')
	viewobj.marker['upper_acc3'].location = [700.0, -400.0, 250.0]
	viewobj.createRequestAcc('upper_acc3','upper_acc3')
	viewobj.createMarker('upper_acc4','upper_2')
	viewobj.marker['upper_acc4'].location = [700.0, 400.0, 250.0]
	viewobj.createRequestAcc('upper_acc4','upper_acc4')








	

