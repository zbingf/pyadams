"""
    TCP-CAR
    SELECT-REQ
"""

# 标准库
import tkinter as tk
import math
# from pprint import pprint, pformat

# 自建库
from tcp_car import *
import tcp_cmd_fun as tcmdf


# ----------
req_filter = json_read(ACAR_REQUEST_PATH)
round_list = lambda list1, n: [round(v, n) for v in list1]



# req-车架受力
def get_request_frame_force(model_name):
    
    reqs = tcmdf.get_request_by_filter(model_name, req_filter['frame_force'])
    # print(reqs)
    return reqs


# req-车架受力-当前模型
def get_cur_request_frame_force():

    model_name = tcmdf.get_current_model()
    return get_request_frame_force(model_name)


# 选择目标req
def tk_req_select(reqs):
    
    window = tk.Tk()    
    n_frame = math.ceil(len(reqs)/20)
    frames = [tk.Frame(window) for n in range(n_frame)]
    for frame in frames:
        frame.pack(side='left', fill=tk.X)
    cb_list, var_list = [], []

    new_frames = []
    for loc, req in enumerate(reqs):
        if loc%20==0: frame = frames.pop(0)
        req = '.'.join(req.split('.')[-2:])
        var_n = tk.BooleanVar()
        cb_n = tk.Checkbutton(
            frame, 
            variable=var_n,
            text=req, 
            onvalue=True, 
            offvalue=False) # , width=20
        cb_n.pack(side='top', anchor='w') # side='left'
        var_n.set(True)
        cb_list.append(cb_n)
        var_list.append(var_n)
        new_frames.append(frame)

    window.mainloop()
    
    values = [var.get() for var in var_list]
    # window.destroy()
    new_reqs = [req for req, v in zip(reqs, values) if v]
    # print(window, var_list)
    # print(new_reqs)
    return new_reqs


# 选择当前
def tk_select_cur_res_frame_force():

    return tk_req_select(get_cur_request_frame_force())



# ------------------------------------------------
# --------------------TEST------------------------



def test_req_select():
    reqs = tk_req_select(get_cur_request_frame_force())
    if not reqs: return 
    
    for req in reqs:
        result = tcmdf.get_request_data_one(req)
        print(result)
        if result['type'] == 'force':
            
            print('{},{},{},{},'.format(
                result['result_name'], 
                *round_list(result['i_loc'], 2)
                )
            )
    # print(reqs)



if __name__=='__main__':

    test_req_select()