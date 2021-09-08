"""
	python version : 3.7
	Adams version : 2017.2
	用途：
		Car文件 解析
	2020/11
"""
import re
import os
import matplotlib.pyplot as plt


class FileRead:
	'''
		文件读取
	'''
	def __init__(self,path):
		self.filepath = path

	def read(self):
		with open(self.filepath,'r') as f:
			data_str = f.read()
		f.close()
		self.data_str = data_str

	def tolist(self,del_space=False):
		'''
			将str文本转化为list
			del_space = False 不删除空列表
		'''
		data_list = self.data_str.split('\n')
		if del_space:
			new_data_list = []
			for line in data_list:
				if line :
					new_data_list.append(line)
			self.data_list = new_data_list

		else:
			self.data_list = data_list

class FileSpring(FileRead):
	'''
		弹簧文件 *.spr 文件读取
		self.x 横坐标 位移
		self.y 纵坐标 力
	'''
	def __init__(self,path):
		super().__init__(path)
		self.read()
		self.tolist(False)
		self.__get_title()
		self.__get_maindata()

	def __get_title(self):
		pattern = re.compile('(.*}).*',re.DOTALL)
		title = pattern.match(self.data_str).group(1)+'\n'
		self.title = title

	def get_springlength(self):
		try:
			pattern = re.compile('.*(FREE_LENGTH\s*=\s*\S*).*',re.DOTALL | re.IGNORECASE)
			pattern2 = re.compile('.*=\s*(\S*).*',re.DOTALL | re.IGNORECASE)
			line = pattern.match(self.data_str).group(1)
			length = float(pattern2.match(line).group(1))
			self.free_length_str = line
			self.free_length = length
			return length,line
		except IndexError:
			return None

	def __get_maindata(self):
		start = False
		pattern = re.compile('\s*(\S*)\s*(\S*)\s*')
		x = []
		y = []
		for line in self.data_list:
			if start and line:
				reobj = pattern.match(line)
				f1 = (float(reobj.group(1)))
				f2 = (float(reobj.group(2)))
				x.append(f1)
				y.append(f2)
			if '}' in line:
				start = True
		self.x = x
		self.y = y

	def show(self):
		plt.plot(self.x,self.y,label = 'spring displacement vs force')
		plt.xlabel('dis mm')
		plt.ylabel('force N')
		plt.legend()
		plt.show()

class FileDamper(FileSpring):
	'''
		减振器 *.dam 数据读取
		self.x 横坐标 速度
		self.y 纵坐标 力
	'''
	def __init__(self,path):
		super().__init__(path)

	def show(self):
		plt.plot(self.x,self.y,label = 'damper velocity vs force')
		plt.xlabel('vel mm/s')
		plt.ylabel('force N')
		plt.legend()
		plt.show()

class FileEdit:
	'''
		文件编辑
	'''
	def __init__(self,fileobj):
		self.filepath = fileobj.filepath
		self.fileobj = fileobj
		self.data_str = fileobj.data_str

	def write(self,newpath=None):
		if newpath!=None:
			filepath = newpath
		else:
			filepath = self.filepath
		with open(filepath,'w') as f:
			f.write(self.data_str)

class FileSpringEdit(FileEdit,FileSpring):
	'''
		弹簧文件编辑
	'''
	def __init__(self,sprobj):
		super().__init__(sprobj)
		self.x = self.fileobj.x
		self.y = self.fileobj.y
		self.title = self.fileobj.title

	def updata(self,newpath=None):
		'''
			更新文件 title x y 拼接
			newpath 创建新文件
		'''
		data = []
		for x0,y0 in zip(self.x,self.y):
			data.append('{} {} '.format(x0,y0))
		data1 = '\n'.join(data)
		self.data_str = self.title + data1

		self.write(newpath)

	def length_edit(self,length):
		'''
			弹簧自由长度替换
		'''
		self.get_springlength()
		self.free_length = length
		# print(self.free_length_str)
		self.title = re.sub(self.free_length_str,'FREE_LENGTH  =  {}'.format(length),self.title)
		# print(self.title)

class FileDamperEdit(FileSpringEdit):
	'''
		减振器文件编辑
	'''
	def __init__(self,dprobj):
		super().__init__(dprobj)




if __name__ == '__main__':
	sprpath = r'..\code_test\file_test.spr'
	new_sprpath = r'..\code_test\file_test_new.spr'
	sprobj = FileSpring(sprpath)
	# sprobj.show()
	print(sprobj.get_springlength())
	spredit_obj = FileSpringEdit(sprobj)
	spredit_obj.x[0] = -200.0
	spredit_obj.length_edit(200)
	spredit_obj.updata(new_sprpath)
	# spredit_obj.show()
	print(FileSpringEdit.__mro__)

	# dampath = r'.\tests\files\mdi_0001.dpr'
	# dprobj = FileDamper(dampath)
	# dprobj.show()