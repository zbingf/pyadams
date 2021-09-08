
# road 路面创建
## rdf_road 主文件
可进行路面生成、拼接等操作，适用于pac、ftire等轮胎模型
调用模块：
	scipy.spatial.Delaunay
	numpy

### 拼接
+ Delaunay算法拼接路面
+ X向路面拼接，按顺序从负数至正进行拼接
+ Y向路面拼接，按顺序从负数至正进行拼接

### 路面生成类型
+ 圆井盖路面
	
+ 根据中心线生成（自定义宽度、AngleZ倾角）
	+ 搓板（sin）路
	+ 深坑路


