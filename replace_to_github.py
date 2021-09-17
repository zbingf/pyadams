'''
	将代码复制到github文件路径
'''

import os
import shutil
import pysnooper

# @pysnooper.snoop()
def dir_remove(path):
	try:
		shutil.rmtree(path)
		print(f'删除 {path}')
	except:
		pass

# @pysnooper.snoop()
def dir_copy(path1,path2):
	try:
		shutil.copytree(path1, path2)
		print(f'复制 {path2}')
	except:
		pass

target_dir = r'D:\github\pyadams'

pyadams_path = os.path.join(target_dir, 'pyadams')
codes_path = os.path.join(target_dir, 'codes')
dir_remove(pyadams_path)
dir_remove(codes_path)
dir_copy(r'.\pyadams', pyadams_path)
dir_copy(r'.\codes', codes_path)
dir_remove(os.path.join(pyadams_path, 'tests'))
dir_remove(os.path.join(pyadams_path, '__pycache__'))



