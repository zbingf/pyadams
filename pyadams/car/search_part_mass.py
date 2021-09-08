# -*- coding: utf-8 -*-
'''
	检索子系统文件
	获取 车身子系统 部件质量参数
'''
import os
import re
import os.path

def body_part_mass(filepath):
	with open(filepath,'r') as f:
		strfile = f.read()
	if is_body(strfile):
		parts = part_data(strfile)
		return parts
	else:
		return False

def is_body(strdata):
	'''
		判断子系统主特征是否是 body
	'''
	str1 = ".*(MAJOR_ROLE|major_role)\s*=\s*'body'"
	logic1 = False
	obj1 = re.match(str1,strdata,re.S)
	if obj1:
		logic1 = True
	return logic1

def part_data(strdata):
	'''
		解析文本字符串
	'''
	listdata = strdata.split('\n')
	start = False
	part_list = []
	for line in listdata:
		if '[PART_ASSEMBLY]'.lower() in line.lower():
			start = True
			list1 = []
		if '$---' in line and start:
			start = False
			part_list.append(list1)
		if start:
			list1.append(line)
	str1 = "\s*(\S+)\s*=\s*(\S+)"
	part_datas = []
	for part in part_list:
		for line in part:
			obj1 = re.match(str1,line)
			if obj1 :
				part_name = obj1.group(1)
				if 'MASS'.lower() in part_name.lower():
					mass = float(obj1.group(2))
				if 'IXX'.lower() in part_name.lower():
					ixx = float(obj1.group(2))
				if 'IYY'.lower() in part_name.lower():
					iyy = float(obj1.group(2))
				if 'IZZ'.lower() in part_name.lower():
					izz = float(obj1.group(2))
				if 'USAGE'.lower() in part_name.lower():
					name = obj1.group(2)
		if ixx > iyy:
			ixx,iyy = iyy,ixx
		part_mass = [name,mass,ixx,iyy,izz]
		part_datas.append(part_mass)
	return part_datas


def body_mass_search(mainpath,mass_data_path):
	'''
		mainpath： 数据库路径
		mass_data_path ： 车身质量数据存储路径
		检索整个数据库 的子系统（.sub）
		主特征: body 
		获取质量参数: 质量、转动惯量 
	'''
	sf = open(mass_data_path,'w')
	sf.write('cdb_name,sub_name,sub_path,part_name,mass,Ixx,Iyy,Izz\n')
	for root,dirs,files in os.walk(mainpath):
		for filename in files:
			if '.sub' in filename.lower():
				sub_path = os.path.join(root, filename)
				datas = body_part_mass(sub_path)
				cdb_name = os.path.basename(os.path.dirname(root))
				if datas:
					for data in datas:
						str1 = f'{cdb_name},{filename},{sub_path},{data[0]},{data[1]},{data[2]},{data[3]},{data[4]}\n'
						sf.write(str1)
	sf.close()




if __name__ == '__main__':

	mainpath = r'D:\software\MSC.Software\Adams\2019\acar'
	mass_data_path = r'..\code_test\car\search_part_mass\part_mass.txt'
	body_mass_search(mainpath,mass_data_path)





