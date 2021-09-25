# 2019/5/19
# AdamsModalTCP
# 调用自建模块 AdamsFile AdamsTCP
# 外库：numpy 
###################################################################
# 主函数 data_recv=modalChoose(pathData)
# 选择模型，运行子模块
# 输出 bytes类型 字节
###################################################################
# 子函数： setDeleteRes、getAsyAdr、getSpringDamperData

###################################################################
# 子模块： steerTravel、wheelTravel、springPreload
# 1、outputStr=steerTravel(asyName,cdbName,steerOutMax,steerInMax,travelIterations,precisionRange,steerGain=10)
# 	转向行程确定
# 2、outputStr=wheelTravel(asyName,cdbName,damperTravel,airspringTravel,travelIterations,precisionRange,wheelGain=0.8)
# 	轮跳行程确定，空气弹簧/减振器 悬架
# 3、outputStr=springPreload(asyName,cdbName)
# 	整车空气弹簧预载确定
###################################################################
import os,sys,time,re,glob,pathlib,math,itertools
import AdamsFile,AdamsTCP
from AdamsTCP_fun import *
from AdamsFile_fun import *
import numpy
# import matplotlib.pyplot as plt

def modelChoose(pathData):
	listStr=pathData.split('^:^')
	print(listStr)
	if listStr[0]=='springPreload':
		asyName=listStr[1]
		cdbName=listStr[2]
		simType=listStr[3]
		outputStr=springPreload(asyName=asyName,cdbName=cdbName,simType=simType)
		data_recv=outputStr.encode()
	elif listStr[0]=='steerTravel':
		asyName=listStr[1]
		cdbName=listStr[2]
		steerOutMax=float(listStr[3])
		steerInMax=float(listStr[4])
		steerTravelIterations=float(listStr[5])
		steerTravelPrecisionRange=float(listStr[6])
		steerTravelGain=float(listStr[7])
		outputStr=steerTravel(asyName=asyName,cdbName=cdbName,
			steerOutMax=steerOutMax,steerInMax=steerInMax,
			travelIterations=steerTravelIterations,
			precisionRange=steerTravelPrecisionRange,steerGain=steerTravelGain)
		data_recv=outputStr.encode()
	elif listStr[0]=='wheelTravel':
		asyName=listStr[1]
		cdbName=listStr[2]
		damperTravel=float(listStr[3])
		airspringTravel=float(listStr[4])
		wheelTravelIterations=float(listStr[5])
		wheelTravelPrecisionRange=float(listStr[6])
		wheelTravelGain=float(listStr[7])
		outputStr=wheelTravel(asyName=asyName,cdbName=cdbName,
			damperTravel=damperTravel,airspringTravel=airspringTravel,
			travelIterations=wheelTravelIterations,
			precisionRange=wheelTravelPrecisionRange,wheelGain=wheelTravelGain)
		data_recv=outputStr.encode()
	elif listStr[0]=='massAdjust':
		asyName=listStr[1]
		cdbName=listStr[2]
		massW=listStr[3]
		massIxx=listStr[4]
		massIyy=listStr[5]
		massIzz=listStr[6]
		massMarker=listStr[7]
		massPart=listStr[8]
		massAdjust(asyName,cdbName,massW,massIxx,massIyy,massIzz,massMarker,massPart)
		data_recv=b'success'
	elif listStr[0]=='hardpointAdjust':
		hardpointName=listStr[1]
		hardpointLoc=listStr[2]
		hardpointSym=listStr[3]
		hardpointAdjust(hardpointName,hardpointLoc,hardpointSym)
		data_recv=b'success'
	elif listStr[0]=='funCdbNames':
		data_recv=funCdbNames()
	elif listStr[0]=='funAsyNames':
		cdbName=listStr[1]
		data_recv=funAsyNames(cdbName)
	elif listStr[0]=='changeCurrent':
		cdbName=listStr[1]
		asyName=listStr[2]
		data_recv=funChangeCurrent(cdbName,asyName)
	elif listStr[0]=='funGetCurrentAsy':
		data_recv=funGetCurrentAsy()

	elif listStr[0]=='designSim':
		varName=listStr[1]
		varRange=listStr[2]
		editCmd=listStr[3]
		varState=listStr[4]
		varSingle=listStr[5]
		designSim(varName,varRange,editCmd,varState,varSingle)

		# print(varName)
		# print(varRange)
		# print(varState)
		# print(editCmd)
		data_recv=b'success'

	return data_recv

