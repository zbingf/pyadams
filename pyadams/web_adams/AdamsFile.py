# 2019/5/19
# 读取Adams 相关文件
###################################################################
# 包含子函数：cfgPathSearch、batPathSearch
# 1、cfgPath=cfgPathSearch() 输出adams 配置文件 cfg 的路径
# 2、fullPath=batPathSearch(batName) adams调用文件bat 的路径检索
###################################################################
# 包含类：asyFile、subFile、cfgFile、resFile
# asyFile 装配文件处理
#	data、fileAdr、hardpoint、parameter、subsystem、testrig、solver_settings
# subFile 子系统文件处理
#	继承 asyFile
#	data(dict)、hardpoint、subHeader(dict)、fileAdr、spring、damper、bumpstop、reboundstop、bushing、parameter
# 	类方法：subHeaderRead、springRead、damperReead、bumpstopRead、reboundstopRead、bushingRead
# cfgFile 配置文件处理
#	
# resFile 后处理文件res处理
#

import re,copy,glob,time

class asyFile:
	data=dict()
	fileAdr=''
	hardpoint=[]
	parameter=[]
	subsystem=[]
	testrig=[]
	solver_settings=[]
	regType=[r'(?:\s*){}(?:\s*)=(?:\s*)\'(?:\s*)(\S*)(?:\s*)\'', # test = ' target2 '
	r'(?:\s*){}(?:\s*)=(?:\s*)(\S*)(?:\s*)', # test =  target2 
	r'(?:\s*)(\S*)(?:\s*)=(?:\s*)\'(?:\s*)(\S*)(?:\s*)\'', # target1 = ' target2 '
	r'(?:\s*)(\S*)(?:\s*)=(?:\s*)(\S*)(?:\s*)', # target1 =  target2 
	r'\$?(?:\s*){}(?:\s*):(?:\s*)(\S*)(?:\s*)', # $ test :  target2 
	]
	def __init__(self,fileAdr):
		self.fileAdr=fileAdr
		self.fileRead(fileAdr)
		self.hardpointRead()
		self.parameterRead()
		self.subsystemRead()
		self.testrigRead()
		self.solver_settingRead()
	@classmethod
	def fileRead(self,fileAdr):
		'''
		read sub file 
		'''
		fileId=open(fileAdr,'r')
		dataStr=fileId.readlines()
		fileId.close()
		reg=r'\[(\w*)\]'
		data=dict()
		temp=[]
		for line in dataStr:
			line=line.lower()
			m=re.match(reg,line)
			if m:
				if 'nameOld' in vars():
					data[nameOld].append(temp)
				nameNew=m.group(1)
				if nameNew not in data:
					data[nameNew]=[]
				temp=[]
				nameOld=nameNew
			elif re.match(r'^\$-',line):
				continue
			else:
				temp.append(line)
		data[nameNew].append(temp)
		self.data=data
	def hardpointRead(self):
		'''
		'''
		data=self.data
		reg_hp=r'(?:\s*)\'(?:\s*)(\w*)(?:\s*)\'(?:\s*)\'(?:\s*)(single|left/right|left|right)'+\
			r'(?:\s*)\'(?:\s*)(-?\d*.?\d*)(?:\s*)(-?\d*.?\d*)(?:\s*)(-?\d*.?\d*)(?:\s*)'
		hardpoint=[]
		if 'hardpoint' in data:
			for line in data['hardpoint']:
				for temp in line:
					a=re.match(reg_hp,temp)
					if a:
						hardpoint.append([a.group(1),a.group(2),a.group(3),
							a.group(4),a.group(5)])
		self.hardpoint=hardpoint
		return self.hardpoint
	def parameterRead(self):
		'''
		'''
		data=self.data
		reg_par=r'(?:\s*)\'(?:\s*)(\w*)(?:\s*)\'(?:\s*)\'(?:\s*)(single|left/right|left|right)'+\
			r'(?:\s*)\'(?:\s*)\'(?:\s*)(-?\w*)(?:\s*)\'(?:\s*)(-?\w*.?\w*\+?\w*)(?:\s*)'
		parameter=[]
		if 'parameter' in data:
			for line in data['parameter']:
				for temp in line:
					a=re.match(reg_par,temp)
					if a:
						parameter.append([a.group(1),a.group(2),a.group(3),a.group(4)])
		self.parameter=parameter
		return self.parameter
	def subsystemRead(self):
		'''
		'''
		regData=[]
		regData.append(self.regType[4].format(r'major(?:\s*)role'))
		regData.append(self.regType[4].format(r'minor(?:\s*)role'))
		regData.append(self.regType[4].format('template'))
		regData.append(self.regType[0].format('usage'))
		subsystem=self.singelParameterMatchList(tiltName='subsystem',data=self.data,regData=regData)
		self.subsystem=subsystem
		return self.subsystem
	def testrigRead(self):
		'''
		'''
		regData=[]
		regData.append(self.regType[0].format('usage'))
		testrig=self.singelParameterMatchList(tiltName='testrig',data=self.data,regData=regData)
		self.testrig=testrig

	def solver_settingRead(self):
		'''
		'''
		data=self.data
		tiltName='solver_settings'
		solver_settings=[]
		reg1=r'(?:\s*)(\w*)(?:\s*)=(?:\s*)\'?((\w*)|(\d*.?\d*))(?:\s*)\'?'
		if tiltName.lower() in data:
			for line in data[tiltName]:
				for temp in line:
					a_temp=[]
					a=re.match(reg1,temp)
					if a:
						a_temp.append(a.group(1))
						a_temp.append(a.group(2))
					solver_settings.append(a_temp)
		self.solver_settings=solver_settings
		return self.solver_settings
	@staticmethod
	def singelParameterMatchList(tiltName,data,regData):
		'''
		# input: tiltName,data,regData
		'''
		dataOut=[]
		if tiltName.lower() in data:
			for line in data[tiltName]:
				temp=[]
				for line2 in line:

					for reg in regData:
						m=re.match(reg,line2)
						if m:
							temp.append(m.group(1))
				dataOut.append(temp)
		return dataOut
	@staticmethod
	def doubleParameterMatchDict(tiltName,data,regData):
		'''
		'''
		dataOut=dict()
		if tiltName.lower() in data:
			for line in data[tiltName]:
				temp=[]
				for line2 in line:
					for reg in regData:
						m=re.match(reg,line2)
						if m:
							dataOut[m.group(1)]=m.group(2)
		return dataOut
	@staticmethod
	def symmetrySplit(dataInput,loc):
		'''
		dataInput type:list 
		'''
		len_data=len(dataInput)
		for n in range(0,len_data):
			if dataInput[n][loc] == r'left/right':
				dataInput[n][loc]='right'
				dataInput.append(copy.copy(dataInput[n]))
				dataInput[n][loc]='left'
		return dataInput


