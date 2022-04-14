
# ADAMS cmd命令


## command_server 


command_server show
    | var set var=.mdi.command_server.pydummy real = (eval(run_python_code('import mdi.command_server as command_server')))
    | var set var=.mdi.command_server.py_dummy_cl real=(eval(run_python_code('command_server.listener_dialog.show()')))



command_server start
    | var set var=.mdi.command_server.pydummy real = (eval(run_python_code('import mdi.command_server as command_server')))
    | var set var=.mdi.command_server.py_dummy_cl real=(eval(run_python_code('command_server.listener_dialog.start_clicked()')))


command_server stop
    | var set var=.mdi.command_server.pydummy real = (eval(run_python_code('import mdi.command_server as command_server')))
    | var set var=.mdi.command_server.py_dummy_cl real=(eval(run_python_code('command_server.listener_dialog.stop_clicked()')))



# 启动command_server 
```
command_server start

```

# 调用外部程序

```
var set var=.mdi.command_server.pydummy real = (eval(run_python_code('import os')))
var set var=.mdi.command_server.py_dummy_cl real=(eval(run_python_code('os.popen("temp.txt")')))
```


# 终止command_server
```
command_Server stop
```



# K&C
```
acar files assembly open &
assembly_name="#asy_path#" 


acar analysis suspension parallel_travel submit &
assembly=.#model_name# &
output_prefix="K_and_C_P" &
nsteps=#p_step# &
bump_disp=#p_bump# &
rebound_disp=#p_rebound# &
&
steering_input=angle &
vertical_setup=wheel_center_height &
vertical_input=wheel_center_height &
vertical_type=absolute &
comment="" &
analysis_mode=#mode# &
log_file=yes 


acar analysis suspension opposite_travel submit &
assembly=.#model_name# &
output_prefix="K_and_C_O" &
nsteps=#o_step# &
bump_disp=#o_bump# &
rebound_disp=#o_rebound# &
&
steering_input=angle &
vertical_setup=wheel_center_height &
vertical_input=wheel_center_height &
vertical_type=absolute &
coordinate_system=vehicle &
comment="" &
analysis_mode=#mode# &
log_file=yes 


 acar analysis suspension static_load submit &
 assembly=.#model_name# &
 output_prefix="K_and_C_brake" &
  nsteps=#brake_step# &
  analysis_mode=#mode# &
  comment="" &
  log_file=yes &
  coordinate_system=vehicle &
  steering_input=angle &
  vertical_setup=wheel_center_height &
  vertical_input=wheel_center_height &
  vertical_type=absolute &
  brake_for_upr_l=#brake_left_upper# &
  brake_for_upr_r=#brake_right_upper# &
  brake_for_lwr_l=#brake_left_lower# &
  brake_for_lwr_r=#brake_right_lower#


 acar analysis suspension static_load submit &
 assembly=.#model_name# &
 output_prefix="K_and_C_damage" &
  nsteps=#damage_step# &
  analysis_mode=#mode# &
  comment="" &
  log_file=yes &
  coordinate_system=vehicle &
  steering_input=angle &
  vertical_setup=wheel_center_height &
  vertical_input=wheel_center_height &
  vertical_type=absolute &
  damage_rad_l=0 &
  damage_rad_r=0 &
  damage_for_upr_l=#damage_left_upper# &
  damage_for_upr_r=#damage_right_upper# &
  damage_for_lwr_l=#damage_left_lower# &
  damage_for_lwr_r=#damage_right_lower#


 acar analysis suspension static_load submit &
 assembly=.#model_name# &
 output_prefix="K_and_C_align" &
  nsteps=#align_step# &
  analysis_mode=#mode# &
  comment="" &
  log_file=yes &
  coordinate_system=vehicle &
  steering_input=angle &
  vertical_setup=wheel_center_height &
  vertical_input=wheel_center_height &
  vertical_type=absolute &
  align_tor_upr_l=#align_left_upper# &
  align_tor_upr_r=#align_right_upper# &
  align_tor_lwr_l=#align_left_lower# &
  align_tor_lwr_r=#align_right_lower#

```



