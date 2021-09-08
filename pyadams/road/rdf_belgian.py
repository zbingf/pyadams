"""
	比利时路 1.0
	
	单个石块 → 单行石块 →多行石块

	2021/05/21

"""
from pyadams.road import rdf_road
import random
import logging

def pe_belgian_road_single2(size, init_loc, edge):
	"""
		单个石块
	"""
	x0, y0, z0 = init_loc 		# 初始中心位置
	x_edge, y_edge = edge 		# 包含边缘的尺寸
	x_len, y_len, z_len = size 	# 块各方向尺寸

	points = [
		[1, 	x0-x_len/2,	y0+y_len/2,	z0],
		[2, 	x0-x_len/2,	y0-y_len/2,	z0],
		[3, 	x0+x_len/2,	y0+y_len/2,	z0],
		[4, 	x0+x_len/2,	y0-y_len/2,	z0],
		[5, 	x0-x_len/2, y0+y_len/2, z0+z_len],
		[6, 	x0-x_len/2, y0-y_len/2, z0+z_len],
		[7, 	x0+x_len/2, y0+y_len/2, z0+z_len],
		[8, 	x0+x_len/2, y0-y_len/2, z0+z_len],
		[9, 	x0-x_edge/2,y0+y_edge/2,z0],
		[10, 	x0-x_edge/2,y0-y_edge/2,z0],
		[11, 	x0+x_edge/2,y0+y_edge/2,z0],
		[12, 	x0+x_edge/2,y0-y_edge/2,z0],
	]

	elements = [
		[5,6,7,1.0],
		[6,7,8,1.0],
		[1,3,5,1.0],
		[3,5,7,1.0],
		[3,4,7,1.0],
		[4,7,8,1.0],
		[2,4,6,1.0],
		[4,6,8,1.0],
		[1,2,5,1.0],
		[2,5,6,1.0],
		[1,2,9,1.0],
		[2,9,10,1.0],
		[1,3,9,1.0],
		[3,9,11,1.0],
		[3,4,11,1.0],
		[4,11,12,1.0],
		[2,4,10,1.0],
		[4,10,12,1.0],
	]
	return points, elements

def pe_belgian_road_single(size, init_loc, edge, d_chamfer=6):
	"""
		单个石块
		带倒角
		points, element生成
	"""
	# d_chamfer = 3

	x0, y0, z0 = init_loc 		# 初始中心位置
	x_edge, y_edge = edge 		# 包含边缘的尺寸
	x_len, y_len, z_len = size 	# 块各方向尺寸
	
	points = [
		[1, 	x0-x_len/2,	y0+y_len/2,	z0],
		[2, 	x0-x_len/2,	y0-y_len/2,	z0],
		[3, 	x0+x_len/2,	y0+y_len/2,	z0],
		[4, 	x0+x_len/2,	y0-y_len/2,	z0],
		[5, 	x0-x_len/2, y0+y_len/2, z0+z_len-d_chamfer],
		[6, 	x0-x_len/2, y0-y_len/2, z0+z_len-d_chamfer],
		[7, 	x0+x_len/2, y0+y_len/2, z0+z_len-d_chamfer],
		[8, 	x0+x_len/2, y0-y_len/2, z0+z_len-d_chamfer],
		[9, 	x0-x_edge/2,y0+y_edge/2,z0],
		[10, 	x0-x_edge/2,y0-y_edge/2,z0],
		[11, 	x0+x_edge/2,y0+y_edge/2,z0],
		[12, 	x0+x_edge/2,y0-y_edge/2,z0],

		[13, 	x0-x_len/2+d_chamfer, y0+y_len/2-d_chamfer, z0+z_len],
		[14, 	x0-x_len/2+d_chamfer, y0-y_len/2+d_chamfer, z0+z_len],
		[15, 	x0+x_len/2-d_chamfer, y0+y_len/2-d_chamfer, z0+z_len],
		[16, 	x0+x_len/2-d_chamfer, y0-y_len/2+d_chamfer, z0+z_len],
	]

	elements = [
		# [5,6,7,1.0],
		# [6,7,8,1.0],
		[13,14,15,1.0],
		[14,15,16,1.0],

		[1,3,5,1.0],
		[3,5,7,1.0],
		[3,4,7,1.0],
		[4,7,8,1.0],
		[2,4,6,1.0],
		[4,6,8,1.0],
		[1,2,5,1.0],
		[2,5,6,1.0],
		[1,2,9,1.0],
		[2,9,10,1.0],
		[1,3,9,1.0],
		[3,9,11,1.0],
		[3,4,11,1.0],
		[4,11,12,1.0],
		[2,4,10,1.0],
		[4,10,12,1.0],

		[5,6,13,1.0],
		[6,13,14,1.0],

		[5,7,13,1.0],
		[7,13,15,1.0],

		[7,8,15,1.0],
		[8,15,16,1.0],

		[6,8,14,1.0],
		[8,14,16,1.0],
	]
	return points, elements

