import os,re,glob
import AdamsFile
'''
	调用AdamsFile

'''


def fileDeleteLine(targetAdr,newAdr,reStr):
	with open(targetAdr,'r') as fileId:
		fileData=fileId.readlines()
	loc=0
	locDel=[]
	for line in fileData:
		if re.match(reStr,line):
			locDel.append(loc)
		loc+=1

	for n in range(1,len(locDel)+1):
		del fileData[locDel[-n]]

	with open(newAdr,'w') as fileId:
		for line in fileData:
			line2=line.replace('\n','',-1)
			print(line2,file=fileId)
	print('fileDeleteLine end')


def subGeomDelete(subPath):
	subAdr=glob.glob(subPath+'\\*.sub')
	for line in subAdr:
		fileDeleteLine(line,line,'(\s*)((EXTERNAL_GEOMETRY_FILE)|(external_geometry_file))(\s*)')


def deleteUnusedCdb(cfgAdr):
	fileDeleteLine(cfgAdr,cfgAdr,'(\s*)!(\s*)((DATABASE)|(database))(\s*)')

# test ------------------------------------------------------------------------

# subPath=r'E:\ADAMS\Test.cdb\subsystems.tbl'
# subGeomDelete(subPath)