# 悬架仿真模块
## Static Load
    | !
    | !  Adams Car
    | !  Copyright (C) 2017 MSC Software Corporation
    | !  All Rights Reserved.
    | !
    | !*******************************************************************
    | !
    | ! $assembly:t=model
    | ! $variant:t=string:d=""
    | ! $output_prefix:t=string
    | ! $nsteps:t=integer:u=10:gt=0
    | ! $steer_upper:t=real:d=0
    | ! $steer_lower:t=real:d=0
    | ! $steering_input:t=list(length,angle):u=length
    | ! $vertical_setup:t=list(contact_patch_height,wheel_center_height):d=wheel_center_height
    | ! $vertical_input:t=list(contact_patch_height,wheel_center_height,wheel_vertical_force,wheel_delta_vertical_force,length,force):d=wheel_center_height
    | ! $vertical_type:t=list(absolute,relative,none):d=absolute
    | ! $align_tor_upr_l:t=real:d=0:C=1,2
    | ! $align_tor_upr_r:t=real:d=0:C=1,2
    | ! $align_tor_lwr_l:t=real:d=0:C=1,2
    | ! $align_tor_lwr_r:t=real:d=0:C=1,2
    | ! $otm_upr_l:t=real:d=0:C=1,2
    | ! $otm_upr_r:t=real:d=0:C=1,2
    | ! $otm_lwr_l:t=real:d=0:C=1,2
    | ! $otm_lwr_r:t=real:d=0:C=1,2
    | ! $roll_res_tor_upr_l:t=real:d=0:C=1,2
    | ! $roll_res_tor_upr_r:t=real:d=0:C=1,2
    | ! $roll_res_tor_lwr_l:t=real:d=0:C=1,2
    | ! $roll_res_tor_lwr_r:t=real:d=0:C=1,2
    | ! $damage_rad_l:t=real:d=0:C=1,2
    | ! $damage_rad_r:t=real:d=0:C=1,2
    | ! $damage_for_upr_l:t=real:d=0:C=1,2
    | ! $damage_for_upr_r:t=real:d=0:C=1,2
    | ! $damage_for_lwr_l:t=real:d=0:C=1,2
    | ! $damage_for_lwr_r:t=real:d=0:C=1,2
    | ! $verti_for_upr_l:t=real:d=0:C=1,2
    | ! $verti_for_upr_r:t=real:d=0:C=1,2
    | ! $verti_for_lwr_l:t=real:d=0:C=1,2
    | ! $verti_for_lwr_r:t=real:d=0:C=1,2
    | ! $later_for_upr_l:t=real:d=0:C=1,2
    | ! $later_for_upr_r:t=real:d=0:C=1,2
    | ! $later_for_lwr_l:t=real:d=0:C=1,2
    | ! $later_for_lwr_r:t=real:d=0:C=1,2
    | ! $brake_for_upr_l:t=real:d=0:C=1,2
    | ! $brake_for_upr_r:t=real:d=0:C=1,2
    | ! $brake_for_lwr_l:t=real:d=0:C=1,2
    | ! $brake_for_lwr_r:t=real:d=0:C=1,2
    | ! $drivn_for_upr_l:t=real:d=0:C=1,2
    | ! $drivn_for_upr_r:t=real:d=0:C=1,2
    | ! $drivn_for_lwr_l:t=real:d=0:C=1,2
    | ! $drivn_for_lwr_r:t=real:d=0:C=1,2
    | ! $comment:t=string:c=0:d=""
    | ! $log_file:t=list(yes,no):u=yes
    | ! $coordinate_system:t=list(vehicle,iso):d=vehicle
    | ! $analysis_mode:t=list(interactive,graphical,background,files_only):d=interactive
    | ! $error_variable:t=variable:d=.ACAR.variables.errorFlag
    | !
    | !END_OF_PARAMETERS
    | !
    | if condition=(!str_is_space("$variant"))
    |    variable set variable=$error_variable integer=(eval(switch_assy_variant($assembly, "$variant")))
    | end
    | !
    | if condition=($error_variable)
    |    return
    | end
    | !
    | if condition=(!anym($assembly.event_class.string_value == {"__MDI_SUSPENSION_TESTRIG", "__MDI_TASA_TESTRIG"}))
    |    acar assembly suspension setup &
    |     assembly=$assembly &
    |     variant=$variant &
    |     error_variable=$error_variable
    | end
    | !
    | if condition=($error_variable)
    |    return
    | end
    | !
    | acar analysis suspension static_load set_inputs &
    |  assembly=$assembly & 
    |  align_tor_upr_l=$align_tor_upr_l &
    |  align_tor_upr_r=$align_tor_upr_r &
    |  align_tor_lwr_l=$align_tor_lwr_l &
    |  align_tor_lwr_r=$align_tor_lwr_r &
    |  otm_upr_l=$otm_upr_l &
    |  otm_upr_r=$otm_upr_r &
    |  otm_lwr_l=$otm_lwr_l &
    |  otm_lwr_r=$otm_lwr_r &
    |  roll_res_tor_upr_l=$roll_res_tor_upr_l &
    |  roll_res_tor_upr_r=$roll_res_tor_upr_r &
    |  roll_res_tor_lwr_l=$roll_res_tor_lwr_l &
    |  roll_res_tor_lwr_r=$roll_res_tor_lwr_r &
    |  damage_rad_l=$damage_rad_l &
    |  damage_rad_r=$damage_rad_r &
    |  damage_for_upr_l=$damage_for_upr_l &
    |  damage_for_upr_r=$damage_for_upr_r &
    |  damage_for_lwr_l=$damage_for_lwr_l &
    |  damage_for_lwr_r=$damage_for_lwr_r &
    |  verti_for_upr_l=$verti_for_upr_l &
    |  verti_for_upr_r=$verti_for_upr_r &
    |  verti_for_lwr_l=$verti_for_lwr_l &
    |  verti_for_lwr_r=$verti_for_lwr_r &
    |  later_for_upr_l=$later_for_upr_l &
    |  later_for_upr_r=$later_for_upr_r &
    |  later_for_lwr_l=$later_for_lwr_l &
    |  later_for_lwr_r=$later_for_lwr_r &
    |  brake_for_upr_l=$brake_for_upr_l &
    |  brake_for_upr_r=$brake_for_upr_r &
    |  brake_for_lwr_l=$brake_for_lwr_l &
    |  brake_for_lwr_r=$brake_for_lwr_r &
    |  drivn_for_upr_l=$drivn_for_upr_l &
    |  drivn_for_upr_r=$drivn_for_upr_r &
    |  drivn_for_lwr_l=$drivn_for_lwr_l &
    |  drivn_for_lwr_r=$drivn_for_lwr_r &
    |  caller=$_self
    | !
    | variable set variable_name=$_self.axleCnt integer_value=1
    | !
    | variable set variable_name=$error_variable &
    |  integer_value=0
    | !
    | acar files loadcase create &
    |  loadcase=5 &
    |  file_name="static_load" &
    |  steer_upper=$steer_upper &
    |  steer_lower=$steer_lower &
    |  nsteps=$nsteps &
    |  steering_input=$steering_input &
    |  vertical_setup=$vertical_setup &
    |  vertical_input=$vertical_input &
    |  vertical_type=$vertical_type &
    |  coordinate_system=$coordinate_system &
    |  align_tor_upr_l=(eval($_self.align_tor_upr_l_var[1])) &   
    |  align_tor_upr_r=(eval($_self.align_tor_upr_r_var[1])) &
    |  align_tor_lwr_l=(eval($_self.align_tor_lwr_l_var[1])) &
    |  align_tor_lwr_r=(eval($_self.align_tor_lwr_r_var[1])) &
    |  otm_upr_l=(eval($_self.otm_upr_l_var[1])) &
    |  otm_upr_r=(eval($_self.otm_upr_r_var[1])) &
    |  otm_lwr_l=(eval($_self.otm_lwr_l_var[1])) &
    |  otm_lwr_r=(eval($_self.otm_lwr_r_var[1])) &
    |  roll_res_tor_upr_l=(eval($_self.roll_res_tor_upr_l_var[1])) &
    |  roll_res_tor_upr_r=(eval($_self.roll_res_tor_upr_r_var[1])) &
    |  roll_res_tor_lwr_l=(eval($_self.roll_res_tor_lwr_l_var[1])) &
    |  roll_res_tor_lwr_r=(eval($_self.roll_res_tor_lwr_r_var[1])) &
    |  damage_rad_upr_l=(eval($_self.damage_rad_l_var[1])) &
    |  damage_rad_upr_r=(eval($_self.damage_rad_r_var[1])) &
    |  damage_rad_lwr_l=(eval($_self.damage_rad_l_var[1])) &
    |  damage_rad_lwr_r=(eval($_self.damage_rad_r_var[1])) &
    |  damage_for_upr_l=(eval($_self.damage_for_upr_l_var[1])) &
    |  damage_for_upr_r=(eval($_self.damage_for_upr_r_var[1])) &
    |  damage_for_lwr_l=(eval($_self.damage_for_lwr_l_var[1])) &
    |  damage_for_lwr_r=(eval($_self.damage_for_lwr_r_var[1])) &
    |  verti_for_upr_l=(eval($_self.verti_for_upr_l_var[1])) &
    |  verti_for_upr_r=(eval($_self.verti_for_upr_r_var[1])) &
    |  verti_for_lwr_l=(eval($_self.verti_for_lwr_l_var[1])) &
    |  verti_for_lwr_r=(eval($_self.verti_for_lwr_r_var[1])) &
    |  later_for_upr_l=(eval($_self.later_for_upr_l_var[1])) &
    |  later_for_upr_r=(eval($_self.later_for_upr_r_var[1])) &
    |  later_for_lwr_l=(eval($_self.later_for_lwr_l_var[1])) &
    |  later_for_lwr_r=(eval($_self.later_for_lwr_r_var[1])) &
    |  brake_for_upr_l=(eval($_self.brake_for_upr_l_var[1])) &
    |  brake_for_upr_r=(eval($_self.brake_for_upr_r_var[1])) &
    |  brake_for_lwr_l=(eval($_self.brake_for_lwr_l_var[1])) &
    |  brake_for_lwr_r=(eval($_self.brake_for_lwr_r_var[1])) &
    |  drivn_for_upr_l=(eval($_self.drivn_for_upr_l_var[1])) &
    |  drivn_for_upr_r=(eval($_self.drivn_for_upr_r_var[1])) &
    |  drivn_for_lwr_l=(eval($_self.drivn_for_lwr_l_var[1])) &
    |  drivn_for_lwr_r=(eval($_self.drivn_for_lwr_r_var[1])) &
    |  caller=$_self &
    |  no_of_axle=(eval($_self.axleCnt)) & 
    |  temporary_file=yes &
    |  error_variable=$error_variable
    | if condition=($error_variable)
    |    return
    | end
    | !
    | if condition=($assembly.event_class == "__MDI_TASA_TESTRIG")
    |    variable set variable_name=$_self.axleCnt integer_value=($_self.axleCnt+1)
    |    acar files loadcase create &
    |     loadcase=5 &
    |     file_name="static_load_2" &
    |     steer_upper=$steer_upper &
    |     steer_lower=$steer_lower &
    |     nsteps=$nsteps &
    |     steering_input=$steering_input &
    |     vertical_setup=$vertical_setup &
    |     vertical_input=$vertical_input &
    |     vertical_type=$vertical_type &
    |     coordinate_system=$coordinate_system &
    |     align_tor_upr_l=(eval($_self.align_tor_upr_l_var[2])) &   
    |     align_tor_upr_r=(eval($_self.align_tor_upr_r_var[2])) &
    |     align_tor_lwr_l=(eval($_self.align_tor_lwr_l_var[2])) &
    |     align_tor_lwr_r=(eval($_self.align_tor_lwr_r_var[2])) &
    |     otm_upr_l=(eval($_self.otm_upr_l_var[2])) &
    |     otm_upr_r=(eval($_self.otm_upr_r_var[2])) &
    |     otm_lwr_l=(eval($_self.otm_lwr_l_var[2])) &
    |     otm_lwr_r=(eval($_self.otm_lwr_r_var[2])) &
    |     roll_res_tor_upr_l=(eval($_self.roll_res_tor_upr_l_var[2])) &
    |     roll_res_tor_upr_r=(eval($_self.roll_res_tor_upr_r_var[2])) &
    |     roll_res_tor_lwr_l=(eval($_self.roll_res_tor_lwr_l_var[2])) &
    |     roll_res_tor_lwr_r=(eval($_self.roll_res_tor_lwr_r_var[2])) &
    |     damage_rad_upr_l=(eval($_self.damage_rad_l_var[2])) &
    |     damage_rad_upr_r=(eval($_self.damage_rad_r_var[2])) &
    |     damage_rad_lwr_l=(eval($_self.damage_rad_l_var[2])) &
    |     damage_rad_lwr_r=(eval($_self.damage_rad_r_var[2])) &
    |     damage_for_upr_l=(eval($_self.damage_for_upr_l_var[2])) &
    |     damage_for_upr_r=(eval($_self.damage_for_upr_r_var[2])) &
    |     damage_for_lwr_l=(eval($_self.damage_for_lwr_l_var[2])) &
    |     damage_for_lwr_r=(eval($_self.damage_for_lwr_r_var[2])) &
    |     verti_for_upr_l=(eval($_self.verti_for_upr_l_var[2])) &
    |     verti_for_upr_r=(eval($_self.verti_for_upr_r_var[2])) &
    |     verti_for_lwr_l=(eval($_self.verti_for_lwr_l_var[2])) &
    |     verti_for_lwr_r=(eval($_self.verti_for_lwr_r_var[2])) &
    |     later_for_upr_l=(eval($_self.later_for_upr_l_var[2])) &
    |     later_for_upr_r=(eval($_self.later_for_upr_r_var[2])) &
    |     later_for_lwr_l=(eval($_self.later_for_lwr_l_var[2])) &
    |     later_for_lwr_r=(eval($_self.later_for_lwr_r_var[2])) &
    |     brake_for_upr_l=(eval($_self.brake_for_upr_l_var[2])) &
    |     brake_for_upr_r=(eval($_self.brake_for_upr_r_var[2])) &
    |     brake_for_lwr_l=(eval($_self.brake_for_lwr_l_var[2])) &
    |     brake_for_lwr_r=(eval($_self.brake_for_lwr_r_var[2])) &
    |     drivn_for_upr_l=(eval($_self.drivn_for_upr_l_var[2])) &
    |     drivn_for_upr_r=(eval($_self.drivn_for_upr_r_var[2])) &
    |     drivn_for_lwr_l=(eval($_self.drivn_for_lwr_l_var[2])) &
    |     drivn_for_lwr_r=(eval($_self.drivn_for_lwr_r_var[2])) &
    |     caller=$_self &
    |     no_of_axle=(eval($_self.axleCnt)) & 
    |     temporary_file=yes &
    |     error_variable=$error_variable
    |    if condition=($error_variable)
    |       return
    |    end
    | end
    | !
    | if condition=($assembly.event_class == "__MDI_TASA_TESTRIG")
    |    acar analysis suspension loadcase submit &
    |     assembly=$assembly &
    |     output_prefix=$output_prefix &
    |     output_suffix="static_load" &
    |     comment=$output_prefix &
    |     loadcase_files=(eval($_self.filename_1)),(eval($_self.filename_2)) &
    |     analysis_mode=$analysis_mode &
    |     load_results=yes &
    |     multiple_analyses=no &
    |     temporary_file=yes &
    |     log_file=no &
    |     analysis_status=$error_variable
    | else
    |    acar analysis suspension loadcase submit &
    |     assembly=$assembly &
    |     output_prefix=$output_prefix &
    |     output_suffix="static_load" &
    |     comment=$output_prefix &
    |     loadcase_files=(eval($_self.filename)) &
    |     analysis_mode=$analysis_mode &
    |     load_results=yes &
    |     multiple_analyses=no &
    |     temporary_file=yes &
    |     log_file=no &
    |     analysis_status=$error_variable 
    | end
    | !
    | !-- remove loadcase file
    | variable set variable=$_self.deleteit &
    |  integer_value=(eval(remove_file($_self.filename))) 
    | !
    | if condition=($assembly.event_class == "__MDI_TASA_TESTRIG")
    |    if condition=($log_file && $error_variable == 0)
    |       acar analysis suspension static_load log &
    |        assembly=$assembly &
    |        analysis_name="$'output_prefix'_static_load" &
    |        analysis_mode=$analysis_mode &
    |        analysis_log_file="$'output_prefix'_static_load.log" &
    |        nsteps=$nsteps &
    |        steer_upper=$steer_upper &
    |        steer_lower=$steer_lower &
    |        steering_input=$steering_input &
    |        vertical_setup=$vertical_setup &
    |        vertical_input=$vertical_input &
    |        align_tor_upr_l=(eval($_self.align_tor_upr_l_var[1])),(eval($_self.align_tor_upr_l_var[2])) &
    |        align_tor_upr_r=(eval($_self.align_tor_upr_r_var[1])),(eval($_self.align_tor_upr_r_var[2])) &
    |        align_tor_lwr_l=(eval($_self.align_tor_lwr_l_var[1])),(eval($_self.align_tor_lwr_l_var[2])) &
    |        align_tor_lwr_r=(eval($_self.align_tor_lwr_r_var[1])),(eval($_self.align_tor_lwr_r_var[2])) &
    |        verti_for_upr_l=(eval($_self.verti_for_upr_l_var[1])),(eval($_self.verti_for_upr_l_var[2])) &
    |        verti_for_upr_r=(eval($_self.verti_for_upr_r_var[1])),(eval($_self.verti_for_upr_r_var[2])) &
    |        verti_for_lwr_l=(eval($_self.verti_for_lwr_l_var[1])),(eval($_self.verti_for_lwr_l_var[2])) &
    |        verti_for_lwr_r=(eval($_self.verti_for_lwr_r_var[1])),(eval($_self.verti_for_lwr_r_var[2])) &
    |        later_for_upr_l=(eval($_self.later_for_upr_l_var[1])),(eval($_self.later_for_upr_l_var[2])) &
    |        later_for_upr_r=(eval($_self.later_for_upr_r_var[1])),(eval($_self.later_for_upr_r_var[2])) &
    |        later_for_lwr_l=(eval($_self.later_for_lwr_l_var[1])),(eval($_self.later_for_lwr_l_var[2])) &
    |        later_for_lwr_r=(eval($_self.later_for_lwr_r_var[1])),(eval($_self.later_for_lwr_r_var[2])) &
    |        brake_for_upr_l=(eval($_self.brake_for_upr_l_var[1])),(eval($_self.brake_for_upr_l_var[2])) &
    |        brake_for_upr_r=(eval($_self.brake_for_upr_r_var[1])),(eval($_self.brake_for_upr_r_var[2])) &
    |        brake_for_lwr_l=(eval($_self.brake_for_lwr_l_var[1])),(eval($_self.brake_for_lwr_l_var[2])) &
    |        brake_for_lwr_r=(eval($_self.brake_for_lwr_r_var[1])),(eval($_self.brake_for_lwr_r_var[2])) &
    |        drivn_for_upr_l=(eval($_self.drivn_for_upr_l_var[1])),(eval($_self.drivn_for_upr_l_var[2])) &
    |        drivn_for_upr_r=(eval($_self.drivn_for_upr_r_var[1])),(eval($_self.drivn_for_upr_r_var[2])) &
    |        drivn_for_lwr_l=(eval($_self.drivn_for_lwr_l_var[1])),(eval($_self.drivn_for_lwr_l_var[2])) &
    |        drivn_for_lwr_r=(eval($_self.drivn_for_lwr_r_var[1])),(eval($_self.drivn_for_lwr_r_var[2])) &
    |        comment=$comment
    |    end
    | else
    |    if condition=($log_file && $error_variable == 0)
    |       acar analysis suspension static_load log &
    |        assembly=$assembly &
    |        analysis_name="$'output_prefix'_static_load" &
    |        analysis_mode=$analysis_mode &
    |        analysis_log_file="$'output_prefix'_static_load.log" &
    |        nsteps=$nsteps &
    |        steer_upper=$steer_upper &
    |        steer_lower=$steer_lower &
    |        steering_input=$steering_input &
    |        vertical_setup=$vertical_setup &
    |        vertical_input=$vertical_input &
    |        align_tor_upr_l=(eval({$align_tor_upr_l}[1])) &
    |        align_tor_upr_r=(eval({$align_tor_upr_r}[1])) &
    |        align_tor_lwr_l=(eval({$align_tor_lwr_l}[1])) &
    |        align_tor_lwr_r=(eval({$align_tor_lwr_r}[1])) &
    |        verti_for_upr_l=(eval({$verti_for_upr_l}[1])) &
    |        verti_for_upr_r=(eval({$verti_for_upr_r}[1])) &
    |        verti_for_lwr_l=(eval({$verti_for_lwr_l}[1])) &
    |        verti_for_lwr_r=(eval({$verti_for_lwr_r}[1])) &
    |        later_for_upr_l=(eval({$later_for_upr_l}[1])) &
    |        later_for_upr_r=(eval({$later_for_upr_r}[1])) &
    |        later_for_lwr_l=(eval({$later_for_lwr_l}[1])) &
    |        later_for_lwr_r=(eval({$later_for_lwr_r}[1])) &
    |        brake_for_upr_l=(eval({$brake_for_upr_l}[1])) &
    |        brake_for_upr_r=(eval({$brake_for_upr_r}[1])) &
    |        brake_for_lwr_l=(eval({$brake_for_lwr_l}[1])) &
    |        brake_for_lwr_r=(eval({$brake_for_lwr_r}[1])) &
    |        drivn_for_upr_l=(eval({$drivn_for_upr_l}[1])) &
    |        drivn_for_upr_r=(eval({$drivn_for_upr_r}[1])) &
    |        drivn_for_lwr_l=(eval({$drivn_for_lwr_l}[1])) &
    |        drivn_for_lwr_r=(eval({$drivn_for_lwr_r}[1])) &
    |        comment=$comment
    |    end
    | end
    | !
    | variable delete variable_name=(eval(db_children($_self,"variable")))




