

# import matplotlib.pyplot as plt


# #  中文设置
# plt.rcParams['font.family']=['sans-serif']
# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus']=False

# #
# plt.xlim((-1,2))
# plt.ylim((-2,3))
# plt.xlabel('x')
# plt.ylabel('y')

# plt.xticks([-10,1,2,3,4])
# plt.yticks([-2,-1,0,1.1,5.5],['a','b','测试','d',r'$really\ good$'])
# plt.show()



# import matplotlib.pyplot as plt
# import numpy

# def f(t):
#     'A damped exponential'
#     s1 = numpy.cos(2*numpy.pi*t)
#     e1 = numpy.exp(-t)
#     return s1*e1

# t1 = numpy.arange(0.0,5.0,0.2)
# l = plt.plot(t1,f(t1),'ro')  # x,y  '颜色、形状'
# plt.setp(l,markersize=30)
# plt.setp(l,markerfacecolor='C0')
# plt.show()



# import numpy as np
# import matplotlib.pyplot as plt


# x1 = np.linspace(0.0, 5.0)
# x2 = np.linspace(0.0, 2.0)

# y1 = np.cos(2 * np.pi * x1) * np.exp(-x1)
# y2 = np.cos(2 * np.pi * x2)

# plt.subplot(2, 1, 1)
# plt.plot(x1, y1, 'o-')
# plt.title('A tale of 2 subplots')
# plt.ylabel('Damped oscillation')

# plt.subplot(2, 1, 2)
# plt.plot(x2, y2, '.-')
# plt.xlabel('time (s)')
# plt.ylabel('Undamped')

# plt.show()


# import matplotlib # 注意这个也要import一次
# import matplotlib.pyplot as plt
# from IPython.core.pylabtools import figsize # import figsize
# #figsize(12.5, 4) # 设置 figsize
# plt.rcParams['savefig.dpi'] = 300 #图片像素
# plt.rcParams['figure.dpi'] = 300 #分辨率
# # 默认的像素：[6.0,4.0]，分辨率为100，图片尺寸为 600&400
# # 指定dpi=200，图片尺寸为 1200*800
# # 指定dpi=300，图片尺寸为 1800*1200
# # 设置figsize可以在不改变分辨率情况下改变比例




import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['savefig.dpi'] = 500 #图片像素
plt.rcParams['figure.dpi'] = 500 #分辨率

fig = plt.figure()
ax1 = fig.add_subplot(2,2,1)
ax2 = fig.add_subplot(2,2,2)
ax3 = fig.add_subplot(2,2,3)
ax4 = fig.add_subplot(2,2,4)

ax1.plot(np.random.randn(50).cumsum(),'k')
# 柱状图
ax2.hist(np.random.randn(100),bins=20,color='k',alpha=0.3)
# 散点图
ax3.scatter(np.arange(30),np.arange(30)+3*np.random.randn(30))

plt.plot(np.random.randn(50).cumsum(),'k--')

plt.savefig(r'D:\temp_delete\test.png')

# plt.show()


