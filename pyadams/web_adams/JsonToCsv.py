# -*- coding: utf-8 -*-
import csv,json

def JsonToCsv(jsonFileAdr,csvFileAdr):
    '''
        Json 格式文件 转化为 Csv
    '''
    with open(jsonFileAdr,'r',encoding='utf-8') as f:
        dataList=f.readlines()

    csvFileId=open(csvFileAdr,'wt',newline='')

    n=0
    for line in dataList:
        # print(line)
        data=json.loads(line)
        if n==0:
            keyObj=data.keys()
            keyList=[]
            for line in keyObj:
                keyList.append(line)
            n+=1
            lineList=[]
        else:
            lineList.append(data)

    # print(lineList)
    csvWirteId=csv.DictWriter(csvFileId,keyList)
    csvWirteId.writeheader()
    csvWirteId.writerows(lineList)

    # for line in dataList:
    #     # print(line)
    #     data=json.loads(line)
    #     if n==0:
    #         keyObj=data.keys()
    #         keyList=[]
    #         for line in keyObj:
    #             keyList.append(line)
    #         n+=1
    #         csvWirteId=csv.writer(csvFileId)
    #         # print(keyList)
    #         csvWirteId.writerow(keyList)

    #     lineList=[]
    #     for key in keyList:
    #         lineList.append(data[key])
    #     csvWirteId.writerow(lineList)

    csvFileId.close()
    # print(dataList)
    print('Json file convert to csv file successful')