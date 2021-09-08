"""
参考视频:
	https://pcauto.pcvideo.com.cn/video-59802.html

主要翻滚试验工况
1、螺旋翻滚
2、边坡翻滚


试验方法


螺旋翻滚
试验概述：车辆单侧轮胎驶上“单边桥”，
车辆发生侧翻
第一段角度：8°（固定）
第二段角度：8~20°（可调范围）
速度：最高可以80km/h


边坡翻滚
工况描述：车辆以固定的车速驶入斜坡，确定第二和三段的
角度，使车辆侧翻。
速度：V=10~25km/h
方向：车身切入角为12°
第一段角度：25.2°（固定）
第二段角度：35-55°（可调范围）
第三段角度：由第二段确定


需要翻滚的X轴角速度，Y和Z方向的加速度数据
需要整个模型，可以让我进行后期的修改


"""


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
import rdf_file
RoadBuild = rdf_file.RoadBuild
RoadElement = rdf_file.RoadElement


def SpiralRollRdf(rdf_path, L_1, L_2, deg_1, deg_2, width, x_end, isLeft=True):

	x0 = -30000
	x1 = 5000
	# x_end = 100000

	x2 = x1 + L_1
	x3 = x2 + L_2

	z0 = 0
	z1 = 0
	z2 = z1 + L_1 * tan(deg_1/180*pi)
	z3 = z2 + L_2 * tan(deg_2/180*pi)

	y_m = 0
	if isLeft: # 左侧翘板
		y_l = width/2
		y_r = -width/2
	else:
		y_l = -width/2
		y_r = width/2

	p1 = [1, x0, y_l, z0]
	p2 = [2, x0, y_m, z0]
	p3 = [3, x1, y_l, z1]
	p4 = [4, x1, y_m, z1]
	p5 = [5, x2, y_l, z2]
	p6 = [6, x2, y_m, z2]
	p7 = [7, x3, y_l, z3]
	p8 = [8, x3, y_m, z3]

	p9 	= [9, x0, y_m, z0]
	p10 = [10, x0, y_r, z0]
	p11 = [11, x1, y_m, z0]
	p12 = [12, x1, y_r, z0]
	p13 = [13, x2, y_m, z0]
	p14 = [14, x2, y_r, z0]
	p15 = [15, x3, y_m, z0]
	p16 = [16, x3, y_r, z0]

	p17 = [17, x3, y_l, z0]
	p18 = [18, x_end, y_l, z0]
	p19 = [19, x_end, y_m, z0]
	p20 = [20, x_end, y_r, z0]


	points = [p1,p2,p3,p4,p5,p6,p7,p8,
		p9,p10,p11,p12,p13,p14,p15,p16,
		p17,p18,p19,p20]

	elements = [
		[1,2,3,1],
		[2,3,4,1],
		[3,4,5,1],
		[4,5,6,1],
		[5,6,7,1],
		[6,7,8,1],
		[9,10,11,1],
		[10,11,12,1],
		[11,12,13,1],
		[12,13,14,1],
		[13,14,15,1],
		[14,15,16,1],
		[15,17,18,1],
		[15,18,19,1],
		[15,16,19,1],
		[16,19,20,1],
		[7,8,17,1],
		[8,17,15,1],
	]
	
	
	rdf_road_obj = RoadBuild(rdf_path)
	re_obj = RoadElement(points=points, elements=elements, move_id=1)
	rdf_road_obj.add_roadelement(re_obj)
	rdf_road_obj.create()

	return None

if __name__ == '__main__':


	rdf_path = r'D:\document\ADAMS\test_road_rdf.rdf'

	# 第一段长度
	L_1 = 1000
	# 第一段 角度 deg
	deg_1 = 8
	# 第二段长度
	L_2 = 2000
	# 第二段 角度 deg
	deg_2 = 8
	# 路面宽度
	width = 20000

	x_end = 100000

	SpiralRollRdf(rdf_path, L_1, L_2, deg_1, deg_2, width, x_end)

