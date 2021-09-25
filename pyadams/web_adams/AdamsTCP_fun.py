import os,sys,time,re,glob,pathlib,math
import AdamsFile,AdamsTCP
import numpy
'''
	调用AdamsFile ， AdamsTCP

'''

# 调用 AdamsTCP

#	set模块
#	setSimulateTCP(cmds) 调用：AdamsTCP、os;用于仿真cmd命名发送
#	setAddCdb(cdbName,cdbPah)
#	setRemoveCdb(cdbName)
#	setDefaultCdb(cdbName)
#	setOpenAsy(asyAdr)
#	setCurrenModel(modelName)
#	setDeleteRes(asyName,resName)
#	setCloseAsy(asyName)
#	###########################################
#	get模块
#	getCurrentModel()
# 	getCurrentModel()
# 	getCurrentCDB()
# 	getCurrentModel()
# 	getCurrentCDB()
# 	getSimPath()
# 	getResData(asyName,resName,requests,components)
# 	getAsyAdr(cdbName,asyName)
# 	getCdbAdr(cdbName)
# 	getAsyNames(cdbName)
# 	getCdbNames()
# 	getSpringDamperData(asyAdr)

#	###########################################
#	isSteeringExist() 转向系统是否存在

#getCurrentModel()
#	获取当前界面的仿真模型
#getCurrentCDB()
#	获取当前cdb数据库
#simPath=deleteRes(asyName,resName) 
#	调用：AdamsTCP
#	删除 res文件 及adams analysis 
#	输出adams 仿真路径
#(cfgObj,asyAdr)=getAsyAdr(cdbName,asyName)
#	调用：AdamsFile
#	输入 cdbName='Test'  asyName='.test'
#	输出cfgObj(CDB数据库-AdamsFile.cdbFile) 以及 装配系统文件
#getCdbNames()
#
#getAsyNames(cdbName)
#
#(springDataUsed,damperDataUsed)=getSpringDamperData(asyAdr)
# 	调用：AdamsFile
# 	输入装配系统文件路径
# 	输出弹簧数据、减振器数据
#	spring:[0] usage; [1] symmetry; [2] property_file; [3] value_type; [4] user_value;
#	spring:[5] springFullName; [6] springRequestName; [7] componentForce; [8] componentDis
#	spring:[9] componentVelocity;
# 	damper:[0] usage; [1] symmetry; [2] property_file;
#	damper:[3] damperFullName; [4] damperRequestName; [5] componentForce; [6] componentDis;
#	damper:[7] componentVelocity; 
#getResData(asyName,resName,requests,components)
#   在ADAMS 后处理已读取 res数据的状态下输出 指定数据


def setSimulateTCP(cmds):
	if re.match('(.*)?\n(.*)?',cmds):
		temp=AdamsTCP.cmdConvert(cmds)
	else:
		temp=cmds
	state_cmd=AdamsTCP.cmdSend(cmds=temp,typeIn='cmd')
	if 'cmd: 1'==state_cmd.decode():
		print(state_cmd.decode())
		print('sim failed')
		os._exit(0)

def setAddCdb(cdbName,cdbPah):
	cmd='acar toolkit database add &\n'+\
	' database_name="{}" &\n'.format(cdbName)+\
	' database_path="{}"'.format(cdbPah)
	AdamsTCP.cmdSend(cmds=AdamsTCP.cmdConvert(cmd),typeIn='cmd')	

def setRemoveCdb(cdbName):
	cmd='acar toolkit database remove &\n'+\
	' database_name="{}"'.format(cdbName)
	AdamsTCP.cmdSend(cmds=AdamsTCP.cmdConvert(cmd),typeIn='cmd')

def setDefaultCdb(cdbName):
	cmd='acar toolkit database default writable &\n'+\
	' database_name="{}"'.format(cdbName)
	AdamsTCP.cmdSend(cmds=AdamsTCP.cmdConvert(cmd),typeIn='cmd')

def setOpenAsy(asyAdr):
	cmd='acar files assembly open &\n'+\
	' assembly_name="{}"'.format(asyAdr)
	AdamsTCP.cmdSend(cmds=AdamsTCP.cmdConvert(cmd),typeIn='cmd')

def setCurrenModel(modelName):
	cmd='model display model_name={} fit_to_view=yes'.format(modelName)
	AdamsTCP.cmdSend(cmds=cmd,typeIn='cmd')

