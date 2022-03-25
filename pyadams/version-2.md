
# pyadams v2 2021.06
+ 规则
    + 开头前缀ing : 编写中
    + lambda函数放置于代码开头, 不进行额外调用
    + 每个模块均带测试函数 test_*.py

+ run
    + admrun.py         | adm模型运行
    + cmd_link.py        | cmd命令控制adams,后台调用运行
    + tcp_link.py        | tcp连接adams
    + multirun.py       | 多进程计算
    + threadingrun.py   | 多线程计算


+ file
    文件类计算
    + file_edit.py | 常用文档处理

    + office 处理类
        + office_docx.py | word处理
        + office_xlsx.py | excel处理
    
    + adams 类
        + admfile.py | adm模型处理

        + carfile.py | car模型文件处理

        + result.py | 后处理文件

        + tdxfile.py | 轮胎文件  (未完成)

    + fem 类
        + bdf_transient_modal.py | bdf文件处理-模态叠加-前处理文件

    + tkfile.py | tk常用交互

    + test_file_module.py | 测试


+ datacal
    数据计算
    + \__init__.py | 常用数据处理函数  

    + durablecal.py | 耐久方面计算

    + freqcal.py    | 频域计算

    + tscal.py      | 时域计算

    + plot.py       | 作图

    + 算法类
        + optimization_pso.py | 优化算法-粒子群算法PSO

+ car
    adams.car模块相关应用
    + 后处理
        + post_force_load.py | 提载
        + port_handle_crc.py | 稳态回转
        + post_handle_s.py   | 蛇行

    + 文档检索
        + search_part_mass.py |  部件质量
        + search_spring_k.py  |  弹簧刚度

    + 判定
        + request_check.py    | 检查部分request

    + 迭代
        + sus_ite.py | 1/2悬架拉线位移迭代

    + 用户关联
        + cal_road_correlation.py | 用户关联


+ road
    路面相关建模
    + 