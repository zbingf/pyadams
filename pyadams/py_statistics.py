"""
	代码行数统计

"""

import os
import time
import re

import logging
logging.basicConfig(level=logging.INFO)
PY_FILE_NAME = os.path.basename(__file__)
logger = logging.getLogger(PY_FILE_NAME)

class TimeCal: # 计时用
	''' 计时 '''
	def __init__(self):
		self.start_time=time.time()
		self.time_list=[]
		self.results=[]

	def run_time(self): # 总运行时间
		''' 从创建实例到当前运行的时间 '''
		temp1 = time.time() - self.start_time
		self.time_list.append(temp1)
		return temp1

	def last_time(self): # 最近运行时间间隔
		''' 最近运行时间间隔 '''
		self.run_time()
		if len(self.time_list)==1:
			return self.time_list[0]
		else:
			return self.time_list[-1]-self.time_list[-2]

#遍历文件, 递归遍历文件夹中的所有
def search_file(base_dir):

	# 指定想要统计的文件类型	
	whitelist = ['py']
	file_paths = []
	for parent, dirnames, filenames in os.walk(base_dir):
		for filename in filenames:
			ext = filename.split('.')[-1]
			#只统计指定的文件类型，略过一些log和cache文件
			if ext in whitelist:
				file_paths.append(os.path.join(parent, filename))

	return file_paths

#统计一个文件的行数
def count_line(file_path):
	
	count = 0
	lines = []
	with open(file_path, 'r', encoding='utf-8') as f:
		file_str = f.read()
	
	for line in file_str.split('\n'):
		line = re.sub('\s', '', line)
		if line :
			if '#' == line[0]:
				continue
			else:
				count += 1
				lines.append(line)

	return count, lines



if __name__ == '__main__' :

	time_obj = TimeCal()
	file_paths = search_file('.')
	# print(file_paths, len(file_paths))
	
	keys = ['test', PY_FILE_NAME, 'ing', 'old']

	total_count = 0
	totallines = []
	for file_path in file_paths:
		isCal = True
		for key in keys:
			if key in file_path:
				logger.info(f'排除:{file_path}')
				isCal = False
				break
		if isCal:
			count, lines = count_line(file_path)
			logger.info(f'计算:{file_path}')
			logger.info(f'行数:{count}')
			total_count = total_count + count
			totallines.extend(lines)

	# print('\n'.join(totallines))
	print('total lines:',total_count)
	print('Done! Cost Time: {:0.2f} second'.format(time_obj.last_time()) )
