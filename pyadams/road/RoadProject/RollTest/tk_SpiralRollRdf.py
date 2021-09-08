

import tkui
import SpiralRollRdf

# UI模块
class TkSpiralRollRdf(tkui.TkUi):
	"""
		AdmSim 主程序
	"""
	def __init__(self,title):
		super().__init__(title)
		str_label = '-'*40


		self.frame_label_only({'label_text':'第一段配置','label_width':50})
		self.frame_entry({
			'frame':'L_1','var_name':'L_1','label_text':'第一段长度 mm',
			'label_width':15,'entry_width':30,
			})

		self.frame_entry({
			'frame':'deg_1','var_name':'deg_1','label_text':'第一段角度 deg',
			'label_width':15,'entry_width':30,
			})

		self.frame_label_only({'label_text':'第二段配置','label_width':50})

		self.frame_entry({
			'frame':'L_2','var_name':'L_2','label_text':'第二段长度 mm',
			'label_width':15,'entry_width':30,
			})

		self.frame_entry({
			'frame':'deg_2','var_name':'deg_2','label_text':'第二段角度 deg',
			'label_width':15,'entry_width':30,
			})

		self.frame_label_only({'label_text':'路面配置','label_width':50})

		self.frame_entry({
			'frame':'width', 'var_name':'width', 'label_text':'路面宽度 mm',
			'label_width':15, 'entry_width':30,
			})

		self.frame_entry({
			'frame':'x_end', 'var_name':'x_end', 'label_text':'路面总长度 mm',
			'label_width':15, 'entry_width':30,
			})

		self.frame_savepath({
			'frame' : 'rdf_path', 'var_name':'rdf_path', 'path_name' : 'rdf file',
			'path_type' : '.rdf', 'button_name' : '路面文件保存路径',
			'button_width' : 15, 'entry_width' : 30,
			})

		self.frame_radiobuttons({
			'frame':'isLeft',
			'var_name':'isLeft',
			'texts':['左侧起跳', '右侧起跳'],
			})

		self.frame_buttons_RWR({
			'frame' : 'rrw',
			'button_run_name' : '运行',
			'button_write_name' : '保存',
			'button_read_name' : '读取',
			'button_width' : 15,
			'func_run' : self.fun_run,
			})

		self.frame_note()

		# 初始化设置
		self.vars['L_1'].set(500)
		self.vars['L_2'].set(3000)
		self.vars['deg_1'].set(8)
		self.vars['deg_2'].set(20)
		self.vars['width'].set(10000)
		self.vars['x_end'].set(100000)


	def fun_run(self):
		"""
			运行按钮调用函数
			主程序
		"""
		# 获取界面数据
		params = self.get_vars_and_texts()

		isLeft = True if params['isLeft'] == 1 else False

		SpiralRollRdf.SpiralRollRdf(params['rdf_path'], params['L_1'], 
			params['L_2'], params['deg_1'], params['deg_2'],
			params['width'], params['x_end'], isLeft)


		self.print('计算完成')

		return True

if __name__ == '__main__':
	pass
	# Ui测试
	obj = TkSpiralRollRdf('螺旋翻滚路面-RDF文件生成').run()
