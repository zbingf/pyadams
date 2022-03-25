"""
	tk常用交互
"""

import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import os.path

def file_prepost(type_names, file_types): #数据转化
	
	if isinstance(file_types, str):
		file_types = [file_types]
		type_names = [type_names]
	list_filetypes = []
	for file_type, type_name, in zip(file_types, type_names):
		list_filetypes.append((type_name, file_type))

	tuple_filetypes = tuple(list_filetypes)
	return tuple_filetypes

# 选择文件  单选/多选
def choose_files(type_names, file_types, title, isSingle=True, isMultiChoose=True): #文件选择
	
	if isSingle: tk.Tk().withdraw()

	tuple_filetypes = file_prepost(type_names, file_types)

	if isMultiChoose:
		file_paths = tkinter.filedialog.askopenfilenames(filetypes=tuple_filetypes, title=title)
	else:
		file_paths = tkinter.filedialog.askopenfilename(filetypes=tuple_filetypes, title=title)

	return file_paths

# 选择文件保存路径
def save_file(type_name, file_type, title, isSingle=True): #文件保存路徑

	if isSingle: tk.Tk().withdraw()

	tuple_filetypes= file_prepost(type_name, file_type)

	path = tkinter.filedialog.asksaveasfilename(filetypes=tuple_filetypes, title=title)

	str_list1 = path.split('.')
	if len(str_list1)>1:
		name_in = '.'.join(str_list1[:-1])
		type_in = str_list1[-1]
	else:
		name_in = path
		type_in = ''

	if not path or not name_in:	return None

	for line in tuple_filetypes:
		if type_in.lower() in line[1].lower() and type_in:
			path = name_in + '.' + type_in
			break
	else:
		if type_in:
			path = name_in + '.' + type_in + '.' + file_type
		else:
			path = name_in + '.' + file_type

	if len(os.path.basename(path)) <= len(file_type)+1:
		return None

	return path

def ask(str1, title='提问', isSingle=True):
	if isSingle: tkinter.Tk().withdraw()
	return tkinter.messagebox.askokcancel(title, str1)

def warning(str1, title='UE', isSingle=True):
	if isSingle: tkinter.Tk().withdraw()
	return tkinter.messagebox.showwarning(title, str1)

def error(str1,	title='错误', isSingle=True):
	if isSingle: tkinter.Tk().withdraw()
	return tkinter.messagebox.showerror(title, str1)

def info(str1,	title='提示', isSingle=True):
	if isSingle: tkinter.Tk().withdraw()
	return tkinter.messagebox.showinfo(title, str1)

if __name__ == '__main__':
	pass
	# ask('1')
	# warning('2')
	# error('3')
	# info('4')
	
	# print(save_file('python', 'py', '保存为py文件'))
	print(choose_files(['result', 'others'], ['res', '*'], '读取res文件'))