
"""
	RDF路面创建模块

	node 为 对象
	point 为 列表
	triangle 为对象
	element 为 列表
	roadelement 为对象 路面子模块
	roadbuild 为对象 路面rdf主模块
"""
from math import *
import copy
# import logging
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
	
class RoadBuild:
	"""
		创建RDF路面
	"""
	def __init__(self,rdf_path=None):
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

