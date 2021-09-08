'''
	python version : 3.7
	Adams version : 2017.2
	
	与adams建立TCP/IP 通信
	运行命令

	adams_tcplink.cmd_send(cmds,type_in)  发送数据到adams ，type_in共分两种 cmd 和 query
	输出为bytes类型
	AdamsTcp.cmd_convert(cmds)   将多行cmd单个命令合并成一行

	2020/5/19
'''

import socket
import re
import sys
import time
import glob


# 连接设置
PORT=5002
LOCALHOST='127.0.0.1'


def cmd_send(cmds,type_in='cmd'): # cmd 数据传送
	'''
	type_in : query or cmd
	query 获取参数
	cmd 发送cmd命令
	'''
	if type('')==type(cmds):
		if '&' in cmds:
			cmds=cmd_convert(cmds)

	if type([])==type(cmds):
		cmd=[]
		for line in cmds:
			cmd.append(bytes('{} {}'.format(type_in,line),encoding='utf8'))
	elif type('')==type(cmds):
		cmd=[bytes('{} {}'.format(type_in,cmds),encoding='utf8')]
	for line in cmd:
		socket_obj=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		n=1
		while n==1:
			try:
				socket_obj.connect((LOCALHOST,PORT))
				break
			except socket.error:
				time.sleep(1)
		socket_obj.send(line)
		print(line)
	if type_in=='query':
		socket_obj.recv(1024)
		socket_obj.send(b"OK")
	return socket_obj.recv(1024)


def cmd_convert(cmd_str): # cmd数据转化
	'''
		file_path is cmd file
		单个命令成一行
	'''
	return re.sub(r'&(\s*)\n',' ',cmd_str).split('\n')


def cmd_to_lines(cmd_str): # 多个cmd命令转化,导出cmd列表
	'''
		去掉cmd中的& 符号
		将命令转化为多个单行命令
	'''
	list1 = cmd_str.split('\n')
	line = []
	list2 = []
	cmds = []
	for n in list1:
		if n:
			if '&' in n:
				line.append(n)
			else:
				line.append(n)
				list2.append(' '.join(line))
				line = []
		else:
			pass
			line = []

	for line in list2:
		cmds.append(line.replace('&',' '))
	
	return cmds


def cmds_run(cmd_str): # 直接运行,未处理的多个命令行
	'''
		多行运行
	'''
	# 命令转化
	cmds = cmd_to_lines(cmd_str)
	for line in cmds:
		# 运行命令
		cmd_send(cmds=line, type_in='cmd')

	return 'cmds_run end'



if __name__ == '__main__':
	'''
		测试
	'''
	# print(cmd_send(cmds='eval(cdb_get_write_default())',type_in='query').decode())
	# print('adams_tcplink')
	
	# 数据转化测试
	print(cmd_convert('asdfsa&\n asdf \n'))

	
	# file_path=r'E:\ADAMS\temp.cmd'
	# cmd_send(cmds=cmd_convert(file_path),type_in='cmd')