# sub function
def numpy_calLoc(arr,row,column):
	# 输入 列表
	# 输出矩阵
	# 用于定位矩阵
	# row=[0,2]
	# column=[1,11,17,23,34]
	if len(row)>1:
		for n in range(0,len(row)-1):
			if n==0:
				arrData=numpy.row_stack((arr[row[n],column],arr[row[n+1],column]))
			else:
				arrData=numpy.row_stack((arrData,arr[row[n+1],column]))
		return arrData
	else:
		return arr[row[0],column]

###################################################################
# steerTrave simulate
def steerTravel(asyName,cdbName,steerOutMax,steerInMax,travelIterations,precisionRange,steerGain=10):
	def subSimSteer(asyName,steerUpper,steerLower):
		simStr='acar analysis suspension steering submit &\n'+\
			'assembly={} &\n'.format(asyName)+\
			'variant=default &\n'+\
			'output_prefix="autoSteerTravel" &\n'+\
			'nsteps=21 &\n'+\
			'steer_upper={} &\n'.format(steerUpper)+\
			'steer_lower={} &\n'.format(steerLower)+\
			'&\n'+\
			'&\n'+\
			'vertical_setup=wheel_center_height &\n'+\
			'vertical_type=absolute &\n'+\
			'vertical_input=wheel_center_height &\n'+\
			'coordinate_system=vehicle &\n'+\
			'steering_input=angle &\n'+\
			'comment="" &\n'+\
			'analysis_mode=interactive &\n'+\
			'log_file=yes '
		return simStr
	def subSteerJudge(mainAngel,minorAngel,steerWheelAngle,
		steerOutMax,steerInMax,steerGain):
		if mainAngel.max() > minorAngel.max():
			# + :left in ;right out
			# 内转为正
			if steerWheelAngle[numpy.argmax(mainAngel)]>0:
				# 主轮：内转-车轮转角正,方向盘正
				mainIn=abs(mainAngel.max())
				mainInWheel=abs(steerWheelAngle.max())
				mainOut=abs(mainAngel.min())
				mainOutWheel=abs(steerWheelAngle.min())

				mainInWheel=mainInWheel+(steerInMax-mainIn)*steerGain
				mainOutWheel=mainOutWheel+(steerOutMax-mainOut)*steerGain
				wheelMax=mainInWheel
				wheelMin=-mainOutWheel
				# return (-mainOutWheel,mainInWheel)
			else:
				# 主轮：内转-车轮转角正,方向盘负
				mainIn=abs(mainAngel.max())
				mainInWheel=abs(steerWheelAngle.min())
				mainOut=abs(mainAngel.min())
				mainOutWheel=abs(steerWheelAngle.max())
				mainInWheel=mainInWheel+(steerInMax-mainIn)*steerGain
				mainOutWheel=mainOutWheel+(steerOutMax-mainOut)*steerGain
				wheelMax=mainOutWheel
				wheelMin=-mainInWheel
				# return (-mainInWheel,mainOutWheel)
		else:
			# + :left out ;right in
			# 内转为负
			if steerWheelAngle[numpy.argmin(mainAngel)]>0:
				# 主轮：内转-车轮转角负,方向盘正
				mainIn=abs(mainAngel.min())
				mainInWheel=abs(steerWheelAngle.max())
				mainOut=abs(mainAngel.max())
				mainOutWheel=abs(steerWheelAngle.min())
				mainInWheel=mainInWheel+(steerInMax-mainIn)*steerGain
				mainOutWheel=mainOutWheel+(steerOutMax-mainOut)*steerGain
				wheelMax=mainInWheel
				wheelMin=-mainOutWheel
				# return (-mainOutWheel,mainInWheel)
			else:
				# 主轮：内转-车轮转角负,方向盘负
				mainIn=abs(mainAngel.min())
				mainInWheel=abs(steerWheelAngle.min())
				mainOut=abs(mainAngel.max())
				mainOutWheel=abs(steerWheelAngle.max())
				mainInWheel=mainInWheel+(steerInMax-mainIn)*steerGain
				mainOutWheel=mainOutWheel+(steerOutMax-mainOut)*steerGain
				wheelMax=mainOutWheel
				wheelMin=-mainInWheel
				# return (-mainInWheel,mainOutWheel)
		return (wheelMin,wheelMax,mainIn,mainOut)
	# print(asyName)
	# print(cdbName)
	# print(steerOutMax)
	# print(steerInMax)
	# print(travelIterations)
	# print(precisionRange)
	# print(steerGain)
	(cfgObj,asyAdr)=getAsyAdr(cdbName,asyName)
	asyObj=AdamsFile.asyFile(asyAdr)
	resName='autoSteerTravel_steering'
	simPath=getSimPath()
	resAdr=simPath+'\\'+resName+'.res'
	n=1
	while True:
		if n==1:
			steerUpper=500
			steerLower=-500
		else:
			steerUpper=wheelMax
			steerLower=wheelMin
		
		if n>travelIterations:
			break
		# sim before
		setDeleteRes(asyName,resName)
		# sim steer
		setSimulateTCP(subSimSteer(asyName,steerUpper,steerLower))
		# read_file
		requests=['steer_angle','steer_angle','steering_wheel_input']
		components=['left','right','steering_wheel_input']
		resObj=AdamsFile.resFile(resAdr)
		resData=resObj.resResearch(request=requests,component=components)
		resArr=numpy.array(resData)*180/3.141592654
		# cal
		(wheelMin,wheelMax,mainIn,mainOut)=subSteerJudge(mainAngel=resArr[0],minorAngel=resArr[1],steerWheelAngle=resArr[2],
			steerOutMax=steerOutMax,steerInMax=steerInMax,steerGain=steerGain)

		outputStr=r'steerWheelAngleMax:{}\n'.format(wheelMax)+\
			r'steerWheelAngleMin:{}\n'.format(wheelMin)+\
			r'mainIn:{}\n'.format(mainIn)+\
			r'mainOut:{}\n'.format(mainOut)+\
			r'迭代次数:{}\n'.format(n)
		print(outputStr)
		temp1=abs(mainIn-steerInMax)<precisionRange
		temp2=abs(mainOut-steerOutMax)<precisionRange
		if temp1 & temp2:
			print(mainIn-steerInMax)
			print(mainOut-steerOutMax)
			break
		n+=1
	print('结束转向行程计算')
	return outputStr
	# print(resArr[1].max())
	# print(resArr[2].max())
	# plt.plot(resArr[0],resArr[1])
	# plt.show()

