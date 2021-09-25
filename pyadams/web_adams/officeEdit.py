# wordEdit.py
import win32com
from win32com.client import Dispatch,constants
class wordEdit:
	def __init__(self,wordAdr):
		word=win32com.client.Dispatch('Word.Application')
		word.Visible=1
		word.DisplayAlerts=0
		document=word.Documents.Open(wordAdr)
		content=document.content
		selection=word.selection

		self.word=word
		self.document=document
		self.content=content
		self.selection=selection

	def replaceEdit(self,oldList,newList):
		selection=self.selection

		def replaceStr(oldStr,newStr):
			selection.Find.ClearFormatting()
			selection.Find.Replacement.ClearFormatting()
			selection.Find.Execute(oldStr,False,False,False,False,False,True,1,True,newStr,2)

		def addPicture(oldStr,pictureAdr):
			selection.Find.ClearFormatting()
			selection.Find.Replacement.ClearFormatting()
			while True:
				selection.start=0
				if (selection.Find.Execute(oldStr,False,False,False,False,False,True,1,True,'none',0)):
					selection.text=''
					selection.InlineShapes.AddPicture(pictureAdr,False,True)
				else:
					break

		for oldStr,newStr in zip(oldList,newList):
			if oldStr[0]=='$':
				replaceStr(oldStr,newStr)
			elif oldStr[0]=='#':
				addPicture(oldStr,newStr)

		self.selection=selection

	def saveAs2(self,targetAdr):
		self.document.SaveAs2(targetAdr,12,False,'',True,'',False,False,False,False,False,15)


# 
# wordAdr=r'C:\Users\ABing\Desktop\testAuto.docx'
# oldList=['$test','$asd','#p1']
# newList=['测试','轮换',r'C:\Users\ABing\Pictures\13696314771470811891.jpg']
# targetAdr=r'C:\Users\ABing\Desktop\newAuto.docx'

# word=wordEdit(targetAdr)
# word.replaceEdit(oldList,newList)
# word.saveAs2(targetAdr)

pptAdr=r'C:\Users\ABing\Desktop\test11.pptx'
ppt=win32com.client.Dispatch('PowerPoint.Application')
ppt.Presentations.Open(pptAdr)
ppt.Visible=True
ppt.TextChange

print('end')
