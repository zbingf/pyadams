"""
	RDF格式路面-创建模块

	node 为 对象
	point 为 列表
	triangle 为对象
	element 为 列表
	roadelement 为对象 路面子模块
	roadbuild 为对象 路面rdf主模块
"""
from math import *
import numpy as np
from scipy.spatial import Delaunay
import copy
import logging

# 文件开头
RDF_START = """$---------------------------------------------------------------------MDI_HEADER
[MDI_HEADER]
FILE_TYPE  =  'rdf'
FILE_VERSION  =  5.00
FILE_FORMAT  =  'ASCII'
(COMMENTS)
{comment_string)
'Big bump for testing durability tire.'
$--------------------------------------------------------------------------units
[UNITS]
 LENGTH             = 'mm'
 FORCE              = 'newton'
 ANGLE              = 'radian'
 MASS               = 'kg'
 TIME               = 'sec'
$---------------------------------------------------------------------definition
[MODEL]
 METHOD             = '3D'
 FUNCTION_NAME      = 'ARC904'
$-------------------------------------------------------------------------offset
[REFSYS]
 OFFSET                   =  0.0 0.0 0.0
 ROTATION_ANGLE_XY_PLANE  =  0.0
$--------------------------------------------------------------------------nodes
[NODES]
 NUMBER_OF_NODES    = #num_nodes
{ node   x_value   y_value   z_value }
#nodes_data
$-----------------------------------------------------------------------elements
[ELEMENTS]
 NUMBER_OF_ELEMENTS    = #num_elements
{ node_1   node_2  node_3   mu }
#elements_data
"""

class Node:	
	""" 
		Node点 
		若 node_id, x, y, z 数值都一样则不生成实例
	"""
	objs = {}	# {(node_id, x, y, z):obj,...}

	def __new__(cls, node_id, x, y, z):
		obj_key = (node_id, x, y, z)
		if obj_key not in cls.objs:
			obj = object.__new__(cls)
			cls.objs[obj_key] = obj
			return obj
		else:
			return cls.objs[obj_key]

	def __init__(self, node_id, x, y, z):
		self.node_id = node_id
		self.x = x
		self.y = y
		self.z = z
		self.get_point()
		self.key = tuple(self.point)

	def set_move_location(self, x=0, y=0, z=0):
		""" 设置坐标xyz 偏移 """
		self.x += x
		self.y += y
		self.z += z
		self.get_point()
		self.updata_key()

	def set_move_id(self,num_int):
		""" 设置id 偏移 """
		self.node_id += num_int
		self.get_point()
		# print(self.point)
		self.updata_key()

	def set_id(self,num_int):
		""" 设置id 赋值"""
		self.node_id = num_int
		self.get_point()
		self.updata_key()

	def get_point(self):
		""" 获取point """
		self.point = [self.node_id, self.x, self.y, self.z]
		return self.point

	def updata_key(self):
		""" 更新objs的key """
		key = self.key
		new_key = tuple(self.point)
		Node.objs[new_key] = Node.objs.pop(key)
		self.key = new_key


class Triangle:
	""" 
		三角网格 
		存储node实例 和 摩擦系数
	"""
	def __init__(self, node1, node2, node3, friction):

		if isinstance(node1,Node):
			self.node1 = node1
			self.node2 = node2
			self.node3 = node3
		else:
			self.node1 = Node(*node1)
			self.node2 = Node(*node2)
			self.node3 = Node(*node3)

		self.friction = friction

	def set_move_location(self, x=0, y=0, z=0):
		""" 设置坐标xyz 偏移 """
		self.node1.set_move_location(x, y, z)
		self.node2.set_move_location(x, y, z)
		self.node3.set_move_location(x, y, z)

	def set_move_id(self,num_int):
		""" 设置node id 整体偏移 """
		self.node1.set_move_id(num_int)
		self.node2.set_move_id(num_int)
		self.node3.set_move_id(num_int)

	def set_friction(self,friction):
		""" 摩擦系数 """
		self.friction = friction

	def get_node_objs(self):
		""" 获取node实例 """
		return [self.node1,self.node2,self.node3]

	def get_points(self):
		""" 获取node的points数据 """
		point1 = self.node1.get_point()
		point2 = self.node2.get_point()
		point3 = self.node3.get_point()
		self.points = [point1, point2, point3]
		return self.points

	def get_element(self):
		""" 获取emlemet数据 """
		self.element = [self.node1.node_id, self.node2.node_id, self.node3.node_id, self.friction]
		return self.element


