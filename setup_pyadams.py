
from setuptools import setup, find_packages

setup(
	name = 'pyadams',
	version = "2.0",
	packages = find_packages(exclude=['program','old_project']),
	# package_dir = {'':'pyadams'}, 
	# include_package_data = True,
	 package_data = {
        '': ['*.*'], }
)

print(find_packages(exclude=['program','old_project']))

import os
import shutil
def dir_remove(path):
	try:
		shutil.rmtree(path)

	except:
		pass

dir_remove(r'build')
dir_remove(r'dist')
dir_remove('pyadams.egg-info')