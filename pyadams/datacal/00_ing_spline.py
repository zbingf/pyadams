"""
	数据拟合 - 未完成
	调用 scipy库
"""

from scipy import interpolate

def single_to_UnivariateSpline(data, d=1, **keys):
	"""
		data [float, float, ...]
	"""
	x = [n/d for n in range(len(data))]
	obj = interpolate.UnivariateSpline(x, data,**keys)
	return obj(x)


if __name__ == '__main__':
	pass
	# single_to_UnivariateSpline(x, s=0.01)
	