###################################################################
# sim wheelTravel
def wheelTravel(asyName,cdbName,damperTravel,airspringTravel,travelIterations,
	precisionRange,wheelGain=0.8):
	def subSimLoadcase(asyName,lcfAdr,model='interactive'):
		simStr='acar analysis suspension loadcase submit & \n'+\
		'assembly={} & \n'.format(asyName)+\
		'variant=default & \n'+\
		'output_prefix="autoSimLoadcase" & \n'+\
		'loadcase_files="file://{}" & \n'.format(lcfAdr)+\
		'load_results=yes & \n'+\
		'comment="" & \n'+\
		'analysis_mode={} & \n'.format(model)+\
		'log_file=yes '
		return simStr
	def subAllTravel(lowerTravelP,upperTravelP,lowerTravelO,upperTravelO):
		lowerToUpperO=numpy.linspace(lowerTravelO,upperTravelO,11)
		upperToLowerO=numpy.linspace(upperTravelO,lowerTravelO,11)
		lowerToZeroO=numpy.linspace(lowerTravelO,0,6)
		upperToZeroO=numpy.linspace(upperTravelO,0,6)
		zeroToUpperO=numpy.linspace(0,upperTravelO,6)
		zeroToLowerO=numpy.linspace(0,lowerTravelO,6)

		lowerToUpperP=numpy.linspace(lowerTravelP,upperTravelP,11)
		upperToLowerP=numpy.linspace(upperTravelP,lowerTravelP,11)
		lowerToZeroP=numpy.linspace(lowerTravelP,0,6)
		upperToZeroP=numpy.linspace(upperTravelP,0,6)
		zeroToUpperP=numpy.linspace(0,upperTravelP,6)
		zeroToLowerP=numpy.linspace(0,lowerTravelP,6)

		leftTravel=numpy.append(lowerToUpperO,upperToZeroO)
		leftTravel=numpy.append(leftTravel,zeroToLowerP)
		leftTravel=numpy.append(leftTravel,lowerToUpperP)

		rightTravel=numpy.append(upperToLowerO,lowerToZeroO)
		rightTravel=numpy.append(rightTravel,zeroToLowerP)
		rightTravel=numpy.append(rightTravel,lowerToUpperP)


		fullTravel=numpy.column_stack((leftTravel,rightTravel))
		zeroArr=numpy.zeros((len(leftTravel),9))
		allTravel=numpy.column_stack((fullTravel,zeroArr))
		# fullTravel=numpy.row_stack((leftTravel,rightTravel))
		# allTravelList=allTravel.tolist()
		return allTravel

	lcfName='loadcaseNew'
	resName='autoSimLoadcase_{}'.format(lcfName)
	runPath=os.getcwd()
	lcfAdr=r'{}/temp/{}.lcf'.format(runPath,lcfName)
	simPath=getSimPath()
	resAdr=simPath+'\\'+resName+'.res'
	(cfgObj,asyAdr)=getAsyAdr(cdbName,asyName)
	asyObj=AdamsFile.asyFile(asyAdr)

	# get request / component
	(springDataUsed,damperDataUsed)=getSpringDamperData(asyAdr)
	print(springDataUsed)
	print(damperDataUsed)
	requests=[]
	components=[]
	nSpring=0
	locSpringLeft=[]
	locSpringRight=[]
	nDamper=0
	locDamperLeft=[]
	locDamperRight=[]
	springDamperLength=[]
	# damperLength=[]
	for temp in springDataUsed:
		requests.append(temp[6])
		components.append(temp[8])
		springDamperLength.append(float(AdamsTCP.cmdSend(cmds=temp[5]+'.dmCalc',typeIn='query')))
		if temp[1]=='left':
			locSpringLeft.append(nSpring)
		elif temp[1]=='right':
			locSpringRight.append(nSpring)
		nSpring+=1
	nDamper=nSpring
	for temp in damperDataUsed:
		requests.append(temp[4])
		components.append(temp[6])
		springDamperLength.append(float(AdamsTCP.cmdSend(cmds=temp[3]+'.dmCalc',typeIn='query')))
		if temp[1]=='left':
			locDamperLeft.append(nDamper)
		elif temp[1]=='right':
			locDamperRight.append(nDamper)
		nDamper+=1
	springDamperLength=numpy.array(springDamperLength)
	# print('start length:')
	# print(springDamperLength)
	# print(locSpringLeft)
	# print(locDamperLeft)
	# cal 
	n=0
	while True:
		n+=1
		if n==1:
			# 平行轮跳-下跳动
			lowerTravelP=-damperTravel*wheelGain
			# 平行轮跳-上跳动
			upperTravelP=airspringTravel*wheelGain
			# 反向轮跳-下跳
			lowerTravelO=-damperTravel*wheelGain
			# 反向轮跳-上跳
			upperTravelO=airspringTravel*wheelGain
		elif n>travelIterations:
			break
		else:
			if leftSpring.size>5:
				# 超过1对弹簧
				deltaSprP=(airspringTravel-(springDamperLength[locSpringLeft]-leftSpring[:,4]))
				deltaSprO=(airspringTravel-(springDamperLength[locSpringRight]-rightSpring[:,0]))
			else:
				deltaSprP=(airspringTravel-(springDamperLength[locSpringLeft]-leftSpring[4]))
				deltaSprO=(airspringTravel-(springDamperLength[locSpringRight]-rightSpring[0]))

			if leftDamper.size>5:
				# 超过1对减振器
				deltaDamP=(damperTravel-(leftDamper[:,3]-springDamperLength[locDamperLeft]))
				deltaDamO=(damperTravel-(leftDamper[:,0]-springDamperLength[locDamperLeft]))
			else:
				deltaDamP=(damperTravel-(leftDamper[3]-springDamperLength[locDamperLeft]))
				deltaDamO=(damperTravel-(leftDamper[0]-springDamperLength[locDamperLeft]))

			deltaAll=[deltaDamP,deltaSprP,deltaDamO,deltaSprO]
			# print(deltaAll)
			lowerTravelP=lowerTravelP-deltaDamP.min()*wheelGain
			upperTravelP=upperTravelP+deltaSprP.min()*wheelGain
			lowerTravelO=lowerTravelO-deltaDamO.min()*wheelGain
			upperTravelO=upperTravelO+deltaSprO.min()*wheelGain
			if (abs(deltaDamP).min()<precisionRange) & (abs(deltaSprP).min()<precisionRange):
				if (abs(deltaDamO).min()<precisionRange) & (abs(deltaSprO).min()<precisionRange):
					break

		allTravel=subAllTravel(lowerTravelP,upperTravelP,lowerTravelO,upperTravelO)

		# read loadcase title
		with open('temp/loadcaseTitle.lcf','r') as lcfId:
			loadcaseList=lcfId.readlines()

		# apend loadcase
		for temp in allTravel:
			linesStr=''
			for temp2 in temp:
				linesStr=linesStr+' '+str(temp2)
			linesStr=linesStr+' \n'
			loadcaseList.append(linesStr)

		# write loadcase
		with open('temp/loadcaseNew.lcf','w') as lcfId:
			for lineStr in loadcaseList:
				lcfId.write(lineStr)

		# sim before
		setDeleteRes(asyName,resName)
		# sim steer
		setSimulateTCP(subSimLoadcase(asyName,lcfAdr))

		# read_file
		resObj=AdamsFile.resFile(resAdr)
		resData=resObj.resResearch(request=requests,component=components)
		resArr=numpy.array(resData)

		leftSpring=numpy_calLoc(resArr,locSpringLeft,[1,11,17,23,34])
		rightSpring=numpy_calLoc(resArr,locSpringRight,[1,11,17,23,34])
		leftDamper=numpy_calLoc(resArr,locDamperLeft,[1,11,17,23,34])
		rightDamper=numpy_calLoc(resArr,locDamperRight,[1,11,17,23,34])
		# print('leftSpring length:')
		# print(leftSpring)

		# 0 lower 1 upper opposite
		# 2 zero
		# 3 lower 4 upper parallel

	outputStr=r'平行下跳量：:{}\n'.format(lowerTravelP)+\
		r'平行上跳量：:{}\n'.format(upperTravelP)+\
		r'反向下跳量：:{}\n'.format(lowerTravelO)+\
		r'反向上跳量：:{}\n'.format(upperTravelO)+\
		r'迭代次数:{}\n'.format(n-1)+\
		r'偏差:{}\n'.format(str(deltaAll))
	print('success')
	return outputStr

