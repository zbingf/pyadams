import os,sys,time,re,glob,pathlib,math
import AdamsFile,AdamsTCP
from AdamsTCP_fun import *
import numpy


# 辨识 是否有 转向
# 平行轮跳

def cmdSimPara(asyName,simName='autoSim',simStep=50,bump_disp=50,rebound_disp=-50,analysis_mode='interactive'):
	cmdStr='acar analysis suspension parallel_travel submit &\n'+\
	' assembly={} &\n'.format(asyName)+\
	' variant=default &\n'+\
	' output_prefix="{}" &\n'.format(simName)+\
	' nsteps={} &\n'.format(simStep)+\
	' bump_disp={} &\n'.format(bump_disp)+\
	' rebound_disp={} &\n'.format(rebound_disp)+\
	'  &\n'+\
	' steering_input=angle &\n'+\
	' vertical_setup=wheel_center_height &\n'+\
	' vertical_input=wheel_center_height &\n'+\
	' vertical_type=absolute &\n'+\
	' comment="" &\n'+\
	' analysis_mode={} &\n'.format(analysis_mode)+\
	' log_file=yes'
	# print(cmdStr)
	return cmdStr

def cmdSimOppo(asyName,simName='autoSim',simStep=50,bump_disp=50,rebound_disp=-50,analysis_mode='interactive'):
	cmdStr='acar analysis suspension opposite_travel submit &\n'+\
	' assembly={} &\n'.format(asyName)+\
	' variant=default &\n'+\
	' output_prefix="{}" &\n'.format(simName)+\
	' nsteps={} &\n'.format(simStep)+\
	' bump_disp={} &\n'.format(bump_disp)+\
	' rebound_disp={} &\n'.format(rebound_disp)+\
	' &\n'+\
	' steering_input=angle &\n'+\
	' vertical_setup=wheel_center_height &\n'+\
	' vertical_input=wheel_center_height &\n'+\
	' vertical_type=absolute &\n'+\
	' coordinate_system=vehicle &\n'+\
	' comment="" &\n'+\
	' analysis_mode={} &\n'.format(analysis_mode)+\
	' log_file=yes'
	# print(cmdStr)
	return cmdStr

def cmdSimSusStaticLoad(asyName,simName='autoSim',simStep=100,analysis_mode='interactive',
	steer_upper=0,steer_lower=0,
	align_tor_upr_l=0,align_tor_upr_r=0,align_tor_lwr_l=0,align_tor_lwr_r=0,
	otm_upr_l=0,otm_upr_r=0,otm_lwr_l=0,otm_lwr_r=0,
	roll_res_tor_upr_l=0,roll_res_tor_upr_r=0,roll_res_tor_lwr_l=0,roll_res_tor_lwr_r=0,
	damage_rad_l=0,damage_rad_r=0,
	damage_for_upr_l=0,damage_for_upr_r=0,damage_for_lwr_l=0,damage_for_lwr_r=0,
	verti_for_upr_l=0,verti_for_upr_r=0,verti_for_lwr_l=0,verti_for_lwr_r=0,
	later_for_upr_l=0,later_for_upr_r=0,later_for_lwr_l=0,later_for_lwr_r=0,
	brake_for_upr_l=0,brake_for_upr_r=0,brake_for_lwr_l=0,brake_for_lwr_r=0,
	drivn_for_upr_l=0,drivn_for_upr_r=0,drivn_for_lwr_l=0,drivn_for_lwr_r=0):
	cmdStr='acar analysis suspension static_load submit &\n'+\
	'assembly={} &\n'.format(asyName)+\
	'variant=default &\n'+\
	'output_prefix="{}" &\n'.format(simName)+\
	'nsteps={} &\n'.format(simStep)+\
	'analysis_mode={} &\n'.format(analysis_mode)+\
	'comment="" &\n'+\
	'log_file=yes &\n'+\
	'coordinate_system=vehicle &\n'+\
	'steer_upper={} &\n'.format(steer_upper)+\
	'steer_lower={} &\n'.format(steer_lower)+\
	'steering_input=angle &\n'+\
	'vertical_setup=wheel_center_height &\n'+\
	'vertical_input=wheel_center_height &\n'+\
	'vertical_type=absolute &\n'+\
	'align_tor_upr_l={} &\n'.format(align_tor_upr_l)+\
	'align_tor_upr_r={} &\n'.format(align_tor_upr_r)+\
	'align_tor_lwr_l={} &\n'.format(align_tor_lwr_l)+\
	'align_tor_lwr_r={} &\n'.format(align_tor_lwr_r)+\
	'otm_upr_l={} &\n'.format(otm_upr_l)+\
	'otm_upr_r={} &\n'.format(otm_upr_r)+\
	'otm_lwr_l={} &\n'.format(otm_lwr_l)+\
	'otm_lwr_r={} &\n'.format(otm_lwr_r)+\
	'roll_res_tor_upr_l={} &\n'.format(roll_res_tor_upr_l)+\
	'roll_res_tor_upr_r={} &\n'.format(roll_res_tor_upr_r)+\
	'roll_res_tor_lwr_l={} &\n'.format(roll_res_tor_lwr_l)+\
	'roll_res_tor_lwr_r={} &\n'.format(roll_res_tor_lwr_r)+\
	'damage_rad_l={} &\n'.format(damage_rad_l)+\
	'damage_rad_r={} &\n'.format(damage_rad_r)+\
	'damage_for_upr_l={} &\n'.format(damage_for_upr_l)+\
	'damage_for_upr_r={} &\n'.format(damage_for_upr_r)+\
	'damage_for_lwr_l={} &\n'.format(damage_for_lwr_l)+\
	'damage_for_lwr_r={} &\n'.format(damage_for_lwr_r)+\
	'verti_for_upr_l={} &\n'.format(verti_for_upr_l)+\
	'verti_for_upr_r={} &\n'.format(verti_for_upr_r)+\
	'verti_for_lwr_l={} &\n'.format(verti_for_lwr_l)+\
	'verti_for_lwr_r={} &\n'.format(verti_for_lwr_r)+\
	'later_for_upr_l={} &\n'.format(later_for_upr_l)+\
	'later_for_upr_r={} &\n'.format(later_for_upr_r)+\
	'later_for_lwr_l={} &\n'.format(later_for_lwr_l)+\
	'later_for_lwr_r={} &\n'.format(later_for_lwr_r)+\
	'brake_for_upr_l={} &\n'.format(brake_for_upr_l)+\
	'brake_for_upr_r={} &\n'.format(brake_for_upr_r)+\
	'brake_for_lwr_l={} &\n'.format(brake_for_lwr_l)+\
	'brake_for_lwr_r={} &\n'.format(brake_for_lwr_r)+\
	'drivn_for_upr_l={} &\n'.format(drivn_for_upr_l)+\
	'drivn_for_upr_r={} &\n'.format(drivn_for_upr_r)+\
	'drivn_for_lwr_l={} &\n'.format(drivn_for_lwr_l)+\
	'drivn_for_lwr_r={}'.format(drivn_for_lwr_r)
	return cmdStr

