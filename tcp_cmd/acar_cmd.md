
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