def setDeleteRes(asyName,resName):
	# delete res
	# asyNme :  .mdi_front_vehicle
	# resName: test_steer

	# delete analysis
	# current adams simPath
	simPath=AdamsTCP.cmdSend(cmds='getcwd()',typeIn='query').decode()
	# cmd delete adams analysis
	temp='analysis delete analysis_name={}.{}'.format(asyName,resName)
	AdamsTCP.cmdSend(cmds=temp,typeIn='cmd')
	# delete file 
	resDel=glob.glob(simPath+r'\{}.*'.format(resName))
	if resDel:
		for line in resDel:
			print('delete:'+line)
			os.remove(line)
	# return simPath

def setCloseAsy(asyName):
	asyName='.'+asyName.split('.')[-1]
	cmd='acar files assembly close assembly_name={}'.format(asyName)
	AdamsTCP.cmdSend(cmds=cmd,typeIn='cmd')

###############################################

def getCurrentModel():
	return AdamsTCP.cmdSend(cmds='.gui.main.front.contents',typeIn='query').decode()

def getCurrentCDB():
	return AdamsTCP.cmdSend(cmds='eval(cdb_get_write_default())',typeIn='query').decode()

def getCurrentModel():
	return AdamsTCP.cmdSend(cmds='.gui.main.front.contents',typeIn='query').decode()

def getCurrentCDB():
	return AdamsTCP.cmdSend(cmds='eval(cdb_get_write_default())',typeIn='query').decode()


def getSimPath():
	# get adams current simulation path
	return AdamsTCP.cmdSend(cmds='getcwd()',typeIn='query').decode()


def getResData(asyName,resName,requests,components):
	simPath=getSimPath()
	resData=[]
	for n in range(0,len(requests)):
		cmdstr='numeric_results write  &\n'+\
			'result_set_component_name = {}.{}.{}.{} &\n'.format(asyName,resName,requests[n],components[n])+\
			'sort_by = by_time  &\n'+\
			'order = ascending  &\n'+\
			'write_to_terminal = off  &\n'+\
			'file_name = "auto_{}.txt"'.format(n)

		fileName='auto_{}'.format(n)
		fileAdr=r'{}/{}.txt'.format(simPath,fileName)
		try:
			os.remove(fileAdr)
		except:
			print('no fielAdr')
		AdamsTCP.cmdSend(cmds=AdamsTCP.cmdConvert(cmdstr),typeIn='cmd')

		with open(fileAdr,'r') as fileId:
			resList=fileId.readlines()
		subData=[]
		n=0
		for line in resList:
			if ' A ' in line:
				n+=1
				break
			n+=1
		resList=resList[n:]
		for line in resList:
			subData.append(float(line))
		resData.append(subData)
	return resData


def getCurrentAsy():
	asyStr=AdamsTCP.cmdSend(cmds='.acar.dboxes.dbox_fil_ass_clo.o_assembly_name.CHOICES',typeIn='query').decode()
	# print(asyStr)
	if ',' in asyStr:
		asyData=eval(asyStr)
		asyData=list(asyData)
	else:
		asyData=[asyStr]
	# print(asyData)
	# print(type(asyData))
	return asyData



def isSteeringExist():
	asyName=getCurrentModel()
	cdbName=getCurrentCDB()
	(cfgObj,asyAdr)=getAsyAdr(cdbName,asyName)
	asyObj=AdamsFile.asyFile(asyAdr)
	subData=asyObj.subsystem
	steeringExist=False
	for line in subData:
		if line[0].lower()=='steering':
			steeringExist=True
			break
	return steeringExist

def getAsyAdr(cdbName,asyName):
	# get asyAdr
	cfgPath=AdamsFile.cfgPathSearch()
	cfgObj=AdamsFile.cfgFile(cfgPath)
	cdbPath=cfgObj.database[cdbName.lower()]
	asyAdr=cdbPath+'/assemblies.tbl/'+asyName.split('.')[-1]+'.asy'
	return (cfgObj,asyAdr)

def getCdbAdr(cdbName):
	cfgPath=AdamsFile.cfgPathSearch()
	cfgObj=AdamsFile.cfgFile(cfgPath)
	cdbPath=cfgObj.database[cdbName.lower()]
	return  (cfgObj,cdbPath)

def getAsyNames(cdbName):
# for cdbName in cdbNames:
	asyNames=[]
	cfgPath=AdamsFile.cfgPathSearch()
	cfgObj=AdamsFile.cfgFile(cfgPath)
	if cdbName=='private':
		return ['none']
	cdbPath=cfgObj.database[cdbName]
	searchPath=r'{}/assemblies.tbl/*.asy'.format(cdbPath)
	fullSearch=glob.glob(searchPath)
	for path in fullSearch:
		reg=re.match('^(.*)assemblies.tbl(.*)',path).group(2)
		asyName=reg[1:-4]
		asyNames.append(asyName)
		# print(asyNames)
	return asyNames

