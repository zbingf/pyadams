import AdamsTCP
import AdamsModelTCP

import re
import urllib
import logging
import os.path
import http.server

PY_FILE_NAME = os.path.basename(__file__).replace('.py', '')
LOG_PATH = PY_FILE_NAME+'.log'
logger = logging.getLogger(PY_FILE_NAME)
logging.basicConfig(level=logging.INFO)

class AjaxHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        # 计算返回数据
        data = callback(self.path)

        content = data[0]
        contentType = data[1]
        self.send_response(200)
        self.send_header("Content-type", contentType)
        self.end_headers()
        self.wfile.write(content)


def AjaxHandlerCallbackFunc(path):

    content     = b"None"
    contentType = "text/plain"
    path = urllib.parse.unquote(path) # 解析
    logger.info(f'AjaxHandlerCallbackFunc: {path}')

    if path == '/': 
        # 首页
        f = open('pyGUI.html','rb')
        content = f.read()
        contentType = 'text/html'
        f.close()

    elif path == '/favicon.ico':
        # 
        f = open('img/favicon.ico','rb')
        content = f.read()
        contentType = 'image/png'
        f.close()

    else:
        reg1 = re.match(r'^/(\w*)\s(.*)', path)  # 主页
        reg2 = re.match(r'^/htmls/(\w*)\s(.*)', path) # 次页
        isIntype = False
        typeModels = ['cmd', 'query', 'model', 'python']
        # print(path)
        if reg1:
            if reg1.group(1).lower() in typeModels:
                pathType = reg1.group(1)
                pathData = reg1.group(2)
                content = pathTcp(pathType=pathType, pathData=pathData)
                isIntype = True

        elif reg2:
            if reg2.group(1).lower() in typeModels:
                pathType = reg2.group(1)
                pathData = reg2.group(2)
                content  = pathTcp(pathType=pathType, pathData=pathData)
                isIntype = True

        if isIntype == False:
            (content, contentType) = pathGET(path)
    
    # type(content) is byte
    return (content, contentType)

def pathGET(dataStr):
    try:
        reg1=re.match(r'^[/]?(.*)$',dataStr).group(1)
        f=open(reg1,'rb')
        content=f.read()
        f.close()
        fileType=reg1.split('.')[-1]
        if fileType.lower()=='css':
            contentType='text/css'
        elif fileType.lower() in ['ico','jpg','png']:
            contentType='image/png'
        elif fileType.lower()=='js':
            contentType='text/javascript'
        elif fileType.lower()=='html':
            contentType='text/html'
        return (content,contentType)
    except:
        return (dataStr.encode(),'text/plain')

def pathTcp(pathType,pathData):
    if pathType=='cmd':
        data_recv=AdamsTCP.cmdSend(cmds=pathData,typeIn='cmd')
    elif pathType=='query':
        data_recv=AdamsTCP.cmdSend(cmds=pathData,typeIn='query')
    elif pathType=='model':
        data_recv=AdamsModelTCP.modelChoose(pathData)
    elif pathType=='python':
        data_recv=b'None'
    return data_recv #byte


# 回调
def callback(path):
    return AjaxHandlerCallbackFunc(path)


# 运行
def run(PORT=8080, localhost='127.0.0.1'):
    try:
        # callback = AjaxHandlerCallbackFunc
        server = http.server.HTTPServer((localhost, PORT), AjaxHandler)
        logger.info(f"\nHTTP server is starting at :\n\t {localhost}:{PORT}")
        logger.info("Press Ctrl+C to quit")
        # print(f"\nHTTP server is starting at :\n\t {localhost}:{PORT}")
        # print("Press Ctrl+C to quit") 
        server.serve_forever()

    except KeyboardInterrupt:
        logger.info("^Shutting down server...")
        # print("^Shutting down server...")
        server.socket.close()


if __name__ == '__main__':

    run()