

# import Car_Passability_v5

from scipy import interpolate


spline_s = 0.01
wheel_angles = [0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
ts = [n for n in range(len(wheel_angles))]
fit_obj = interpolate.UnivariateSpline(ts, wheel_angles, s=spline_s)


# print(fit_wheel_angles)
# print(type(fit_wheel_angles))


import matplotlib.pyplot as plt

dt = 0.3
ts = [n*dt for n in range(int(len(wheel_angles)/dt))]
plt.plot(ts, fit_obj(ts))
plt.show()

