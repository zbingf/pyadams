"""
	未完成

	读取res文件，获取频率数据

	get_res_samplerate
	
"""

from pyadams.ui import tkui
from pyadams.file import result
DataModel = result.DataModel

import logging
import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)


class ResSamplerateUi(tkui.TkUi):
	def __init__(self, title, frame=None):
		super().__init__(title, frame=frame)

		self.frame_loadpaths({
			'frame':'res_files', 'var_name':'res_files', 'path_name':'res files',
			'path_type':'.res', 'button_name':'res files',
			'button_width':15, 'entry_width':40,
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

		self.frame_text_lines({
			'frame':'strs',
			'text_name':'strs',
			'text_width':80, 'text_height':25,
			})

	def fun_run(self):

		params = self.get_vars_and_texts()

		if isinstance(params['res_files'], str): params['res_files'] = [params['res_files']]

		dataobj = DataModel('tk_res_samplerate')


		strs = []
		for path in params['res_files']:
			dataobj.new_file(path, path)
			samplerate_mean = dataobj[path].get_samplerate()
			# samplerate_mean = result.get_res_samplerate(path, nlen=20, loc_start=4)
			# samplerate_mean = round(samplerate_mean, 2)
			name = os.path.basename(path)
			strs.append(f'{name} : {samplerate_mean} Hz')

		self.set_text('strs', '\n'.join(strs))

		self.print('计算完成')


if __name__=='__main__':
	
	ResSamplerateUi('Res采样频率查看').run()

