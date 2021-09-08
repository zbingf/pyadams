"""
	未进行更新

	ADAMS 2017.2 
	模型文件读写
	
	读取Adams 相关文件
	##################################################################
	包含子函数：cfg_path_search、bat_path_search
	1、cfgPath=cfg_path_search() 输出adams 配置文件 cfg 的路径
	2、fullPath=bat_path_search(bat_name) adams调用文件bat 的路径检索
	##################################################################
	包含类：AsyFile、SubFile、CfgFile、ResFile
	AsyFile 装配文件处理
		data、file_path、hardpoint、parameter、subsystem、testrig、solver_settings
	SubFile 子系统文件处理
		继承 AsyFile
		data(dict)、hardpoint、subHeader(dict)、file_path、spring、damper、bumpstop、reboundstop、bushing、parameter
		类方法：subheader_read、spring_read、damper_read、bumpstop_read、reboundstop_read、bushing_read
	CfgFile 配置文件处理
		
	ResFile 后处理文件res处理

"""
import re
import copy
import glob
import time

try:
	import pyadams.adamsbase.car_file_loc as car_file_loc
except:
	import os,sys
	path_loc=os.getcwd()
	str_match=r'(.*[\\/])pyadams.*?'
	path=re.match(str_match,path_loc).group(1)
	sys.path.append(path)
	import pyadams.adamsbase.car_file_loc as car_file_loc


class AsyFile:
	"""
		asy 装配文件读取
	"""	
	# 正则表达式匹配格式
	reg_list=[
		r'(?:\s*){}(?:\s*)=(?:\s*)\'(?:\s*)(\S*)(?:\s*)\'', # test = ' target2 '
		r'(?:\s*){}(?:\s*)=(?:\s*)(\S*)(?:\s*)', # test =  target2 
		r'(?:\s*)(\S*)(?:\s*)=(?:\s*)\'(?:\s*)(\S*)(?:\s*)\'', # target1 = ' target2 '
		r'(?:\s*)(\S*)(?:\s*)=(?:\s*)(\S*)(?:\s*)', # target1 =  target2 
		r'\$?(?:\s*){}(?:\s*):(?:\s*)(\S*)(?:\s*)', # $ test :  target2 
	]

	def __init__(self,file_path):
		# 输入文件路径
		self.file_path=file_path
		self.file_read(file_path)
		self.hardpoint_read()
		self.parameter_read()
		self.subsystem_read()
		self.testrig_read()
		self.solver_setting_read()

	def file_read(self,file_path):
		'''
			read sub file 
		'''
		fileid=open(file_path,'r')
		data_str=fileid.readlines()
		fileid.close()
		reg=r'\[(\w*)\]'
		data=dict()
		temp=[]
		for line in data_str:
			line=line.lower()
			m=re.match(reg,line)
			if m:
				if 'nameOld' in vars():
					data[nameOld].append(temp)
				nameNew=m.group(1)
				if nameNew not in data:
					data[nameNew]=[]
				temp=[]
				nameOld=nameNew
			elif re.match(r'^\$-',line):
				continue
			else:
				temp.append(line)
		data[nameNew].append(temp)
		self.data=data

	def hardpoint_read(self):
		'''
			硬点数据读取
		'''
		data=self.data
		reg_hp=r'(?:\s*)\'(?:\s*)(\w*)(?:\s*)\'(?:\s*)\'(?:\s*)(single|left/right|left|right)'+\
			r'(?:\s*)\'(?:\s*)(-?\d*.?\d*)(?:\s*)(-?\d*.?\d*)(?:\s*)(-?\d*.?\d*)(?:\s*)'
		hardpoint=[]
		if 'hardpoint' in data:
			for line in data['hardpoint']:
				for temp in line:
					a=re.match(reg_hp,temp)
					if a:
						hardpoint.append([a.group(1),a.group(2),a.group(3),
							a.group(4),a.group(5)])
		self.hardpoint=hardpoint
		return self.hardpoint

	def parameter_read(self):
		'''
		'''
		data=self.data
		reg_par=r'(?:\s*)\'(?:\s*)(\w*)(?:\s*)\'(?:\s*)\'(?:\s*)(single|left/right|left|right)'+\
			r'(?:\s*)\'(?:\s*)\'(?:\s*)(-?\w*)(?:\s*)\'(?:\s*)(-?\w*.?\w*\+?\w*)(?:\s*)'
		parameter=[]
		if 'parameter' in data:
			for line in data['parameter']:
				for temp in line:
					a=re.match(reg_par,temp)
					if a:
						parameter.append([a.group(1),a.group(2),a.group(3),a.group(4)])
		self.parameter=parameter
		return self.parameter

	def subsystem_read(self):
		'''
		'''
		reg_list=[]
		reg_list.append(self.reg_list[4].format(r'major(?:\s*)role'))
		reg_list.append(self.reg_list[4].format(r'minor(?:\s*)role'))
		reg_list.append(self.reg_list[4].format('template'))
		reg_list.append(self.reg_list[0].format('usage'))
		subsystem=self.singel_parameter_match(title_name='subsystem',data=self.data,reg_list=reg_list)
		self.subsystem=subsystem
		return self.subsystem

	def testrig_read(self):
		'''
		'''
		reg_list=[]
		reg_list.append(self.reg_list[0].format('usage'))
		testrig=self.singel_parameter_match(title_name='testrig',data=self.data,reg_list=reg_list)
		self.testrig=testrig

	def solver_setting_read(self):
		'''
		'''
		data=self.data
		title_name='solver_settings'
		solver_settings=[]
		reg1=r'(?:\s*)(\w*)(?:\s*)=(?:\s*)\'?((\w*)|(\d*.?\d*))(?:\s*)\'?'
		if title_name.lower() in data:
			for line in data[title_name]:
				for temp in line:
					a_temp=[]
					a=re.match(reg1,temp)
					if a:
						a_temp.append(a.group(1))
						a_temp.append(a.group(2))
					solver_settings.append(a_temp)
		self.solver_settings=solver_settings
		return self.solver_settings

	@staticmethod
	def singel_parameter_match(title_name,data,reg_list):
		'''
			单参数获取
			指定规则正则表达式
			输入:
				title_name : data中的指定位置
				data : 总数据
				reg_list : 列表，正则表达式
			输出:
				列表
		'''
		dataOut=[]
		if title_name.lower() in data:
			for line in data[title_name]:
				temp=[]
				for line2 in line:

					for reg in reg_list:
						m=re.match(reg,line2)
						if m:
							temp.append(m.group(1))
				dataOut.append(temp)
		return dataOut

	@staticmethod
	def double_parameter_match(title_name,data,reg_list):
		'''
			双参数获取
			指定规则正则表达式
			输入:
				title_name : data中的指定位置
				data : 总数据
				reg_list : 列表，正则表达式
			输出:
				字典 : 第一个匹配为字典 键值 ，第二个为键值对应的 元素
		'''
		dataOut=dict()
		if title_name.lower() in data:
			for line in data[title_name]:
				temp=[]
				for line2 in line:
					for reg in reg_list:
						m=re.match(reg,line2)
						if m:
							dataOut[m.group(1)]=m.group(2)
		return dataOut

	@staticmethod
	def symmetry_split(dataInput,loc):
		'''
			对称分割
			输入：

			dataInput type:list 
		'''
		len_data=len(dataInput)
		for n in range(0,len_data):
			if dataInput[n][loc] == r'left/right':
				dataInput[n][loc]='right'
				dataInput.append(copy.copy(dataInput[n]))
				dataInput[n][loc]='left'
		return dataInput