class subFile(asyFile):
	'''
	the sub file data structure is the same as asy file
	including data , hardpoint , fileAdr , parameter
	'''
	data=dict()
	hardpoint=[]
	subHeader=dict()
	fileAdr=''
	spring=[]
	damper=[]
	bumpstop=[]
	reboundstop=[]
	bushing=[]
	parameter=[]
	def __init__(self,fileAdr):
		# super(subFile,self).__init__(fileAdr)
		self.fileAdr=fileAdr
		self.fileRead(fileAdr)
		self.hardpointRead()
		self.parameterRead()
		self.subHeaderRead()
		self.springRead()
		self.damperReead()
		self.bumpstopRead()
		self.reboundstopRead()
		self.bushingRead()
	@classmethod
	def subHeaderRead(self):
		'''
		'''
		regData=[]
		for n in range(0,3):
			regData.append(self.regType[2])
		subHeader=self.doubleParameterMatchDict(tiltName='subsystem_header',data=self.data,regData=regData)
		self.subHeader=subHeader

	def springRead(self):
		'''
		'''
		regData=[]
		regData.append(self.regType[0].format('usage'))
		regData.append(self.regType[0].format('symmetry'))
		regData.append(self.regType[0].format('property_file'))
		regData.append(self.regType[0].format('value_type'))
		regData.append(self.regType[1].format('user_value'))
		spring=self.singelParameterMatchList(tiltName='nspring_assembly',data=self.data,regData=regData)
		spring=self.symmetrySplit(dataInput=spring,loc=1)
		self.spring=spring

	def damperReead(self):
		'''
		'''
		regData=[]
		regData.append(self.regType[0].format('usage'))
		regData.append(self.regType[0].format('symmetry'))
		regData.append(self.regType[0].format('property_file'))
		damper=self.singelParameterMatchList(tiltName='damper_assembly',data=self.data,regData=regData)
		damper=self.symmetrySplit(dataInput=damper,loc=1)
		self.damper=damper 

	def bumpstopRead(self):
		'''
		'''
		regData=[]
		regData.append(self.regType[0].format('usage'))
		regData.append(self.regType[0].format('symmetry'))
		regData.append(self.regType[0].format('property_file'))
		regData.append(self.regType[0].format('distance_type'))
		regData.append(self.regType[1].format('user_distance'))
		bumpstop=self.singelParameterMatchList(tiltName='bumpstop_assembly',data=self.data,regData=regData)
		bumpstop=self.symmetrySplit(dataInput=bumpstop,loc=1)
		self.bumpstop=bumpstop
	def reboundstopRead(self):
		regData=[]
		regData.append(self.regType[0].format('usage'))
		regData.append(self.regType[0].format('symmetry'))
		regData.append(self.regType[0].format('property_file'))
		regData.append(self.regType[0].format('distance_type'))
		regData.append(self.regType[1].format('user_distance'))
		reboundstop=self.singelParameterMatchList(tiltName='reboundstop_assembly',data=self.data,regData=regData)
		reboundstop=self.symmetrySplit(dataInput=reboundstop,loc=1)
		self.reboundstop=reboundstop
	def bushingRead(self):
		'''
		'''
		regData=[]
		regData.append(self.regType[0].format('usage'))
		regData.append(self.regType[0].format('symmetry'))
		regData.append(self.regType[0].format('property_file'))
		bushing=self.singelParameterMatchList(tiltName='bushing_assembly',data=self.data,regData=regData)
		bushing=self.symmetrySplit(dataInput=bushing,loc=1)
		self.bushing=bushing
