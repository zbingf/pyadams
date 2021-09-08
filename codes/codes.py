"""
row         行
col         列
"""
#####################################
import pprint
# help(pprint)
a = pprint.pformat({1:1,2:2,3:3,4:4,5:5})
print(a)
pprint.pprint({1:1, 2:2, 3:3, 4:[4],})


#####################################
import os
cur_path = os.getcwd()                  # 获取当前路径  
os.chdir(cur_path)                      # 更改当前路径
# os.remove()                           # 删除文件
# os.mkdir()                            # 创建文件夹
# os.curdir()
# os.system(os.path.abspath('./code_test/test.jpg')) 		# 会阻塞程序继续运行
# os.popen(os.path.abspath('./code_test/test.jpg')) 		# 

# os.rename(r'D:\document\ADAMS\test1.txt', r'D:\document\test2.txt')


# help(os)
#####################################
import os.path
print('#'*100)
print('os.path')

print(os.path.abspath('./test'))        # 绝对路径
print(os.path.split(cur_path))          # 分离路径
print(os.path.join(cur_path, 'test'))   # 拼接路径
print(os.path.isdir(cur_path))          # 是否为文件夹
print(os.path.exists(cur_path))         # 是否存在
print(os.path.basename(cur_path))       # 文件(夹)名
print(os.path.dirname(cur_path))        # 父目录路径
print(os.path.realpath(__file__))

# help(os.path)
#####################################
import numpy as np
print('#'*100)
print('numpy')
a_arr = np.array(range(10))             # list 转 array
print(a_arr)
a_list = a_arr.tolist()                 # array 转 list
print(a_list)

# help(np)
#####################################
import re

#####################################

#####################################
import shutil
# shutil.rmtree(path) 					# 删除整个文件夹及内容
#####################################
import subprocess


#####################################
import math
# help(math)


#####################################
import time
time.sleep(0.5)
today = time.strftime('%Y%m%d', time.localtime(time.time()))
print(today)
print(time.localtime(time.time()))

print(time.strftime('%Y.%M.%d - %H:%M:%S', time.localtime(time.time())))
print('time')
# help(time.strftime)
#####################################

