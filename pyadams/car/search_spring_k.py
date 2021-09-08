# -*- coding: utf-8 -*-
'''
	检索弹簧文件
	计算弹簧平均刚度
'''
import os.path
import os
import re
import numpy as np

def spring_file(filepath):
	'''
		读取弹簧文件
		处理数据,计算刚度,求取平均值	
	'''
	with open(filepath,'r') as f:
		list1 = f.readlines()
	start = False
	x,y = [],[]
	for num,line in enumerate(list1):
		if start:
			obj = re.match('\s*(\S+)\s+(\S+).*',line)
			if obj and len(obj.group())>1:
				x.append(float(obj.group(1)))
				y.append(float(obj.group(2)))
		if '{' in line and '}' in line:
			start = True

	x_arr = np.array(x)
	y_arr = np.array(y)
	x_diff = np.diff(x_arr)
	y_diff = np.diff(y_arr)
	# 刚度数据
	k = y_diff / x_diff
	return k.mean()

def spring_k_mean(mainpath,spring_data_path):
	'''
		mainpath： 数据库路径
		spring_data_path ： 弹簧数据存储路径
		历遍数据库路径内的所有 '.cdb'文件夹 内的弹簧文件
		获取弹簧数据 ，并计算平均刚度，
	'''
	sf = open(spring_data_path,'w')
	sf.write('spring_file_name,spring_file_path,spring_mean_k\n')
	for root,dirs,files in os.walk(mainpath):
		for filename in files:
			if '.spr' in filename.lower() and 'springs.tbl' in root.lower():
				spring_path = os.path.join(root,filename)
				k_mean = spring_file(spring_path)
				str1 = '{},{},{}\n'.format(filename, spring_path, k_mean)
				sf.write(str1)
	sf.close()

	return True





if __name__ == '__main__':
	'''
		计算
	'''
	pass
	test_spring_k_mean()
	# mainpath = r'E:\Software\MSC.Software\Adams\2019\acar'
	# spring_data_path = r'..\code_test\car\search_spring_k\spring_mean.txt'
	# spring_k_mean(mainpath,spring_data_path)
