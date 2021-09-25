var display=String("log") //返回显示ID

function InfoGet(dataSend,functionName) //发送文档，运行functionName
{
	var xmlhttp
	if(window.XMLHttpRequest){
		xmlhttp=new XMLHttpRequest();
	}
	else{
		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP")
	}
	xmlhttp.open("GET",dataSend,true);
	xmlhttp.send();
	xmlhttp.onreadystatechange=function(){
		if(xmlhttp.readyState==4 && xmlhttp.status==200){
			data=xmlhttp.responseText
			document.getElementById(display).innerHTML=data;
			functionName(data)
		}
	}
}

// 仿真按钮调用按键
function funDesignSim()
{
	// modelName=document.getElementById("currentModel").value
	// cdbName=document.getElementById("currentDefaultCDB").value
	varName=document.getElementById("varName").value
	varRange=document.getElementById("varRange").value
	editCmd=document.getElementById("editCmd").value
	simulateCmd=document.getElementById("simulateCmd").value
	dataStr="modal designSim^:^"+varName+"^:^"+varRange+"^:^"+editCmd+"^:^"+simulateCmd
	// alert(dataStr)
	function subFun(data)
	{
		// alert(data.replace("\\n","<br>"))
		// document.getElementById("log").innerHTML=data.replace(/\\n/g,"<br>");
		document.getElementById("log").innerHTML=data.replace(/\\n/g,"<br>");
	}
	InfoGet(dataStr,subFun)
}
