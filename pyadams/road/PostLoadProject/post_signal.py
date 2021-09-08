# ------------------------------------------------------
# 立柱位移加载信号
import matplotlib.pyplot as plt

#子函数
add_list   = lambda list1, value: [ n + value for n in list1 ]
multi_list = lambda list1, value: [ n * value for n in list1 ]


# 双线读取
def csv_read_two_lines(csv_path):
    """
        csv_path csv文件
        文件格式如下:
            left_x,left_z,right_x,right_z
            0,0,0,0
            2000,0,2000,0
            2001,-25.4,2001,-25.4
            2305,-25.4,2305,-25.4
            2306,0,2306,0
    """
    with open(csv_path, 'r') as f:
        lines_csv = [line for line in f.read().split('\n') if line]
    data = []
    len_init = None
    for loc, line in enumerate(lines_csv):
        list1 = [n for n in line.split(',') if n]
        if len_init == None:
            len_init = len(list1)
            for n in range(len_init):
                data.append([])

        if len(list1) == len_init:
            for n, value in enumerate(list1):
                if loc>0:
                    value = float(value)
                data[n].append(value)

    return data

# 线性插值计算, 获取指定位置的预估值
def cal_liner(xs, ys, x0):
    num = len(xs)
    for n in range(num):
        if x0 == xs[n]:
            return ys[n]
        if x0 > xs[n]:
            if n == num-1:
                return ys[-1]
            continue
        else:
            x1 = xs[n]
            y1 = ys[n]
            x2 = xs[n-1]
            y2 = ys[n-1]
            k = (y1-y2)/(x1-x2)
            return k*(x0-x1)+y1

# 加载信号生成
def cal_map(vel, xs, ys, time_len, samplerate=512):
    """
        vel 车速 km/h
        xs 纵向距离 mm
        ys 高度 mm
        time_len 时间 s
        samplerate 信号采样频率 Hz
    """
    vel = vel/3.6*1000
    xs[0] = 0
    time1 = multi_list(xs, 1.0/vel)
    times = [n/samplerate for n in range(time_len*samplerate)]
    output = []
    for t in times:
        output.append(cal_liner(time1, ys, t))

    return times, output




def create_post_signal(params):
    """
        创建台架加载通道
    """

    vel      = params['vel']
    x_axle   = params['x_axle']
    time_len = params['time_len']
    csv_res_path  = params['csv_res_path']
    csv_line_path = params['csv_line_path']

    # 曲线读取
    data = csv_read_two_lines(csv_line_path)

    # ------------------------------------------------------
    # 信号创建
    xs_l = data[0][1:] # 左x距离 mm
    zs_l = data[1][1:] # 左z高度 mm
    xs_r = data[2][1:] # 右x距离 mm
    zs_r = data[3][1:] # 右z高度 mm
    
    times, output_l_dic, output_r_dic = {}, {}, {}

    times, output_l_dic[0] = cal_map(vel, xs_l, zs_l, time_len)
    _, output_r_dic[0]     = cal_map(vel, xs_r, zs_r, time_len)

    titles = ['Axle_0_left(mm),Axle_0_right(mm)']
    for loc, value in enumerate(x_axle):

        _, output_l_dic[loc+1] = cal_map(vel, add_list(xs_l, value),
            zs_l, time_len)

        _, output_r_dic[loc+1] = cal_map(vel, add_list(xs_r, value),
            zs_r, time_len)

        titles.append(f'Axle_{loc+1}_left(mm),Axle_{loc+1}_right(mm)')

    # 创建文本
    with open(csv_res_path, 'w') as f:
        # 开头
        f.write('time(s),' + ','.join(titles) + '\n')
        # 数据输入
        for n in range(len(times)):
            line = [times[n]]
            for loc in range(len(titles)):
                line.append(output_l_dic[loc][n])
                line.append(output_r_dic[loc][n])

            f.write(','.join([str(v) for v in line]) + '\n')

    # ------------------------------------------------------
    # 图像显示
    fig_obj = plt.figure(1)
    n_len   = len(titles)

    ax1 = fig_obj.add_subplot(211)
    for n in range(n_len):
        ax1.plot(times, output_l_dic[n])
    ax1.set_title('left')
    ax1.set_xlabel('time(s)')

    ax2 = fig_obj.add_subplot(212)
    for n in range(n_len):
        ax2.plot(times, output_r_dic[n])
    ax2.set_title('right')
    ax2.set_xlabel('time(s)')
    fig_obj.tight_layout()

    plt.savefig(csv_res_path+'.png')
    plt.close()

    return csv_res_path