asyName='.mdi_front_vehicle'
simPath=getSimPath()

# # 仿真分析模块
# # 平行 ±50mm
# setDeleteRes(asyName=asyName,resName='autoSim_parallel_travel')
# setSimulateTCP(cmdSimPara(asyName=asyName))

# # 反向 ±50mm
# setDeleteRes(asyName=asyName,resName='autoSim_opposite_travel')
# setSimulateTCP(cmdSimOppo(asyName=asyName))
# # 平行 0mm
# setDeleteRes(asyName=asyName,resName='autoSim_0_parallel_travel')
# setSimulateTCP(cmdSimPara(asyName=asyName,simName='autoSim_0',simStep=10,
# 	bump_disp=0,rebound_disp=0))
# # # 纵向力 
# setDeleteRes(asyName=asyName,resName='autoSim_susBrakeSim_static_load')
# cmdStr=cmdSimSusStaticLoad(asyName=asyName,simName='autoSim_susBrakeSim',brake_for_upr_l=1000,brake_for_lwr_l=-1000,
# 	brake_for_upr_r=1000,brake_for_lwr_r=-1000)
# setSimulateTCP(cmdStr)
# # # 侧向力
# setDeleteRes(asyName=asyName,resName='autoSim_susDamageSim_static_load')
# cmdStr=cmdSimSusStaticLoad(asyName=asyName,simName='autoSim_susDamageSim',damage_for_upr_l=1000,damage_for_lwr_l=-1000,
# 	damage_for_upr_r=1000,damage_for_lwr_r=-1000)
# setSimulateTCP(cmdStr)
# # # 扭转
# setDeleteRes(asyName=asyName,resName='autoSim_susAlignSim_static_load')
# cmdStr=cmdSimSusStaticLoad(asyName=asyName,simName='autoSim_susAlignSim',align_tor_upr_l=1000,align_tor_lwr_l=-1000,
# 	align_tor_upr_r=1000,align_tor_lwr_r=-1000)
# setSimulateTCP(cmdStr)

def calLength(data):
	print(data)
	print(type(data))
	print(len(data))

resNames=['autoSim_parallel_travel','autoSim_opposite_travel','autoSim_0_parallel_travel',
	'autoSim_susBrakeSim_static_load','autoSim_susDamageSim_static_load','autoSim_susAlignSim_static_load']
resAdr=[]
for line in resNames:
	resAdr.append(simPath+'/'+line+'.res')

# # 数据读取模块


