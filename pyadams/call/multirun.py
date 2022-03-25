'''
	python version : 3.7
	Adams version : 2017.2
	多进程计算
	调用 multiprocessing

	2020/09
'''
import multiprocessing
import os
import time

from pyadams.call import cmd_link


class TimeCal: # 计时用
	''' 计时 '''
	def __init__(self):
		self.start_time=time.time()
		self.time_list=[]
		self.results=[]

	def run_time(self): # 总运行时间
		''' 从创建实例到当前运行的时间 '''
		temp1 = time.time() - self.start_time
		self.time_list.append(temp1)
		return temp1

	def last_time(self): # 最近运行时间间隔
		''' 最近运行时间间隔 '''
		self.run_time()
		if len(self.time_list)==1:
			return self.time_list[0]
		else:
			return self.time_list[-1]-self.time_list[-2]

class MyProcess: # 多进程运行
	''' 
		多进程运行 
		调用multiprocessing
	'''
	def __init__(self):
		# 各进程
		self.sub_process=multiprocessing.Process
		self.process_list=[]
		self.time_obj=TimeCal()
		self.queue_obj=multiprocessing.Queue()

	# def process_fun(self,func): # 测试
	# 	'''目标运行函数 装饰'''
	# 	def new_fun(fullargs):
	# 		queue_obj=fullargs[0]
	# 		print(queue_obj)
	# 		results=func(**fullargs[1])
	# 		queue_obj.put(results)
	# 		print("newfunc")
	# 	return new_fun

	def process_run(self,target,args=None): # 运行指定进程
		'''
			运行指定进程
			target 目标运行函数
			args 目标函数的参数
		'''
		p=self.sub_process(target=target,args=args)
		p.start()
		self.process_list.append(p)

	def waiting_all_process(self,t=None): # 等待所有进程运行完毕
		''' 
			等待所有进程运行完毕 t设置超时中断 
		'''
		while True:
			time.sleep(0.2)
			is_alive_list=[]
			for p in self.process_list:
				is_alive_list.append(p.is_alive())
			# if sum(is_alive_list)==0:
			if self.current_running_num() == 0:
				return True,"full success"
			if t!=None and type(t)!=str:
				if self.timeObj.run_time()>t:
					self.terminate_all_process()
					return False,"over time"
			elif t!=None:
				return False,"error t"
			# print('计算中')
			# print(self.process_list)
			# print(is_alive_list)

	def terminate_all_process(self): # 终止所有进程
		''' 
			终止所有进程 
		'''
		for p in self.process_list:
			p.terminate()
		for p in self.process_list:
			p.join()

	def queue_get(self): # 获取进程输出
		'''
			获取进程的输出
		'''
		self.results=[self.queue_obj.get() for n in self.process_list]
		return self.results

	def current_running_num(self): # 当前运行的进程数
		'''
			获取当前运行中的进程个数
		'''
		is_alive_list=[p.is_alive() for p in self.process_list]
		return sum(is_alive_list)

	def set_limit_running(self,limit_n): # 设置运行上限
		'''
			limit_n 同时运行个数
			每次创建新进程时 均需调用一次
		'''
		while True:
			num=self.current_running_num()
			if num<limit_n:
				break
			time.sleep(1)
			# print(str(num)+'进行中121212')

def __do_this(queue_obj,what,n): # 测试用
	'''仅用于测试'''
	# what=args[0]
	# n=args[1]
	print(f"process {os.getpid()} say:{what}")
	for n1 in range(n*2+1):
		time.sleep(1)
		print(f"{what} : {n1}")

	queue_obj.put(f"{what} : {n1}")



def multi_cmd_run(cmds,cmdset=None,run_path=None,limit_n=4):
	'''
		多进程调用cmd命令
	'''
	if run_path!=None:
		os.chdir(run_path)
	pobj = MyProcess()
	n = 0
	for cmd in cmds:
		n += 1
		simpath = 'sim_{}'.format(n)
		if not os.path.exists(simpath):
			os.mkdir(simpath)
		os.chdir(simpath)
		if cmdset==None:
			pobj.process_run(target=cmd_link.cmd_send,args=(cmd,))
		else:
			pobj.process_run(target=cmd_link.cmd_send,args=(cmd,cmdset['cmd_path'],
				cmdset['mode'],cmdset['savefile'],cmdset['res_path'],cmdset['minutes'],))
		os.chdir('..')
		pobj.set_limit_running(limit_n)
		
	pobj.waiting_all_process()
	# os.rmdir('sim_{}'.format(n))
	# res = pobj.queue_get()
	# print(res)


if __name__=="__main__":

	# 测试
	# pobj = MyProcess()
	# for n in range(4):
	# 	pobj.process_run(target=__do_this,args=(pobj.queue_obj,f"function {n}",n))
	# 	pobj.set_limit_running(4)		
	# pobj.waiting_all_process()
	# res = pobj.queue_get()
	# print(res)

	cmds = [r'file bin read alert=no file="D:\document\FEMFAT_LAB\mast\six_dof_rig_stewart.bin"']*4
	cmdset = {'cmd_path':None,
	'mode':'car',
	'savefile':False,
	'res_path':None,
	'minutes':10}
	multi_cmd_run(cmds,cmdset,r'D:\document\ADAMS')
	print("main end")

