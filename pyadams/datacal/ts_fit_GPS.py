
# GPS数据数据匹配


# 输入数据 : 
# 		目标: t list, 经度 list, 维度 list
#  		计算: t list, 经度 list, 维度 list
# 输出数据 : 时间范围
# 			[[start,end], [start,end]]

# 调整参数 : 时间偏差允许范围 t_range, 经度维度位置允许范围 dis_range

"""
1 目标数据的首尾部经纬度
	data_target [longitude, latitude, t_tar_d]

2 获取计算数据的首点经纬度 list位置 [int,,] loc_starts
3 获取计算数据的末点经纬度 list位置 [int,,] loc_ends

4 区间确保: loc_starts[0] < loc_ends[0+n]
	根据首末确认时间
		t_cal_d = t_cal[loc_ends[0+n]] - t_cal[loc_starts[0]]
		abs(t_cal_d - t_tar_d) < t_range
	
	数据均在范围内则: return [loc_start, loc_end], [t_start, t_end]
	否则: return False

5 

6


*1 经纬度坐标点判断
	dis = ((long_tar-long_cal)**2 + (lat_tar-lat_cal)**2)**0.5
	if dis < dis_range:
		return ture

*2 
""" 




