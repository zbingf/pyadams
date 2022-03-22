
# TCP CMD
通过TCP控制adams



# win32com 操作 word



# 结构

--------------------
	ADAMS CAR 
--------------------
	TCP CMD FUN
--------------------
	TCP CAR
+ sim-static-spring-preload预载调整
+ sim-static-only(静态计算-整车状态输出)
+ sim-brake-制动迭代
+ request数据截取
--------------------
	POST
+ post-static-only-静态计算-整车状态
	+ word list处理输出

--------------------
	Auto
+ auto_brake
+ auto_static_only
+ auto_spring_preload



# 结构

----------------------------------
	ADAMS CAR 					
----------------------------------
	TCP CMD FUN					
----------------------------------
	TCP CAR					
+ spring-preload			
+ static-only					
+ brake						
+ request-select			
--------------------		
	POST					
+ static-only				
+ brake						
							
----------------------------------
	AUTO
+ auto_brake
+ auto_static_only
+ auto_spring_preload
----------------------------------


[mermaid](https://mermaid-js.github.io/mermaid/#/flowchart)

```mermaid
flowchart TB
	
    subgraph A0[ADAMS_CAR]

    end
   
    subgraph B0[TCP_CMD_FUN]
    end

	subgraph C0[TCP_CAR]
    end

    subgraph D0[POST]
    end

    subgraph E0[AUTO]
    end
	
	A0 --tcp link--> B0

```


```mermaid
flowchart TB
	
    subgraph A0[   ADAMS_CAR   ]

    end
   
    subgraph B0[TCP_CMD_FUN]
    end

	subgraph C0[TCP_CAR]

		C1[spring-preload]
		C2[static-only]
		C3[brake]
		C4[request-select]
    end

    subgraph D0[POST]

    	D1[static-only]
    	D2[brake]
    end

    subgraph E0[AUTO]

    	E1[auto_brake]
    	E2[auto_static_only]
    	E3[auto_spring_preload]
    end
	
	A0 --tcp link--> B0
	B0 --> C0
    C0 --> D0
    D0 --> E0
    C0 --> E0
```


# 版本
version 1.12
    + 修改 get_aggregate_mass 函数
    + 
    + 