class cfgFile:
	fileAdr=''
	data=[]
	database=dict()
	def __init__(self,fileAdr):
		self.fileAdr=fileAdr
		self.cfgFileRead(fileAdr)
		self.databaseRead()
	def cfgFileRead(self,fileAdr):
		fileId=open(fileAdr,'r')
		data=fileId.readlines()
		fileId.close()
		self.data=data
	def databaseRead(self):
		database=dict()
		data=self.data
		reg1=r'(?:\s*)database(?:\s*)(\S*)(?:\s*)(.*cdb)(?:\s*)'
		for line in data:
			line=line.lower()
			m=re.match(reg1,line)
			if m:
				database[m.group(1)]=m.group(2)
		self.database=database

	def convert2ap(self,dataAdr):
		'''
		'''
		dataAdr=dataAdr.lower()
		reg1=r'<(\S*)>(\S*)'
		reg2=r'mdids://(\w*)/(\S*)'
		m=re.match(reg1,dataAdr)
		m2=re.match(reg2,dataAdr)
		if m :
			cdbName=m.group(1)
			subPath=m.group(2)
		elif m2:
			cdbName=m2.group(1)
			subPath=m2.group(2)
		try:
			if subPath[0]!=r'\\' and subPath[0]!=r'/':
				subPath=r'/'+subPath
			absolutePath=self.database[cdbName]+subPath
		except:
			absolutePath=''
			print('warning :{}---{}'.format(dataAdr,cdbName))
		return absolutePath
	def convert2rp(self,dataAdr):
		'''
		'''
		dataAdr=dataAdr.lower()
		reg1=r'(?:\S*)/(\S*).cdb/(\S*)'
		m=re.match(reg1,dataAdr)
		if m:
			cdbName=m.group(1)
			subPath=m.group(2)
			relativePath=r'mdids://{}/{}'.format(cdbName,subPath)
		return relativePath