def pe_belgian_road_line(n_line, x_init, x_set, y_set, z_set, y_edge_set, x_edge_set):
	"""
		单行石块路
		points, element生成
	"""
	fun_random = lambda a1, a2: a1 + a2*random.random()
	x_len1, x_len2 = x_set
	y_len1, y_len2 = y_set
	z_len1, z_len2 = z_set
	edge_offset1, edge_offset2 = y_edge_set
	
	x_edge = x_len1 + x_len2 + x_edge_set


	x_loc = x_init
	z_loc = 0
	y_loc = -n_line * (y_len1+y_len2/2)/2


	rdf_road_obj = rdf_road.RoadBuild()

	for n in range(n_line):
		x_len = fun_random(x_len1, x_len2)
		y_len = fun_random(y_len1, y_len2)
		z_len = fun_random(z_len1, z_len2)
		if n == 0:
			y_edge = y_len + fun_random(edge_offset1, edge_offset2)
			y_edge_old = y_edge
		else:
			y_edge = y_len + fun_random(edge_offset1, edge_offset2)

		y_loc += (y_edge + y_edge_old)/2 +1
		y_edge_old = y_edge

		params = {
			'size': [x_len, y_len, z_len],
			'init_loc':[x_loc, y_loc, z_loc],
			'edge':[x_edge, y_edge],
		}

		points, elements = pe_belgian_road_single(**params)

		obj1 = rdf_road.RoadElement(points=points, elements=elements)
		rdf_road_obj.add_roadelement(obj1)

	rdf_road_obj.set_element_join_y()

	points, elements = rdf_road_obj.get_points_elements()

	return points, elements

def pe_belgian_road(num, n_line, x_init, x_set, y_set, z_set, y_edge_set, x_edge_set):
	"""
		比利时路面 
		points, element生成
	"""
	rdf_road_obj = rdf_road.RoadBuild()
	x_edge = sum(x_set) + x_edge_set
	x_init_loc = x_init

	for n in range(num):
		x_init_loc += x_edge+1
		if divmod(n,2)[-1]==1:
			n_line_new = n_line
		else:
			n_line_new = n_line-1

		params = {
			'n_line':n_line_new,
			'x_init':x_init_loc,
			'x_set':x_set,
			'y_set':y_set,
			'z_set':z_set,
			'y_edge_set':y_edge_set,
			'x_edge_set':x_edge_set,
		}
		points, elements = pe_belgian_road_line(**params)
		obj1 = rdf_road.RoadElement(points=points, elements=elements)
		rdf_road_obj.add_roadelement(obj1)

	rdf_road_obj.set_element_join_x() 	# x向拼接

	points, elements = rdf_road_obj.get_points_elements()

	return points, elements

