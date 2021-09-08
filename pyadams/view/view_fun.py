# -*- coding: utf-8 -*-
'''
	python版本： 2.7
	adams python 模块应用
	主要针对 View 模块
	
'''

import os
import sys
import json
import re
import os.path
import shutil
import math

try:
	# Adams 模块需要在adams中调用
	import Adams
except:
	# 非ADAMS调用
	pass

# solve cmd设置 
CMD_SOLVE = '''
	executive set numerical model = .#model_name corrector = modified
	executive set numerical model = .#model_name error = 0.1
	executive set numerical model = .#model_name formulation = I3
	executive set numerical model = .#model_name integrator = GSTIFF
	executive set equilibrium model = .#model_name error = 0.1
	executive set equilibrium model = .#model_name maxit = 100
'''
# request cmd设置
CMD_REQUEST_ACC = '''
	output_control create request  &
   request_name = #request_name  &
   adams_id = #adams_id &
   f2 = "ACCX(#marker, #ground, #marker)/9806.65"  &
   f3 = "ACCY(#marker, #ground, #marker)/9806.65"  &
   f4 = "ACCZ(#marker, #ground, #marker)/9806.65" 
'''

CMD_ADM_CREATE = '''
	defaults adams_output  &
	statement_order = as_found_in_file  &
	arguments_per_line = single  &
	text_case = upper  &
	indent_spaces = 1  &
	write_default_values = off  &
	scientific_notation = -4,5  &
	trailing_zeros = off  &
	decimal_places = 10  &
	zero_threshold = 1e-15  &
	round_off = on  &
	significant_figures = 10  &
	export_all_graphics = off

	model verify model_name = .#model_name  &
	write_to_terminal = off

	file adams_data_set write  &
	model_name = .#model_name  &
	file_name = "#model_name"  &
	write_to_terminal = off

'''

# cmd 命令转化
def cmd_to_lines(str1):
	'''
		去掉cmd中的& 符号
		将命令转化为多个单行命令
	'''
	list1 = str1.split('\n')
	line = []
	list2 = []
	cmds = []
	for n in list1:
		if n:
			if '&' in n:
				line.append(n)
			else:
				line.append(n)
				list2.append(' '.join(line))
				line = []
		else:
			pass
			line = []

	for line in list2:
		cmds.append(line.replace('&',' '))
	
	return cmds

def cmds_run(str1,target_str,replace_str): # 处理文档并使用 adams运行cmds
	"""
		1、处理文档、
		2、ADAMS 运行 cmd
		str1 		:	主体cmd
		target_str	:	被替换目标
		replace_str	:	写入内容
	"""
	cmds = cmd_to_lines(str1.replace(target_str,replace_str))
	for line in cmds:
		Adams.execute_cmd(line)	

# loc cal 坐标计算------------------------------------------

def sum_point(point1,point2): # 坐标求和
	"""
		坐标求和
	"""
	new_point = [point1[n]+point2[n] for n in range(3)]
	# print(new_point)
	return new_point

def sub_point(point1,point2): # 坐标相减
	"""
		坐标相减
	"""
	new_point = [point1[n]-point2[n] for n in range(3)]
	
	return new_point

def gain_point(point1,gain): # 坐标 比例放大
	"""
		坐标放大，乘以系数gain
	"""
	new_point = [point1[n]*gain for n in range(3)]
	# print(new_point)
	return new_point

# loc cal ------------------------------------------

# part 部件设置------------------------------------------

def set_mass(partobj,markobj):
	# 设置质量
	# partobj part实例
	# markobj mark实例
	partobj.cm = markobj
	partobj.mass = 0.1
	partobj.ixx = 0.1
	partobj.iyy = 0.1
	partobj.izz = 0.1

# part ------------------------------------------

# mark & hardpoint  --------------------------------------------

def ori_z_two_point(obj,obj1,obj2):
	'''
		根据两点确定Z轴方向
		obj 目标调整对象 mark点
		obj1 点mark1实例对象
		obj2 点mark2实例对象
	'''

	str1 = 'ORI_ALONG_AXIS({}, {}, "z") '.format(
		obj1.name,obj2.name)
	obj.orientation = Adams.expression(str1)