## opposite_travel 
    | !
    | !  Adams Car
    | !  Copyright (C) 2017 MSC Software Corporation
    | !  All Rights Reserved.
    | !
    | !*******************************************************************
    | !
    | ! $assembly:t=model
    | ! $variant:t=string:d=""
    | ! $output_prefix:t=string
    | ! $nsteps:t=integer:u=10:gt=0
    | ! $bump_disp:t=real:u=0:C=1,2
    | ! $rebound_disp:t=real:u=0:C=1,2
    | ! $stat_steer_pos:t=real:d=0
    | ! $steering_input:t=list(length,angle):u=length
    | ! $vertical_setup:t=list(contact_patch_height,wheel_center_height):d=wheel_center_height
    | ! $vertical_input:t=list(contact_patch_height,wheel_center_height,length):d=wheel_center_height
    | ! $vertical_type:t=list(absolute,relative,none):d=absolute
    | ! $comment:t=string:c=0:d=""
    | ! $log_file:t=list(yes,no):u=yes
    | ! $coordinate_system:t=list(vehicle,iso):d=vehicle
    | ! $analysis_mode:t=list(interactive,graphical,background,files_only):d=interactive
    | ! $error_variable:t=variable:d=.ACAR.variables.errorFlag
    | !
    | !END_OF_PARAMETERS
    | !
    | if condition=(!str_is_space("$variant"))
    |    variable set variable=$error_variable integer=(eval(switch_assy_variant($assembly, "$variant")))
    | end
    | !
    | if condition=($error_variable)
    |    return
    | end
    | !
    | if condition=(!anym($assembly.event_class.string_value == {"__MDI_SUSPENSION_TESTRIG", "__MDI_TASA_TESTRIG"}))
    |    acar assembly suspension setup &
    |     assembly=$assembly &
    |     variant=$variant &
    |     error_variable=$error_variable
    | end
    | !
    | if condition=($error_variable)
    |    return
    | end
    | !
    | if condition=($assembly.event_class == "__MDI_TASA_TESTRIG")
    |    if condition=(rows({$bump_disp})==2)
    |       var set var=$_self.bmpval real=(eval({$bump_disp}[1])),(eval({$bump_disp}[2]))
    |    else
    |       var set var=$_self.bmpval real=$bump_disp,$bump_disp
    |    end
    |    if condition=(rows({$rebound_disp})==2)
    |       var set var=$_self.rebval real=(eval({$rebound_disp}[1])),(eval({$rebound_disp}[2])) 
    |    else
    |       var set var=$_self.rebval real=$rebound_disp,$rebound_disp
    |    end
    | end
    | variable set variable_name=$_self.axleCnt integer_value=1
    | variable set variable_name=$error_variable &
    |  integer_value=0
    | !
    | acar files loadcase create &
    |  loadcase=2 &
    |  file_name="opposite_travel" &
    |  bump_disp=(eval({$bump_disp}[1])) &
    |  rebound_disp=(eval({$rebound_disp}[1])) &
    |  nsteps=$nsteps &
    |  stat_steer_pos=$stat_steer_pos &
    |  steering_input=$steering_input &
    |  vertical_setup=$vertical_setup &
    |  vertical_input=$vertical_input &
    |  vertical_type=$vertical_type &
    |  coordinate_system=$coordinate_system &
    |  temporary_file=yes &
    |  caller=$_self &
    |  no_of_axle=(eval($_self.axleCnt)) &
    |  error_variable=$error_variable
    | if condition=($error_variable)
    |    return
    | end
    | !
    | if condition=($assembly.event_class == "__MDI_TASA_TESTRIG")
    |    variable set variable_name=$_self.axleCnt integer_value=($_self.axleCnt+1)
    |    acar files loadcase create &
    |     loadcase=2 &
    |     file_name="opposite_travel_2" &
    |     bump_disp=(eval($_self.bmpval[2])) &
    |     rebound_disp=(eval($_self.rebval[2])) &
    |     nsteps=$nsteps &
    |     stat_steer_pos=$stat_steer_pos &
    |     steering_input=$steering_input &
    |     vertical_setup=$vertical_setup &
    |     vertical_input=$vertical_input &
    |     vertical_type=$vertical_type &
    |     coordinate_system=$coordinate_system &
    |     temporary_file=yes &
    |     caller=$_self &
    |     no_of_axle=(eval($_self.axleCnt)) &   
    |     error_variable=$error_variable
    |    if condition=($error_variable)
    |       return
    |  end
    | end
    | !
    | if condition=($assembly.event_class == "__MDI_TASA_TESTRIG")
    |    acar analysis suspension loadcase submit &
    |     assembly=$assembly &
    |     output_prefix=$output_prefix &
    |     output_suffix="opposite_travel" &
    |     comment=$output_prefix &
    |     loadcase_files=(eval($_self.filename_1)),(eval($_self.filename_2)) &
    |     analysis_mode=$analysis_mode &
    |     load_results=yes &
    |     multiple_analyses=no &
    |     temporary_file=yes &
    |     log_file=no &
    |     analysis_status=$error_variable
    | else
    |    acar analysis suspension loadcase submit &
    |     assembly=$assembly &
    |     output_prefix=$output_prefix &
    |     output_suffix="opposite_travel" &
    |     comment=$output_prefix &
    |     loadcase_files=(eval($_self.filename)) &
    |     analysis_mode=$analysis_mode &
    |     load_results=yes &
    |     multiple_analyses=no &
    |     temporary_file=yes &
    |     log_file=no &
    |     analysis_status=$error_variable
    | end
    | !
    | !-- remove loadcase file
    | variable set variable=$_self.deleteit &
    |  integer_value=(eval(remove_file($_self.filename)))
    | !
    | if condition=($log_file && $error_variable == 0)
    |    acar analysis suspension log &
    |     assembly=$assembly &
    |     analysis_name="$'output_prefix'_opposite_travel" &
    |     analysis_type="Opposite Wheel Travel" &
    |     analysis_mode=$analysis_mode &
    |     analysis_log_file="$'output_prefix'_opposite_travel.log" &
    |     nsteps=$nsteps &
    |     vertical_setup=$vertical_setup &
    |     input_parameters=bump_disp,rebound_disp,stat_steer_pos,steering_input &
    |     parameter_values=("$bump_disp"),("$rebound_disp"),("$stat_steer_pos"),("$steering_input") &
    |     comment=$comment
    | end
    | !
    | variable delete variable_name=(eval(db_children($_self,"variable")))


