
var display=String("log") //返回显示ID




// 异步
function InfoGet_true(dataSend,functionName) //发送文档，运行functionName
{
	var xmlhttp
	if(window.XMLHttpRequest)
	{
		xmlhttp=new XMLHttpRequest();
	}
	else
	{
		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP")
	}
	xmlhttp.open("GET",dataSend,true);
	xmlhttp.send();
	xmlhttp.onreadystatechange=function()
	{
		if(xmlhttp.readyState==4 && xmlhttp.status==200)
		{
			data=xmlhttp.responseText
			document.getElementById(display).innerHTML=data;
			functionName(data)
		}
	}
}
// 同步
function InfoGet_false(dataSend,functionName)
{
	var xmlhttp
	if(window.XMLHttpRequest)
	{
		xmlhttp=new XMLHttpRequest();
	}
	else
	{
		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP")
	}
	xmlhttp.open("GET",dataSend,false);
	xmlhttp.send();
	functionName(xmlhttp.responseText)
	return xmlhttp.responseText
}
function funGetSelect(strId)
{
	obj=document.getElementById(strId);
	index=obj.selectedIndex;
	data=obj.options[index].value;
	return data
}
function funEmpty(){}
// ————————————————————————————————————————————————————————————————————————————————————————————————————————
// ————————————————————————————————————————————————————————————————————————————————————————————————————————
// ————————————————————————————————————————————————————————————————————————————————————————————————————————

// 按钮 当前 回调
function funCurrent() //当前界面
{
	var buttonCurrentSend=String("query .gui.main.front.contents");
	var buttonDefaultCDBSend=String("query (eval(cdb_get_write_default()))");
	document.getElementById("currentDefaultCDB").value=InfoGet_false(buttonDefaultCDBSend,funEmpty);
	document.getElementById("currentModel").value=InfoGet_false(buttonCurrentSend,funEmpty);
}

// 按钮 更新全部 回调
function funUpdataAll()
{
	funCdbNames();
	funAsyName();
	funCurrent();
	funGetCurrentAsy();
	// document.getElementById("cdb").value=""
	// document.getElementById("cdbNames").innerHTML="<option>Detroit Lions</option><option>Detroit Pistons</option>"
}
function funCdbNames()
{
	dataStr="model funCdbNames ";
	// alert(dataStr)
	function subFun(data)
	{
		document.getElementById("log").innerHTML='success';
		document.getElementById("cdbName").innerHTML=data;
	}
	InfoGet_false(dataStr,subFun)
}
function funAsyName()
{
	dataStr="model funAsyNames ";
	cdbName=funGetSelect("cdbName");
	dataStr="model funAsyNames^:^"+cdbName;
	function subFun(data)
	{
		document.getElementById("log").innerHTML='success';
		document.getElementById("asyName").innerHTML=data;
	}
	InfoGet_false(dataStr,subFun);
}
// 设置当前界面
function funChangeCurrent()
{
	cdbName=funGetSelect("cdbName");
	asyName=funGetSelect("asyName");
	dataStr="model changeCurrent^:^"+cdbName+"^:^"+asyName;
	// alert(dataStr)
	function subFun(data)
	{
		document.getElementById("log").innerHTML='success';
	}
	InfoGet_false(dataStr,subFun);
	funGetCurrentAsy();
	funCurrent();
}
// 当前已打开文件
function funGetCurrentAsy()
{
	dataStr="model funGetCurrentAsy "
	// alert(dataStr)
	function subFun(data)
	{
		document.getElementById("log").innerHTML='success';
		document.getElementById("asyNameOpened").innerHTML=data;
	}
	InfoGet_false(dataStr,subFun)
}
// 关闭asy装配文件
function funCloseAsy()
{
	dataStr='cmd acar files assembly close assembly_name=.'+funGetSelect('asyNameOpened')
	// alert(str2)
	InfoGet_false(dataStr,funEmpty)
	funGetCurrentAsy()
}

// ————————————————————————————————————————————————————————————————————————————————————————————————————————
// ————————————————————————————————————————————————————————————————————————————————————————————————————————
// ————————————————————————————————————————————————————————————————————————————————————————————————————————
// 仿真按钮调用按键

// 按钮 运行cmd 回调
function funCmdInput()
{
	var dataCmdInput=document.getElementById("cmdInput").innerText
	// alert(dataCmdInput)
	function emptyInput(data){}
	InfoGet_true(dataCmdInput,emptyInput)
}


