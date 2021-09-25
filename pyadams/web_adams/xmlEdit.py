# xmlEdit.py

import xml.etree.ElementTree as et
from xml.etree import ElementTree
from xml.dom import minidom

def prettify(elem):
	rough_string=ElementTree.tostring(elem,'utf-8')
	reparsed=minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent=" ")

# tree=et.ElementTree(file='test.xml')

# tree=et.parse('test.xml')
# root=tree.getroot()
# print(root.tag)
# print(root.attrib)


# for second in root:
# 	print(second.tag,second.attrib)
# 	for third in second:
# 		print(third.tag,third.attrib,third.text)



first=et.Element('braking')
second1=et.SubElement(first,'data')
second2=et.SubElement(first,'figure')
third1=et.SubElement(second2,'v60')


print(prettify(first))
# tree.write('output.xml')