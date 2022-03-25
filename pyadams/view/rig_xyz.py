# -*- coding: utf-8 -*-
'''
	For ADAMS 2017.2
	six dof rig
	创建	六自由度振动台架 
	X、Y、Z、Rx、Ry、Rz
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

# print(__name__)


GROUND_NAME = 'ground'
MARKER_NAME_FRONT = 'mar_'
POINT_NAME_FRONT = 'hp_'
PART_NAME_FRONT = 'part_'
CONSTRAINTS_NAME_FRONT = 'const_'
G = 9806.65

hp_objs = {}
mar_objs = {}
part_objs = {}
const_objs = {}
request_data = {}

# loc cal ------------------------------------------
def rand_singel_general(t=10,hz=32,gain=1):
	import numpy
	num = t*hz
	x = [float(n)/hz for n in range(num)]
	y = numpy.random.rand(num)
	y = y.tolist()
	y[0]=y[-1]=0
	return x,y
# ------------------------------------------



# create --------------------------------------------
def create_point(partobj,name,location=None):
	if location == None:
		location = [0,0,0]
	obj = partobj.DesignPoints.create(name= POINT_NAME_FRONT+name)
	obj.location = location
	hp_objs[name] = obj
	return obj

def create_marker(partobj,name,location=None,orientation=None):
	if location == None:
		location = [0,0,0]
	if orientation == None:
		orientation = [0,0,0]
	obj = partobj.Markers.create(name = MARKER_NAME_FRONT+name)
	obj.location = location
	obj.orientation = orientation
	mar_objs[name] = obj
	return obj

def create_part(model_obj,name):
	obj = model_obj.Parts.createRigidBody( name = PART_NAME_FRONT+name)
	part_objs[name] = obj
	return obj
	
	# constraint --------------------------------------------
def create_translational_center(model_obj,name,part1,part2,markobj1,markobj2):
	# i_marker = part1.Markers.create(name = name+'_i')
	i_marker = create_marker(part1,name = name+'_i')
	# j_marker = part2.Markers.create(name = name+'_j')
	j_marker = create_marker(part2,name = name+'_j')
	ori_z_two_point(i_marker,i_marker,j_marker)
	ori_z_two_point(j_marker,i_marker,j_marker)
	loc_on_line(i_marker,markobj1,markobj2,0.5)
	loc_on_line(j_marker,markobj1,markobj2,0.5)
	obj = model_obj.Constraints.createTranslational(name=CONSTRAINTS_NAME_FRONT+name, i_marker=i_marker, j_marker=j_marker) 
	const_objs[name] = [obj,i_marker,j_marker]
	return obj

def create_translational_relative(model_obj,name,part1,part2,locobj,ori,oriobj=None):
	i_marker = create_marker(part1,name = name+'_i')
	j_marker = create_marker(part2,name = name+'_j')
	# ori = [90,90,0]
	if type(oriobj) == type(None):
		i_marker.orientation = ori
		j_marker.orientation = ori
	ori_relative(i_marker,oriobj,orientation=ori)
	ori_relative(j_marker,oriobj,orientation=ori)
	loc_relative(i_marker,locobj)
	loc_relative(j_marker,locobj)
	obj = model_obj.Constraints.createTranslational(name=CONSTRAINTS_NAME_FRONT+name, i_marker=i_marker, j_marker=j_marker)
	const_objs[name] = [obj,i_marker,j_marker]
	return obj

def create_revolute_relative(model_obj,name,part1,part2,locobj,ori,oriobj=None):
	i_marker = create_marker(part1,name = name+'_i')
	j_marker = create_marker(part2,name = name+'_j')
	# ori = [90,90,0]
	if type(oriobj) == type(None):
		i_marker.orientation = ori
		j_marker.orientation = ori
	ori_relative(i_marker,oriobj,orientation=ori)
	ori_relative(j_marker,oriobj,orientation=ori)
	loc_relative(i_marker,locobj)
	loc_relative(j_marker,locobj)
	obj = model_obj.Constraints.createRevolute(name=CONSTRAINTS_NAME_FRONT+name, i_marker=i_marker, j_marker=j_marker)
	const_objs[name] = [obj,i_marker,j_marker]
	return obj

def create_fixed(model_obj,part1,part2,marobj,name):
	i_marker = create_marker(part1,name = name+'_i',location = marobj.location)
	j_marker = create_marker(part2,name = name+'_j',location = marobj.location)
	obj = model_obj.Constraints.createFixed(name=CONSTRAINTS_NAME_FRONT+name, i_marker=i_marker, j_marker=j_marker) 
	const_objs[name] = [obj,i_marker,j_marker]
	return obj

def create_spherical(model_obj,part1,part2,marobj,name):
	i_marker = create_marker(part1,name =+name+'_i',location = marobj.location)
	j_marker = create_marker(part2,name = name+'_j',location = marobj.location)
	obj = model_obj.Constraints.createSpherical(name=CONSTRAINTS_NAME_FRONT+name, i_marker=i_marker, j_marker=j_marker) 
	const_objs[name] = [obj,i_marker,j_marker]
	return obj

# edit ------------------------------------

def ori_relative(obj,obj1,orientation=None):
	if orientation == None:
		orientation=[0,0,0]
	x,y,z = orientation
	str1 = "ORI_RELATIVE_TO( {{ {},{},{} }} , {} )".format(x,y,z,obj1.name)
	obj.orientation = Adams.expression(str1)


def loc_relative(obj,obj1,location=None):
	if location == None:
		location=[0,0,0]
	x,y,z = location
	str1 = "LOC_RELATIVE_TO( {{ {},{},{} }} , {} )".format(x,y,z,obj1.name)
	obj.location = Adams.expression(str1)

def set_mass(partobj,markobj):
	partobj.cm = markobj
	partobj.mass = 0.1
	partobj.ixx = 0.1
	partobj.iyy = 0.1
	partobj.izz = 0.1
# ------------------------------------------

def set_default():
	d = Adams.defaults
	d.units.length = 'mm'
	d.units.mass = 'kg'
	d.units.time = 'second'
	d.units.angle = 'degrees'
	d.units.force = 'newton'

def del_and_create(model_name):
	try:
		model_obj = Adams.Models.create(name = model_name )
	except:
		Adams.Models[model_name].destroy()
		model_obj = Adams.Models.create(name = model_name )
	return model_obj

def get_and_create(model_name):
	try:
		model_obj = Adams.Models.create(name = model_name )
	except:
		model_obj = Adams.Models[model_name]
	return model_obj

def output_adm(model_name,filepath):
	if model_name[0] != '.':
		model_name = '.' + model_name
	cmd_str = 'defaults adams_output  '+\
		'  statement_order = as_found_in_file  '+\
		'  arguments_per_line = single  '+\
		'  text_case = upper  '+\
		'  indent_spaces = 1  '+\
		'  write_default_values = off  '+\
		'  scientific_notation = -4,5  '+\
		'  trailing_zeros = off  '+\
		'  decimal_places = 10  '+\
		'  zero_threshold = 1e-15  '+\
		'  round_off = on  '+\
		'  significant_figures = 10  '+\
		'  export_all_graphics = off '
	cmd_str2 = 'file adams_data_set write  '+\
		'  model_name = {}  '+\
		'  file_name = "{}"  '+\
		'  write_to_terminal = off'
	str1 = cmd_str2.format(model_name,filepath)
	Adams.execute_cmd(cmd_str)
	Adams.execute_cmd(str1)

def request_acc_marker(name,adamsid,marobj1,marobj2):
	# name marobj1,marobj2,adamsid
	cmd_str = 'output_control create request '+\
	' request_name = {}  '.format(name)+\
	' adams_id = {} '.format(adamsid)+\
	' f2 = "ACCX({}, {}, {})/{}" '.format(marobj1.name,marobj2.name,marobj1.name,G)+\
	' f3 = "ACCY({}, {}, {})/{}" '.format(marobj1.name,marobj2.name,marobj1.name,G)+\
	' f4 = "ACCZ({}, {}, {})/{}" '.format(marobj1.name,marobj2.name,marobj1.name,G)
	request_data[name] = {'id':adamsid,'type':'acc_xyz'}
	# print(cmd_str)
	Adams.execute_cmd(cmd_str)

# --------------------------------------------
def dof_six_xyz_create():
	print('-'*20,'start','-'*20)
	model_name = 'six_dof_rig'

	path = os.getcwd()
	sys.path.append(path)
	set_default()
	model_obj = del_and_create(model_name)
	ground = model_obj.Parts[GROUND_NAME]

	gravity_obj= model_obj.Forces.createGravity(name='gravity', xyz_component_gravity = [0, 0, -G]) 

	# parameter
	# hp_center = [0,0,0]
	hp_center = [400.0, 0, 250.0]
	part_names = ['x','y','z','rx','ry','rz']

	part_dz = 50
	part_width = 200
	part_thickness = 10

	hp_center_obj = create_point(ground,'center',hp_center)
	mar_center_obj = create_marker(ground,'center')
	loc_relative(mar_center_obj,hp_center_obj)
	for num,name in enumerate(part_names):
		partobj = create_part(model_obj,name)
		marobj = create_marker(partobj,name)
		loc_relative(marobj,hp_center_obj,location=[0,0,-part_dz*(5-num)])
		set_mass(partobj,marobj)

	# constraints
	create_translational_relative(model_obj,'trans_x',ground,part_objs['x'],locobj=hp_center_obj,ori=[90,90,0],oriobj=mar_center_obj)
	create_translational_relative(model_obj,'trans_y',part_objs['x'],part_objs['y'],locobj=hp_center_obj,ori=[0,90,0],oriobj=mar_center_obj)
	create_translational_relative(model_obj,'trans_z',part_objs['y'],part_objs['z'],locobj=hp_center_obj,ori=[0,0,0],oriobj=mar_center_obj)

	create_revolute_relative(model_obj,'rev_x',part_objs['z'],part_objs['rx'],locobj=hp_center_obj,ori=[90,90,0],oriobj=mar_center_obj)
	create_revolute_relative(model_obj,'rev_y',part_objs['rx'],part_objs['ry'],locobj=hp_center_obj,ori=[0,90,0],oriobj=mar_center_obj)
	create_revolute_relative(model_obj,'rev_z',part_objs['ry'],part_objs['rz'],locobj=hp_center_obj,ori=[0,0,0],oriobj=mar_center_obj)
	

	# geometry
	dis = part_width/2
	for name in part_names:
		part_objs[name].Geometries.createBlock(name='block_'+name+'_1' ,corner_marker = mar_objs[name] ,x=dis,y=dis,z=-part_thickness)
		part_objs[name].Geometries.createBlock(name='block_'+name+'_2' ,corner_marker = mar_objs[name] ,x=dis,y=-dis,z=-part_thickness)
		part_objs[name].Geometries.createBlock(name='block_'+name+'_3' ,corner_marker = mar_objs[name] ,x=-dis,y=-dis,z=-part_thickness)
		part_objs[name].Geometries.createBlock(name='block_'+name+'_4' ,corner_marker = mar_objs[name] ,x=-dis,y=dis,z=-part_thickness)


	spline_obj = {}
	# create spline
	for num,name in enumerate(part_names):
		data = rand_singel_general(t=10,hz=32,gain=1)
		# spline_obj[name] = model_obj.DataElements.createSpline(name = 'spline_'+name ,adams_id = num+1, 
		# 	x=[float(n)/10 for n in range(100)], y = [math.sin(float(n))*0.1 for n in range(100)]) 
		spline_obj[name] = model_obj.DataElements.createSpline(name = 'spline_'+name ,adams_id = num+1, 
			x=data[0], y = data[1] ) 
	print(data[0])
	# create motion
	for num,name in enumerate(part_names):
		if num < 3 :
			temp = model_obj.Constraints.createMotionT(name = 'motion_'+name, joint_name=const_objs['trans_'+name][0].name)
			temp.function = 'AKISPL(time,0,{}, 0)*9800'.format(spline_obj[name].full_name,name)
			temp.time_derivative = 'acceleration'
		else:
			temp = model_obj.Constraints.createMotionR(name = 'motion_'+name, joint_name=const_objs['rev_'+name[1]][0].name)
			temp.function = 'AKISPL(time,0,{}, 0)/180*PI'.format(spline_obj[name].full_name,name)
			temp.time_derivative = 'displacement'

	# measure 
	loc_lf = [100.0, -400.0, 250.0 ]
	loc_rf = [100.0, 400.0, 250.0]
	loc_lr = [700.0, -400.0, 250.0]
	loc_rr = [700.0, 400.0, 250.0]
	mar_lf_obj = create_marker(part_objs['rz'],'lf',loc_lf)
	mar_rf_obj = create_marker(part_objs['rz'],'rf',loc_rf)
	mar_lr_obj = create_marker(part_objs['rz'],'lr',loc_lr)
	mar_rr_obj = create_marker(part_objs['rz'],'rr',loc_rr)

	request_acc_marker('acc_lf',1,mar_lf_obj,mar_center_obj)
	request_acc_marker('acc_rf',2,mar_rf_obj,mar_center_obj)
	request_acc_marker('acc_lr',3,mar_lr_obj,mar_center_obj)
	request_acc_marker('acc_rr',4,mar_rr_obj,mar_center_obj)

	# create adm output
	# output_adm(model_name,model_name)

	print('-'*20,'end','-'*20)


if __name__ == "__main__":

	cmd_str = 'file python read file_name="{}"'.format(__file__)

	sys.path.append(r'..')
	import call.tcp_link as tcp_link
	tcp_link.cmd_send(cmd_str)

else:
	sys.path.append(r'D:\github\pycae\pyadams\view')
	from view_fun import *
	# run in adams 2017.2
	dof_six_xyz_create()


	


