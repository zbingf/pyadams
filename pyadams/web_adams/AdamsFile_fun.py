import os,sys,time,re,glob,pathlib,math
import AdamsFile
'''
	调用 AdamsFile
	不调用 AdamsTCP
'''
# 	getAsyAdr(cdbName,asyName)
# 	getCdbAdr(cdbName)
# 	getAsyNames(cdbName)
# 	getCdbNames()
# 	getSpringDamperData(asyAdr)
#	getSuspensionSubAdr(asyAdr)
#	getDatabase(databasePath) 获取数据库cdb名称以及路径
#	getDatabaseAsyNames(databasePath,cdbName)
#	getDatabaseCdbAdr(databasePath,cdbName)
#	getDatabaseAsyAdr(databasePath,cdbName,asyName)

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

def getSuspensionSubAdr(asyAdr):
	cfgObj=AdamsFile.cfgFile(AdamsFile.cfgPathSearch())
	asyName='.'+os.path.split(asyAdr)[1].split('.asy')[0]
	asyObj=AdamsFile.asyFile(asyAdr)
	subData=asyObj.subsystem
	susSubAdr=[]
	for line in subData:
		if line[0]=='suspension':
			susSubAdr.append(cfgObj.convert2ap(line[3]))
	return susSubAdr

def getDatabase(databasePath):
	# databasePath=r'E:\ADAMS'
	searchPath=r'{}/*.cdb'.format(databasePath)
	# print(searchPath)
	fullSearch=glob.glob(searchPath)
	# print(fullSearch)
	cdbDict={}
	cdbNames=[]
	for line in fullSearch:
		cdbName=os.path.basename(line)[0:-4]
		cdbDict[cdbName]=line
		cdbNames.append(cdbName)
	return (cdbNames,cdbDict)
	# (cdbNames,cdbDict)=getDatabase(databasePath)


def getDatabaseAsyNames(databasePath,cdbName):
	(cdbNames,cdbDict)=getDatabase(databasePath)
	cdbPath=cdbDict[cdbName]
	searchPath=r'{}/assemblies.tbl/*.asy'.format(cdbPath)
	fullSearch=glob.glob(searchPath)
	asyNames=[]
	for path in fullSearch:
		reg=re.match('^(.*)assemblies.tbl(.*)',path).group(2)
		asyName=reg[1:-4]
		asyNames.append('.'+asyName)
		# print(asyNames)
	return asyNames

def getDatabaseCdbAdr(databasePath,cdbName):
	cdbAdr=databasePath+'/'+cdbName+'.cdb'
	return cdbAdr

def getDatabaseAsyAdr(databasePath,cdbName,asyName):
	asyAdr=databasePath+'/'+cdbName+'.cdb/assemblies.tbl/'+asyName.split('.')[-1]+'.asy'
	return asyAdr







# databasePath=r'E:\ADAMS'
# (cdbNames,cdbDict)=getDatabase(databasePath)
# cdbName=cdbNames[-1]
# asyNames=getDatabaseAsyNames(databasePath,cdbName)
# print(asyNames)
# print(getDatabaseAsyAdr(databasePath,cdbName,asyNames[0]))
# print(getDatabaseCdbAdr(databasePath,cdbName))
# print(getSuspensionSubAdr(getDatabaseAsyAdr(databasePath,cdbName,asyNames[0])))






