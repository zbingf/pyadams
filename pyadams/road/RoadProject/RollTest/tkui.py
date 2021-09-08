"""
	tkinter 应用
"""
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import json
import re

list2str = lambda list1: ','.join([str(n) for n in list1])
str2list = lambda str1: [float(n) for n in str1.split(',')]
str2int = lambda str1: [int(n) for n in str1.split(',')]

class TkUi:
	"""
		调用tkinter
	"""
	count = 0
	def __init__(self, title):
		TkUi.count +=1 
		# 主界面
		# if isFirst:	
		if TkUi.count == 1 :		
			window = tk.Tk()
		else:
			window = tk.Toplevel()
		window.title(title)
		window.protocol('WM_DELETE_WINDOW', self.close_window)

		self.window = window
		self.frames = {}
		self.entrys = {}
		self.vars = {}
		self.buttons = {}
		self.scale = {}
		self.text = {}
		self.check = {}
		self.loc = 1

	def run(self):
		"""
			运行 UI 界面
		"""
		self.window.mainloop()
		# help(self.window.mainloop)

	def frame_loadpath(self, params): # 读取导航及输入框
		"""
			导入路径
			{
			'frame':'mnf_load',
			'var_name':'mnf_load',
			'path_name':'mnf file',
			'path_type':'.mnf',
			'button_name':'mnf load',
			'button_width':15,
			'entry_width':30,
			}
		"""
		frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)

		def loadpath():
			path = tkinter.filedialog.askopenfilename(filetypes = ((params['path_name'],params['path_type']),))
			var.set(path)

		button = tk.Button(frame,text=params['button_name'],width=params['button_width'],command=loadpath)
		button.pack(side='left')

		var = tk.StringVar()
		var.set('')
		entry = tk.Entry(frame,width=params['entry_width'],show=None,textvariable=var)
		entry.pack(side='left',expand=tk.YES,fill=tk.X)

		self.vars[params['var_name']] = var
		self.buttons[params['var_name']] = button
		self.entrys[params['var_name']] = entry

		self.loc += 1

	def frame_loadpaths(self, params): # 多文件加载
		"""
			导入路径
			{
			'frame':'mnf_load',
			'var_name':'mnf_load',
			'path_name':'mnf file',
			'path_type':'.mnf',
			'button_name':'mnf load',
			'button_width':15,
			'entry_width':30,
			}
		"""
		frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)

		def loadpath():
			path = tkinter.filedialog.askopenfilenames(filetypes = ((params['path_name'],params['path_type']),))
			var.set(','.join(path))

		button = tk.Button(frame,text=params['button_name'],width=params['button_width'],command=loadpath)
		button.pack(side='left')

		var = tk.StringVar()
		var.set('')
		entry = tk.Entry(frame,width=params['entry_width'],show=None,textvariable=var)
		entry.pack(side='left',expand=tk.YES,fill=tk.X)

		self.vars[params['var_name']] = var
		self.buttons[params['var_name']] = button
		self.entrys[params['var_name']] = entry

		self.loc += 1

	def frame_savepath(self, params): # 保存导航及输入框
		"""
			路径保存用
			{
			'frame':'h3d_save',
			'var_name':'h3d_save',
			'path_name':'mnf file',
			'path_type':'.h3d',
			'button_name':'h3d save',
			'button_width':15,
			'entry_width':30,
			}
		"""
		frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)

		def savepath():
			path = tkinter.filedialog.asksaveasfilename(filetypes = ((params['path_name'],params['path_type']),))
			if len(path) < len(params['path_type'])+1 :
				path += params['path_type']
			if not path[-len(params['path_type']):] == params['path_type'] :
				path += params['path_type']
			if path == params['path_type']:
				path = ''
			var.set(path)

		button = tk.Button(frame,text=params['button_name'],width=params['button_width'],command=savepath)
		button.pack(side='left')

		var = tk.StringVar()
		var.set('')
		entry = tk.Entry(frame,width=params['entry_width'],show=None,textvariable=var)
		entry.pack(side='left',expand=tk.YES,fill=tk.X)

		self.vars[params['var_name']] = var
		self.buttons[params['var_name']] = button
		self.entrys[params['var_name']] = entry

		self.loc += 1

	def frame_button(self, params): # 按钮框
		"""
			按钮
			{
			'frame':'test',
			'button_name':'test',
			'button_width':15,
			'func':self.func1, # 回调函数
			}
		"""
		frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)


		button = tk.Button(frame,text=params['button_name'],width=params['button_width'],command=params['func'])
		button.pack(side='left',expand=tk.YES,fill=tk.X)

		# if 'button' in params.keys():
		# 	self.buttons[params['frame']] = button
		# else:
		# 	self.buttons[params['frame']] = button
		self.buttons[params['frame']] = button
		self.loc += 1

	def frame_entry(self, params): # 注释及输入框
		"""
			注释及输入
			params = {
				'frame':'qwer',
				'var_name':'qwer',
				'label_text':'adsf',
				'label_width':15,
				'entry_width':30,
			}
		"""
		frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)

		label = tk.Label(frame,text=params['label_text'],width=params['label_width'])
		label.pack(side='left')

		var = tk.StringVar()
		var.set('')
		entry = tk.Entry(frame,width=params['entry_width'],show=None,textvariable=var)
		entry.pack(side='left',expand=tk.YES,fill=tk.X)
		
		self.vars[params['var_name']] = var
		self.entrys[params['var_name']] = entry

		return True

	def frame_label_only(self, params): # 仅注释
		"""
			注释及输入
			params = {
				'label_text':'adsf',
				'label_width':15,
			}
		"""
		if 'frame' in params:
			frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)

		else:
			frame = tk.Frame(self.window)
			frame.pack(expand=tk.YES, fill=tk.BOTH)
			
		label = tk.Label(frame,text=params['label_text'],width=params['label_width'])
		label.pack(side='left',expand=tk.YES,fill=tk.X) #

		return True

	def frame_check_entry(self, params):
		"""
		params = {
			'frame':'check_entry',
			'check_text':'adsf',
			'check_var':'isVar',
			'entry_var':'var',
			'entry_width':30,
		}
		"""
		frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)

		# 复选框
		var = tk.BooleanVar()
		check = tk.Checkbutton(frame,
			variable = var,
			text=params['check_text'],
			onvalue = True, offvalue = False)
		check.pack(side='left')

		self.check[params['check_var']] = check
		self.vars[params['check_var']] = var

		# entry框
		var = tk.StringVar()
		var.set('')
		entry = tk.Entry(frame,width=params['entry_width'],show=None,textvariable=var)
		entry.pack(side='left',expand=tk.YES,fill=tk.X)
		
		self.entrys[params['entry_var']] = entry
		self.vars[params['entry_var']] = var
		
		return True

	def frame_buttons_RWR(self, params): # 运行，保存，读取按钮
		"""
			运行、保存、读取
			{
				'frame':'rrw',
				'button_run_name':'a',
				'button_write_name':'b',
				'button_read_name':'c',
				'button_width':15,
				'func_run':self.func1,
			}
		"""
		frame = tk.Frame(self.window)
		frame.pack(fill=tk.X) # expand=tk.YES,

		button_run = tk.Button(frame,text=params['button_run_name'],width=params['button_width'],command=params['func_run'])
		button_run.pack(side='left',expand=tk.YES,fill=tk.X)

		button_write = tk.Button(frame,text=params['button_write_name'],width=params['button_width'],command=self.write)
		button_write.pack(side='left',expand=tk.YES,fill=tk.X)

		button_read = tk.Button(frame,text=params['button_read_name'],width=params['button_width'],command=self.read)
		button_read.pack(side='left',expand=tk.YES,fill=tk.X)
		
		self.frames[params['frame']] = frame

		return True

	def frame_note(self): # 备注框，配合self.print
		"""
			用于备注
		"""
		frame = tk.Frame(self.window)
		frame.pack(fill=tk.X) # expand=tk.YES,
		var = tk.StringVar()
		var.set('')
		label = tk.Label(frame,show=None,textvariable=var) # ,width=params['entry_width']
		label.pack(side='left',expand=tk.YES,fill=tk.X) # ,expand=tk.YES

		self.note = var

		return True

	def frame_value_edit(self, params): # 注释+输入+滚动框，变量变更
		"""
			变量 编辑
			带 scale
			frame_value_edit2 = {
			'frame':'value_2',
			'var_name':'value_2',
			'label_text':'变量2', 
			'label_width':15,
			'entry_width':15,
			'scale_range':100, # 
			}
		"""
		frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)

		# 开头备注
		label = tk.Label(frame,text=params['label_text'],width=params['label_width'])
		label.pack(side='left')
		
		# 数值栏
		var = tk.StringVar()
		var.set('')

		
		def entry_callback():
			var.set(var_entry.get())
		var_entry = tk.StringVar()
		var_entry.set(str(params['value']))
		entry = tk.Entry(frame,width=params['entry_width'],show=None,textvariable=var_entry,
			validate='focusout', # focusout
			validatecommand=entry_callback)
		entry.pack(side='left')


		def scale_callback(v): # 回调
			var.set( str(float(entry.get())*(1+float(v)/200)) )
			self.scale_run()

		# scale 
		scale = tk.Scale(frame, from_=-params['scale_range'], to=params['scale_range'], orient=tk.HORIZONTAL,
			length=200, showvalue=0, resolution=1, command=scale_callback)
		scale.pack(side='left')

		label2 = tk.Label(frame, width=params['entry_width'],textvariable=var)
		label2.pack(side='left')

		self.vars[params['var_name']] = var
		self.scale[params['var_name']] = scale

	def frame_text_lines(self, params): # 多行文字输入框
		"""
			多行输入
			params = {
			'frame':'text_1',
			'text_name':'text_1',
			'text_width':50,
			'text_height':15,
			}
		"""
		frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)

		text = tk.Text(frame,
			width=params['text_width'],
			height=params['text_height'],bg='white')
		
		# text.insert("insert", "test")  # 插入
		text.pack(side='left', fill=tk.BOTH, expand=tk.YES)

		if 'isExpand' in params: # 是否扩展
			if params['isExpand']:
				text.pack(expand=tk.YES)
			else:
				text.pack(expand=tk.NO)
		else:
			text.pack(expand=tk.YES)


		self.text[params['text_name']] = text

	def frame_checkbutton(self, params): # 单一复选框
		"""
			复选框
			params = {
			'frame':'check_1',
			'var_name':'check_1',
			'check_text':'是否作图',
			}
		"""
		frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)

		var_name = params['var_name']
		var = tk.BooleanVar()

		check = tk.Checkbutton(frame,
			variable = var,
			text=params['check_text'],
			onvalue = True, offvalue = False)
		check.pack(side='left')


		self.check[var_name] = check
		self.vars[var_name] = var

	def frame_checkbuttons(self, params): # 多个复选框
		"""
			复选框
		params = {
			'frame':'check_1',
			'vars':['isA','isB'],
			'check_texts':['是否A','是否B'],
		}
		"""
		frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)

		for varname, check_text in zip(params['vars'], params['check_texts']):
			var = tk.BooleanVar()
			check = tk.Checkbutton(frame,
				variable = var,
				text=check_text,
				onvalue = True, offvalue = False)
			check.pack(side='left') # 

			self.check[varname] = check
			self.vars[varname] = var

	def frame_radiobuttons(self, params): # 单选框
		"""
			单选框
			params = {
			'frame':'loading_type',
			'var_name':'loading_type',
			'texts':['rsp读取方式', 'res读取方式', 'res输入,读取rsp'],
			}
			输出变量状态:  计数从1开始
		"""
		frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)

		var = tk.IntVar()
		var.set(1)

		for num, text in enumerate(params['texts']):
			radio = tk.Radiobutton(frame, text=text, variable=var, value=num+1)
			radio.pack(side='left', expand=tk.YES, fill=tk.X)

		self.vars[params['frame']] = var

	def get_text(self, name): # 多行文本数据读取
		"""
			获取 text 多行文本
			name ： text的frame名称
		"""
		return self.text[name].get(1.0,tk.END)

	def set_text(self, name, str1): # 多行文本框写入
		"""
			写入 text 多行文本
			name ： text 的frame名称
			str1 ： 写入字符窜
		"""
		self.text[name].delete(1.0,tk.END)
		self.text[name].insert('insert',str1)
		return True

	def get_vars(self): # 获取当前所有var变量
		
		var_names = list(self.vars.keys())
		params = {}
		for name in var_names:
			params[name] = self.strline_parse(self.vars[name].get())
			

		return params

	def get_texts(self): # 获取所有text的多行字符串数据
		
		var_names = list(self.text.keys())
		params = {}
		for name in var_names:
			params[name] = self.get_text(name)

		return params

	def get_vars_and_texts(self): # 所有 var及text数据导出
		# 注：var与text的key不能重名
		params = self.get_vars()
		params2 = self.get_texts()
		params.update(params2)
		return params

	def scale_run(self): # scale统一调用
		"""
			用于scale 的统一调用
		"""
		pass

	def write(self):
		"""
			写入 json
			用于保存数据
		"""
		values = {}
		for name in self.vars.keys():
			values[name] = self.vars[name].get()
		
		if len(self.text.keys()) > 0:
			for name in self.text.keys():
				values[name+'_TYPE_TEXT'] = self.get_text(name)

		path = tkinter.filedialog.asksaveasfilename(filetypes = (('json','.json'),))
		if '.json' != path[-5:]:
			path += '.json'

		if '.json' != path:
			with open(path,"w") as f:
				json.dump(values,f)
			self.print('写入结束')
		else:
			self.print('未写入')

		return True

	def read(self, path=None):
		"""
			读取 json
			用于读取数据
		"""
		if path == None:
			path = tkinter.filedialog.askopenfilename(filetypes = (('json','.json'),))

		if '.json' != path[-5:]:
			path += '.json'

		if '.json' != path : 
			"""非空"""
			with open(path,"r") as f:
				values = json.load(f)

			for name in values.keys():
				if name not in self.vars.keys():
					if '_TYPE_TEXT' in name:
						# text 数据
						self.set_text(name.split('_TYPE_TEXT')[0],values[name])
						continue
					else:
						self.print('读取错误，变量: {} 不存在'.format(name))
						return False
				self.vars[name].set(values[name])

			self.print('读取结束')
		else:
			self.print('取消读取')
		return True

	def print(self, str1): # 备注框写入
		"""
			备注
			需提前调用 frame_note
		"""
		self.note.set(str1)
		return True

	def create_frame(self, frame_name, expand=tk.YES, fill=tk.X): # 根据frame名称返回frame对象
		"""
			创建frame
				若frame已存在则直接返回frame对象
		"""
		if frame_name in self.frames.keys():
			frame = self.frames[frame_name]
			frame.pack(expand=expand, fill=fill)
		else:
			frame = tk.Frame(self.window)
			frame.pack(expand=expand, fill=fill)
			self.frames[frame_name] = frame

		return frame

	def close_window(self):
		# 关闭时结束程序
		self.window.quit()
		self.window.destroy()
		
	@staticmethod
	def strline_parse(value): 
		"""解析单行字符串数据"""
		def str_single_parse(str_value):
			"""	无空格单行字符串,非列表格式转化 """
			isFloat = lambda str1: re.match(r'\A\+?\-?\d+\.\d+\Z',str1) 	# 是否为字符串
			isInt = lambda str1: re.match(r'\A\+?\-?\d+\Z',str1)			# 是否为整数
			isNone = lambda str1: str1.lower()=='none'
			isbool = lambda str1: str1.lower()=='false' or str1.lower()=='true'
			str2bool = lambda str1: True if str1.lower()=='true' else False
			if isFloat(str_value): 
				value = float(str_value)
				if value==int(value):
					return int(value)
				else:
					return value
			if isInt(str_value): return int(str_value)
			if isbool(str_value): return str2bool(str_value)
			if isNone(str_value): return None
			return str_value

		if type(value) != str: # 非字符串,返回
			return value

		str_value = re.sub(r'\s','',value).lower()	# 去空格

		if ',' in str_value:
			list1 = str_value.split(',')
			list2 = []
			for n in list1:
				list2.append(str_single_parse(n))
			return list2

		return str_single_parse(value)