def rdf_belgian(rdf_path, x_set, y_set, z_set, x_edge_set, y_edge_set, belgian_len, width, 
			x_start_belgian, x_front, x_rear):
	"""
		比利时路创建
		输入参数:
			rdf_path 		目标rdf路径
			x_set 			x方向设置 [基础长度, 波动长度]
			y_set 			y方向设置 [基础长度, 波动长度]
			z_set 			z方向设置 [基础长度, 波动长度]
			x_edge_set 		边界X向长度 float
			y_edge_set 		边界y向长度  [基础边界, 波动边界]
			belgian_len 	比利时路长度
			width 			比利时路宽度
			x_start_belgian 比利时路X开始位置,向前
			x_front 		x前方路面结尾位置,向前
			x_rear 			x后方路面结尾位置,向后 
	"""

	# rdf_path = r'D:\document\ADAMS\test_road_rdf.rdf'
	# x_set = [60,10] 	# 石块x向长度 
	# y_set = [100,20]	# 石块y向长度 
	# z_set = [25.2,10]	# 石块z向长度 
	# y_edge_set = [5,3]	# 边界y向长度 
	# x_edge_set = 4 		# 边界x向长度
	# belgian_len = 30000 # 比利时路长度 mm
	# width = 6000 		# 比利时路宽度 mm

	"""
		第一段, 车辆行驶末端平面, 	x0
		第二段, 比利时路结尾平面, 	x1
		第三段, 比利时路末端, 		x2
		第四段, 比利时路开头, 		x3
		第五段, 比利时路开头平面, 	x4
		第六段, 车辆尾部结尾平面, 	x5
	"""

	x0 = -x_front 			# 路面结尾位置 mm
	x3 = -x_start_belgian 	# 比利时起始位置 mm
	x5 = x_rear  			# 车辆尾部路面结尾位置 mm

	x4 = x3 + 1500 	# 开始位置
	x2 = x3 - belgian_len
	x1 = x2 - 1500

	y_line = y_set[0] + y_set[1]/2 + y_edge_set[0] + y_edge_set[1]/2
	n_line = int(width/y_line)

	x_line = sum(x_set) + x_edge_set
	num = int(belgian_len/x_line)

	params = {
		'num':num,
		'n_line':n_line,
		'x_init':x2,
		'x_set':x_set,
		'y_set':y_set,
		'z_set':z_set,
		'y_edge_set':y_edge_set,
		'x_edge_set':x_edge_set,
	}

	points, elements = pe_belgian_road(**params)
	rdf_road_obj = rdf_road.RoadBuild(rdf_path)
	obj1 = rdf_road.RoadElement(points=points, elements=elements, move_id=1)
	
	# 平面参数
	flat_dic = {
		'length':1000,
		'width':8000,
		'f':1,
		'x0':x0,
		'y0':0,
		'z0':0,
	}
	rdf_road_obj.add_roadelement(rdf_road.RoadFlat(flat_dic)) 
	
	flat_dic['x0'] = x1
	rdf_road_obj.add_roadelement(rdf_road.RoadFlat(flat_dic)) 

	rdf_road_obj.add_roadelement(obj1) 	# 比利时路面

	flat_dic['x0'] = x4
	rdf_road_obj.add_roadelement(rdf_road.RoadFlat(flat_dic))
	flat_dic['x0'] = x5
	rdf_road_obj.add_roadelement(rdf_road.RoadFlat(flat_dic))
	
	rdf_road_obj.set_element_join_x()
	rdf_road_obj.create(isXYChange=False)

	return None

def test_single():
	"""单个石块测试"""
	points, elements = pe_belgian_road_single([50,50,50],[0,0,0],[100,100])
	rdf_path = r'D:\document\ADAMS\test_road_rdf.rdf'
	rdf_road_obj = rdf_road.RoadBuild(rdf_path)
	obj1 = rdf_road.RoadElement(points=points, elements=elements, move_id=1)
	rdf_road_obj.add_roadelement(obj1)
	rdf_road_obj.create(isXYChange=False)

def test_line():
	"""单行石块测试"""
	params = {
		'n_line':70,
		'x_init':0,
		'x_set':[50,10],
		'y_set':[80,20],
		'z_set':[25.2,10],
		'edge_set':[20,3],
	}
	points, elements = pe_belgian_road_line(**params)
	rdf_path = r'D:\document\ADAMS\test_road_rdf.rdf'
	rdf_road_obj = rdf_road.RoadBuild(rdf_path)
	obj1 = rdf_road.RoadElement(points=points, elements=elements, move_id=1)
	rdf_road_obj.add_roadelement(obj1)
	rdf_road_obj.create(isXYChange=False)

def test_belgian():

	rdf_path = r'D:\document\ADAMS\test_road_rdf.rdf'
	x_set = [80,20] 	# 石块x向长度 
	y_set = [140,50]	# 石块y向长度 
	z_set = [25.2,10]	# 石块z向长度 
	y_edge_set = [5,3]	# 边界y向长度 
	x_edge_set = 1 		# 边界x向长度
	belgian_len = 30000 # 比利时路长度 mm
	width = 5000 		# 比利时路宽度 mm

	x_start_belgian = 5000
	x_front = 100000
	x_rear 	= 20000

	rdf_belgian(rdf_path, x_set, y_set, z_set, x_edge_set, y_edge_set, belgian_len, width, 
		x_start_belgian, x_front, x_rear)

# test_single()
# test_line()
# rdf_belgian()

test_belgian()