'''sub 子系统文件读取'''
class SubFile(AsyFile):
	'''
		the sub file data structure is the same as asy file
		including data , hardpoint , file_path , parameter
	'''
	def __init__(self,file_path):
		# super(SubFile,self).__init__(file_path)
		self.file_path=file_path
		self.file_read(file_path)
		self.hardpoint_read()
		self.parameter_read()
		self.subheader_read()
		self.spring_read()
		self.damper_read()
		self.bumpstop_read()
		self.reboundstop_read()
		self.bushing_read()

	def subheader_read(self):
		'''
		'''
		reg_list=[]
		for n in range(0,3):
			reg_list.append(self.reg_list[2])
		subHeader=self.double_parameter_match(title_name='subsystem_header',data=self.data,reg_list=reg_list)
		self.subHeader=subHeader

	def spring_read(self):
		'''
		'''
		reg_list=[]
		reg_list.append(self.reg_list[0].format('usage'))
		reg_list.append(self.reg_list[0].format('symmetry'))
		reg_list.append(self.reg_list[0].format('property_file'))
		reg_list.append(self.reg_list[0].format('value_type'))
		reg_list.append(self.reg_list[1].format('user_value'))
		spring=self.singel_parameter_match(title_name='nspring_assembly',data=self.data,reg_list=reg_list)
		spring=self.symmetry_split(dataInput=spring,loc=1)
		self.spring=spring

	def damper_read(self):
		'''
		'''
		reg_list=[]
		reg_list.append(self.reg_list[0].format('usage'))
		reg_list.append(self.reg_list[0].format('symmetry'))
		reg_list.append(self.reg_list[0].format('property_file'))
		damper=self.singel_parameter_match(title_name='damper_assembly',data=self.data,reg_list=reg_list)
		damper=self.symmetry_split(dataInput=damper,loc=1)
		self.damper=damper 

	def bumpstop_read(self):
		'''
		'''
		reg_list=[]
		reg_list.append(self.reg_list[0].format('usage'))
		reg_list.append(self.reg_list[0].format('symmetry'))
		reg_list.append(self.reg_list[0].format('property_file'))
		reg_list.append(self.reg_list[0].format('distance_type'))
		reg_list.append(self.reg_list[1].format('user_distance'))
		bumpstop=self.singel_parameter_match(title_name='bumpstop_assembly',data=self.data,reg_list=reg_list)
		bumpstop=self.symmetry_split(dataInput=bumpstop,loc=1)
		self.bumpstop=bumpstop

	def reboundstop_read(self):
		reg_list=[]
		reg_list.append(self.reg_list[0].format('usage'))
		reg_list.append(self.reg_list[0].format('symmetry'))
		reg_list.append(self.reg_list[0].format('property_file'))
		reg_list.append(self.reg_list[0].format('distance_type'))
		reg_list.append(self.reg_list[1].format('user_distance'))
		reboundstop=self.singel_parameter_match(title_name='reboundstop_assembly',data=self.data,reg_list=reg_list)
		reboundstop=self.symmetry_split(dataInput=reboundstop,loc=1)
		self.reboundstop=reboundstop

	def bushing_read(self):
		'''
		'''
		reg_list=[]
		reg_list.append(self.reg_list[0].format('usage'))
		reg_list.append(self.reg_list[0].format('symmetry'))
		reg_list.append(self.reg_list[0].format('property_file'))
		bushing=self.singel_parameter_match(title_name='bushing_assembly',data=self.data,reg_list=reg_list)
		bushing=self.symmetry_split(dataInput=bushing,loc=1)
		self.bushing=bushing