# # # 平行
# requestPara=['wheel_travel']*2 + ['left_tire_forces','right_tire_forces'] +\
# 	['toe_angle']*2 + ['camber_angle']*2 + ['wheel_travel_track']*2 +\
# 	['wheel_travel_base']*2+['caster_angle']*2+['caster_moment_arm']*2+\
# 	['kingpin_incl_angle']*2+['scrub_radius']*2+['anti_dive_braking']*2+\
# 	['anti_lift_acceleration']*2+['ride_rate']*2+['wheel_rate']*2


# componentPara=['vertical_left','vertical_right']+['normal']*2+\
# 	['left','right']*2+['track_left','track_right']+['base_left','base_right']+\
# 	['left','right']*8

# # # 反向
# requestOppo=['wheel_travel']*2 + ['left_tire_forces','right_tire_forces'] +\
# 	['toe_angle']*2 + ['camber_angle']*2 + ['wheel_travel_track']*2 +\
# 	['wheel_travel_base']*2+['caster_angle']*2+['caster_moment_arm']*2+\
# 	['kingpin_incl_angle']*2+['scrub_radius']*2+\
# 	['susp_roll_rate']+['total_roll_rate']+	['roll_center_location']

# componentOppo=['vertical_left','vertical_right']+['normal']*2+\
# 	['left','right']*2+['track_left','track_right']+['base_left','base_right']+\
# 	['left','right']*4+['suspension_roll_rate']+['total_roll_rate']+['vertical']

# # # 纵向力

# paraObj=AdamsFile.resFile(resAdr[0])
# paraData=paraObj.resResearch(requestPara,componentPara)

# oppoObj=AdamsFile.resFile(resAdr[1])
# oppoData=oppoObj.resResearch(requestOppo,componentOppo)

# calLength(requestPara)
# calLength(componentPara)
# calLength(paraData)

# calLength(requestOppo)
# calLength(componentOppo)
# calLength(oppoData)



# 0\1 轮跳 ; 2\3 轮胎侧向力
# 4\5 前束 ; 6\7 外倾角 ; 8\9 轮距
# 10\11 轴距 ; 12\13 主销后倾角 ; 14\15 主销后倾拖距
# 16\17 主销内倾角 ; 18\19 主销偏置距 ; 20\21 抗点头率
# 22\23 抗抬头率 ; 24\25 轮胎接地点垂向刚度 ; 26\27 轮心垂向刚度
# 28 悬架侧倾角刚度 29 轮胎接地点侧倾角刚度 30 侧倾中心高
# 31\32 悬架纵向刚度 ; 33 全轮距 
# 34\35 轮心侧向力

requestAll=['wheel_travel']*2 + ['left_tire_forces','right_tire_forces'] +\
	['toe_angle']*2 + ['camber_angle']*2 + ['wheel_travel_track']*2 +\
	['wheel_travel_base']*2+['caster_angle']*2+['caster_moment_arm']*2+\
	['kingpin_incl_angle']*2+['scrub_radius']*2+['anti_dive_braking']*2+\
	['anti_lift_acceleration']*2+['ride_rate']*2+['wheel_rate']*2+\
	['susp_roll_rate']+['total_roll_rate']+	['roll_center_location']+\
	['fore_aft_wheel_center_stiffness']*2+['total_track']+\
	['left_hub_forces','right_hub_forces']

componentAll=['vertical_left','vertical_right']+['normal']*2+\
	['left','right']*2+['track_left','track_right']+['base_left','base_right']+\
	['left','right']*8+\
	['suspension_roll_rate']+['total_roll_rate']+['vertical']+\
	['left','right']+['track']+\
	['lateral']*2


def readResSus(resAdr):
	susObj=AdamsFile.resFile(resAdr)
	susData=susObj.resResearch(requestAll,componentAll)
	susArr=numpy.array(susData)
	angleLoc_piToAngle=[4,5,6,7,12,13,16,17]
	angleLoc_angleToPi=[28,29]
	# 转化 弧度为角度 deg
	susArr[angleLoc_piToAngle]=susArr[angleLoc_piToAngle]*180/math.pi
	# 角刚度单位 转化为 N*mm/deg
	susArr[angleLoc_angleToPi]=susArr[angleLoc_angleToPi]/180*math.pi
	return susArr

susParaArr=readResSus(resAdr[0])
susOppoArr=readResSus(resAdr[1])
susStaticArr=readResSus(resAdr[2])
susBrakeArr=readResSus(resAdr[3])
susDamageArr=readResSus(resAdr[4])
susAlignArr=readResSus(resAdr[5])

print(max(susParaArr[4]))
print(min(susParaArr[4]))


# # 数据计算模块



# if len(cmdStr)>int(1024):
# 	print(cmdStr)



# 

# AdamsTCP.cmdSend(cmds=cmds,typeIn='cmd')


# print(isSteeringExist())


