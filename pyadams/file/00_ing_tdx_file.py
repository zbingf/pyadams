"""
	TDX 轮胎试验数据读取
"""

import re
import os
import logging

def list2change(list1):
	# 二维数据, 行列调换
	new_list = []
	for n in range(len(list1[0])):
		temp = []
		for line in list1:
			temp.append(line[n])
		new_list.append(temp)

	return new_list

def tdx_data_read(tdx_path):
	# tdx文件数据读取

	with open(tdx_path, 'r') as f:
		data_lines = f.read().split('\n')
	keys = []
	data = []
	iskey = False
	isdata = False
	for line in data_lines:
		if '**MEASURCHANNELS' in line.upper():
			iskey, isdata = True, False
			continue
		
		if '**MEASURDATA' in line.upper():
			iskey, isdata = False, True
			continue

		if '**END' in line.upper():
			isdata = True
			continue

		line = re.sub('\s', ' ', line)
		list1 = [n for n in line.split(' ') if n]
		if iskey and list1:
			keys.append(list1[0])
		if isdata and list1:
			data.append([float(n) for n in list1])

	data_dic = {}
	for key, line in zip(keys, list2change(data)):
		data_dic[key] = line

	return data_dic, keys