'''cfg 文件读取'''
class CfgFile:
	'''
		配置文件 cfg  读取
	'''
	def __init__(self,file_path):
		self.file_path=file_path
		self.file_read(file_path)
		self.database_read()

	def file_read(self,file_path):
		fileid=open(file_path,'r')
		data=fileid.readlines()
		fileid.close()
		self.data=data

	def database_read(self):
		database=dict()
		data=self.data
		reg1=r'(?:\s*)database(?:\s*)(\S*)(?:\s*)(.*cdb)(?:\s*)'
		for line in data:
			line=line.lower()
			m=re.match(reg1,line)
			if m:
				database[m.group(1)]=m.group(2)
		self.database=database

	def convert_apath(self,file_path):
		'''
		'''
		file_path=file_path.lower()
		reg1=r'<(\S*)>(\S*)'
		reg2=r'mdids://(\w*)/(\S*)'
		m=re.match(reg1,file_path)
		m2=re.match(reg2,file_path)
		if m :
			cdb_name=m.group(1)
			subPath=m.group(2)
		elif m2:
			cdb_name=m2.group(1)
			subPath=m2.group(2)
		
		if subPath[0]!=r'\\' and subPath[0]!=r'/':
			subPath=r'/'+subPath
		try:
			absolutePath=self.database[cdb_name]+subPath
		except:
			# 判断是否系统默认 数据库
			tempPath=car_file_loc.cdb_search_default(cdb_name)
			if tempPath:
				absolutePath=tempPath+subPath
			else:
				absolutePath=''
				print('warning :{}---{}'.format(file_path,cdb_name))
		return absolutePath

	def convert_rpath(self,file_path):
		'''
		'''
		file_path=file_path.lower()
		reg1=r'(?:\S*)/(\S*).cdb/(\S*)'
		m=re.match(reg1,file_path)
		if m:
			cdb_name=m.group(1)
			subPath=m.group(2)
			relativePath=r'mdids://{}/{}'.format(cdb_name,subPath)
		return relativePath


if __name__=='__main__':

	# SubFile test
	print('='*20,'SubFile','='*20)
	sub_path=r'E:\Software\MSC.Software\Adams\2017_2\acar\shared_car_database.cdb\subsystems.tbl\TR_Front_Suspension.sub'
	print('\n\nread file:{}'.format(sub_path))
	subData=SubFile(sub_path)

	print('\n\nsubData.subHeader')
	for line in subData.subHeader:
		print(line+' = '+subData.subHeader[line])
	print('\n\nsubData.spring')
	for line in subData.spring:
		print(line)
	print('\n\nsubData.damper')
	for line in subData.damper:
		print(line)
	print('\n\nsubData.bumpstop')
	for line in subData.bumpstop:
		print(line)
	print('\n\nsubData.reboundstop')
	for line in subData.reboundstop:
		print(line)
	print('\n\nsubData.bushing')
	for line in subData.bushing:
		print(line)
	print('\n\nsubData.hardpoint')
	for line in subData.hardpoint:
		print(line)
	print('\n\nsubData.parameter')
	for line in subData.parameter:
		print(line)


	# AsyFile test
	print('='*20,'AsyFile','='*20)
	asyAdr=r'E:\Software\MSC.Software\Adams\2017_2\acar\shared_car_database.cdb\assemblies.tbl\MDI_Demo_Vehicle.asy'
	print('read file:{}'.format(asyAdr))
	asyData=AsyFile(asyAdr)
	print('\n\nasyData.hardpoint')
	for line in asyData.hardpoint:
		print(line)
	print('\n\nasyData.parameter')
	for line in asyData.parameter:
		print(line)
	print('\n\nasyData.subsystem')
	for line in asyData.subsystem:
		print(line)
	print('\n\nasyData.testrig')
	for line in asyData.testrig:
		print(line)
	print('\n\nasyData.solver_settings')
	for line in asyData.solver_settings:
		print(line)

