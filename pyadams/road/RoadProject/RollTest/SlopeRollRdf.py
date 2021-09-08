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

from math import *
import rdf_file
RoadBuild = rdf_file.RoadBuild
RoadElement = rdf_file.RoadElement


def SlopeRollRdf(rdf_path, length, angle, L_1, L_2, L_3, deg_1, deg_2, deg_3, isLeft=True):


	angle = abs(angle)

	x0 = -20000
	x1 = 2000
	x2 = x1 + L_1
	x3 = x2 + L_2
	x4 = x3 + L_3

	y_m = 0
	if isLeft:
		y_l = 30000
		y_r = -length # -width/2
	else:
		y_l = length
		y_r = -30000 # -width/2

	z0 = 0
	z1 = 0
	z2 = z1 - L_1 * tan(deg_1/180*pi)
	z3 = z2 - L_2 * tan(deg_2/180*pi)
	z4 = z3 - L_3 * tan(deg_3/180*pi)

	p1 = [1, x0, y_l, z0]
	p2 = [2, x0, y_r, z0]
	p3 = [3, x1, y_l, z1]
	p4 = [4, x1, y_r, z1]
	p5 = [5, x2, y_l, z2]
	p6 = [6, x2, y_r, z2]
	p7 = [7, x3, y_l, z3]
	p8 = [8, x3, y_r, z3]
	p9 = [9, x4, y_l, z4]
	p10 = [10, x4, y_r, z4]

	points = [p1,p2,p3,p4,p5,p6,p7,p8,p9,p10]
	
	for n in range(10):
		if isLeft==True:
			points[n] = RoadElement.axis_rotate_z(points[n], 90, x0=x1, y0=0)
		else:
			points[n] = RoadElement.axis_rotate_z(points[n], -90, x0=x1, y0=0)



	for n in range(0,10):
		if isLeft==True:
			points[n] = RoadElement.axis_rotate_z(points[n], -angle, x0=x1, y0=0)
		else:
			points[n] = RoadElement.axis_rotate_z(points[n], angle, x0=x1, y0=0)

	
	elements = [
		[1,2,3,1],
		[2,3,4,1],
		[3,4,5,1],
		[4,5,6,1],
		[5,6,7,1],
		[6,7,8,1],
		[7,8,9,1],
		[8,9,10,1],
	]

	rdf_road_obj = RoadBuild(rdf_path)
	re_obj = RoadElement(points=points, elements=elements, move_id=1)
	rdf_road_obj.add_roadelement(re_obj)
	rdf_road_obj.create()

	return None

if __name__ == '__main__':


	rdf_path = r'D:\document\ADAMS\test_road_rdf.rdf'

	# 第一段长度
	L_1 = 3000
	# 第一段 角度 deg
	deg_1 = 25.2
	# 第二段长度
	L_2 = 3000
	# 第二段 角度 deg
	deg_2 = 55
	# 第二段长度
	L_3 = 10000
	# 第二段 角度 deg
	deg_3 = 55


	# 路面宽度
	length = 200000

	angle = 12
	isLeft = False

	SlopeRollRdf(rdf_path, length, angle, L_1, L_2, L_3, deg_1, deg_2, deg_3, isLeft)