###################################################################
# springPreload simulate
def springPreload(asyName,cdbName,simType='settle'):
	def sunSimStatic(asyName,simName='autoSim',analysisMode='interactive',simType='settle'):
		"""	
		AdamsFile.adamsCmd.cmdStaticSimulate(aysName=data['asyName'],simName='autoSim',
		analysisMode='interactive')
		"""
		dataOut='acar analysis full_vehicle static submit &\n'+\
		' assembly={} &\n'.format(asyName)+\
		' variant=default &\n'+\
		' output_prefix="{}" &\n'.format(simName)+\
		' comment="" &\n'+\
		' analysis_mode={} &\n'.format(analysisMode)+\
		' road_data_file="mdids://acar_shared/roads.tbl/2d_ssc_flat.rdf" &\n'+\
		' gear_position=0 &\n'+\
		' static_task={} &\n'.format(simType)+\
		' linear=no &\n'+\
		' log_file=yes'
		return dataOut
	def subSpringEdit(springFullName,springAdr,userValue,
			valueType,symmetric):
		"""
		AdamsFile.adamsCmd.subSpringEdit(springFullName=line[5],springAdr=springAdr,userValue='0',
			valueType='preload',symmetric='no')
		"""
		dataOut='acar standard_interface spring &\n'+\
		' spring={} &\n'.format(springFullName)+\
		' property_file="{}" &\n'.format(springAdr)+\
		' user_value={} &\n'.format(userValue)+\
		' value_type={} &\n'.format(valueType)+\
		' symmetric={}\n'.format(symmetric)
		print(dataOut)
		return dataOut

	resName='autoSim_static'
	simPath=getSimPath()
	runPath=os.getcwd()
	resAdr=simPath+'\\'+resName+'.res'

	(cfgObj,asyAdr)=getAsyAdr(cdbName,asyName)
	(springDataUsed,damperDataUsed)=getSpringDamperData(asyAdr)
	print(springDataUsed)
	print(damperDataUsed)
	requests=[]
	components=[]
	for temp in springDataUsed:
		requests.append(temp[6])
		components.append(temp[7])
	print(requests)
	print(components)

	# spring edit
	rigidSpringAdr=runPath+r'\temp\for_preload.spr'
	for springData in springDataUsed:
		springCmd=subSpringEdit(springFullName=springData[5],springAdr=rigidSpringAdr,userValue=0,
				valueType='preload',symmetric='yes')
		AdamsTCP.cmdSend(cmds=AdamsTCP.cmdConvert(springCmd),typeIn='cmd')
		print(springCmd)

	# sim before
	setDeleteRes(asyName,resName)
	# sim static
	setSimulateTCP(sunSimStatic(asyName=asyName,simType=simType))
	# res file read
	resObj=AdamsFile.resFile(resAdr)
	resData=resObj.resResearch(request=requests,component=components)
	print(resData)

	# spring edit
	n=0
	for springData in springDataUsed:
		springCmd=subSpringEdit(springFullName=springData[5],springAdr=springData[2],userValue=resData[n][-1],
				valueType='preload',symmetric='no')
		AdamsTCP.cmdSend(cmds=AdamsTCP.cmdConvert(springCmd),typeIn='cmd')
		n+=1
		# print(springCmd)

	# sim before
	setDeleteRes(asyName,resName)
	# sim static
	setSimulateTCP(sunSimStatic(asyName=asyName,simType=simType))
	
	outputStr='success'
	return  outputStr

