# AdamsResCal.py
'''
	仅通过后处理 及 相关输入进行计算
	调用 AdamsFile
'''
import AdamsFile
import numpy,math
import matplotlib.pyplot as plt

# 子函数
def roundList(list1,num):
	newList=[]
	for n in list1:
		newList.append(round(n,num))
	return newList

# 后处理模块

def brakingResCal(resAdr,reqs,comps,targetAdr,simType):
	'''
		制动后处理读取
		输出图片路径及数据
		初始车速：60 or 30 km/h
	'''
	requests=['chassis_displacements','chassis_displacements','chassis_accelerations','chassis_velocities','vas_brake_demand_data','chassis_displacements']
	components=['longitudinal','pitch','longitudinal','longitudinal','value','yaw']
	requests.extend(reqs)
	components.extend(comps)
	resObj=AdamsFile.resFile(resAdr)
	resData=resObj.resResearch(requests,components)
	# 转矩阵
	resData=numpy.array(resData)

	xDis,xAngle,xAcc,xV=resData[0]/1000,resData[1]/math.pi*180,resData[2],resData[3]
	brakeDemand,yawDis=resData[4],resData[5]/math.pi*180
	yDis,zDis=resData[6],resData[7]

	# 制动起始
	n=0
	for temp in brakeDemand:
		if temp>0:
			break
		n+=1
	xDisDiff=xDis-xDis[n]
	yDisDiff=yDis-yDis[n]
	zDisDiff=zDis-zDis[n]
	xAngleDiff=xAngle-xAngle[n]
	# 纵向加速度 g
	xMaxAcc=max(abs(max(xAcc)),abs(min(xAcc)))
	# 制动距离 m
	xDisMaxDiff=max(xDisDiff)
	# 纵倾角 deg
	if numpy.mean(xAngle)>0:
		xAngleMaxDiff=abs(max(xAngleDiff))
	else:
		xAngleMaxDiff=abs(min(xAngleDiff))
	# 沉头量 mm
	if numpy.mean(zDis)>0:
		zDisMaxDiff=abs(max(zDisDiff))
	else:
		zDisMaxDiff=abs(min(zDisDiff))
	# 最大跑偏量 mm
	yDisMaxDiff=max(abs(max(yDisDiff)),abs(min(yDisDiff)))
	# 初始车速 --------------------------------------------------------------------60 及 30
	xVStart=math.ceil(xV[n])
	if xVStart>50:
		xVStart=60
	else:
		xVStart=30
	# 仿真时间
	# 通过 制动开始计算
	simTime=numpy.array(resObj.simTimeGet())
	if simType==0:
		strType='max'
	else:
		strType='n'
	# 图片数据
	xlabelList=['time (s)','time (s)','time (s)','time (s)','time (s)','time (s)']
	ylabelList=['break_x_dis_m','break_y_dis_mm','break_z_dis_mm','break_z_angle_deg','break_x_acc_g','break_yaw_dis_g']
	xList=[simTime[n:],simTime[n:],simTime[n:],simTime[n:],simTime[n:],simTime[n:]]
	yList=[xDisDiff[n:],yDisDiff[n:],zDisDiff[n:],xAngleDiff[n:],xAcc[n:],yawDis[n:]]
	figAdrList,figOldList=[],[]
	for n in range(len(xList)):
		plt.plot(xList[n],yList[n])
		plt.xlabel(xlabelList[n])
		plt.ylabel(ylabelList[n])
		plt.grid(True,linestyle='--',color='r')
		figAdr=targetAdr+r'\%s_v%d_%s.png'%(ylabelList[n],xVStart,strType)
		figOldStr=r'#\%s_v%d_%s'%(ylabelList[n],xVStart,strType)
		plt.savefig(figAdr)
		plt.close()
		figAdrList.append(figAdr)
		figOldList.append(figOldStr)
	# 数值数据
	oldList=['$Disx_V%d_%s'%(xVStart,strType),'$Disy_V%d_%s'%(xVStart,strType),'$Disz_V%d_%s'%(xVStart,strType),'$Anglex_V%d_%s'%(xVStart,strType)]
	newList=roundList([xDisMaxDiff,yDisMaxDiff,zDisMaxDiff,xAngleMaxDiff],2)
	# 合并
	oldList.extend(figOldList)
	newList.extend(figAdrList)
	return oldList,newList