class RoadElement:
	""" 
		路面单元 
		生成与存储三角网格
	"""

	def __init__(self, triangles=None, points=None, elements=None, move_id=0):

		# self.points = points
		# self.elements = elements
		self.node_xmax = []
		self.node_xmin = []
		self.node_ymax = []
		self.node_ymin = []
		
		self.nodes = []
		self.node_id_end = None  # 最大id号
		self.angle_x = 0
		self.angle_y = 0

		if isinstance(triangles,list):
			if isinstance(triangles[0],Triangle):
				self.triangles = triangles
				# print('self.triangles')
		if points!=None and elements!=None:
			for point in points: 
				point[0] = point[0]+move_id
			for element in elements:
				element[0] = element[0]+move_id
				element[1] = element[1]+move_id
				element[2] = element[2]+move_id

			self.set_triangles(points,elements)

	def set_triangles(self,points,elements):
		""" 
			points, elements 	输入
			设置 self.triangles
		"""
		self.triangles = []
		# print(points[0])
		for element in elements:
			triangle_param = []
			for n in range(3):
				p_loc = element[n] - points[0][0] 
				# print(element[n],points[p_loc][0])
				# assert element[n]==points[p_loc][0] ,"points顺序不对"
				triangle_param.append(points[p_loc]) 
			triangle_param.append(element[3])

			self.triangles.append(Triangle(*triangle_param)) 

		self.get_points()
		self.get_elements()

	def set_move_location(self, x=0, y=0, z=0):
		""" 设置坐标xyz 偏移 """
		if not self.nodes:
			self.get_nodes()
		for node in self.nodes:
			node.set_move_location(x, y, z)

		self.get_points()

	def set_move_id(self,num_int):
		""" 设置node id 整体偏移 """
		if not self.nodes:
			self.get_nodes()
		for node in self.nodes:
			node.set_move_id(num_int)

		self.get_points()
		self.get_elements()

	def get_nodes(self):
		""" 获取node实例 去重 """
		self.nodes = []
		for triangle_obj in self.triangles:
			self.nodes += triangle_obj.get_node_objs()

		self.nodes = list(set(self.nodes))

		return self.nodes

	def get_points(self):
		""" 获取points 去重 排序"""
		if not self.nodes:
			self.get_nodes()
		self.points = []
		for node_obj in self.nodes:
			self.points.append(node_obj.get_point())

		self.points = sorted(self.points,key=lambda list1:list1[0])

		self.node_id_end = self.points[-1][0]

		return self.points

	def get_elements(self):
		""" 获取 """

		self.elements = []
		for triangle_obj in self.triangles:
			self.elements.append(triangle_obj.get_element())
		return self.elements

	def get_locations(self, isReload=False):
		""" 获取坐标数据 """
		if isReload:
			self.get_points()
		if self.points == None:
			self.get_points()

		points = self.points
		xs = [line[1] for line in points]
		ys = [line[2] for line in points]
		zs = [line[3] for line in points]
		return xs, ys, zs

	def get_direction_x_point(self,angle=None,d=0.01):
		'''
			检索端点 , 指定方向
			根据指定方向进行检索，搜索该方向上的最大值和最小值
			对应含义：头部和尾部
			输入数据:
				ori 	int 	指定方向 :  x,y,z 分别对应 1,2,3
				angle 	float 	角度deg单位, 坐标绕Z轴旋转
				d 		float 	判定偏差范围 
			
			返回数据:
				p_mins 	list 	头部, points
				p_maxs 	list 	尾部, points

		'''
		ori = 1

		self.get_points() # 获取 self.point
		if angle == None:
			angle = self.angle_x
		else:
			self.angle_x = angle

		if angle != None:
			angle = -angle
			# import copy
			new_point = copy.deepcopy(self.points)
			# print(new_point[0])
			for line in new_point:
				_,x,y,z = self.axis_rotate_z(line,angle,x0=0,y0=0)
				# line[1],line[2],line[3] = x,y,z
				line[1] = x

			# print(new_point[0])
			targets = [line[ori] for line in new_point]
		else:
			targets = [line[ori] for line in self.points]

		val_max = max(targets)
		val_min = min(targets)

		p_maxs = []
		p_mins = []
		for loc,val in enumerate(targets):
			if abs(val-val_max) < d:
				p_maxs.append(self.points[loc])
			if abs(val-val_min) < d:
				p_mins.append(self.points[loc])

		for p_min, p_max in zip(p_mins, p_maxs):
			self.node_xmax.append(Node.objs[tuple(p_max)])
			self.node_xmin.append(Node.objs[tuple(p_min)])

		return p_mins,p_maxs

	def get_direction_y_point(self,angle=None,d=0.01):
		'''
			检索端点 , 指定方向
			根据指定方向进行检索，搜索该方向上的最大值和最小值
			对应含义：头部和尾部
			输入数据:
				ori 	int 	指定方向 :  x,y,z 分别对应 1,2,3
				angle 	float 	角度deg单位, 坐标绕Z轴旋转
				d 		float 	判定偏差范围 
			
			返回数据:
				p_mins 	list 	头部, points
				p_maxs 	list 	尾部, points

		'''
		ori = 2

		self.get_points() # 获取 self.point
		# if angle == None:
		# 	angle = self.angle_y
		# else:
		# 	self.angle_y = angle

		# if angle != None:
		# 	angle = -angle
		# 	import copy
		# 	new_point = copy.deepcopy(self.points)
		# 	# print(new_point[0:2])
		# 	print(new_point[0])
		# 	for line in new_point:
		# 		_,x,y,z = self.loc_rotate_z(line,angle,x0=0,y0=0)
		# 		line[1],line[2],line[3] = x,y,z
		# 	# print(new_point[0:2])
		# 	targets = [line[ori] for line in new_point]
		# 	# print('angle:',angle)
		# 	print(new_point[0])
		# else:
		# 	targets = [line[ori] for line in self.points]

		targets = [line[ori] for line in self.points]

		val_max = max(targets)
		val_min = min(targets)

		p_maxs = []
		p_mins = []
		for loc,val in enumerate(targets):
			if abs(val-val_max) < d:
				# print(val)
				p_maxs.append(self.points[loc])
				# print(self.points[loc])
			if abs(val-val_min) < d:
				p_mins.append(self.points[loc])

		for p_min, p_max in zip(p_mins, p_maxs):
			self.node_ymax.append(Node.objs[tuple(p_max)])
			self.node_ymin.append(Node.objs[tuple(p_min)])
		
		# print('--------get_direction_y_point--------')
		# print('sum targets:',sum(targets),'target[0]:',targets[0])
		# print('points[0]:',self.points[0])
		# print('len(targets):',len(targets),'len(self.points)',len(self.points))
		# print('val_min:',val_min,'val_max:',val_max)
		# print('p_mins[0]:',p_mins[0],'p_maxs[0]:',p_maxs[0])
		# print('----------------')

		return p_mins,p_maxs

	@staticmethod
	def road_center_line(x_list,y_list,z_list,width,f,angle): # 根据中心线创建 倾斜面 X朝向
		"""
			用于根据中心线生辰左右一直的路面

			x,y,z 	list 	[float,float,...]
							为中线上的点的坐标 mm
			width 	float 	路面宽度 mm
			f 		float 	相对附着系数
			angle 	float 	角度deg, y方向的线段数据, 绕z轴旋转
							根据斜角 angle 计算左右X向差值
			
			导出 硬点及拼接数据
			
			ps对应points 		list 	points列表数据 
								格式为 [[编号 x y z],[编号 x y z],...]

			es 为 elements列表数据
				格式为 [[point编号1,point编号2,point编号3],...]

		"""
		n = 1
		ps = []
		es = []
		for x,y,z in zip(x_list,y_list,z_list):
			x0 = x + tan(angle/180*pi) * width/2
			y0 = y - width/2
			ps.append([n,x0,y0,z])
			n += 1
			x1 = x + -tan(angle/180*pi) * width/2
			y1 = y + width/2
			ps.append([n,x1,y1,z])
			n += 1

		for num in range(len(ps)):
			if num > len(ps)-3:
				break
			es.append([num+1 , num+2, num+3, f])

		return ps,es

	@staticmethod
	def axis_rotate_z(point, angle, x0=0, y0=0):
		"""
			坐标轴 坐标轴 绕Z轴旋转, 逆时针!!, 逆时针!!
			输入数据:
				point 	list 	[编号 x y z]
				angle 	float	旋转角度
				x0 		float 	
				y0 		float 	
			输出数据:
				point 	list 	[编号 x y z] , 旋转后坐标
		"""
		rad = angle/180*pi

		x = point[1]
		y = point[2]
		new_x = x*cos(rad) - y*sin(rad) + x0
		# new_y = x*sin(rad) - y*cos(rad) + y0
		new_y = y*cos(rad) + x*sin(rad) + y0

		return [point[0],new_x,new_y,point[3]]

	@staticmethod
	def axis_rotate_zs(points, angle, x0=0, y0=0):

		new_points = []
		for n, point in enumerate(points):
			new_points.append(
				RoadElement.axis_rotate_z(point, angle, x0=0, y0=0)
				)
		return new_points

	@staticmethod
	def nodes_to_points(nodes):
		points = []
		for node in nodes:
			points.append(node.get_point())

		return points

	
