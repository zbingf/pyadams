"""
	优化计算模块
	
	粒子群算法

	主函数: pso
"""
from functools import partial
import numpy as np

def _obj_wrapper(func, args, kwargs, x):
	return func(x, *args, **kwargs)

def _is_feasible_wrapper(func, x):
	return np.all(func(x)>=0)  # 全部≥0则返回True

def _cons_none_wrapper(x):
	return np.array([0])

def _cons_ieqcons_wrapper(ieqcons, args, kwargs, x):
	return np.array([y(x, *args, **kwargs) for y in ieqcons])

def _cons_f_ieqcons_wrapper(f_ieqcons, args, kwargs, x):
	return np.array(f_ieqcons(x, *args, **kwargs))
	
def pso(func, lb, ub, ieqcons=[], f_ieqcons=None, args=(), kwargs={}, 
		swarmsize=100, omega=0.5, phip=0.5, phig=0.5, maxiter=100, 
		minstep=1e-8, minfunc=1e-8, debug=False, processes=1,
		particle_output=False):
	"""
	Perform a particle swarm optimization (PSO)
   
	Parameters
	==========
	func : function 目标函数-最小值
		The function to be minimized
	lb : array   下限
		The lower bounds of the design variable(s)
	ub : array   上限
		The upper bounds of the design variable(s)
   
	Optional
	========
	ieqcons : list
		A list of functions of length n such that ieqcons[j](x,*args) >= 0.0 in 
		a successfully optimized problem (Default: [])
	f_ieqcons : function 约束函数
		Returns a 1-D array in which each element must be greater or equal 
		to 0.0 in a successfully optimized problem. If f_ieqcons is specified, 
		ieqcons is ignored (Default: None)
	args : tuple
		Additional arguments passed to objective and constraint functions
		(Default: empty tuple)
	kwargs : dict
		Additional keyword arguments passed to objective and constraint 
		functions (Default: empty dict)
	swarmsize : int 粒子数
		The number of particles in the swarm (Default: 100)
	omega : scalar 速度因子
		Particle velocity scaling factor (Default: 0.5)
	phip : scalar 	自身经验因子
		Scaling factor to search away from the particle's best known position
		(Default: 0.5)
	phig : scalar   全局集体经验因子
		Scaling factor to search away from the swarm's best known position
		(Default: 0.5)
	maxiter : int
		The maximum number of iterations for the swarm to search (Default: 100)
	minstep : scalar
		The minimum stepsize of swarm's best position before the search
		terminates (Default: 1e-8)
	minfunc : scalar
		The minimum change of swarm's best objective value before the search
		terminates (Default: 1e-8)
	debug : boolean
		If True, progress statements will be displayed every iteration
		(Default: False)
	processes : int
		The number of processes to use to evaluate objective function and 
		constraints (default: 1)
	particle_output : boolean
		Whether to include the best per-particle position and the objective
		values at those.
   
	Returns
	=======
	g : array  最佳参数
		The swarm's best known position (optimal design)
	f : scalar
		The objective value at ``g``
	p : array
		The best known position per particle
	pf: arrray
		The objective values at each position in p
   
	"""
	g_record = []
	fg_record = []

	assert len(lb)==len(ub), 'Lower- and upper-bounds must be the same length'
	assert hasattr(func, '__call__'), 'Invalid function handle'
	lb = np.array(lb)
	ub = np.array(ub)
	assert np.all(ub>lb), 'All upper-bound values must be greater than lower-bound values'
   
	vhigh = np.abs(ub - lb)
	vlow = -vhigh

	# Initialize objective function  目标函数初始化
	obj = partial(_obj_wrapper, func, args, kwargs)
	
	# Check for constraint function(s) #########################################
	if f_ieqcons is None:
		if not len(ieqcons):
			if debug:
				print('No constraints given.')
			cons = _cons_none_wrapper 	# 无约束目标为0
		else:
			if debug:
				print('Converting ieqcons to a single constraint function')
			cons = partial(_cons_ieqcons_wrapper, ieqcons, args, kwargs)
	else:
		if debug:
			print('Single constraint function given in f_ieqcons')
		cons = partial(_cons_f_ieqcons_wrapper, f_ieqcons, args, kwargs)
	is_feasible = partial(_is_feasible_wrapper, cons)

	# Initialize the multiprocessing module if necessary
	# 进程数
	if processes > 1:
		import multiprocessing
		mp_pool = multiprocessing.Pool(processes)
		
	# Initialize the particle swarm ############################################
	S = swarmsize 	# 粒子数
	D = len(lb)  # the number of dimensions each particle has  变量数
	x = np.random.rand(S, D)  # particle positions 变量值s
	v = np.zeros_like(x)  # particle velocities  速度s
	p = np.zeros_like(x)  # best particle positions 
	fx = np.zeros(S)  # current particle function values
	fs = np.zeros(S, dtype=bool)  # feasibility of each particle
	fp = np.ones(S)*np.inf  # best particle function values 最佳计算结果
	g = []  # best swarm position 	最小值对应参数
	fg = np.inf  # best swarm position starting value 最小值
	
	# Initialize the particle's position
	x = lb + x*(ub - lb)

	# Calculate objective and constraints for each particle
	if processes > 1:
		fx = np.array(mp_pool.map(obj, x))
		fs = np.array(mp_pool.map(is_feasible, x))
	else:
		# 单线程计算
		for i in range(S):
			fx[i] = obj(x[i, :]) # 计算结果
			fs[i] = is_feasible(x[i, :]) # 约束函数 符合约束函数计算结果≥0 则返回 True
	   
	# Store particle's best position (if constraints are satisfied)
	i_update = np.logical_and((fx < fp), fs) # 结算结果 < 当前最佳计算结果 且 符合约束函数则更新
	p[i_update, :] = x[i_update, :].copy() 	 # p存储各粒子最佳x参数
	fp[i_update] = fx[i_update] 			 # fp存储各例子最佳计算结果

	# Update swarm's best position
	i_min = np.argmin(fp) # 最小值的下标
	if fp[i_min] < fg:
		fg = fp[i_min]
		g = p[i_min, :].copy()
	else:
		# At the start, there may not be any feasible starting point, so just
		# give it a temporary "best" point since it's likely to change
		g = x[0, :].copy()
	   
	# Initialize the particle's velocity 初始速度定义
	v = vlow + np.random.rand(S, D)*(vhigh - vlow)
	   
	# Iterate until termination criterion met ##################################
	it = 1
	while it <= maxiter: # 迭代开始
		rp = np.random.uniform(size=(S, D)) # 自身经验 随机因子
		rg = np.random.uniform(size=(S, D)) # 全局经验 随机因子

		# Update the particles velocities
		v = omega*v + phip*rp*(p - x) + phig*rg*(g - x)
		# Update the particles' positions
		x = x + v
		# Correct for bound violations
		maskl = x < lb
		masku = x > ub
		x = x*(~np.logical_or(maskl, masku)) + lb*maskl + ub*masku

		# Update objectives and constraints
		if processes > 1:
			fx = np.array(mp_pool.map(obj, x))
			fs = np.array(mp_pool.map(is_feasible, x))
		else:
			for i in range(S):
				fx[i] = obj(x[i, :])
				fs[i] = is_feasible(x[i, :])

		# Store particle's best position (if constraints are satisfied)
		i_update = np.logical_and((fx < fp), fs)
		p[i_update, :] = x[i_update, :].copy()
		fp[i_update] = fx[i_update]

		# Compare swarm's best position with global best position
		i_min = np.argmin(fp)
		if fp[i_min] < fg:
			if debug:
				print('New best for swarm at iteration {:}: {:} {:}'\
					.format(it, p[i_min, :], fp[i_min]))

			p_min = p[i_min, :].copy()
			stepsize = np.sqrt(np.sum((g - p_min)**2)) # 计算结果差值 均方根值

			if np.abs(fg - fp[i_min]) <= minfunc:
				print('Stopping search: Swarm best objective change less than {:}'\
					.format(minfunc))
				if particle_output:
					return p_min, fp[i_min], p, fp
				else:
					return p_min, fp[i_min], g_record, fg_record
			elif stepsize <= minstep:
				print('Stopping search: Swarm best position change less than {:}'\
					.format(minstep))
				if particle_output:
					return p_min, fp[i_min], p, fp
				else:
					return p_min, fp[i_min], g_record, fg_record
			else:
				g = p_min.copy()
				fg = fp[i_min]

		if debug:
			print('Best after iteration {:}: {:} {:}'.format(it, g, fg))
		it += 1
		g_record.append(g)
		fg_record.append(fg)

	print('Stopping search: maximum iterations reached --> {:}'.format(maxiter))
	
	if not is_feasible(g):
		print("However, the optimization couldn't find a feasible design. Sorry")
	if particle_output:
		return g, fg, p, fp  # 输出全局及粒子自身 最佳参数及结果
	else:
		return g, fg, g_record, fg_record # 输出全局 最佳参数及结果


