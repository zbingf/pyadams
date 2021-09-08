# 多元线性回归预测
# 调用：
# 	sklearn
# 	pyadams.ui.tkui

from pyadams.ui import tkui

# 初始设置
# TkUi = tkui.TkUi 							# TkUi 对象
VarSearchUi = tkui.VarSearchUi 				# 多变量修改 UI


import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)



# 多元线性回归GUI模块
def linear_regression_ui(x_init, xs, ys, y_names=None, y_repeats=None): # 多元线性回归GUI
	"""
		多元线性回归
		调用 VarSearchUi GUI
		x_inint list 一维 初始x值输入 
		xs 		list 二维 多组x数据 
		ys 		list 二维 多组y数据
	"""
	# 多元线性回归
	from sklearn.linear_model import LinearRegression

	# 多目标y ,叠加
	line_regs = []
	for n in range(len(ys[0])):
		ytemp = [ line[n] for line in ys]
		lin_regn = LinearRegression() # 多元线性回归
		lin_regn.fit(xs,ytemp)
		line_regs.append(lin_regn)
	# @pysnooper.snoop()
	def fun_cal(fitobjs,values): # 数值预测，代入 VarSearchUi中
		"""
			fitobjs list 线性回归实例组, 每个的输入为values输出对应的y
			values list  x数值
		"""
		# 
		list2str_n = lambda list1,nlen : ','.join([str(n).ljust(nlen) for n in list1])
		list2str_10 = lambda list1: ','.join([str(n).ljust(10) for n in list1])
		y = [ round(obj.predict([values])[0],3) for obj in fitobjs ]

		output_strs = []
		if y_names != None :
			# title = list2str_n(y_names, max_len) + '\n'
			max_len = len( max(y_names, key=lambda x:len(x)) ) + 1
			isTitle = True
		else :
			# title = '\n'
			max_len = 0
			isTitle = False
		
		if y_repeats != None and isinstance(y_repeats,list):
			max_repeat = len(max(y_repeats, key=lambda x:len(x))) + 1
			new_max_len = max_len + max_repeat
			rlen = len(y_repeats)
			n_rows = int(len(y)/rlen)
			for num,r in enumerate(y_repeats):
				if isTitle:
					title = list2str_n( [r+':'+name for name in y_names], new_max_len) + '\n'
				else:
					title = r + '\n'
				output_strs.append(title)
				# print(y[num*n_rows:(num+1)*n_rows])
				# print(list2str_n( y[num*n_rows:(num+1)*n_rows] , new_max_len))
				output_strs.append(	list2str_n( y[num*n_rows:(num+1)*n_rows] , new_max_len) + '\n' ) 
		elif isinstance(y_repeats,str):
			output_strs.append( y_repeats + '\n' )
			output_strs.append( list2str_n( y, 10) )
		else:
			output_strs.append( list2str_n( y, 10) )

		return ''.join(output_strs)

	# GUI调用
	VarSearchUi(title='灵敏度分析', n_var=len(x_init), values=x_init,
		fun_cal=fun_cal, var_cal=line_regs).run()

if __name__ == '__main__':
	# pass
	logging.basicConfig(level=logging.INFO)
	logger.info('start')
	linear_regression_ui([1,1,1,1], [[1,1,1,0],[1,1,0,1]], 
		[[0.5,0.5,0.5,0.5],[1,1,1,1]], y_names=None, y_repeats=None)