class resFile:
	fileAdr=[]
	data=[]
	dataStr=[]
	requestId=dict()
	def __init__(self,fileAdr):
		self.fileAdr=fileAdr
		self.dataRead(fileAdr)
		self.dataStrRequest()
	@classmethod
	def tiltRead(self,fileAdr):
		fileId=open(fileAdr,'r')
		dataStr=[]
		n=0
		while True:
			line=fileId.readline().lower()
			if '<stepmap' in line:
				n=1
			if r'</stepmap>' in line:
				dataStr.append(line)
				n=0
				break
			if n==1:
				dataStr.append(line)
		fileId.close()
		self.dataStr=dataStr

	def dataRead(self,fileAdr):
		fileId=open(fileAdr,'r')
		data=[]
		dataStr=[]
		n=0
		while True:
			line=fileId.readline().lower()
			if '<stepmap' in line:
				n=1
			if r'</stepmap>' in line:
				dataStr.append(line)
				n=0
				break
			if n==1:
				dataStr.append(line)
		self.dataStr=dataStr
		while  True:
			line=fileId.readline().lower()
			if '<step' in line:
				data_n=[]
				while True:
					line2=fileId.readline().lower()
					if '</step>' in line2:
						break
					d1=line2.replace('\n','')
					d2=d1.split(' ')
					data_n.extend(d2)
				data.append(data_n)
			if '</analysis>' in line:
				break
		fileId.close()
		self.data=data

	def dataStrRequest(self):
		dataStr=self.dataStr
		reg=r'^<Entity name="(.*)"(?:\s*)entity="(.*)"(?:\s*)entType="Request"(?:\s*)objectId="([0-9]*)">'.lower()
		reg2=r'^<Component name="([0-9a-z_]*)"(?:.*)id="([0-9]*)"(?:.*)/>'.lower()
		n=0
		requestId=dict()
		for line in dataStr:
			a=re.match(reg,line)
			b=re.match(reg2,line)
			if a:
				entityName=a.group(1)
				n=1
			if b and (n==1):
				componentNmae=b.group(1)
				locId=b.group(2)
				requestId[entityName+'.'+componentNmae]=int(locId)
			if r'<entity>' in line:
				n=0
				entityName=[]
		self.requestId=requestId

	def resResearch(self,request,component):
		data=self.data
		requestId=self.requestId
		dataId=[]
		dataOut=[]
		for n in range(0,len(request)):
			keyName=request[n]+'.'+component[n]
			try:
				dataId.append(requestId[keyName])
			except:
				print('warning :{}'.format(keyName))
		for n in dataId:
			n1=n-1
			temp=[]
			for n2 in range(0,len(data[:])):
				temp.append(float(data[n2][n1]))
			dataOut.append(temp)
		return dataOut
	def simTimeGet(self):
		data=self.data
		simTime=[]
		for n in range(len(data[:])):
			simTime.append(float(data[n][0]))
		return simTime