# # 输入 制动计算---------------------------------------------------
# reqs=['chassis_displacements','chassis_displacements'] #['zhidongpaopian','zhidongpaopian']
# comps=['lateral','vertical'] #['dy','dz']
# oldList=['$name']
# newList=['K6RA']
# # 后处理路径
# resAdr=r'E:\ADAMS\test_brake.res'
# # 图片目标路径
# targetAdr=r'E:\ADAMS\temptest'
# # 制动后处理计算
# oldList1,newList1=brakingResCal(resAdr=resAdr,reqs=reqs,comps=comps,targetAdr=targetAdr,simType=0)
# # doc文档替换目标及内容
# oldList.extend(oldList1)
# newList.extend(newList1)
# print(oldList)
# print(newList)

def crcHandleResCal(resAdr,targetAdr=None,L=None):
	'''
		单位 m/s deg m/s^2 m
		1、输入参数：
			轴距、车重
			起始时间、结果时间
			后处理文件路径
		2、读取后处理数据-稳态回转：
			request需求：车速、方向盘转角、侧倾角、侧向加速度、横摆角速度
			计算：不足转向度、中性转向点、半径比
		3、评分计算
	'''
	# 数据读取
	requests=['chassis_accelerations','chassis_velocities',
		'chassis_velocities','chassis_displacements',
		'jms_steering_wheel_angle_data','chassis_displacements',
		'chassis_displacements']
	components=['lateral','yaw',
		'longitudinal','roll',
		'displacement','lateral',
		'longitudinal']
	resObj=AdamsFile.resFile(resAdr)
	resData=resObj.resResearch(requests,components)
	# 转矩阵
	resData=numpy.array(resData)
	# 单位转换
	lateralAcc,yawV,xV,rollDis,steerWheelDis=resData[0]*9.8,resData[1]/math.pi*180,resData[2]/3.6,resData[3]/math.pi*180,resData[4]/math.pi*180
	yDis,xDis=resData[5]/1000,resData[6]/1000

	# 转弯半径 m
	yawV[abs(yawV)<0.1]=yawV[abs(yawV)>0][0]
	Rk=57.3*xV/yawV
	R0=Rk[Rk>0][0]
	Rk[Rk<1e-3]=R0
	print('R0:'+str(R0))
	# 侧偏角差值
	delta_a=57.3*L*(1/R0-1/Rk)
	# 0.4g 状态对应侧偏角
	loc_04g=abs(lateralAcc)>(0.4*9.8)
	rollDis_04g=rollDis[loc_04g][0]
	# 2m/s^2 状态
	loc_2acc=abs(lateralAcc)>2
	rollDis_2acc=abs(rollDis[loc_2acc][0])
	delta_a_2acc=delta_a[loc_2acc][0]
	# 2m/s^2 不足转向度
	U_2acc=delta_a_2acc/2
	# 2m/s^2 侧倾度
	rollDisK_2acc=rollDis_2acc/2
	# 中性转向点
	if sum(delta_a[loc_2acc])>0:
		for num,n in enumerate(delta_a):
			if n==max(delta_a):
				break
	else:
		for num,n in enumerate(delta_a):
			if n==min(delta_a):
				break
	print('mid-steer-point:'+str(lateralAcc[num]))
	print(U_2acc)
	print(rollDis_2acc)
	# 路径显示
	n=math.floor(len(xDis)/3)
	plt.plot(xDis[0:n],yDis[0:n],'b')
	plt.plot(xDis[n:n*2],yDis[n:n*2],'y')
	plt.plot(xDis[n*2:],yDis[n*2:],'r')
	plt.plot(xDis[-1],yDis[-1],'*k')
	plt.show()


def sHandleResCal(resAdr,targetAdr=None,L=None):
	'''
		单位 m/s deg m/s^2 m
		1、输入参数：
			轴距、车重
			起始时间、结果时间
			后处理文件路径
		2、读取后处理数据-稳态回转：
			request需求：车速、方向盘转角、侧倾角、侧向加速度、横摆角速度
			计算：不足转向度、中性转向点、半径比
		3、评分计算
	'''
	# 数据读取
	requests=['chassis_accelerations','chassis_velocities',
		'chassis_velocities','chassis_displacements',
		'jms_steering_wheel_angle_data','chassis_displacements',
		'chassis_displacements']
	components=['lateral','yaw',
		'longitudinal','roll',
		'displacement','lateral',
		'longitudinal']
	resObj=AdamsFile.resFile(resAdr)
	resData=resObj.resResearch(requests,components)
	# 转矩阵
	resData=numpy.array(resData)
	# 单位转换
	lateralAcc,yawV,xV,rollDis,steerWheelDis=resData[0]*9.8,resData[1]/math.pi*180,resData[2]/3.6,resData[3]/math.pi*180,resData[4]/math.pi*180
	yDis,xDis=resData[5]/1000,resData[6]/1000










