"""
	紧用于测试
"""

from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
import numpy as np

# 圆 	-	成功
points_circle = np.array([
	[100,0],
	[76.60444,64.27876],
	[17.36482,98.48078],
	[-50,86.60254],
	[-93.9693,34.20201],
	[-93.9693,-34.202],
	[-50,-86.6025],
	[17.36482,-98.4808],
	[76.60444,-64.2788],
	[100,-16.45],
	[0,0],
	])

# 圆环  - 失败
points_circle_ring = np.array([
	[100,0],
	[76.60444,64.27876],
	[17.36482,98.48078],
	[-50,86.60254],
	[-93.9693,34.20201],
	[-93.9693,-34.202],
	[-50,-86.6025],
	[17.36482,-98.4808],
	[76.60444,-64.2788],
	[100,-16.45],
	[50,0],
	[38.30222,32.13938],
	[8.682409,49.24039],
	[-25,43.30127],
	[-46.9846,17.10101],
	[-46.9846,-17.101],
	[-25,-43.3013],
	[8.682409,-49.2404],
	[38.30222,-32.1394],
	[50,-15.22],
	])
# 半圆环 - 失败
points_circle_ring_half = points_circle_ring[points_circle_ring[:,1]>0]


points_circle_1 = points_circle
circle_2_locs = []
for point in points_circle_ring:
	if point not in points_circle:
		circle_2_locs.append(True)
	else:
		circle_2_locs.append(False)

points_circle_2 = points_circle_ring[circle_2_locs]



# 平行线 	-	成功
list1 = [[n*10,100] for n in range(10)]
list2 = [[n*15-30,0] for n in range(13)]
list1.extend(list2)
points_two_line = np.array(list1)
# points_two_line = list1


def show(points):

	tri = Delaunay(points)
	new_tris = tri.simplices.copy()
	print(new_tris)

	
	plt.triplot(points[:,0],points[:,1],new_tris)
	plt.plot(points[:,0],points[:,1],'o')
	





if __name__ == '__main__':

	# show(points_circle)
	# show(points_circle_ring)
	# show(points_circle_ring_half)
	show(points_two_line) # 曲线见的拼接
	plt.show()