def hardpointAdjust(hardpointName,hardpointLoc,hardpointSym):

	# def subHardpoint(hardpointName,hardpointLoc,symmetric)

	if hardpointSym.lower()=='y' or hardpointSym.lower()=='n':
		if hardpointSym.lower()=='y':
			symmetric='yes'
		elif hardpointSym.lower()=='n':
			symmetric='no'
		cmd='acar standard_interface hardpoint &\n'+\
	 		'hardpoint={} &\n'.format(hardpointName)+\
	 		'location={} &\n'.format(hardpointLoc)+\
	 		'symmetric={}'.format(symmetric)
	elif hardpointSym.lower()=='s':	
		cmd='acar standard_interface hardpoint &\n'+\
	 		'hardpoint={} &\n'.format(hardpointName)+\
	 		'location={}'.format(hardpointLoc)

	AdamsTCP.cmdSend(cmds=AdamsTCP.cmdConvert(cmd),typeIn='cmd')

def massAdjust(asyName,cdbName,massW,massIxx,massIyy,massIzz,massMarker,massPart):
	cmd='acar toolkit adjust mass &\n'+\
		 'model={} &\n'.format(asyName)+\
		 'desired_model_mass={} &\n'.format(massW)+\
		 'cg_location=0,0,0 &\n'+\
		 'ixx={} &\n'.format(massIxx)+\
		 'iyy={} &\n'.format(massIyy)+\
		 'izz={} &\n'.format(massIzz)+\
		 ' &\n'+\
		 ' &\n'+\
		 ' &\n'+\
		 'relative_to={} &\n'.format(massMarker)+\
		 'm_part={}'.format(massPart)
	AdamsTCP.cmdSend(cmds=AdamsTCP.cmdConvert(cmd),typeIn='cmd')