class RoadRaisedSin(RoadElement): # sin凸块
	"""
		凸包路
		拟合Sin函数
		根据路面中心线生成路面
	"""
	def __init__(self, dic_param):
		super().__init__()
		length 	= dic_param['length']
		hight 	= dic_param['hight']
		angle 	= dic_param['angle']
		width 	= dic_param['width']
		dx 		= dic_param['dx']
		f 		= dic_param['f']
		x0 		= dic_param['x0']
		y0 		= dic_param['y0']
		z0 		= dic_param['z0']

		self.angle_x = angle
		self.f = f

		# 凸包中心点生成
		xs,ys,zs = self.point_sin(length,hight,
			dx=dx, x0=x0, y0=y0, z0=z0)
		
		# 根据中心线生成 points,elements
		points,elements = self.road_center_line(xs, ys, zs, width, f=f, angle=angle)

		for point in points:
			for n,value in enumerate(point):
				if n !=0:
					point[n] = round(point[n],3)

		# 数据转化为 triangles 实例数据
		self.set_triangles(points,elements)

	@staticmethod
	def point_sin(length,hight,dx,x0=0.0,y0=0.0,z0=0.0): # 创建 单个正弦波路 (搓板路) XZ平面
		"""
			sin 正弦波 - 中心线
			单个凸包 中心线生成 正弦函数形状
			length 凸包长 X
			hight 凸包高度 Z
			dx 采点的 X向 间隔
			x0 初始X位置 
		"""
		num = int(length//dx)
		xs,ys,zs = [],[],[]
		for n in range(num):
			xs.append(n*dx+x0)
			ys.append(0+y0)
			zs.append(hight*sin(pi/length*n*dx+z0))
		
		xs[-1] = length+x0
		ys[-1] = y0
		zs[-1] = z0
		return xs,ys,zs


class RoadFlat(RoadElement): # 平面

	def __init__(self, dic_param):
		super().__init__()
		length 	= dic_param['length']
		width 	= dic_param['width']
		f 		= dic_param['f']
		x0 		= dic_param['x0']
		y0 		= dic_param['y0']
		z0 		= dic_param['z0']

		angle = 0
		self.angle_x = 0
		self.f = f

		# 平面中心点生成
		xs,ys,zs = self.point_flat(length,
			x0=x0, y0=y0, z0=z0)

		# 根据中心线生成 points,elements
		points,elements = self.road_center_line(xs, ys, zs, width, f=f, angle=angle)

		# 数据转化为 triangles 实例数据
		self.set_triangles(points,elements)

	@staticmethod
	def point_flat(length,x0,y0,z0):
		""" 平面中心线 """
		xs = [x0-length/2, x0+length/2]
		ys = [y0, y0]
		zs = [z0, z0]

		return xs,ys,zs


class RoadBuild:
	"""
		创建RDF路面
	"""
	def __init__(self, rdf_path=None):
		"""
			RoadElement

			rdf_path 为目标rdf路径
		"""
		self.roadelements = []
		self.points = []
		self.elements = []
		self.elements_join_x = []
		self.elements_join_y = []
		self.points_loc = 0
		self.rdf_path = rdf_path

	def add_roadelement(self, roadelement_obj):
		"""
			路面添加
			point 和 element 导入并顺延编号
		"""
		self.roadelements.append(roadelement_obj)
		# print(self.points_loc)
		start_id = roadelement_obj.points[0][0]-1
		offset_id = self.points_loc-start_id
		roadelement_obj.set_move_id(offset_id)
		self.points_loc = roadelement_obj.node_id_end

	def set_element_join_x(self, f=1): # 路面拼接X
		"""
			拼接路面
			根据RoadElement 的实例顺序进行拼接
			x 向拼接
		"""
		
		p_mins,p_maxs = self.roadelements[0].get_direction_x_point()

		# cal_nodes = []
		# cal_nodes.append(self.roadelements[0].node_xmax)
		cal_points = []
		cal_points.append(p_maxs)
		for num in range(1,len(self.roadelements)):
			p_mins2,p_maxs2 = self.roadelements[num].get_direction_x_point()
			# cal_nodes.append(self.roadelements[num].node_xmin)
			# cal_nodes.append(self.roadelements[num].node_xmax)
			cal_points.append(p_mins2)
			cal_points.append(p_maxs2)

		cal_points = cal_points[:-1]

		add_elements = []
		for n in range(int(len(cal_points)/2)):
			points_0 = cal_points[2*n+0]
			points_1 = cal_points[2*n+1]
			locations_0 = [line[1:3] for line in points_0]
			locations_1 = [line[1:3] for line in points_1]

			# 网格划分
			tri_obj = Delaunay(locations_0+locations_1)
			tris = tri_obj.simplices.copy()
			temp_points = points_0+points_1
			for tri in tris:
				temp_element = [temp_points[n][0] for n in tri]
				temp_element.append(f)
				add_elements.append(temp_element)

		self.elements_join_x = add_elements

		return add_elements

	def set_element_join_y(self, f=1): # 路面拼接Y
		"""
			拼接路面
			根据RoadElement 的实例顺序进行拼接
			x 向拼接
		"""
		
		p_mins,p_maxs = self.roadelements[0].get_direction_y_point()

		cal_points = []
		cal_points.append(p_maxs)
		for num in range(1,len(self.roadelements)):
			p_mins2,p_maxs2 = self.roadelements[num].get_direction_y_point()
			cal_points.append(p_mins2)
			cal_points.append(p_maxs2)

		cal_points = cal_points[:-1]

		add_elements = []
		for n in range(int(len(cal_points)/2)):
			points_0 = cal_points[2*n+0]
			points_1 = cal_points[2*n+1]
			locations_0 = [line[1:3] for line in points_0]
			locations_1 = [line[1:3] for line in points_1]

			# 网格划分
			tri_obj = Delaunay(locations_0+locations_1)
			tris = tri_obj.simplices.copy()
			temp_points = points_0+points_1
			for tri in tris:
				temp_element = [temp_points[n][0] for n in tri]
				temp_element.append(f)
				add_elements.append(temp_element)

		self.elements_join_y = add_elements

		return add_elements

	def set_move_location(self, x=0, y=0, z=0): # 平移模块

		for roadelement_obj in self.roadelements:
			roadelement_obj.set_move_location(x, y, z)

	def get_points_elements(self): # 获取整个模块points和elements
		""" 
			获取points elements 
			包含拼接路面的 elements
			isJoinX 	bool 	是否拼接X向
			isJoinY 	bool 	是否拼接Y向
		"""
		self.points 	= []
		self.elements 	= []

		for roadelement_obj in self.roadelements:
			self.points += roadelement_obj.get_points()
			self.elements += roadelement_obj.get_elements()
		# if isJoinX:
		# 	self.set_element_join_x()

		# if isJoinY:
		# 	self.set_element_join_y()			
		return self.points, self.elements+self.elements_join_x+self.elements_join_y

	def create(self, isXYChange=True):  # 创建路面文件
		"""
			生成rdf路面
		"""
		ps,es = self.get_points_elements()
		if isXYChange:
			ps 	= self.change_points_xy(ps)

		nodes_data = '\n'.join([' '.join([str(n) for n in line]) for line in ps])
		elements_data = '\n'.join([' '.join([str(n) for n in line]) for line in es])

		data_str = RDF_START.replace('#num_nodes',str(len(ps)))
		data_str = data_str.replace('#num_elements',str(len(es)))
		data_str = data_str.replace('#nodes_data',nodes_data)
		data_str = data_str.replace('#elements_data',elements_data)

		with open(self.rdf_path,'w') as f:
			f.write(data_str)

	@staticmethod
	def change_points_xy(points, isNew=True): # xy 180度旋转
		# xy 180度旋转
		if isNew:
			new_points = copy.deepcopy(points)
		else:
			new_points = points

		for point in new_points:
			point[1] = -point[1]
			point[2] = -point[2]

		return new_points


def road_washboards(dic_param): # 搓板路 方向 -x
	"""	
		搓板路面生成,完全拼接
		dic_param 搓板路 数据
			length 单个搓板长度 mm
			hight 凸台高度 mm
			angle 路面角度 deg
			width 路面宽度 mm
			dx 	搓板 采点间隔 mm
			f 	摩擦系数
			x0 	起始位置 mm
			y0 	Y向起始位置 mm
			z0 	z向起始位置 mm
			num 		搓板个数
			rdf_path 	rdf文件路径
			x0_delta 	搓板间距等差变更
	"""

	# 搓板路
	length 	= dic_param['length']
	hight 	= dic_param['hight']
	angle 	= dic_param['angle']
	width 	= dic_param['width']
	dx 		= dic_param['dx']
	f 		= dic_param['f']
	x0 		= dic_param['x0']
	y0 		= dic_param['y0']
	z0 		= dic_param['z0']
	num 	= dic_param['num']

	if 'rdf_path' in dic_param: # 若rdf_path有路径
		roadobj = RoadBuild(dic_param['rdf_path'])
	else:
		roadobj = RoadBuild()

	if 'x0_delta' in dic_param:
		x0_delta = dic_param['x0_delta']
	else:
		x0_delta = 0

	# 前后段平面数据
	dic_flat = {
		'length':100, 'width':width, 'f' :1,
		'x0' :10000, 'y0' :y0, 'z0' :z0,}

	isFlatStart, isFlatEnd = False, False
	if 'x_start' in dic_param:
		dic_flat['x0'] = dic_param['x_start']
		flat1 = RoadFlat(dic_flat)
		isFlatStart = True
	if 'x_end' in dic_param:
		dic_flat['x0'] = dic_param['x_end']
		flat2 = RoadFlat(dic_flat)
		isFlatEnd = True

	# 起始平面添加
	if isFlatStart:
		roadobj.add_roadelement(flat1)
	# 搓板路面添加
	for n in range(num):
		if n ==0:
			s = x0
		else:
			s += dic_param['distance']+(n-1)*x0_delta
			# print(dic_param['distance']+(n-1)*x0_delta)
		dic_param['x0'] = s
		# print(dic_param['x0'])
		roadobj.add_roadelement(RoadRaisedSin(dic_param))
	
	# 添加末端平面
	if isFlatEnd:
		roadobj.add_roadelement(flat2)
	# 路面模块拼接
	roadobj.set_element_join_x() 
	points, elements = roadobj.get_points_elements()

	if 'rdf_path' in dic_param: # rdf路面路径存在创建路面
		roadobj.create()

	return points, elements


def circular_ring(dic_param):
	"""
		圆环创建
		radius_in 	内圆半径
		radius_out	外圆半径
		n_split 	圆分割点数
		f 			地面相对摩擦系数
		length_x 	方框X向长度
		length_y 	方框Y向长度
	"""
	# points1 内环
	# points2 外环
	radius_in = dic_param['radius_in']
	radius_out = dic_param['radius_out']
	n_split = dic_param['n_split']
	x0 = dic_param['x0']
	y0 = dic_param['y0']
	z0 = dic_param['z0']
	f = dic_param['f']
	length_x = dic_param['length_x']
	length_y = dic_param['length_y']
	hight = dic_param['hight']
	move_id = dic_param['move_id']


	points_in = point_circular(radius_in, n_split, x0, y0, z0)
	points_out = point_circular(radius_out, n_split, x0, y0, z0, move_id=1+len(points_in))

	points = points_in + points_out
	points.sort(key=lambda list1:list1[0])
	elements = join_two_line_to_ring(points_in, points_out, f)
	
	# 内外圈-圆环拼接
	point_center = [len(points)+1, x0, y0, z0]
	points_in.append(point_center)
	points.append(point_center)
	elements.extend( delaunay_element(points_in, f) )

	# 内圈z坐标移动- 高度设置
	for point_in in points_in:
		point_in[3] = z0 + hight

	# 外部矩形框
	points_box = point_box(length_x, length_y, n_split, x0, y0, z0, move_id=1+len(points))
	points.extend(points_box)
	elements.extend(join_two_line_to_ring(points_out, points_box, f))

	if move_id!=1:
		for point in points:
			point[0] += move_id-1
		for element in elements:
			element[0] += move_id-1
			element[1] += move_id-1
			element[2] += move_id-1

	return points,elements


def delaunay_element(points, f): # 封闭面生成 element 
	
	locations = [point[1:3] for point in points]
	# 网格划分
	tri_obj = Delaunay(locations)
	tris = tri_obj.simplices.copy()
	elements = []
	for tri in tris:
		temp_element = [points[n][0] for n in tri] + [f]
		elements.append(temp_element)
	
	return elements


def point_circular(radius, n_split, x0=0, y0=0, z0=0, move_id=1, alpha0=pi/4):
	""" 顺时针生成points数据 """
	alpha_del = 2*pi/n_split
	points = []
	for n in range(int(n_split)):
		point = []
		point.append(n+move_id)
		y = radius*cos(alpha0+alpha_del*n) + x0
		x = radius*sin(alpha0+alpha_del*n) + y0
		point.append(x)
		point.append(y)
		point.append(z0)
		points.append(point)

	for point in points:
		for n,value in enumerate(point):
			if n !=0:
				point[n] = round(point[n],3)
	# print(points)
	return points


def point_box(length_x, length_y, n_split, x0=0, y0=0, z0=0, move_id=1):
	"""
		矩形 +length_x/2 +length_y/2 开始 
		顺时针计数
	"""
	s1, s2, s3, s4 = 0, 0, 0, 0
	for n in range(1,n_split+1):
		if n%4==1:
			s1 +=1
			continue
		if n%4==2:
			s2 +=1
			continue
		if n%4==3:
			s3 +=1
			continue
		if n%4==0:
			s4 +=1
			continue

	locations1 = [] # 右
	for n in range(s1):
		locations1.append([length_x/2+x0, length_y/2-length_y/s1*n+y0, z0])

	locations2 = []	# 下
	for n in range(s2):
		locations2.append([length_x/2-length_x/s2*n+x0, -length_y/2+y0, z0])

	locations3 = [] # 左
	for n in range(s3):
		locations3.append([-length_x/2+x0, -length_y/2+length_y/s3*n+y0, z0])

	locations4 = [] # 上
	for n in range(s4):
		locations4.append([-length_x/2+length_x/s4*n+x0, length_y/2+y0, z0])
	
	locations = locations1 + locations2 + locations3 + locations4
	points = [ [num+move_id]+location for num,location in enumerate(locations)]

	for point in points:
		for n,value in enumerate(point):
			if n !=0:
				point[n] = round(point[n],3)

	return points


def join_two_line_to_ring(points1, points2, f):
	# 输入的数据顺序已经固定
	# id 不重复

	points = []
	for point1,point2 in zip(points1,points2):
		points.append(point1)
		points.append(point2)

	elements, len_ps = [],len(points)
	for n in range(len_ps):
		if n < len_ps-2:
			element = [points[n][0], points[n+1][0], points[n+2][0], f]
		elif n==len_ps-2:
			element = [points[n][0], points[n+1][0], points[n+2-len_ps][0], f]
		else:
			element = [points[n][0], points[n+1-len_ps][0], points[n+2-len_ps][0], f]
		elements.append(element)

	return elements


if __name__ == '__main__':

	# # 搓板路
	# dic_param = {
	# 	'length' 	:400,
	# 	'hight'		:40,
	# 	'angle'		:0,
	# 	'width' 	:5000,
	# 	'dx' 		:10,
	# 	'f' 		:1,
	# 	'x0' 		:10000,
	# 	'y0' 		:0,
	# 	'z0' 		:0,
	# 	'num' 		:95,
	# 	'distance' 	:1000,
	# 	'rdf_path' 	:r'D:\document\ADAMS\test_road_rdf.rdf',
	# 	'x_start' 	:-10000,
	# 	'x_end'		:200000,
	# 	'x0_delta' 	:-5,
	# }
	# points1, elements1 = road_washboards(dic_param)

	# rdf_road_obj = RoadBuild(r'D:\document\ADAMS\test_road_rdf.rdf')
	# # 左侧
	# left_obj = RoadElement(points=points1, elements=elements1, move_id=1)
	# left_obj.set_move_location(y=-2510)
	# # 右侧
	# right_obj = RoadElement(points=points1, elements=elements1, move_id=2)
	# right_obj.set_move_location(y=2510, x=500)

	# rdf_road_obj.add_roadelement(left_obj)
	# rdf_road_obj.add_roadelement(right_obj)

	# rdf_road_obj.create()

	# -----------------------------
	dic_param = {
	'radius_in':100, 
	'radius_out':200,
	'n_split':20,
	'x0':0,
	'y0':0,
	'z0':0, 
	'f':1,
	'length_x':500,
	'length_y':2000,
	'hight':-100,
	'move_id':1}
	points, elements = circular_ring(dic_param)
	# print(points)
	rdf_road_obj = RoadBuild(r'D:\document\ADAMS\test_road_rdf.rdf')

	# for n, point in enumerate(points):
	# 	points[n] = RoadElement.axis_rotate_z(point, -10, x0=0, y0=0)

	points = RoadElement.axis_rotate_zs(points, -70, x0=0, y0=0)

	ring_obj = RoadElement(points=points, elements=elements, move_id=1)
	rdf_road_obj.add_roadelement(ring_obj)
	rdf_road_obj.create()