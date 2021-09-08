'''
	RPC3 数据读取及对比
	

'''

import tkinter as tk
import tkinter.filedialog
import rpc_read

# def run():

# 主界面
window = tk.Tk()
window.title('迭代数据-RPC文件-读取')
# window.geometry('200x100')

# 变量--------------------------------
var_rpcpath = tk.StringVar()
var_rpcpath.set('')
var_i = tk.StringVar()
var_i.set('')

var_result = tk.StringVar()
var_result.set('导入rpc文件,设定迭代次数')

# 子函数--------------------------------
def button_rpcpath():
	# 读取rsp文件路径
	rpc_path = tkinter.filedialog.askopenfilename( filetypes =  (("RPC3 file", ".rsp"),) ) #(filetypes=( ("Text file", "*.txt*"),("HTML files", "*.html;*.htm")))
	var_rpcpath.set(rpc_path)
	# print(help(tkinter.filedialog.askopenfilename))

def button_cal():
	# 计算
	rpcpath = var_rpcpath.get()
	try:
		i = int(var_i.get())
	except:
		i = None
	print(rpcpath)
	print(i)
	if i == None:
		rpc_read.cal_rpcs_compare(rpcpath)
	else:
		rpc_read.cal_rpcs_compare(rpcpath,i)

	var_result.set('计算结束')
	window.quit()

# 模块--------------------------------
# rpcpath
frm_rpcpath = tk.Frame(window)
frm_rpcpath.pack()
# l_rpcpath = tk.Label(frm_rpcpath, width=15,text='RPC文件路径')
# l_rpcpath.pack(side='left')
b_rpcpath = tk.Button(frm_rpcpath,text='RPC文件路径',width=15,command=button_rpcpath)
b_rpcpath.pack(side='left')
e_rpcpath = tk.Entry(frm_rpcpath, width=30,show=None ,textvariable=var_rpcpath)
e_rpcpath.pack(side='left')

# 迭代次数
frm_iter = tk.Frame(window)
frm_iter.pack()
l_iter = tk.Label(frm_iter,width=15,text='迭代次数')
l_iter.pack(side='left')
e_i = tk.Entry(frm_iter, width=30,show=None,textvariable=var_i)
e_i.pack(side='left')


# 计算按钮
frm_cal = tk.Frame(window)
frm_cal.pack()
b_cal = tk.Button(frm_cal,text='计算',width=15,command=button_cal)
b_cal.pack(side='left')

l_result = tk.Label(window, width=20,textvariable=var_result)
l_result.pack()


# 运行 --------------------------------
window.mainloop()