// 整车预载调整按钮
function funSpringPreload()
{
	funUpdataAll()
	// 输出形式
	// model steerPreload:name=$:cdb=$
	// 模型名称、cdb名
	modelName=document.getElementById("currentModel").value;
	cdbName=document.getElementById("currentDefaultCDB").value;
	// 选项 
	radios=document.getElementsByName("springPreload_simType");
	// alert(radios.length)
	// alert(modelName)
	for(var i=0;i<radios.length;i++)
	{
        if(radios[i].checked)
        {
            value = radios[i].value;
            break;
        }
    }
    springPreload_simType=value;
	// alert(springPreload_simType)

	dataStr="model springPreload^:^"+modelName+"^:^"+cdbName+"^:^"+springPreload_simType
	// alert(dataStr)
	function subFun(data)
	{
		document.getElementById("log").innerHTML=data;
	}
	InfoGet_true(dataStr,subFun)
	// alert("运行整车预载调整完毕")
}
// 转向行程计算按钮
function funSteerTravel()
{
	funUpdataAll()
	// 输出形式
	// model steerTravel:name:cdb:steerOutMax:steerInMax:steerTravelIterations:steerTravelPrecisionRange
	//  模型名、cdb名、外轮最大转角、内轮最大转角、迭代次数、转角允许偏差
	modelName=document.getElementById("currentModel").value
	cdbName=document.getElementById("currentDefaultCDB").value
	steerOutMax=document.getElementById("steerOutMax").value
	steerInMax=document.getElementById("steerInMax").value
	steerTravelIterations=document.getElementById("steerTravelIterations").value
	steerTravelPrecisionRange=document.getElementById("steerTravelPrecisionRange").value
	steerTravelGain=document.getElementById("steerTravelGain").value
	// 
	dataStr="model steerTravel^:^"+modelName+"^:^"+cdbName+"^:^"+steerOutMax+"^:^"+steerInMax+"^:^"+steerTravelIterations+"^:^"+steerTravelPrecisionRange+"^:^"+steerTravelGain
	function subFun(data)
	{
		// alert(data.replace("\\n","<br>"))
		// document.getElementById("logSteerTravel").innerHTML=data.replace(/\\n/g,"<br>");
		document.getElementById("logSteerTravel").value=data.replace(/\\n/g,"\n");
	}
	InfoGet_true(dataStr,subFun)
	// alert("转向行程校正完成")
}
// 轮跳行程
function funWheelTravel()
{
	funUpdataAll()
	// 输出形式
	// model wheelTravel:name:cdb:damperTravel:airspringTravel:wheelTravelIterations:wheelTravelPrecisionRange
	//  模型名、cdb名、减振器行程、空气弹簧行程、迭代次数、行程允许偏差
	modelName=document.getElementById("currentModel").value
	cdbName=document.getElementById("currentDefaultCDB").value
	damperTravel=document.getElementById("damperTravel").value
	airspringTravel=document.getElementById("airspringTravel").value
	wheelTravelIterations=document.getElementById("wheelTravelIterations").value
	wheelTravelPrecisionRange=document.getElementById("wheelTravelPrecisionRange").value
	wheelTravelGain=document.getElementById("wheelTravelGain").value
	// 
	dataStr="model wheelTravel^:^"+modelName+"^:^"+cdbName+"^:^"+damperTravel+"^:^"+airspringTravel+"^:^"+wheelTravelIterations+"^:^"+wheelTravelPrecisionRange+"^:^"+wheelTravelGain
	function subFun(data)
	{
		// alert(data.replace("\\n","<br>"))
		// document.getElementById("logWheelTravel").innerHTML=data.replace(/\\n/g,"<br>");
		document.getElementById("logWheelTravel").value=data.replace(/\\n/g,"\n");
	}
	InfoGet_true(dataStr,subFun)
	alert("轮跳行程校正完成")
}

function funMassAdjust()
{
	funUpdataAll()
	modelName=document.getElementById("currentModel").value
	cdbName=document.getElementById("currentDefaultCDB").value
	massW=document.getElementById("massW").value
	massIxx=document.getElementById("massIxx").value
	massIyy=document.getElementById("massIyy").value
	massIzz=document.getElementById("massIzz").value
	massMarker=document.getElementById("massMarker").value
	massPart=document.getElementById("massPart").value
	dataStr="model massAdjust^:^"+modelName+"^:^"+cdbName+"^:^"+massW+"^:^"+massIxx+"^:^"+massIyy+"^:^"+massIzz+"^:^"+massMarker+"^:^"+massPart
	// alert(dataStr)
	function subFun(data)
	{
		// alert(data.replace("\\n","<br>"))
		// document.getElementById("log").innerHTML=data.replace(/\\n/g,"<br>");
		document.getElementById("log").innerHTML=data.replace(/\\n/g,"<br>");
	}
	InfoGet_true(dataStr,subFun)
	// alert("整车质量调整完毕")
}

function funHardpointAdjust()
{
	hardpointName=document.getElementById("hardpointName").value
	hardpointLoc=document.getElementById("hardpointLoc").value
	hardpointSym=document.getElementById("hardpointSym").value
	dataStr="model hardpointAdjust^:^"+hardpointName+"^:^"+hardpointLoc+"^:^"+hardpointSym
	function subFun(data)
	{
		// alert(data.replace("\\n","<br>"))
		// document.getElementById("log").innerHTML=data.replace(/\\n/g,"<br>");
		document.getElementById("log").innerHTML=data.replace(/\\n/g,"<br>");
	}
	InfoGet_true(dataStr,subFun)
}



function funDesignSim()
{
	var num=5
	var varSplit="^n^"
	for (i = 1; i < num+1; i++)
	{ 
		subName="varName_"+String(i)
		subRange="varRange_"+String(i)
		subState="checkboxDesignSim_"+String(i)
		subSingle="checkboxSingle_"+String(i)
		if(i===1)
		{
			varName=document.getElementById(subName).value
			varRange=document.getElementById(subRange).value
			varState=document.getElementById(subState).checked
			varSingle=document.getElementById(subSingle).checked

		}
		else
		{
			varName=varName+varSplit+document.getElementById(subName).value
			varRange=varRange+varSplit+document.getElementById(subRange).value
			varState=varState+varSplit+document.getElementById(subState).checked
			varSingle=varSingle+varSplit+document.getElementById(subSingle).checked
		}

	}

	editCmd=document.getElementById("editCmd").value
	dataStr="model designSim^:^"+varName+"^:^"+varRange+"^:^"+editCmd+"^:^"+varState+"^:^"+varSingle

	function subFun(data)
	{
		// alert(data.replace("\\n","<br>"))
		// document.getElementById("log").innerHTML=data.replace(/\\n/g,"<br>");
		document.getElementById("log").innerHTML=data.replace(/\\n/g,"<br>");
	}
	InfoGet_true(dataStr,subFun)
	// alert("自定义仿真完毕")
}