def getCdbNames():
	asyNames=[]
	cfgPath=AdamsFile.cfgPathSearch()
	cfgObj=AdamsFile.cfgFile(cfgPath)
	cdbNames=list(cfgObj.database.keys())
	return cdbNames

def getSpringDamperData(asyAdr):
	# input asyAdr
	# out springData (list)
	cfgObj=AdamsFile.cfgFile(AdamsFile.cfgPathSearch())
	asyName='.'+os.path.split(asyAdr)[1].split('.asy')[0]
	asyObj=AdamsFile.asyFile(asyAdr)
	subData=asyObj.subsystem
	susSubAdr=[]
	for line in subData:
		if line[0]=='suspension':
			susSubAdr.append(cfgObj.convert2ap(line[3]))
	# print(susSubAdr)
	# print(len(susSubAdr))
	springDataUsed=[]
	for susAdr in susSubAdr:
		subName=os.path.split(susAdr)[1].split('.sub')[0]
		subObj=AdamsFile.subFile(susAdr)
		# print(subObj.subHeader)
		for subSpring in subObj.spring:
			if subSpring[1]=='single':
				springFullName=asyName+'.'+subName+'.nss_'+subSpring[0]
				springRequestName='nss_'+subSpring[0]+'_data'
			elif subSpring[1]=='left':
				springFullName=asyName+'.'+subName+'.nsl_'+subSpring[0]
				springRequestName='nsl_'+subSpring[0]+'_data'
			elif subSpring[1]=='right':
				springFullName=asyName+'.'+subName+'.nsr_'+subSpring[0]
				springRequestName='nsr_'+subSpring[0]+'_data'
			if subObj.subHeader['minor_role']=='any':
				componentDis='displacement'
				componentForce='force'
				componentVelocity='velocity'
			else:
				componentDis='displacement_'+subObj.subHeader['minor_role']
				componentForce='force_'+subObj.subHeader['minor_role']
				componentVelocity='velocity_'+subObj.subHeader['minor_role']
			'spring:[0] usage; [1] symmetry; [2] property_file; [3] value_type; [4] user_value;'
			subSpring.append(springFullName)
			subSpring.append(springRequestName)
			subSpring.append(componentForce)
			subSpring.append(componentDis)
			subSpring.append(componentVelocity)
			'spring:[5] springFullName; [6] springRequestName; [7] componentForce; [8] componentDis'
			'spring:[9] componentVelocity; '
			springDataUsed.append(subSpring)
		# print(springDataUsed)

	damperDataUsed=[]
	for susAdr in susSubAdr:
		subName=os.path.split(susAdr)[1].split('.sub')[0]
		subObj=AdamsFile.subFile(susAdr)
		for subDamper in subObj.damper:
			# print(subDamper)
			if subDamper[1]=='single':
				damperFullName=asyName+'.'+subName+'.das_'+subDamper[0]
				damperRequestName='das_'+subDamper[0]+'_data'
			elif subDamper[1]=='left':
				damperFullName=asyName+'.'+subName+'.dal_'+subDamper[0]
				damperRequestName='dal_'+subDamper[0]+'_data'
			elif subDamper[1]=='right':
				damperFullName=asyName+'.'+subName+'.dar_'+subDamper[0]
				damperRequestName='dar_'+subDamper[0]+'_data'
			if subObj.subHeader['minor_role']=='any':
				componentDis='displacement'
				componentForce='force'
				componentVelocity='velocity'
			else:
				componentDis='displacement_'+subObj.subHeader['minor_role']
				componentForce='force_'+subObj.subHeader['minor_role']
				componentVelocity='velocity_'+subObj.subHeader['minor_role']
			'damper:[0] usage; [1] symmetry; [2] property_file;'
			subDamper.append(damperFullName)
			subDamper.append(damperRequestName)
			subDamper.append(componentForce)
			subDamper.append(componentDis)
			subDamper.append(componentVelocity)
			'damper:[3] damperFullName; [4] damperRequestName; [5] componentForce; [6] componentDis;'
			'damper:[7] componentVelocity; '
			damperDataUsed.append(subDamper)

	return springDataUsed,damperDataUsed #list


# getCurrentAsy()
# setDefaultCdb('private')
# setRemoveCdb('Test')
# setAddCdb('Test','E:/ADAMS/Test.cdb')
# setDefaultCdb('Test')