def ori_two_mark(obj1,obj2):
	'''
		设置两个mark点，将其Z方向调整为一致，且为相互朝向
		obj1 点mark1的实例对象
		obj2 点mark2的实例对象
	'''
	ori_z_two_point(obj1,obj1,obj2)
	ori_z_two_point(obj2,obj2,obj1)

def ori_to_marker(obj,obj1):
	'''
		参照marker点
		obj 目标调整对象 mark点
		obj1 点mark1实例对象
	'''
	str1 = 'ORI_RELATIVE_TO({}, {}) '.format(
		'{0,0,0}',obj1.name)
	obj.orientation = Adams.expression(str1)

def loc_to_marker(obj,obj1):
	'''
		参照marker点
		obj 目标调整对象 mark点
		obj1 点mark1实例对象
	'''
	str1 = 'LOC_RELATIVE_TO({}, {}) '.format(
		'{0,0,0}',obj1.name)
	obj.location = Adams.expression(str1)

def loc_on_line(obj,obj1,obj2,ratio=0.5):
	'''
		设置点坐标在两点连线之间
		obj 目标调整对象
		obj1 点1 实例对象
		obj2 点2 实例对象
		ratio 所在位置 ， 0.5则为在中间
	'''

	str1 = "LOC_ALONG_LINE({}, {}, DM({},{})*{}) ".format(
		obj1.name,obj2.name,obj1.name,obj2.name,ratio)
	obj.location = Adams.expression(str1)

# mark & hardpoint  --------------------------------------------

# constraint --------------------------------------------
def translational_center_create(model_obj,part1,part2,markobj1,markobj2,name):
	'''
		滑动副创建
		model_obj 为模型model的实例对象
		part1 为部件1的实例对象
		part2 为部件2的实例对象
		markobj1 为坐标点1的mark实例,主要为提取坐标点
		markobj2 为坐标点2的mark实例,主要为提取坐标点
		name 滑动副名称

	'''
	i_marker = part1.Markers.create(name = 'mar_'+name+'_i')
	j_marker = part2.Markers.create(name = 'mar_'+name+'_j')
	# ori_z_two_point(i_marker,i_marker,j_marker)
	# ori_z_two_point(j_marker,i_marker,j_marker)
	ori_z_two_point(i_marker,markobj1,markobj2)
	ori_z_two_point(j_marker,markobj1,markobj2)
	# print(markobj1.name)
	loc_on_line(i_marker,markobj1,markobj2,0.5)
	loc_on_line(j_marker,markobj1,markobj2,0.5)
	return model_obj.Constraints.createTranslational(name=name, i_marker=i_marker, j_marker=j_marker) 

def fixed_create(model_obj,part1,part2,marobj,name):
	'''
		创建固定副
		model_obj 为模型model的实例对象
		part1 为部件1的实例对象
		part2 为部件2的实例对象
		markobj 为固定坐标点的mark实例
		name 为固定副名称
	'''
	i_marker = part1.Markers.create(name = 'mar_'+name+'_i',location = marobj.location)
	j_marker = part2.Markers.create(name = 'mar_'+name+'_j',location = marobj.location)
	return model_obj.Constraints.createFixed(name=name, i_marker=i_marker, j_marker=j_marker) 

def spherical_create(model_obj,part1,part2,marobj,name):
	'''
		创建球铰副
		model_obj 为模型model的实例对象
		创建固定副
		part1 为部件1的实例对象
		part2 为部件2的实例对象
		markobj 为固定坐标点的mark实例
		name 为固定副名称
	'''
	i_marker = part1.Markers.create(name = 'mar_'+name+'_i',location = marobj.location)
	j_marker = part2.Markers.create(name = 'mar_'+name+'_j',location = marobj.location)
	return model_obj.Constraints.createSpherical(name=name, i_marker=i_marker, j_marker=j_marker) 

# constraint --------------------------------------------

# force --------------------------------------------------

def bushing_create(model_obj,part1,part2,markerobj,stiffness,tstiffness,name):
	'''
		创建bushing
		model_obj 模型实例
		part1 部件1 实例
		part1 部件2 实例
		markerobj 参考marker点 实例
		stiffness 刚度  XYZ
		tstiffness 扭转刚度 
		name 名称
	'''
	i_marker = part1.Markers.create(name = 'mar_'+name+'_i')
	j_marker = part2.Markers.create(name = 'mar_'+name+'_j')
	ori_to_marker(i_marker,markerobj)
	ori_to_marker(j_marker,markerobj)
	loc_to_marker(i_marker,markerobj)
	loc_to_marker(j_marker,markerobj)
	# i_marker = 
	bushobj = model_obj.Forces.createBushing(name=name, 
		i_marker=i_marker, 
		j_marker=j_marker, 
		stiffness=stiffness,
		tstiffness=tstiffness,
		# damping=[50,50,50],
		# tdamping=[50,50,50]
		)
	return bushobj