def funCdbNames():
	names=getCdbNames()
	dataStr=''
	for name in names:
		dataStr=dataStr+'<option value="{}">{}</option>'.format(name,name)
	print(dataStr)
	return dataStr.encode()

def funAsyNames(cdbName):
	names=getAsyNames(cdbName)
	dataStr=''
	for name in names:
		dataStr=dataStr+'<option value="{}">{}</option>'.format(name,name)
	# print(dataStr)
	return dataStr.encode()

def funChangeCurrent(cdbName,asyName):
	asyName='.'+asyName.split('.')[-1]
	str1=AdamsTCP.cmdSend(cmds=asyName+'.model_class',typeIn='query').decode()
	print(asyName)
	print(str1)
	setDefaultCdb('private')
	setRemoveCdb(cdbName)
	setAddCdb(cdbName,getCdbAdr(cdbName)[1])
	setDefaultCdb(cdbName)
	if str1!='assembly':
		asyAdr=getAsyAdr(cdbName,asyName)[1]
		# print(asyAdr)
		setOpenAsy(asyAdr)
	setCurrenModel(asyName)
	return 'cal end'.encode()

def funGetCurrentAsy():
	asyData=getCurrentAsy()
	dataStr=''
	for name in asyData:
		dataStr=dataStr+'<option value="{}">{}</option>'.format(name,name)
	return dataStr.encode()

