

import tkui
import SlopeRollRdf

# UI模块
class TkSlopeRollRdf(tkui.TkUi):
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

		self.frame_label_only({'label_text':'第三段配置','label_width':50})

		self.frame_entry({
			'frame':'L_3','var_name':'L_3','label_text':'第三段长度 mm',
			'label_width':15,'entry_width':30,
			})

		self.frame_entry({
			'frame':'deg_3','var_name':'deg_3','label_text':'第三段角度 deg',
			'label_width':15,'entry_width':30,
			})


		self.frame_label_only({'label_text':'路面配置','label_width':50})

		self.frame_entry({
			'frame':'length', 'var_name':'length', 'label_text':'路面总长度 mm',
			'label_width':15, 'entry_width':30,
			})

		self.frame_entry({
			'frame':'angle', 'var_name':'angle', 'label_text':'车身切入角 deg',
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
			'texts':['左侧切入', '右侧切入'],
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
		self.vars['L_1'].set(3000)
		self.vars['L_2'].set(3000)
		self.vars['L_3'].set(10000)
		self.vars['deg_1'].set(25.2)
		self.vars['deg_2'].set(35)
		self.vars['deg_3'].set(55)

		self.vars['angle'].set(12)
		self.vars['length'].set(200000)


	def fun_run(self):
		"""
			运行按钮调用函数
			主程序
		"""
		# 获取界面数据
		params = self.get_vars_and_texts()
		isLeft = True if params['isLeft'] == 1 else False

		# rdf_path = r'D:\document\ADAMS\test_road_rdf.rdf'
		# # 第一段长度
		# L_1 = 3000
		# # 第一段 角度 deg
		# deg_1 = 25.2
		# # 第二段长度
		# L_2 = 3000
		# # 第二段 角度 deg
		# deg_2 = 55
		# # 第二段长度
		# L_3 = 10000
		# # 第二段 角度 deg
		# deg_3 = 55
		# # 路面宽度
		# length = 200000
		# angle = 12

		SlopeRollRdf.SlopeRollRdf(params['rdf_path'], params['length'], 
			params['angle'], 
			params['L_1'], params['L_2'], params['L_3'], 
			params['deg_1'], params['deg_2'], params['deg_3'], 
			isLeft)

		self.print('计算完成')

		return True

if __name__ == '__main__':
	pass
	# Ui测试
	obj = TkSlopeRollRdf('边坡翻滚路面-RDF文件生成').run()
