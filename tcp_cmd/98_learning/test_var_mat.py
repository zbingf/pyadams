# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 20:19:37 2022

@author: zbingf
"""

from scipy.io import loadmat, savemat
import numpy as np

# mdict = {
#     "data" : {
#         "a1": [1,2,3,4],
#         "a2": "asdf",
#         "a3": [[1,2,3,4],[1,2,3,4],[1,2,3,4]],
#         "a4": np.array([[1,2,3,4],[1,2,3,4],[1,2,3,4]]),
#         },
#     }

# savemat('temp_test.mat', mdict)


# from tcp_car import *

# data = read_var(r'D:/github/pyadams/tcp_cmd/02_result/auto_brake/MDI_Demo_Vehicle_20220331_2339.brake')


import mat4py



data = mat4py.loadmat(r'D:\github\pyadams\tcp_cmd\02_result\01_auto_brake\02_data\MDI_Demo_Vehicle_20220401_2206.BraDat.mat')