def designSim(varName,varRange,editCmd,varState,varSingle):
	def funVarRange(varRange):
		if 'list' in varRange:
			varRange=varRange.split('list')[-1]
			varCmds=eval(varRange)
			# print(varCmds)
		else:
			varRange=varRange.split(',')
			varMin=float(varRange[0])
			varMax=float(varRange[1])
			# varNum=float(varRange[2])
			varNum=int(varRange[2])
			varCmds=numpy.linspace(varMin,varMax,varNum)
		return varCmds

	varNames=varName.split('^n^')
	varRanges=varRange.split('^n^')
	varStates=varState.split('^n^')
	varSingle=varSingle.split('^n^')

	# 删除无用数据
	newNames=[]
	temp=[]
	isSingle=[]
	for num in range(0,len(varNames)):
		if varStates[num].lower()=='true':
			newNames.append(varNames[num])
			temp.append(varRanges[num])
			isSingle.append(varSingle[num])

	newRanges=[]
	for varRange in temp:
		newRanges.append(funVarRange(varRange))

	editCmds=editCmd.split('$$')
	# print(editCmd)
	# print(simulateCmd)

	# 单一变量位置
	singleLoc=[]
	# 常规变量位置
	normalLoc=[]
	# 变量数
	nvar=len(newRanges)
	# 变量长度
	varlen=len(newRanges[0])
	
	for num in range(nvar):
		if isSingle[num].lower()=='true':
			singleLoc.append(num)
		else:
			normalLoc.append(num)

	# 所有变量组合
	varListAll=[]
	pn=itertools.product(range(varlen),repeat=len(singleLoc))
	for singleTemp in pn:
		varListOne=list(range(nvar))
		if len(singleLoc)>0:
			for temp in range(len(singleLoc)):
				varListOne[singleLoc[temp]]=singleTemp[temp]
		if len(normalLoc)>0:
			for temp in normalLoc:
				varListOne[temp]=singleTemp[0]
		varListAll.append(varListOne)

	for n in varListAll:
		for subCmd in editCmds:
			# 每条命令更改
			subCmd=subCmd.replace('&','&\n',-1)
			num=0
			for n2 in n:
				subCmd=subCmd.replace('{'+varNames[num]+'}',str(newRanges[num][n2]),-1)
				num+=1
			print(subCmd)
			print('——————————————————————————————')
			# 解析
			cmds=AdamsTCP.cmdConvert(subCmd)
			if '^python^' in cmds[0]:
				pyStr=cmds[0].replace('^python^','')
				eval(pyStr)
			elif '^simulate^' in cmds[0]:
				simStr=cmds[0].replace('^simulate^','')
				setSimulateTCP(simStr)
			else:
				AdamsTCP.cmdSend(cmds=cmds,typeIn='cmd')



