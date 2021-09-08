"""
	
	office文档编辑替换
	需已安装微软office
	
	外部库： pywin32

"""

# WordEdit.py
import win32com
from win32com.client import Dispatch,constants
import collections
import os
import csv
import xlsxwriter

import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


class ExcelEdit:
	"""
		Excel 创建及编辑
	"""
	def __init__(self, filename=None):  # 打开文件 或 新建文件并命名
		self.xlApp = win32com.client.Dispatch("Excel.Application")
		self.xlApp.Visible = 1  #0代表隐藏对象，但可以通过菜单再显示-1代表显示对象2代表隐藏对象，但不可以通过菜单显示，只能通过VBA修改为显示状态"""
		self.xlApp.DisplayAlerts = 0  # 后台运行，不显示，不警告
		if filename != None:
			if os.path.isfile(filename) is True:
				self.filename = filename
				self.xlBook = self.xlApp.Workbooks.Open(filename)
			else:
				self.xlBook = self.xlApp.Workbooks.Add()
				self.xlBook.SaveAs(filename)
		else:
			self.xlBook = self.xlApp.Workbooks.Add()

	def save(self, newfilename=None):  # 保存文件
		if newfilename:
			self.filename = newfilename
			self.xlBook.SaveAs(newfilename)
		else:
			self.xlBook.Save()

	def close(self):  # 关闭文件
		self.xlBook.Close(SaveChanges=0)
		del self.xlApp

	def get_rows(self,sheet = "Sheet1"): # 数据行数
		sht = self.xlBook.Worksheets(sheet)
		return sht.usedrange.rows.count

	def get_cols(self,sheet = "Sheet1"): # 数据列数
		sht = self.xlBook.Worksheets(sheet)
		return sht.usedrange.columns.count

	def get_cell(self, sheet="Sheet1", loclist=[1,1]):  # 获取指定单元格的数据
		"Get value of one cell"
		sht = self.xlBook.Worksheets(sheet)
		return sht.Cells(loclist[0], loclist[1]).Value

	def get_range(self, sheet, start_loc, end_loc):  # 获得一块区域的数据，返回为一个二维元组
		"return a 2d array (i.e. tuple of tuples)"
		sht = self.xlBook.Worksheets(sheet)
		return sht.Range(sht.Cells(start_loc[0], start_loc[1]), sht.Cells(end_loc[0], end_loc[1])).Value

	def add_picture(self, sheet, pictureName, Left, Top, Width, Height):  # 插入图片》》 未完成
		"Insert a picture in sheet"
		sht = self.xlBook.Worksheets(sheet)
		sht.Shapes.AddPicture(pictureName, 1, 1, Left, Top, Width, Height)

	def add_sheet(self,sheet="Sheet1"): # 创建新表格，并命名,重名则尾号添加
		sht = self.xlBook.Worksheets.Add()
		n=1
		while True:
			try:
				sht.Name=sheet
			except:
				sheet=sheet+"_"+str(n)
				if len(sheet)>30:
					sheet=sheet[-30:]
				n+=1
			else:
				break
		return sheet

	def copy_sheet(self,sheet):  # 复制工作表 数字或名称
		"copy sheet"
		sht = self.xlBook.Worksheets
		sht(sheet).Copy(None, sht(sheet))

	def set_cell(self, sheet, value, loclist=[1,1]):  # 设置单元格的数据 指定sheet
		"set value of one cell"
		sht = self.xlBook.Worksheets(sheet)
		sht.Cells(loclist[0], loclist[1]).Value = value

	def set_content_list(self,data_list,sheet="Sheet1",start_loc=[1,1],header = None): # 列表输入
		"""	
			列表输入
			datalist ：列表 二维数据，先行后列
			sheet ：指定工作列表，默认为sheet1
			start_loc ： 输入数据起始位置
			header： 输入数据表头，如不设置，默认为None
		"""
		# 表头判定
		if header != None and type(header) == list:
			# 表头输入
			cols = len(header)
			for col in range(0,cols):
				self.set_cell(sheet=sheet,value=header[col],loclist=[start_loc[0],col+start_loc[1]])#设置头
			start_loc[0] += 1
		# 列表输入
		for row,item in enumerate(data_list):
			# print(item)
			for col in range(0,len(item)):                    
				self.set_cell(sheet=sheet,value=item[col],loclist=[row+start_loc[0],col+start_loc[1]])

	def get_content(self,sheet="Sheet1"): # 获取工作表内容 ,返回字典列表》》 未完成
		"""
			默认起始位置[1,1]
			获取整个工作表内容，返回一个字典列表
			key为header也就是excel首行内容。
		"""
		key_list =[];data_list =[]
		rows = self.get_rows(sheet)
		cols = self.get_cols(sheet)
		print(rows,cols)
		for col in range(0, cols):
			key_list.append((self.get_cell(sheet=sheet,loclist=[1,col + 1])))
		for row in range(rows):
			data = collections.OrderedDict()   #创建有序字典
			for col in range(cols):
				# self.__addWord(data,key_listcol],self.get_cell(sheet=sheet,row=row+2,col=col+1))
				# print(type(self.get_cell(sheet=sheet,row=row + 2, col=col + 1)))
				datakey_listcol = str(self.get_cell(sheet=sheet,loclist=[row + 2, col + 1]))
			data_list.append(data)
		return data_list

	def get_header(self,sheet="Sheet1",start_loc=[1,1]):  # 获取表头》》 未完成
		key_list = []
		cols = self.get_cols(sheet) # 列数
		for col in range(0, cols):
			key_list.append(self.get_cell(sheet=sheet, row=start_loc[0], col=col + start_loc[1]))
		return key_list

	def rename_sheet(self,sheet="Sheet1",newname = None): # 重命名
		if newname == None:
			return False
		else:
			self.xlBook.Worksheets(sheet).Name=newname

	def row_delete(self,sheet="Sheet1",row_start=0,row_stop=0): # 删除指定表格的指定行 未完成
		sht = self.xlBook.Worksheets(sheet)
		# if row_stop!=0
		# for i in range(row_start,row_stop)
		if row_stop!=0 and row_stop!=0:
			avg = "{}:{}".format(str(row_start),str(row_stop))
			sht.rows(avg).delete

	def __addWord(self,theIndex, word, pagenumber): # 未完成
		theIndex.setdefault(word, []).append(pagenumber)  # 存在就在基础上加入列表，不存在就新建个字典



