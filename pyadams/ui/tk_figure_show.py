"""
	数据选取, 选择性作图
"""
from pyadams.ui import tkfig, tkui
import tkinter as tk


class TkFigureShowData:
	# 要求数据长度一致

	def __init__(self, data):
		self.data = data

	def set_data(self, data):
		self.data = data

	def clear_data(self):
		del self.data
		self.data = {}

class TkFigureShow(tkfig.TkFigure, tkui.TkListBox):

	def __init__(self, title, data_obj, frame=None):
		super().__init__(title, frame=frame)
	
		self.data_obj = data_obj

		self.frame_button({'frame':'flist0', 'button_name':'数据获取', 'button_width':50,
			'func':self.set_listbox,})	

		self.frame_button({'frame':'flist0', 'button_name':'读取选中数据', 'button_width':50,
			'func':self.get_listbox,})		

		self.frame_listbox({'frame':'flist1', 'name': 'listbox_x', 'label_name': 'x', 'width':20, 'height':20,
			'selectmode':tk.BROWSE,})

		self.frame_listbox({'frame':'flist2', 'name': 'listbox_y', 'label_name': 'y', 'width':20, 'height':20,
			})

		self.frames['flist0'].pack(side=tk.TOP)
		self.frames['flist1'].pack(side=tk.LEFT)
		self.frames['flist2'].pack(side=tk.LEFT)

		for obj in self.frames['flist0'].winfo_children():
			obj.pack(side=tk.TOP)

		self.frame_figure({
			'frame':'figure_1', 'name':'figure_1', 'figsize':[16/2, 9/2], 'figdpi':100,
			})

		self.frames['figure_1'].pack(side=tk.RIGHT)

		# 鼠标右键交互
		self.window.bind("<Button-3>", self.button_3_callback)

	def button_3_callback(self, event):
		# 鼠标右键
		try:
			self.get_listbox()
		except:
			self.figure_clf()

	def set_listbox(self):

		self.listbox_set('listbox_x', ['None']+list(self.data_obj.data.keys()))
		self.listbox_set('listbox_y', self.data_obj.data.keys())

		return None

	def get_listbox(self):

		x_value_keys = self.listbox_get_select('listbox_x')
		y_value_keys = self.listbox_get_select('listbox_y')

		if not x_value_keys or x_value_keys[0]=='None':
			x_values = list(range(len(self.data_obj.data[y_value_keys[0]])))
			xlabel = 'None'
		else:
			x_values = self.data_obj.data[x_value_keys[0]]
			xlabel = x_value_keys[0]

		y_values = []
		for key in y_value_keys:
			y_values.append(self.data_obj.data[key])

		ylabel = list(y_value_keys)
		splines = tkfig.Splines(x_values, y_values, xlabels=xlabel)
		splines.legend = ylabel
		self.figure_plot('figure_1', splines)

if __name__=='__main__':

	import numpy as np

	t = np.array(range(1000))
	data = {
		'a--1': t,
		'b--2': np.sin(t/10),
		'c--3': np.sin(t/10) * 2,
		'd--4': np.sin(t/10) * t,
		}
	data_obj = TkFigureShowData(data)

	TkFigureShow('TkFigureShow', data_obj).run()