# asyName='.mdi_front_vehicle'
# resName='autoSimLoadcase_loadcaseNew'
# requests=['ackerman','ackerman']
# components=['left','right']
# print(getResData(asyName,resName,requests,components))



# cfgPath=AdamsFile.cfgPathSearch()
# cfgObj=AdamsFile.cfgFile(cfgPath)
# cdbNames=list(cfgObj.database.keys())
# cdbPaths=list(cfgObj.database.values())

# asyAdr=cdbPath+'/assemblies.tbl/'+asyName.split('.')[-1]+'.asy'
# print(cdbNames)
# print(cdbPaths)


# print(getAsyNames('test'))
# print(getCdbNames())

# hardpointName='.mdi_front_vehicle_test.double_wishbone_test.ground.hpl_test'
# hardpointLoc='-250.0, -500.0, 650.0'
# hardpointSym='Y'
# hardpointAdjust(hardpointName,hardpointLoc,hardpointSym)


# asyName='.MDI_Demo_Vehicle'


# varName='test'
# varRange='40,60,3'
# editCmd='acar standard_interface hardpoint &'+\
# 'hardpoint=.mdi_front_vehicle.MDI_FRONT_SUSPENSION.ground.hpl_top_mount &'+\
# 'location={test}, -603.8, 790.0 &'+\
# 'symmetric=yes'+\
# '$$'+\
# 'acar standard_interface hardpoint &'+\
# 'hardpoint=.mdi_front_vehicle.MDI_FRONT_SUSPENSION.ground.hpl_top_mount &'+\
# 'location={test}, -603.8, 790.0 &'+\
# 'symmetric=yes'


# simulateCmd='acar analysis suspension parallel_travel submit &'+\
# 'assembly=.mdi_front_vehicle &'+\
# 'variant=default &'+\
# 'output_prefix="test_{test}" &'+\
# 'nsteps=10 &'+\
# 'bump_disp=50 &'+\
# 'rebound_disp=-50 &'+\
# 'steering_input=angle &'+\
# 'vertical_setup=wheel_center_height &'+\
# 'vertical_input=wheel_center_height &'+\
# 'vertical_type=absolute &'+\
# 'comment="" &'+\
# 'analysis_mode=interactive &'+\
# 'log_file=yes '

# test springPreload
# asyName='.MDI_Demo_Vehicle'
# cdbName='Test'
# springPreload(asyName,cdbName)

# test wheelTravel
# asyName='.mdi_front_vehicle'
# cdbName='Test'
# damperTravel=60
# airspringTravel=60
# travelIterations=10
# precisionRange=0.5
# wheelTravel(asyName,cdbName,damperTravel,airspringTravel,travelIterations,
# 	precisionRange,wheelGain=0.8)

# test steerTravel

# asyName='.mdi_front_vehicle'
# cdbName='Test' 
# steerOutMax=20
# steerInMax=25
# travelIterations=6
# precisionRange=0.1
# steerTravel(asyName=asyName,cdbName=cdbName,
# 	steerOutMax=steerOutMax,steerInMax=steerInMax,
# 	travelIterations=travelIterations,
# 	precisionRange=precisionRange)
