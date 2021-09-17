
def read_file(file_path): 

    # ==============================

    file_path = os.path.abspath(file_path)
    # 判定文件是否存在
    if not(os.path.isfile(file_path)): 
        print('RPC File " %s " Not Found' %file_path)
        return
    
    # 读取开头数据
    file   = open(file_path,'rb')
    r = file.read(512)

    num =  len(r)//128
    dic    = {}
    for i in range(num):
        s = i*128
        e = s + 32
        key = r[s:e]
        key = key.replace(b'\x00',b'').decode()
        if key != '' : 
            v = e+96
            value = r[e:v]
            value = value.replace(b'\x00',b'').decode()
            dic[key] = value

    
    # numHeader = int(dic['NUM_HEADER_BLOCKS'])


    # r = file.read(512*(numHeader-1))
    # num = len(r)//128 
    # for i in range(num):
    #     s = i*128
    #     e = s + 32
    #     key = r[s:e]
    #     key = key.replace(b'\x00',b'').decode()
    #     if key != '' : 
    #         v = e+96
    #         value = r[e:v]
    #         value = value.replace(b'\x00',b'').decode()
    #         dic[key] = value

    # # 开头数据解析
    # # print(dic)
    # # 通道数
    # n_channel = int(dic['CHANNELS']) 
    # # 通道名称
    # name_channels = [ dic['DESC.CHAN_{}'.format(n+1)] for n in range(n_channel)]
    # # print(name_channels)
    # # SCALE 系数
    # scales = [ float(dic['SCALE.CHAN_{}'.format(n+1)]) for n in range(n_channel)]
    # # print(scales)
    # # frame数
    # n_frame = int(dic['FRAMES'])
    # frame = int(dic['PTS_PER_FRAME'])
    # n_half_frame = int(dic['HALF_FRAMES'])
    # n_frame += n_half_frame
    # # print(n_half_frame)
    # # group
    # group = int(dic['PTS_PER_GROUP'])
    # n_group = max(1, int(frame*n_frame//group))
    # # print(frame*n_frame,group,n_group)
    # if frame*n_frame > n_group*group:
    #     n_group +=1

    # # 数据段读取并解析
    # data_list = [ [] for n in range(n_channel) ]

    # for n_g in range(n_group):
    #     for num in range(n_channel):
    #         cal_n = group
    #         if n_g == n_group-1:
    #             # 最后一段数据读取 , 并不一定完整解析
    #             if frame*n_frame < group*n_group:
    #                 cal_n = frame*n_frame - group*(n_group-1)

    #         r = file.read(group*2)
    #         data_raw = struct.unpack('h'*int(group),r)
    #         for n,temp1 in zip(data_raw,range(cal_n)):
    #             data_list[num].append(n*scales[num])

    # # data_list 各同道数据

    # # 关闭文档
    # file.close()


    return None