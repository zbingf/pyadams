"""
# 耐久相关计算
"""


import copy


# ==============================
# 完成
# ==============================

# 雨流计数-3点
def rainflow_3point(list1):
	"""
		雨流计数
		3点

		输出: 幅值, 平均值
	"""
	
	newlist = list_updown(list1)
	num = len(newlist)
	# print(newlist)
	# print('len(newlist)',len(newlist))
	# ---------检测数据用---------
	# plt.subplot(311)
	# plt.plot(newlist)

	# 重新拼接最大值放置最前面
	value_max = max(newlist)
	value_loc = newlist.index(value_max)
	l1 = newlist[value_loc:] + newlist[:value_loc+1]

	# 再只留波峰波谷，防止拼接出现不合理的数据
	newlist = list_updown(l1)
	# print('len(newlist)',len(newlist))

	# ---------检测数据用---------
	# plt.subplot(312)
	# plt.plot(newlist)

	# 雨流计数
	values, means, rainlist = [],[],[]
	num = len(newlist)
	count = 1
	last_num = 0
	while num > 1:
		if num >1 :
			# print(newlist)
			last_num = len(newlist) # 计算前数据长度
			for n in range(num-2):
				# 第一点到倒数第三点
				s1 = newlist[n]-newlist[n+1]
				s2 = newlist[n+2]-newlist[n+1]
				e3 = (newlist[n]+newlist[n+1])/2 # 第一段线均值

				if s1 > 0 and s2 > 0 and s1 <= s2:
					# 第一段 < 第二段高度
					values.append(s1/2) # 振幅
					means.append(e3)

					# ---------检测数据用---------
					# print(n,s1,s2)
					# if n == 0: # 首末峰值
					# 	plt.subplot(313)
					# 	plt.plot(newlist)

					del newlist[n+1] # 删除第一段
					del newlist[n]

					# ---------检测数据用---------
					# count += 1
					# if count == 7:
					# 	plt.subplot(313)
					# 	plt.plot(newlist)
					# print(n,n+1,n+2, values[-1],means[-1])
					# rainlist += [means[-1]-values[-1],means[-1]+values[-1],means[-1]-values[-1]]
					break

		num = len(newlist)
		if last_num == num : # 如果计算一轮后数据长度无变化
			# print(newlist)
			# 波峰波谷重新排列
			newlist = list_updown(newlist)
			# print(len(newlist),newlist)

		# print(num)

	# ---------检测数据用---------
	# plt.subplot(212)
	# plt.plot(rainlist)
	# plt.show()
	# print(num)
	# print(values)
	# print(len(values), len(list1))
	# print(means)
	return values,means # 应力幅，均值 # 一维数组 雨流计数

# 雨流计数子函数
def list_updown(list1):
	"""
		对载荷时间历程进行处理使它只包含峰谷峰谷交替出现
	"""
	import copy
	num = len(list1)
	l1 = list1
	l2 = copy.copy(list1)
	# l1 = [round(n,3) for n in l1]

	# 对载荷时间历程进行处理使它只包含峰谷交替出现
	for n in range(1,num-1):
		# print(l1[n])
		# print(l2[n])
		if l1[n-1] < l1[n] and l1[n] < l1[n+1]:
			# 大于上一个， 小于下一个，处于中间位置
			l2[n] = ''
		elif l1[n-1] > l1[n] and l1[n] > l1[n+1]:
			# 小于上一个，大于下一个，处于中间位置
			l2[n] = ''
		elif l1[n-1] == l1[n]:
			# 和上一个一样
			l2[n] = ''

	if l2[-2] == l2[-1]:
		l2[-2] = ''

	newlist = [n for n in l2 if n]
	num = len(newlist)
	# print(newlist)
	return newlist

# goodman修正
def cal_goodman(values, means, sigma_b):
	"""
		古德曼修正
		goodman
		values 应力幅值
		mean 应力均值
		sigma_b 强度极限
	"""
	return [(a*sigma_b)/(sigma_b-abs(m)) for a,m in zip(values,means) ]

# ==============================
# 未-完成
# ==============================


def fun_4point(list1):
	num = len(list1)
	s = 0
	for n in range(num-4):
		s1 = abs(list1[n+1]-list1[n+2])
		s0 = abs(list1[n+3]-list1[n])
		if s1 <= s0:
			s = 1
			break
		else:
			s = 0
			continue
	print(s)
	return s # 未完成

def rainflow_4point(list1):
	"""
		四点循环计数法
	"""

	num = len(list1)

	import copy
	l1 = list1
	l2 = copy.copy(list1)
	# 对载荷时间历程进行处理使它只包含峰谷交替出现
	for n in range(1,num-1):
		# print(l1[n])
		# print(l2[n])
		if l1[n-1] < l1[n] and l1[n] < l1[n+1]:
			l2[n] = ''
		elif l1[n-1] > l1[n] and l1[n] > l1[n+1]:
			l2[n] = ''
	newlist = [n for n in l2 if n]
	num = len(newlist)
	print(newlist)
	# 步骤二
	# while fun_4point(newlist) == 1 or :
	# 	pass
	if fun_4point(list1) == 1:
		print('test') # 未完成




if __name__ == '__main__':
	temp = rainflow_3point([1,2,3,4,3,2,1,4,2,6,8,12,3])
	print(temp)
	print(cal_goodman(*temp,20))