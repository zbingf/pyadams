# -*- coding: utf-8 -*-
'''	
	!!!!!!!
	For ADAMS 2017.2
	six dof rig
	创建 六自由度台架 
	421加载 ： 4个Z向加载、 2个Y向加载 、 1个Z向加载
	台架上端以柔性体替代
	
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
def dof_six_421_flex_create(parameter,geopara=None,viewobj=None):
	'''
		421振动台架创建
		柔性体连接
		parameter 字典 dict
			name 模型名称
			bushing_stifness 连接点衬套刚度 [x,y,z,tx,ty,tz] 
			load_nodes 加载点node序号 顺序为 [X,YF,YR,ZFL,ZFR,ZRL,ZRR] 共7个加载点
			flex_frame_path ： mnf 柔性体路径
			x_load_length 	X向加载 长度 mm
			y_load_length 	Y向加载 长度 mm
			z_load_length 	台架高度 即 Z加载长度 mm

		geopara 字典类型
			几何参数存储
			length ： 杆件长度
			radius ： 杆件半径
		
		默认设置：
			flexname 柔性体部件名称 'frame'
			spline_name ['x','y_f','y_r','z_fl','z_fr','z_rl','z_rr']

		输出：Viewmodel类 实例
	'''
	print('-'*20+'start'+'-'*20)
	
	# 输入参数解析
	model_name = parameter['name'] # 模型 名称
	bushing_stifness = parameter['bushing_stifness'] # 加载连接点衬套刚度
	load_nodes = parameter['load_nodes']
	filepath = parameter['flex_frame_path']  # 柔性体路径
	x_load_length = parameter['x_load_length'] # X向加载 长度 mm
	y_load_length = parameter['y_load_length'] # Y向加载 长度 mm
	z_load_length = parameter['z_load_length'] # 台架高度 即 Z加载长度 mm

	if geopara == None:
		# 无几何参数则默认
		road_radius = 25
		rod_length = 1000
	else:
		rod_length = geopara['length']
		road_radius = geopara['radius']

	if viewobj == None:
		viewobj = Viewmodel(model_name)

	model_obj = viewobj.model # 模型实例


	# -----------------
	# 柔性体
	# -----------------
	flexname = 'frame' # 柔性体部件名称
	flexobj = viewobj.createFlexbody(flexname,filepath)  # 创建柔性体
	# 创建衬套 台架与柔性体相接
	load_nodes_names = ['x','y_f','y_r','z_fl','z_fr','z_rl','z_rr']
	for name,node_id in zip(load_nodes_names,load_nodes):
		viewobj.createMarkerFlex(name,flexname,node_id)

	# -----------------
	# parameter 参数设置 台架参数
	# -----------------
	# 硬点坐标
	point_z_fl_1 = viewobj.marker['z_fl'].location
	point_z_fr_1 = viewobj.marker['z_fr'].location
	point_z_rl_1 = viewobj.marker['z_rl'].location
	point_z_rr_1 = viewobj.marker['z_rr'].location

	point_z_fl_2 = [point_z_fl_1[0],point_z_fl_1[1],point_z_fl_1[2]-z_load_length]
	point_z_fr_2 = [point_z_fr_1[0],point_z_fr_1[1],point_z_fr_1[2]-z_load_length]
	point_z_rl_2 = [point_z_rl_1[0],point_z_rl_1[1],point_z_rl_1[2]-z_load_length]
	point_z_rr_2 = [point_z_rr_1[0],point_z_rr_1[1],point_z_rr_1[2]-z_load_length]


	point_x_1 = viewobj.marker['x'].location
	point_x_2 = [point_x_1[0]-x_load_length,point_x_1[1],point_x_1[2]]

	point_y_f_1 = viewobj.marker['y_f'].location
	point_y_r_1 = viewobj.marker['y_r'].location

	point_y_f_2 = [point_y_f_1[0],point_y_f_1[1]-y_load_length,point_y_f_1[2]]
	point_y_r_2 = [point_y_r_1[0],point_y_r_1[1]-y_load_length,point_y_r_1[2]]

	# -----------------
	# 创建地面
	# -----------------
	ground = model_obj.Parts['ground']

	# -----------------
	# hardpoint create
	# -----------------
	hp_names = ['z_fl_1','z_fr_1','z_rl_1','z_rr_1',
		'z_fl_2','z_fr_2','z_rl_2','z_rr_2',
		'x_1','x_2','y_f_1','y_r_1','y_f_2','y_r_2']

	hardpoints = [point_z_fl_1,point_z_fr_1,point_z_rl_1,point_z_rr_1,
		point_z_fl_2,point_z_fr_2,point_z_rl_2,point_z_rr_2,
		point_x_1,point_x_2,point_y_f_1,point_y_r_1,point_y_f_2,point_y_r_2]
	
	for name,loc1 in zip(hp_names,hardpoints):
		viewobj.createHardpoint(name,loc1)

	# -----------------
	# part create
	# -----------------
	names = ['lower',
		'z_fl_1','z_fr_1','z_rl_1','z_rr_1','y_f_1','y_r_1','x_1',
		'z_fl_2','z_fr_2','z_rl_2','z_rr_2','y_f_2','y_r_2','x_2']
	for name in names:
		viewobj.createRigidBody(name)
	# mark 位置调整
	viewobj.marker['lower'].location = [0,0,0]

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
	ori_two_mark( viewobj.marker['z_fl_1'],viewobj.marker['z_fl_2'] )
	ori_two_mark( viewobj.marker['z_fr_1'],viewobj.marker['z_fr_2'] )
	ori_two_mark( viewobj.marker['z_rl_1'],viewobj.marker['z_rl_2'] )
	ori_two_mark( viewobj.marker['z_rr_1'],viewobj.marker['z_rr_2'] )

	ori_two_mark( viewobj.marker['y_f_1'],viewobj.marker['y_f_2'] )
	ori_two_mark( viewobj.marker['y_r_1'],viewobj.marker['y_r_2'] )

	ori_two_mark( viewobj.marker['x_1'],viewobj.marker['x_2'] )

	# -----------------
	# constraint 约束设置
	# -----------------
	# 台架上端
	load_part_names = ['x_1','y_f_1','y_r_1','z_fl_1','z_fr_1','z_rl_1','z_rr_1']

	for name,node_id,part_name in zip(load_nodes_names,load_nodes,load_part_names):
		# viewobj.createMarkerFlex(name,flexname,node_id)
		viewobj.bushing[name] = viewobj.bushing_flex_create(flexname,part_name,name,
			bushing_stifness[:3],bushing_stifness[3:],'bushing_'+name,node_id)

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


	# -----------------
	# geometry 创建几何
	# -----------------
	names = ['x_1','y_f_1','y_r_1','z_fl_1','z_fr_1','z_rl_1','z_rr_1',
		'x_2','y_f_2','y_r_2','z_fl_2','z_fr_2','z_rl_2','z_rr_2']
	for name in names:
		viewobj.part[name].Geometries.createCylinder(name= 'geo_rod_'+name, 
				center_marker = viewobj.marker[name],
				length = rod_length, radius = road_radius) 

	# -----------------
	# create spline and motion
	# 加载
	# -----------------
	spline_name = ['x','y_f','y_r','z_fl','z_fr','z_rl','z_rr']
	for n in range(1,8):
		name = spline_name[n-1]
		# 创建spline
		y = [ random.random()*10 for n1 in range(100) ]
		y[0] = 0
		# y = [math.sin(float(n1))*5 for n1 in range(100)]
		viewobj.spline[name] = model_obj.DataElements.createSpline(name = 'spline_'+ name,adams_id = n, 
			x=[float(n)/20 for n in range(100)], y = y) 

		# 创建加载
		viewobj.motionT[name] = model_obj.Constraints.createMotionT(name = 'motion_'+name, joint_name='join_trans_'+name)
		viewobj.motionT[name].function = 'AKISPL(time,0,.{}.spline_{}, 0)'.format(model_name,name)

	# -----------------
	# measure 
	# -----------------


	# -----------------
	# solve set
	# -----------------
	cmds_run(CMD_SOLVE,'#model_name',model_name)

	# -----------------
	# create adm output
	# -----------------
	# cmds_run(CMD_ADM_CREATE,'#model_name',model_name)

	print('-'*50+'\nend\n'+'-'*50)

	return viewobj

def request_acc_flex(viewobj,marker_names,node_ids,flexname='frame'):
	"""
		flex 加速度测量点 创建
		
		viewobj 台架模型实例化
		marker_names 列表，marker名称
		node_ids 列表，测量点node序号
		flexname 台架名称 默认 frame
	"""
	# request_markernames = ['acc1','acc2','acc3','acc3']
	# request_node_id = [10,11,12,14]
	request_markernames = marker_names
	request_node_id = node_ids
	for name,node_id in zip(request_markernames,request_node_id):
		viewobj.createMarkerFlex(name,flexname,node_id)
		viewobj.createRequestAcc(name,name)

	return viewobj

if __name__ == "__main__":
	# 在本界面运行
	cmd_str = 'file python read file_name="{}"'.format(__file__)

	sys.path.append(r'..')
	import call.tcp_link as tcp_link
	tcp_link.cmd_send(cmd_str)

else:
	sys.path.append(r'D:\github\pycae\pyadams\view')
	from view_fun import *

	# run in adams 2017.2
	# 1\ 模型创建
	# 台架参数
	parameter = {
		'name':'six_dof_rig_421', # 模型名称
		'bushing_stifness':[30000,30000,30000,0,0,0], # 加载衬套刚度
		'load_nodes':[23913,3200,11084,13,26998,3706,44253], # X YF YR ZFL ZFR ZRL ZRR
		'flex_frame_path':r'D:\document\ADAMS\View\antiroll_20209_mnf1.mnf', # 车架mnf路径
		'x_load_length':1500, # X向加载 长度 mm
		'y_load_length':1500, # Y向加载 长度 mm
		'z_load_length':1500, # 台架高度 即 Z加载长度 mm
		}
	# 几何参数
	geopara = {
		'length':1000,
		'radius':25,
	}
	
	# 加速度测量点
	# request 设置 marker名称
	request_markernames = ['acc1','acc2','acc3','acc3']
	# flex request 设置 node id  
	request_node_id = [10,11,12,14]
	
	viewobj = dof_six_421_flex_create(parameter,geopara)
	viewobj = request_acc_flex(viewobj,
			request_markernames,request_node_id)
	
	