# force --------------------------------------------------


class Viewmodel: # view
	def __init__(self,model_name):
		'''
			model_name 创建模型名称
		'''
		path = os.getcwd()
		sys.path.append(path)

		d = Adams.defaults
		d.units.length = 'mm'
		d.units.mass = 'kg'
		d.units.time = 'second'
		d.units.angle = 'degrees'
		d.units.force = 'newton'
		try:
			model_obj = Adams.Models.create(name = model_name )
		except:
			Adams.Models[model_name].destroy()
			# print('model_obj.destroy()')
			model_obj = Adams.Models.create(name = model_name )
		else:
			model_obj = Adams.getCurrentModel()
			# print('model_obj = Adams.getCurrentModel()')
			model_obj.destroy()
			# print('model_obj.destroy()')
			model_obj = Adams.Models.create(name = model_name )

		self.gravity = model_obj.Forces.createGravity(name='gravity', 
			xyz_component_gravity = [0 ,0 , -9806.65])

		self.model_name = model_name # 模型名称
		self.defaults = d
		self.model= model_obj # 模型实例
		self.part = {} # 部件 实例
		self.marker = {} # marker 实例
		self.hardpoint = {} # 硬点 实例
		self.bushing = {} # 衬套 实例
		self.spherical = {} # 球铰副 实例
		self.revolute = {} # 旋转副 实例
		self.fixed = {} # 固定副实例
		self.translational = {} # 
		self.geometry = {}
		self.ground = model_obj.Parts['ground']
		self.spline = {}
		self.motionT = {}
		self.request = []
		self.marker['ground'] = self.ground.Markers.create(name = 'mar_ground')

		# self.flexbody = {}

	def createRigidBody(self,name):
		'''
			创建刚性体
		'''
		self.part[name] = self.model.Parts.createRigidBody(name = 'part_'+name)
		self.marker[name] = self.part[name].Markers.create(name = 'mar_'+name)
		self.part[name].cm = self.marker[name]
		self.part[name].mass = 0.1
		self.part[name].ixx = 0.1
		self.part[name].iyy = 0.1
		self.part[name].izz = 0.1
		return self.part[name],self.marker[name]

	def createHardpoint(self,name,loc):
		'''
			创建硬点
		'''
		self.hardpoint[name] = self.ground.DesignPoints.create(name='hp_'+name)
		self.hardpoint[name].location = loc
		return self.hardpoint[name]

	def createMarker(self,name,partname,location=None):
		if location==None:
			self.marker[name] = self.part[partname].Markers.create(name = 'mar_'+name)
		else:
			self.marker[name] = self.part[partname].Markers.create(name = 'mar_'+name ,location = location)
		return self.marker[name]

	def createFlexbody(self,name,filepath):
		'''
			创建 柔性体
		'''
		self.part[name] = self.model.Parts.createFlexBody(name=name, modal_neutral_file_name = filepath) 
		return self.part[name]

	def set_flex_marker_node(self,markername,flexname,node_id):
		'''
			name 
		'''
		marker_name = '.'+self.model_name + '.' + self.part[flexname].name + '.' + self.marker[markername].name
		Adams.execute_cmd('marker modify marker_name = {}  node_id = {}'.format(marker_name,node_id))

	def bushing_flex_create(self,flexname,partname,markername,stiffness,tstiffness,name,node_id):
		'''
			创建bushing
			flexobj 柔性体部件1 实例
			part1 部件2 实例
			markername 参考marker点 字典关键词
			stiffness 刚度  XYZ
			tstiffness 扭转刚度 
			name 名称
		'''
		i_marker = self.part[flexname].Markers.create(name = 'mar_'+name+'_i')
		j_marker = self.part[partname].Markers.create(name = 'mar_'+name+'_j')
		ori_to_marker(i_marker,self.marker[markername])
		ori_to_marker(j_marker,self.marker[markername])
		loc_to_marker(i_marker,self.marker[markername])
		loc_to_marker(j_marker,self.marker[markername])

		# node id 设置

		marker_name = '.'+self.model_name + '.' + self.part[flexname].name + '.' + i_marker.name
		Adams.execute_cmd('marker modify marker_name = {}  node_id = {}'.format(marker_name,node_id))
		# self.set_flex_marker_node(i_marker.name,flexname,node_id)

		# i_marker = 
		bushobj = self.model.Forces.createBushing(name=name, 
			i_marker=i_marker, 
			j_marker=j_marker, 
			stiffness=stiffness,
			tstiffness=tstiffness)

		return bushobj

	def createMarkerFlex(self,markername,flexname,node_id):
		'''
			在柔性体中创建 marker
			marker 名称
			flexname 柔性体名称
			node_id 
		'''
		self.createMarker(markername,flexname)
		self.set_flex_marker_node(markername,flexname,node_id)

	def createRequestAcc(self,requestname,markername):
		'''
			创建request 测量点 加速度
			20210416
		'''
		adams_id = len(self.request) + 1
		self.request.append(requestname)
		str1 = CMD_REQUEST_ACC.replace('#request_name',requestname)
		str1 = str1.replace('#ground',self.marker['ground'].name)
		str1 = str1.replace('#marker',self.marker[markername].name)
		str1 = str1.replace('#adams_id',str(adams_id))
		for line in cmd_to_lines(str1):
			Adams.execute_cmd(line)

	def createRevolute(self,name,partname_i,partname_j,location=None,orientation=None):
		"""
			旋转副创建
			刚性体建创建
			name 旋转副名称
			partname_i 部件名称
			partname_j 部件名称
		"""
		i_marker = self.part[partname_i].Markers.create(name = 'mar_'+name+'_i')		
		if type(orientation) == type(i_marker):
			ori_to_marker(i_marker,orientation)
		elif type(orientation)==list:
			i_marker.orientation = orientation
		else:
			i_marker.orientation = [0,0,0]

		if location == None:
			location = [0,0,0]
		elif type(location) == type(i_marker):
			loc_to_marker(i_marker,location)
		elif type(location) == list:
			i_marker.location = location
		# 差 points

		j_marker = self.part[partname_j].Markers.create(name = 'mar_'+name+'_j')
		ori_to_marker(j_marker,i_marker)
		loc_to_marker(j_marker,i_marker)

		self.revolute[name] = self.model.Constraints.createRevolute(name=name, i_marker=i_marker, j_marker=j_marker)

		return self.revolute[name]



	def createBushing(self,part1name,part2name,markername,stiffness,tstiffness,name):
		'''
			创建bushing
			刚性体之间
			model 模型实例
			part1name 部件1 名称
			part2name 部件2 名称
			markername 参考marker点 名称
			stiffness 刚度  XYZ
			tstiffness 扭转刚度 
			name 名称
		'''
		i_marker = self.part[part1name].Markers.create(name = 'mar_'+name+'_i')
		j_marker = self.part[part2name].Markers.create(name = 'mar_'+name+'_j')
		markerobj = self.marker[markername]
		ori_to_marker(i_marker,markerobj)
		ori_to_marker(j_marker,markerobj)
		loc_to_marker(i_marker,markerobj)
		loc_to_marker(j_marker,markerobj)
		bushobj = self.model.Forces.createBushing(name='bus_'+name, 
			i_marker=i_marker, 
			j_marker=j_marker, 
			stiffness=stiffness,
			tstiffness=tstiffness,
			damping=[0,0,0],
			tdamping=[0,0,0])
		self.bushing[name] = bushobj

		return bushobj

	def createSpherical(self,part1name,part2name,markername,name):
		'''
			创建球铰副
			model 为模型model的实例对象
			创建固定副
			part1name 为部件1的实例对象 名称
			part2name 为部件2的实例对象 名称
			markername 为固定坐标点的mark实例 名称 
			name 为固定副名称
		'''
		marobj = self.marker[markername]
		i_marker = self.part[part1name].Markers.create(name = 'mar_'+name+'_i',location = marobj.location)
		j_marker = self.part[part2name].Markers.create(name = 'mar_'+name+'_j',location = marobj.location)
		self.spherical[name] = self.model.Constraints.createSpherical(name='spher_'+name, i_marker=i_marker, j_marker=j_marker) 
		return self.spherical[name]


