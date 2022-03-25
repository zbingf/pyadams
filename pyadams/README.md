
<!-- ## 数据结构更新  -->

# pyadams
针对ADAMS的模块，包含以下模块

## call
调用adams计算模块
+ admrun : 批处理调用 __Adams/Solve__ 运行 adm 模型文件
+ cmd_link : 批处理调用 __Adams__ 运行Adams cmd命令
+ multirun : __多进程计算__ multiprocessing 多进程计算
+ threadingrun : __多线程计算__ threading模块应用
+ tcp_link : __TCP__ 方式与Adams通信,运行Adams cmd命令

## car
Adams/Car 应用模块
+ adm_edit_leafspring: leafspring 2019版 adm编辑
+ adm_sim 		: admas/car adm模型仿真管理模块
+ cal_road_correlation : 用户关联计算模块,粒子群(PSO)算法
+ post_force_load : 后处理-载荷分解
+ post_handle_crc : 后处理-操纵稳定性-稳态回转
+ post_handle_s : 后处理-操纵稳定性-蛇行试验
+ post_tilt 	: 后处理-侧翻台架
+ request_check : request__部分__数据检查
+ search_part_mass : 检索车身子系统,获取部件质量参数
+ search_spring_k : 检索弹簧文件,计算弹簧平均刚度
+ sus_ite : 迭代-ADAMS-悬架台架迭代


## file 
文件处理模块
+ adm_post_edit : adams/car ride 整车四立柱台架模型, amd文件处理
+ admfile : ADAMS adm模型文件辨识编辑模块
+ result : 后处理文件读取, res&rsp
+ tdx_file: TDX格式文件读取, 轮胎数据
+ bdf_transient_modal : bdf文件, 模态叠加前处理,根据硬点数据,通道数据,直接生成
+ file_edit : 文档编辑\处理
+ office_docx : Word文档生成\编辑
+ office_xlsx : Excel文档生成\编辑
+ pdf_compare_pdi : pdf文件, PDI伪损伤对比生成
+ pdf_scatter_plot : pdf文件, 散点图

## datacal
数据处理模块
+ tscal : 时域数据处理
+ feqcal : 频域数据处理, psd
+ durablecal : 耐久计算模块
+ spline : 曲线
+ plot : 作图
+ optimization_pso : 优化算法, 粒子群(PSO)


## road
路面数据处理模块
+ rdf_road : rdf路面, 基础模块
+ rdf_belgian : rdf路面, 比利时路面 1.0
+ rdf_
+ RoadProject 特定路面
	+ 比利时路 1.0
	+ 螺旋翻滚路面
	+ 边坡翻滚路面

## ui
GUI模块，tkinter调用为主
+ __tk_pyadams_main__:
	+ 主运行程序,集成大部分ui

+ __tk_adm_sim__:
	+ adm文件编辑仿真

+ __tk_drv2cmd__:
	+ drv数据(RPC3格式)-转-Adams/View Cmd命令,



## view
Adams/View 应用模块,包含adams直接运行的py文件  
默认ADAMS版本: __2017.2__ , 其他版本特殊注明

+ drv2cmd:
	+ 将 __RPC3__ 格式的文件转为修改 ADAMS/spline的 __cmd__ 文件

+ view_fun     
	+ 基于Adams( _ADAMS/python_ )的子模块, 供相应的adams/python程序调用

+ rig_421_flex 
	+ adams/python 台架421创建, 加载台架上端以柔性体替代
	+ 调用 __view_fun__

+ rig_421_rev
	+ adams/python 台架421创建, 台架拆分两半  
	+ 调用 __view_fun__

+ rig_stewart_2017  
	+ adams/python 台架MAST创建, 六轴台架  
	+ 调用 __view_fun__

+ rig_stewart_2019  
	+ adams/python 台架MAST创建, 六轴台架
	+ 调用 __view_fun__ , __ADAMS version 2019__

+ rig_xyz : adams/python 台架XYZ创建, 六轴输入顺序 X、Y、Z、Rx、Ry、Rz


## code_test
用于测试的数据

## tests
测试程序模块