'''
    python version : 3.7
    Adams version : 2017.2
    
    与adams建立TCP/IP 通信
    运行命令
    
    cmd_send(cmd,type_in)  发送数据到adams
        + 单个命令运算
        + type_in共分两种 cmd 和 query
        + 输出为bytes类型
    
    cmd_convert(cmd)   将多行cmd命令处理, 1个命令1行
    
    cmds_run(cmd_str)
        + 直接运行多个未处理命令
        + 只发送 cmd 命令

    2022/3/22
'''

# 标准库
import socket
import re
import sys
import time
import glob
import math
import logging


# 连接设置
PORT=5002
LOCALHOST='127.0.0.1'
MSGLEN = 65536


# ----------
logger = logging.getLogger('tcp_link')
logger.setLevel(logging.DEBUG)
is_debug = False


class MySocket:
    """demonstration class only
      - coded for clarity, not efficiency
    """

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        """连接"""
        while 1:
            try:
                self.sock.connect((host, port))
            except Exception as e:
                print("[-]Socket Connect Error")
                #traceback.print_exc()
                time.sleep(2)
                #sys.exit(-1)
            else:
                if is_debug: logger.debug("[*]Socket Connect Success")
                break

    def mysend(self, msg):
        """数据发送"""
        # num = math.ceil(len(msg)/MSGLEN)
        # for n in range(num):
        #     self._send(msg[n*MSGLEN : (n+1)*MSGLEN])
        self._send(msg)
        if is_debug: logger.debug(f"send {msg}")

    def myreceive(self):
        chunks = []
        # num = math.ceil(msg_len/MSGLEN)
        chunk = self._receive(MSGLEN)
        chunks.append(chunk)
        while len(chunk) == MSGLEN:
            if is_debug: logger.debug(f"recv len: {len(chunk)}")
            chunk = self._receive(MSGLEN)
            chunks.append(chunk)
            # time.sleep(0.03)

        return b''.join(chunks)

    def close(self):
        self.sock.close()

    def _send(self, msg):
        sent = self.sock.send(msg)
        if sent == 0:
            raise RuntimeError("socket connection broken")
        return sent

    def _receive(self, msg_len):
        chunk = self.sock.recv(msg_len)
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        return chunk

# 
def cmd_convert(cmd_str): 
    """
        cmd数据转化
        file_path is cmd file
        1个命令1行
        返回list
    """
    new_cmd = re.sub(r'&(\s*)\n',' ',cmd_str).split('\n')
    if isinstance(new_cmd, str):
        new_cmd = [new_cmd]
    return new_cmd


def cmd_send(cmd, type_in='cmd'): # cmd 数据传送
    """
        单个命令运算
        type_in : query or cmd
        query 获取参数
        cmd 发送cmd命令
    """
    # if isinstance(cmd, str):
    #     if '&' in cmd:
    cmd = cmd_convert(cmd)
    cmd_lines = []
    for line in cmd:
        cmd_lines.append(bytes('{} {}'.format(type_in, line),encoding='utf8'))

    msocket = MySocket()
    msocket.connect(LOCALHOST, PORT)

    # recv_buff = msocket.sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) # 接收缓冲
    # print(recv_buff)

    for line in cmd_lines:
        # print('send: ', line)
        msocket.mysend(line)

    if type_in == 'query':
        query_str = msocket.myreceive().decode()
        # print('query_str: ', query_str)
        # if 'query' == query_str[:5]:
        #     print(query_str)
        msocket.mysend(b"OK")
        query_result = msocket.myreceive()
        # print(query_result)
        return query_result

    msocket.close()
    # print('>>>close')



def cmd_to_lines(cmd_str): # 多个cmd命令转化,导出cmd列表
    """
        去掉cmd中的& 符号
        将命令转化为多个单行命令
    """
    list1 = cmd_str.split('\n')
    line = []
    list2 = []
    cmd = []
    for n in list1:
        if n:
            if '&' in n:
                line.append(n)
            else:
                line.append(n)
                list2.append(' '.join(line))
                line = []
        else:
            pass
            line = []

    for line in list2:
        cmd.append(line.replace('&',' '))
    
    return cmd


def cmds_run(cmd_str): # 直接运行,未处理的多个命令行
    """
        多行运行
    """
    # 命令转化
    cmd = cmd_to_lines(cmd_str)
    for line in cmd:
        # 运行命令
        cmd_send(cmd=line, type_in='cmd')

    return 'cmd_run end'




if __name__ == '__main__':
    """
        测试
    """
    
    # print(cmd_send(cmd='eval(cdb_get_write_default())',type_in='query').decode())
    # print('adams_tcplink')
    
    # 数据转化测试
    print(cmd_convert('asdfsa&\n asdf \n'))

    print(cmd_send('.gui.main.front.contents', type_in='query').decode())

    
    # file_path=r'E:\ADAMS\temp.cmd'
    # cmd_send(cmd=cmd_convert(file_path),type_in='cmd')