# csv 转 excel  xlsx
def csv2excel_xlsx(workbook, csv_path, sheet_name):
	"""
		xlsxwriter、csv 库

		csv文件读取 并转化为excel的表跟数据
		workbook 	xlwt.Workbook 实例
		csv_path 	目标csv文件路径
		sheet_name 	目标表跟数据的sheet名称
	"""
	if len(sheet_name)>31: # excel表格名称字符不能超31
		sheet_name = sheet_name[-31:]

	worksheet = workbook.add_worksheet(name = sheet_name)
	with open(csv_path, 'r') as f:
		rows = csv.reader(f)
		for irow, row in enumerate(rows):
			for icol, value in enumerate(row):
				try:
					value = float(value)
				except:
					pass
				worksheet.write(irow, icol, value)

	return workbook


def test_csv2excel_xlsx():

	# 文件保存 - xlsx
	workbook = xlsxwriter.Workbook(filename=csv_path[:-3]+'xlsx')
	csv2excel_xlsx(workbook, csv_path, sheet_name)
	workbook.close()


if __name__ == "__main__":

	pass

	# # Excel
	# excelobj=ExcelEdit(r"D:\python\adams_python\pyadams\adams_pyqt5\test.xlsx")
	# print(excelobj.get_rows())
	# print(excelobj.get_cols())
	# excelobj.add_sheet("test")
	# # excelobj.rename_sheet("Sheet1",'test')
	# excelobj.set_cell("Sheet1","test",[1,1])
	# print(excelobj.get_range("Sheet1",[2,2],[4,4]))
	# # excelobj.copy_sheet("Sheet1")
	# excelobj.copy_sheet("test")
	# excelobj.add_sheet("as")
	# excelobj.set_content_list([[1,2,3,4],[5,6,7,8]],sheet="test",start_loc=[2,2],header=[12,13,14,15])
	# excelobj.rename_sheet("Sheet1","zxcv")
	# print(excelobj.get_content("zxcv"))

	# PPt
	# pptAdr=r"C:\Users\ABing\Desktop\test11.pptx"
	# ppt=win32com.client.Dispatch("PowerPoint.Application")
	# ppt.Presentations.Open(pptAdr)
	# ppt.Visible=True
	# ppt.TextChange

	print("end")


