
from pyadams.ui import tkui

# import matplotlib
# matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
import numpy as np


class Spline:
	def __init__(self, xs_1d, ys_1d, title=None, xlabel=None, ylabel=None):
		self.title = title
		self.xlabel = xlabel
		self.ylabel = ylabel
		self.xs = xs_1d
		self.ys = ys_1d

	def plot(self, axes):

		line = axes.plot(self.xs, self.ys)
		axes.set_title(self.title)
		axes.set_xlabel(self.xlabel)
		axes.set_ylabel(self.ylabel)

		return line

class Splines:

	def __init__(self, xs_2d, ys_2d, titles=None, xlabels=None, ylabels=None):

		self.splines = []
		self.legend  = None

		if np.array(ys_2d).ndim == 1: ys_2d=[ys_2d]

		if titles==None or isinstance(titles, str): titles = [titles]*len(ys_2d)
		if xlabels==None or isinstance(xlabels, str): xlabels = [xlabels]*len(ys_2d)
		if ylabels==None or isinstance(ylabels, str): ylabels = [ylabels]*len(ys_2d)
		if len(xs_2d) != len(ys_2d): xs_2d = [xs_2d]*len(ys_2d)

		for xs_1d, ys_1d, title, xlabel, ylabel in zip(xs_2d, ys_2d, titles, xlabels, ylabels):
			self.splines.append(Spline(xs_1d, ys_1d, title, xlabel, ylabel))

	def plot(self, axes):

		self.lines = []
		for spline in self.splines:
			self.lines.append(spline.plot(axes))

class TkFigure(tkui.TkUi):
	
	def __init__(self, title, frame=None):
		super().__init__(title, frame=frame)

		self.figure = {}		
		self.canvas = {}

	def frame_figure(self, params):
		# 创建图像模块

		# params = {
		# 	'frame': 'fig_test',
		# 	'name': 'fig_test',
		# 	'figsize': [5,4],
		# 	'figdpi': 100,
		# }

		frame = self.create_frame(params['frame'], expand=tk.YES, fill=tk.X)
		fig = Figure(figsize=params['figsize'], dpi=params['figdpi'])
		canvas = FigureCanvasTkAgg(fig, master=frame)
		canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

		self.figure[params['name']] = fig
		self.canvas[params['name']] = canvas

		return None

	def figure_clf(self, name=None):
		# 清空图像
		if name==None:
			for key in self.figure:
				self.figure[key].clf()
			
			for key in self.canvas:
				self.canvas[key].draw()

		else:
			self.figure[name].clf()
			self.canvas[name].draw()

		return None

	def figure_plot(self, name, splines, isClf=True):
		# 作图
		fig = self.figure[name]
		canvas = self.canvas[name]
		if isClf: fig.clf()
		axes = fig.add_subplot(111)
		splines.plot(axes)
		if splines.legend != None: fig.legend(splines.legend)
		fig.tight_layout()
		canvas.draw()

		return None


class TkFigureTest(TkFigure):
	"""docstring for TkFigureTest"""
	def __init__(self, title):
		super().__init__(title)

		params = {
			'frame': 'fig_test',
			'name': 'fig_test',
			'figsize': [5,4],
			'figdpi': 100,
		}
		self.frame_figure(params)

		x = list(range(10))
		y = list(range(10))
		splines = Splines(x, y)
		self.figure_plot(params['name'], splines)


if __name__=='__main__':
	# x = list(range(10))
	# y = list(range(10))
	# splines = Splines(x, y)

	TkFigureTest('TkFigureTest').run()