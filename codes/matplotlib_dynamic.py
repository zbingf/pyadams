# _*_ coding: utf-8 _*_

"""
python_visual_animation.py by xianhu
动态示例
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from mpl_toolkits.mplot3d import Axes3D

# 解决中文乱码问题
plt.rcParams['font.family']=['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus']=False

def simple_plot():
	"""
	simple plot
	"""
	# 生成画布
	plt.figure(figsize=(8, 6), dpi=80)

	# 打开交互模式
	plt.ion()

	# 循环
	for index in range(100):
		# 清除原有图像
		plt.cla()

		# 设定标题等
		plt.title("动态曲线图")
		plt.grid(True)

		# 生成测试数据
		x = np.linspace(-np.pi + 0.1*index, np.pi+0.1*index, 256, endpoint=True)
		y_cos, y_sin = np.cos(x), np.sin(x)

		# 设置X轴
		plt.xlabel("X轴")
		plt.xlim(-4 + 0.1*index, 4 + 0.1*index)
		plt.xticks(np.linspace(-4 + 0.1*index, 4+0.1*index, 9, endpoint=True))

		# 设置Y轴
		plt.ylabel("Y轴")
		plt.ylim(-1.0, 1.0)
		plt.yticks(np.linspace(-1, 1, 9, endpoint=True))

		# 画两条曲线
		plt.plot(x, y_cos, "b--", linewidth=2.0, label="cos示例")
		plt.plot(x, y_sin, "g-", linewidth=2.0, label="sin示例")

		# 设置图例位置,loc可以为[upper, lower, left, right, center]
		plt.legend(loc="upper left", shadow=True)

		# 暂停
		plt.pause(0.1)

	# 关闭交互模式
	plt.ioff()

	# 图形显示
	plt.show()
	return

# simple_plot()


def scatter_plot():
	"""
	scatter plot
	"""
	# 打开交互模式
	plt.ion()

	# 循环
	for index in range(50):
		# 清除原有图像
		# plt.cla()

		# 设定标题等
		plt.title("动态散点图")#, fontproperties=myfont
		plt.grid(True)

		# 生成测试数据
		point_count = 5
		x_index = np.random.random(point_count)
		y_index = np.random.random(point_count)

		# 设置相关参数
		color_list = np.random.random(point_count)
		scale_list = np.random.random(point_count) * 100

		# 画散点图
		plt.scatter(x_index, y_index, s=scale_list, c=color_list, marker="o")

		# 暂停
		plt.pause(0.2)

	# 关闭交互模式
	plt.ioff()

	# 显示图形
	plt.show()
	return

# scatter_plot()


def three_dimension_scatter():
	"""
	3d scatter plot
	"""
	# 生成画布
	fig = plt.figure()

	# 打开交互模式
	plt.ion()

	# 循环
	for index in range(50):
		# 清除原有图像
		fig.clf()

		# 设定标题等
		fig.suptitle("三维动态散点图")#, fontproperties=myfont

		# 生成测试数据
		point_count = 100
		x = np.random.random(point_count)
		y = np.random.random(point_count)
		z = np.random.random(point_count)
		color = np.random.random(point_count)
		scale = np.random.random(point_count) * 100

		# 生成画布
		ax = fig.add_subplot(111, projection="3d")

		# 画三维散点图
		ax.scatter(x, y, z, s=scale, c=color, marker=".")

		# 设置坐标轴图标
		ax.set_xlabel("X Label")
		ax.set_ylabel("Y Label")
		ax.set_zlabel("Z Label")

		# 设置坐标轴范围
		ax.set_xlim(0, 1)
		ax.set_ylim(0, 1)
		ax.set_zlim(0, 1)

		# 暂停
		plt.pause(1/20)

	# 关闭交互模式
	plt.ioff()

	# 图形显示
	plt.show()
	return

# three_dimension_scatter()



def plot_dyn(xlist,ylist,zlist,samplerate):
	"""
	simple plot
	"""
	# samplerate = 100
	step = 1.0 / float(samplerate)
	# 生成画布
	fig = plt.figure(figsize=(8, 6), dpi=80,)

	ax = fig.gca(projection='3d')

	# 打开交互模式
	plt.ion()

	# 循环
	for x,y,z in zip(xlist,ylist,zlist):
		# 清除原有图像
		ax.cla()
		# 设定标题等
		plt.title("动态曲线图")
		plt.grid(True)

		# # 设置X轴
		plt.xlabel("X轴")
		# plt.xlim(-4 + 0.1*index, 4 + 0.1*index)
		# plt.xticks(np.linspace(-4 + 0.1*index, 4+0.1*index, 9, endpoint=True))

		# # 设置Y轴
		plt.ylabel("Y轴")
		# plt.ylim(-1.0, 1.0)
		# plt.yticks(np.linspace(-1, 1, 9, endpoint=True))

		# plt.zlabel("Z轴")
		# 画两条曲线
		plt.plot(x, y, z, "*", linewidth=2.0, label="示例")
		# plt.plot(x, y_sin, "g-", linewidth=2.0, label="sin示例")

		# 设置图例位置,loc可以为[upper, lower, left, right, center]
		# plt.legend(loc="upper left", shadow=True)

		# 暂停
		plt.pause(step)

	# 关闭交互模式
	plt.ioff()

	# 图形显示
	plt.show()
	return

import pyadams.file.result as result
drv_path = r'.\pyadams\code_test\cuoban_acc.rsp'
data_list , dic , name_channels = result.rsp_read(drv_path)
print(name_channels)



xs,ys,zs = [],[],[]
for n2 in range(len(data_list[0])):
	temp = []
	for line in data_list[0::3]:
		temp.append(line[n2])
	xs.append(temp)

	temp = []
	for line in data_list[1::3]:
		temp.append(line[n2])
	ys.append(temp)

	temp = []
	for line in data_list[2::3]:
		temp.append(line[n2])
	zs.append(temp)


# print(name_channels[0::3])

# # 生成测试数据
# index = 1
# x = np.linspace(-np.pi + 0.1*index, np.pi+0.1*index, 256, endpoint=True)
# y, z = np.cos(x), np.sin(x)


# plot_dyn(xs,ys,zs,512)


# import openpyxl
import docx

print(dir(docx))
print(docx.__file__)

