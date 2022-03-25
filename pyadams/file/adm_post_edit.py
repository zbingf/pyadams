"""
	ADAMS / adm 文件
	类型:
		adams/car ride 模块-四立柱台架加载
	version:
		2017.2

"""

import re
import logging

import os.path
PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
logger = logging.getLogger(PY_FILE_NAME)


# 四立柱台架, 删除车身约束
def body_constraint_del(adm_lines): 
	"""
		adm_path 		str 	目标adm路径
		new_adm_path 	str 	新生成adm路径, None则默认为adm_path
		ride 四立柱模型修改
		删除: testrig.josinl_body_stake / testrig.josper_yaw_stake
		目标删除数据如下:
		!                  adams_view_name='testrig.josinl_body_stake'
		JPRIM/6
		, INLINE
		, I = 1000
		, J = 42
		!
		!                   adams_view_name='testrig.josper_yaw_stake'
		JPRIM/7
		, PERPENDICULAR
		, I = 1001
		, J = 43
		!
	"""

	isDel = False
	new_adm_lines = []
	for line in adm_lines:
		newline = re.sub(r'\s', '', line).lower()

		if 'testrig.josinl_body_stake' in newline or \
			'testrig.josper_yaw_stake' in newline:
			isDel = True

		if isDel and '!'==newline[0] and 'testrig' not in newline:
			isDel = False
			logger.info('del: '+ newline)
			# print(newline)
			continue

		if isDel:
			logger.info('del: '+ newline)
			# print(newline)
			continue

		new_adm_lines.append(line)

	return new_adm_lines


# 编辑DIFF
def post_static_pad_load(adm_lines):

	isReplace = False
	n_loc = 0
	new_adm_lines = []
	for line in adm_lines:
		# print(line)
		temp_obj = re.search('testrig.\S\S_static_pad_load', line)
		if temp_obj:
			isReplace = True
			n_loc = 0

		if isReplace and n_loc < 4:
			new_line = re.sub('\s','',line).lower()
			if 'function=' in new_line:
				# print(new_line)	
				line = ', FUNCTION = 0\n'
				logger.info('edit: '+ new_line + ' →→ ' + line[:-1])

		new_adm_lines.append(line)
		n_loc += 1

	return new_adm_lines


# 四立柱台架, adm编辑
def adm_car_post_edit(adm_path, new_adm_path=None): 
	"""
		adm_path 		str 	目标adm路径
		new_adm_path 	str 	新生成adm路径, None则默认为adm_path
	"""
	with open(adm_path,'r') as f:
		adm_lines = f.readlines()

	# 车身约束删除
	adm_lines = body_constraint_del(adm_lines)
	# 
	adm_lines = post_static_pad_load(adm_lines)

	if new_adm_path==None:
		new_adm_path = adm_path

	with open(new_adm_path,'w') as f:
		f.write(''.join(adm_lines))

	return new_adm_path


if __name__ == '__main__':

	adm_path = r'..\tests\adm_post_edit\for_loadcal_front_swept0p8Hz_fourpost.adm'
	logging.basicConfig(level=logging.INFO)
	adm_car_post_edit(adm_path,adm_path+'_temp')