# ====测=======================================================
# ===-试=======================================================
def test_func1(x):
	a = x[0] + 2*x[1] + 3*x[2] -19
	b = x[0] + 3*x[1] + 3*x[2]*2 - 34
	c = x[0] + 3*x[1]*2 + 3*x[2]*2 - 43
	S1 = sum([value**2 for value in [a,b,c]])
	sum_abs = abs(a)+abs(b)+abs(c)
	return S1

def test_func2(x):

	a = x[0] + 2*x[1] + 3*x[2] -19
	b = x[0] + 3*x[1] + 3*x[2]**2 - 58
	c = x[0] + 3*x[1]**2 + 3*x[2]**2 - 76

	S1 = sum([value**2 for value in [a,b,c]])
	sum_abs = abs(a)+abs(b)+abs(c)

	return S1

def f_ieqcons_1(x): # 约束函数

	return x[1]>0.5 and x[1]>2 and x[2]>3


# ===========================================================
# ===========================================================


if __name__ == '__main__':

	# print(test_func([1,3,4]))

	func = test_func2 	# 目标函数 最小值为0
	lb = [0,0,0] 		# 参数上限设定
	ub = [10,10,10] 	# 参数下限设定
	g, fg, g_record, fg_record = pso(func, lb, ub, ieqcons=[], f_ieqcons=None, args=(), kwargs={}, 
		swarmsize=200, omega=0.5, phip=0.5, phig=0.5, maxiter=100, 
		minstep=1e-8, minfunc=1e-8, debug=False, processes=1,
		particle_output=False)

	print(g, fg)
	# import matplotlib.pyplot as plt
	# plt.subplot(211)
	# plt.plot(list(range(len(g_record))), g_record)
	# # print(g_record)
	# plt.subplot(212)
	# plt.plot(list(range(len(fg_record))), fg_record)
	# plt.show()