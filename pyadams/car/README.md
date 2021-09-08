# pyadams.car
## 蛇行试验 post_handle_s.py 
主要接口数据

### 前缀
+ 图像格式: #crc_名称#
    + 例如: #crc_侧向位移#  、 #crc_车速# 
+ 数值格式: $crc_名称$
    + 例如: $crc_R0$ 

### 各图像名称
|  名称              | 含义                |
|  ----              | ----              |
| 侧向位移           |  _                   | 
| 横摆角速度         |  _                | 
| 侧向加速度      | _                  | 
| 方向盘转角             |  _              | 
| 侧倾角               |  _         |
| 车速               |  _         |



### 数值数据
|  名称              | 含义                |
|  ----              | ----              |
| st   | 平均峰值方向盘转角deg           |
| yacc | 平均侧向加速度m/s^2             |
| yawv | 平均峰值横摆角速度deg/(m/s^2)   |
| xv   | 平均车速km/h                   |
| roll | 平均侧倾角deg                  |
| mass | 预估质量kg                     |


### 评价数据
|  名称              | 含义                |
|  ----              | ----              |
| N_r | 平均横摆角速度峰值 | 
| N_theta | 平均方向盘转角峰值 | 
| 标桩间距 | 标桩间距 | 
| v_base | 基准车速 | 
| 车辆类别 | 车辆类别 |



## 稳态回转 post_handle_crc.py 
主要接口数据

### 前缀
+ 图像格式: #crc_名称#
    + 例如: #crc_侧向位移#  、 #crc_车速# 
+ 数值格式: $crc_名称$
    + 例如: $crc_R0$ 

### 各图像名称
|  名称              | 含义                |
|  ----              | ----              |
| 侧向位移           |  _                   | 
| 横摆角速度         |  _                | 
| 前后侧偏角差值      | _                  | 
| 侧倾角             |  _              | 
| 车速               |  _         |



### 数值数据
|  名称              | 含义                |
|  ----              | ----              |
| R0                 | 初始转弯半径        |
| mid_steer_point    | 中性转向点         |
| U_2acc             | 2m/s^2 不足转向度   |
| rollDisK_2acc      | 2m/s^2 侧倾度      |
| rollDis_04g        | 0.4g侧倾角          |
| mass               | 估算整车质量        |
| max_lateralAcc     | 最大侧向加速度       |
| steerWheelDis      | 方向盘转角          |
| L                  | 轴距               |
| max_xv             | 最大车速            |

### 评价数据
|  名称              | 含义                |
|  ----              | ----              |
| N_u                |  不足转向度评价     |
| N_r                |  侧倾度评价         |
| N_m                |  中性转向点评价     |
| 车辆类别            |  -                 |


### json数据
score_data = {
    'N_u' : N_u,    0.2g 不足转向度 评价
    'N_r' : N_r,    0.2g 车身侧倾度 评价
    'N_m' : N_m,    中性转向 评价
    '车辆类别' : 车辆类别,
}
crc_data = {
    'R0'                : R0, 
    'mid_steer_point'   : abs(lateralAcc[mid_steer_acc_loc]),
    'U_2acc'            : U_2acc,
    'rollDisK_2acc'     : abs(rollDisK_2acc),
    'rollDis_04g'       : abs(rollDis_04g),
    'mass'              : mean_mass,
    'max_lateralAcc'    : max_lateralAcc,
    'steerWheelDis'     : abs(mean_steerWheelDis),
    'L'                 : L,
    'max_xv'            : max(abs(xV)),
    }
data_plot = {
    'xDis':xDis, 
    'yDis':yDis, 
    'lateralAcc':lateralAcc, 
    'yawV':yawV, 
    'delta_a':delta_a, 
    'rollDis':rollDis, 
    'xV':xV
    } # 图片list数据










