# -*- coding: utf-8 -*-
'''
	频域处理模块快
	
	傅里叶变换
	PSD计算
'''
import numpy as np
from scipy import signal
import math

def fft(data,samplerate): # 暂停使用
	'''
		暂停使用
		快速傅里叶变换
		输入：simTime,data  （numpy）
	
	'''
	# timediff=np.diff(simTime)
	timestep= 1.0/samplerate
	# round(timediff[timediff>0][0],5)

	fft_data=np.fft.fft(data)
	freq=np.fft.fftfreq(simTime.size,d=timestep)
	loc=freq>=0
	fft_y=abs(fft_data[loc])/len(fft_data)*2
	fft_hz=freq[loc]

	return fft_hz,fft_y

def psd(data,samplerate,nperseg=None,window='hanning'): # PSD计算
	'''
		快速傅里叶变换
		输入：
			data  （numpy）
			samplerate 采样频率
	
	'''

	if nperseg==None:
		nperseg = 2**math.ceil(math.log2(len(data))) # 向上取整
		# nperseg = 2**math.floor(math.log2(len(data))) # 向下取整

	psd_hz,psd_y = signal.welch(data,
		fs=samplerate,  # sample rate
		window=window,   # apply a Hanning window before taking the DFT
		nperseg=nperseg,        # compute periodograms of 256-long segments of x
		detrend='constant') # detrend x by subtracting the mean

	return psd_hz,psd_y

def choose_windows(name="Hanning", N=20):# 窗函数选择
	'''
		窗函数选择
		Rect/Hanning/Hamming
	'''
	if name == "Hamming":
		window = np.array([0.54 - 0.46 * np.cos(2 * np.pi * n / (N - 1)) for n in range(N)])
	elif name == "Hanning":
		window = np.array([0.5 - 0.5 * np.cos(2 * np.pi * n / (N - 1)) for n in range(N)])
	elif name == "Rect":
		window = np.ones(N)
	return window

def random_data(): # 随机数组生成 numpy
	'''
		生成随机数组
	'''
	fs = 10e3
	N = 1e5
	amp = 2*np.sqrt(2)
	freq = 1234.0
	noise_power = 0.001 * fs / 2
	time = np.arange(N) / fs
	x = amp*np.sin(2*np.pi*freq*time)
	x += np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
	# print(len(time),len(x))
	return time,x


if __name__=="__main__":
	import matplotlib.pyplot as plt

	import sys
	sys.path.append('..')
	import file.result	as result

	data_list , dic , name_channels = result.rsp_read(r'..\code_test\cuoban_acc.rsp')

	# FFT计算

	# PSD计算
	psd_hz,psd_y = psd(data_list[2],512,nperseg=None)
	psd_hz1,psd_y1 = psd(data_list[2],512,nperseg=2048)
	psd_hz2,psd_y2 = psd(data_list[2],512,nperseg=4096)
	
	print('time-len:',len(data_list[2])/512)
	print('data-len:',len(data_list[2]))
	
	# plt.subplot(211)
	# plt.subplot(212)
	plt.plot(psd_hz,psd_y)
	plt.plot(psd_hz1,psd_y1)
	plt.plot(psd_hz2,psd_y2)
	plt.legend(['PSD-None','PSD-2048','PSD-4096'])
	plt.show()

	# print(choose_windows(name="Hanning", N=20))
	# help(signal.welch)

