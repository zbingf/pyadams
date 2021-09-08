"""

file 模块
文件读写处理

"""
import re
import os.path

class TxtFile:# 未启用
	"""
		文本读写：
			1、读取
			2、重写
	"""
	def __init__(self,file_path):
		self.file_path = file_path

	def read(self): # 读原数据
		"""
			读取文件
		"""
		with open(self.file_path,'r') as f:
			self.file_str = f.read()

		self.file_list = self.file_str.split('\n')

	def write(self,new_path=None,new_str=None):
		"""
			写入文件
			new_path 新路径, None则使用 file_path
			new_str 新字符串, None则使用 file_str

		"""
		if new_path == None:
			new_path = self.file_path
		if new_str == None:
			new_str = self.file_str

		with open(new_path,'w') as f:
			f.write(new_str)

class CfgFile(TxtFile):# 未启用
	'''
		配置文件 cfg  读取
	'''
	def __init__(self,file_path):
		super().__init__(file_path)
		self.read()
		self.database_read()

	def database_read(self):
		self.data = self.file_str.split('\n')
		database=dict()
		data=self.data
		reg1=r'(?:\s*)database(?:\s*)(\S*)(?:\s*)(.*cdb)(?:\s*)'
		for line in data:
			line=line.lower()
			m=re.match(reg1,line)
			if m:
				database[m.group(1)]=m.group(2)
		self.database=database

	def convert_apath(self,file_path): # 数据转换 ing
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

	def convert_rpath(self,file_path): # 数据转换 ing
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

class LftFile(TxtFile):# 未启用
	"""
		leafspring 文件
	"""
	pass

class CarModelFile(TxtFile):# 未启用
	"""
		car 模型文件
			spring
			damper
			asy
			sub
	"""
	reg_list=[
		r'(?:\s*){}(?:\s*)=(?:\s*)\'(?:\s*)(\S*)(?:\s*)\'', 	# test = ' target2 '
		r'(?:\s*){}(?:\s*)=(?:\s*)(\S*)(?:\s*)', 				# test =  target2 
		r'(?:\s*)(\S*)(?:\s*)=(?:\s*)\'(?:\s*)(\S*)(?:\s*)\'', 	# target1 = ' target2 '
		r'(?:\s*)(\S*)(?:\s*)=(?:\s*)(\S*)(?:\s*)', 			# target1 =  target2 
		r'\$?(?:\s*){}(?:\s*):(?:\s*)(\S*)(?:\s*)', 			# $ test :  target2 
	]

	def __init__(self,file_path):
		super().__init__(file_path)
		self.read()
		self.pre_cal()

	def pre_cal(self):
		'''
			read sub file 
		'''
		data_list = self.file_str.split('\n')

		reg=r'\[(\w*)\]'
		data=dict()
		temp=[]
		for line in data_list:
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

class AsyFile(CarModelFile):# 未启用
	"""
		2019 ADAMS
		[MDI_HEADER] 
		[ASSEMBLY_HEADER] 
		[PLUGINS] 
		[UNITS]
		[SUBSYSTEM]
		[HARDPOINT]
		[PARAMETER]
		[SOLVER_SETTINGS]

	"""

	def __init__(self,file_path):
		super().__init__(file_path)

	def assembly_header():
		"""	
			[ASSEMBLY_HEADER] 辨识
			装配系统 
		"""
		pass

	def subsystem():
		"""	
			[SUBSYSTEM] 辨识
			子系统数据读取
		"""
		pass

class SpringFile(CarModelFile):# 未启用
	"""
		[MDI_HEADER]
		[UNITS]
		[SPRING_DATA]
		[CURVE]
	"""
	def __init__(self,file_path):
		super().__init__(file_path)

class DamperFile(CarModelFile):# 未启用
	"""
		[MDI_HEADER]
		[UNITS]
		[CURVE]
	"""
	def __init__(self,file_path):
		super().__init__(file_path)

class BuhingFile(CarModelFile): # 未启用
	"""
		[MDI_HEADER]
		[UNITS]
		[DAMPING]
		[FX_CURVE]
		[FY_CURVE]
		[FZ_CURVE]
		[TX_CURVE]
		[TY_CURVE]
		[TZ_CURVE]
	"""
	def __init__(self,file_path):
		super().__init__(file_path)



if __name__ == '__main__':
	
	# file_path = r'..\code_test\file_test.spr'
	# obj1 = CarModelFile(file_path)
	# print(obj1.data)

	# file_path = r'..\code_test\asy_2019.asy'
	# obj2 = AsyFile(file_path)
	# # print(obj2.data['mdi_header'])
	# # print(obj2.data['SUBSYSTEM'.lower()])

	# file_path = r'..\code_test\sus_2019.sub'
	# obj3 = CarModelFile(file_path)
	# # print(obj3.data['subsystem_header'])


	# file_path = r'..\code_test\sus_2019.sub'
	# obj4 = CarModelFile(file_path)
	# # print(obj3.data['subsystem_header'])

	# file_path = r'..\code_test\file_test.dpr'
	# obj5 = CarModelFile(file_path)
	# print(obj5.data)

	# file_path = r'..\code_test\file_test.bus'
	# obj6 = CarModelFile(file_path)
	# print(obj6.data)

	# file_path = r'..\code_test\file_test.cfg'
	# obj7 = CfgFile(file_path)
	# print(obj7.database)	
	

	print(get_file_size(r'D:\document\ADAMS\test_9_maintain.res','mb'))

	print(get_file_size(r'D:\document\ADAMS\test_9_maintain.res','gb'))

	# help(AsyFile)