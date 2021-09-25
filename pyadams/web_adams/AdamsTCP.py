# 2019/5/19
# AdamsTcp  与adams建立TCP/IP 通信
# AdamsTcp.cmdSend(cmds,typeIn)  发送数据到adams ，typeIn共分两种 cmd 和 query
# 输出为bytes类型
# AdamsTcp.cmdConvert(cmds)   将多行cmd单个命令合并成一行
# 


import socket,re,sys,time,glob
PORT=5002
localhost='127.0.0.1'
def cmdSend(cmds,typeIn='cmd'):
	'''
	typeIn : query or cmd
	'''
	if type('')==type(cmds):
		if '&' in cmds:
			cmds=cmdConvert(cmds)

	if type([])==type(cmds):
		cmd=[]
		for line in cmds:
			cmd.append(bytes('{} {}'.format(typeIn,line),encoding='utf8'))
	elif type('')==type(cmds):
		cmd=[bytes('{} {}'.format(typeIn,cmds),encoding='utf8')]
	for line in cmd:
		socketObj=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		n=1
		while n==1:
			try:
				socketObj.connect((localhost,PORT))
				break
			except socket.error:
				time.sleep(1)
		socketObj.send(line)
		print(line)
	if typeIn=='query':
		socketObj.recv(1024)
		socketObj.send(b"OK")
	return socketObj.recv(1024)

def cmdConvert(dataStr):
	'''
	fileAdr is cmd file
	'''
	dataCmd=re.sub(r'&(\s*)\n',' ',dataStr)
	dataCmd=dataCmd.split('\n')
	return dataCmd


# fileAdr=r'E:\ADAMS\temp.cmd'
# cmdSend(cmds=cmdConvert(fileAdr),typeIn='cmd')



# cfgPath=AdamsFile.cfgPathSearch()
# print(cfgPath)

# print('END')