


## 字符串判断
+ if str1 in str2
	IF(ISNUMBER(FIND(str1, str2)), 1, 0)

+ b1 if a > b else b2
	IF(a>=b, b1, b2)


## 多条件判断
IF(AND(B2=”生产”,C2=”主操”),”有”,”无”)


## 条件求和
+ SUMIF(条件区域,指定的求和条件,求和的区域)
+ SUMIF(D2:D5,F2,C2:C5)


## 条件计数
+ COUNTIF(B2:B12,E3)
+ COUNTIF(条件区域,指定条件)


## 多条件计数
+ COUNTIFS(B2:B9,F2,C2:C9,G2)
+ COUNTIFS(条件区域1,指定条件1,条件区域2,指定条件2……)