class adamsCmd:
	@staticmethod
	def cmdStaticSimulate(asyName,simName,analysisMode):
		"""	
		AdamsFile.adamsCmd.cmdStaticSimulate(aysName=data['asyName'],simName='autoSim',
		analysisMode='interactive')
		"""
		dataOut='acar analysis full_vehicle static submit &\n'+\
		' assembly=.{} &\n'.format(asyName)+\
		' variant=default &\n'+\
		' output_prefix="{}" &\n'.format(simName)+\
		' comment="" &\n'+\
		' analysis_mode={} &\n'.format(analysisMode)+\
		' road_data_file="mdids://acar_shared/roads.tbl/2d_ssc_flat.rdf" &\n'+\
		' gear_position=0 &\n'+\
		'  &\n'+\
		'  &\n'+\
		'  &\n'+\
		'  &\n'+\
		'  &\n'+\
		'  &\n'+\
		' static_task=settle &\n'+\
		'  &\n'+\
		' linear=no &\n'+\
		'  &\n'+\
		' log_file=yes \n'
		print(dataOut)
		return dataOut

	@staticmethod
	def cmdSpringEdit(springFullName,springAdr,userValue,
			valueType,symmetric):
		"""
		AdamsFile.adamsCmd.cmdSpringEdit(springFullName=line[5],springAdr=springAdr,userValue='0',
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

## function
def cfgPathSearch():
	cfgPath=''
	for n in ['C','D','E','F','G','H','I','J']:
		cfgSearch = glob.glob(r'{}:\Users\*\.acar.cfg'.format(n))
		if cfgSearch:
			cfgPath = cfgSearch[0]
			break
	# print(cfgPath)
	return cfgPath
def batPathSearch(batName):
	fullPath=[]
	for npath in range(0,5):
		for n in ['C','D','E','F','G','H','I','J']:
			locPath=r'\*'*npath
			searchPath=r'{}:{}\MSC.Software\*\*\bin\{}.bat'.format(n,locPath,batName)
			fullSearch=glob.glob(searchPath)
			if fullSearch:
				fullPath=fullSearch[0]
				break
		if fullPath:
			break
	# print(fullPath)
	return fullPath

def isSimSuccess(resAdr,simMinute):
	''' 
	通过判断 msg 来鉴别仿真是否完结
	resAdr路径为Adams仿真路径
	simMinute 为仿真允许时间，单位 分钟min
	'''
	msgAdr=resAdr[0:-3]+r'msg'
	n=1
	isSuccess=False
	while True:
		try:
			with open(msgAdr,'r') as msgObj:
				listStr=msgObj.readlines()
				for temp in listStr:
					if 'Finished ---' in temp:
						isSuccess=True
						break
			if isSuccess:
				break
		except:
			pass
		time.sleep(1)
		n+=1
		if n>simMinute*60:
			break
	return isSuccess

# for test ############################################

#K&C





# cfgAdr=cfgPathSearch()
# batAdr=batPathSearch(batName='adams2017_2')
# print(batAdr)
# print(cfgAdr)

# cfgData=cfgFile(cfgAdr)
# print('\n\ncfgData.cfgData')
# for line in cfgData.database:
# 	print(line+' : '+cfgData.database[line])

# # path convert
# print(cfgData.convert2ap(r'<Test>/subsystems.tbl/TR_Rear_Tires.sub'))
# print(cfgData.convert2rp(cfgData.convert2ap(r'<Test>/subsystems.tbl/TR_Rear_Tires.sub')))



# # subFile test
# subAdr=r'E:\Software\MSC.Software\Adams\2017_2\acar\shared_car_database.cdb\subsystems.tbl\TR_Front_Suspension.sub'
# print('\n\nread file:{}'.format(subAdr))
# subData=subFile(subAdr)

# print('\n\nsubData.subHeader')
# for line in subData.subHeader:
# 	print(line+' = '+subData.subHeader[line])
# print('\n\nsubData.spring')
# for line in subData.spring:
# 	print(line)
# print('\n\nsubData.damper')
# for line in subData.damper:
# 	print(line)
# print('\n\nsubData.bumpstop')
# for line in subData.bumpstop:
# 	print(line)
# print('\n\nsubData.reboundstop')
# for line in subData.reboundstop:
# 	print(line)
# print('\n\nsubData.bushing')
# for line in subData.bushing:
# 	print(line)
# print('\n\nsubData.hardpoint')
# for line in subData.hardpoint:
# 	print(line)
# print('\n\nsubData.parameter')
# for line in subData.parameter:
# 	print(line)


# # asyFile test
# asyAdr=r'E:\Software\MSC.Software\Adams\2017_2\acar\shared_car_database.cdb\assemblies.tbl\MDI_Demo_Vehicle.asy'
# print('read file:{}'.format(asyAdr))
# asyData=asyFile(asyAdr)
# print('\n\nasyData.hardpoint')
# for line in asyData.hardpoint:
# 	print(line)
# print('\n\nasyData.parameter')
# for line in asyData.parameter:
# 	print(line)
# print('\n\nasyData.subsystem')
# for line in asyData.subsystem:
# 	print(line)
# print('\n\nasyData.testrig')
# for line in asyData.testrig:
# 	print(line)
# print('\n\nasyData.solver_settings')
# for line in asyData.solver_settings:
# 	print(line)

# # resFile test
# resData=resFile(r'E:\ADAMS\test_crc.res')
# data=resData.resResearch(request=['chassis_velocities'],
# 	component=['longitudinal'])

# print(max(data[0]))

# # print(locals())
# print('End')