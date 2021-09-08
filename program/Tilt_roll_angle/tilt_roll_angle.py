'''
	侧翻角计算
'''

import tkinter as tk

# 主界面
window = tk.Tk()
window.title('侧翻角计算程序')
# window.geometry('200x100')

# 变量--------------------------------
var_w = tk.StringVar()
var_w.set('')
var_hr = tk.StringVar()
var_hr.set('')
var_h = tk.StringVar()
var_h.set('')
var_result = tk.StringVar()
var_result.set('侧倾角:')

# 子函数--------------------------------
def set_scale_zero():
	s_w.set(1)
	s_hr.set(1)
	s_h.set(1)
	s_w.set(0)
	s_hr.set(0)
	s_h.set(0)
	pass

def scale_w(v):
	var_w.set(str(float(e_w.get())+float(v)))
	button_cal()

def scale_hr(v): 
	var_hr.set(str(float(e_hr.get())+float(v)))
	button_cal()

def scale_h(v): 
	var_h.set(str(float(e_h.get())+float(v)))
	button_cal()

def button_cal():
	# 计算

	var_w.set(str(float(e_w.get())+float(s_w.get())))
	var_hr.set(str(float(e_hr.get())+float(s_hr.get())))
	var_h.set(str(float(e_h.get())+float(s_h.get())))

	w = float(var_w.get())
	hr = float(var_hr.get())
	h = float(var_h.get())

	roll_angle = roll_limit(w, hr, h)

	

	var_result.set(f'侧倾角: {roll_angle} deg')

def roll_limit(w,hr,h):
	# 侧倾极限计算
	pass
	return '暂未完成'
		

# 模块--------------------------------
# 轮距
frm_w = tk.Frame(window)
frm_w.pack()
l_w = tk.Label(frm_w, width=15,text='轮距 mm')
l_w.pack(side='left')
e_w = tk.Entry(frm_w, width=20,show=None)
e_w.pack(side='left')
s_w = tk.Scale(frm_w, from_=-200, to=200, orient=tk.HORIZONTAL,
	length=200, showvalue=0, resolution=1, command=scale_w)
s_w.pack(side='left')
l_w2 = tk.Label(frm_w, width=15,textvariable=var_w)
l_w2.pack(side='left')

# 侧倾中心高
frm_hr = tk.Frame(window)
frm_hr.pack()
l_hr = tk.Label(frm_hr,width=15,text='侧倾中心高 mm')
l_hr.pack(side='left')
e_hr = tk.Entry(frm_hr, width=20,show=None)
e_hr.pack(side='left')
s_hr = tk.Scale(frm_hr, from_=-200, to=200, orient=tk.HORIZONTAL,
	length=200, showvalue=0, resolution=1, command=scale_hr)
s_hr.pack(side='left')
l_hr2 = tk.Label(frm_hr, width=15,textvariable=var_hr)
l_hr2.pack(side='left')

# 质心高
frm_h = tk.Frame(window)
frm_h.pack()
l_h = tk.Label(frm_h,width=15,text='质心高 mm')
l_h.pack(side='left')
e_h = tk.Entry(frm_h, width=20,show=None)
e_h.pack(side='left')
s_h = tk.Scale(frm_h, from_=-200, to=200, orient=tk.HORIZONTAL,
	length=200, showvalue=0, resolution=1, command=scale_h)
s_h.pack(side='left')
l_h2 = tk.Label(frm_h, width=15,textvariable=var_h)
l_h2.pack(side='left')

# 计算按钮
frm_cal = tk.Frame(window)
frm_cal.pack()

b_cal = tk.Button(frm_cal,text='计算',width=15,command=button_cal)
b_cal.pack(side='left')
b_zero = tk.Button(frm_cal,text='置0',width=15,command=set_scale_zero)
b_zero.pack()

l_result = tk.Label(window, width=20,textvariable=var_result)
l_result.pack()


# 运行 --------------------------------
window.mainloop()
