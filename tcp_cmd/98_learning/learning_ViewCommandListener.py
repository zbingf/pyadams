# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'start_stop_dbox.ui'
#
# Created: Thu Apr 16 14:51:11 2015
# by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QApplication, QDialog
import os, threading, aview_main, time
import logging
import socket
import struct
import sys
import mdi.utl


def zprint(string):  # zbingf
    with open(r'D:\MSC.Software\Adams\2017_2\python\win64\Lib\site-packages\mdi\command_server\temp.txt', 'a') as f:
        f.write(string)
        f.write('\n')

# MSG_LEN = 1024  # constant size for tcp/ip messages
MSG_LEN = 8192  # constant size for tcp/ip messages
MSG_PREFIX = "View Command Listener: "

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


def show():
    """
    Display command listener window, start listening
    :return:
    """
    # global mainViewWindow
    # global ListenerWindow

    # if 'command_server' in globals():  # has CommandListener been created?
    #     if 'mainViewWindow' not in globals(command_server):
    #         mainViewWindow = QApplication.activeWindow()
    #
    #         if 'ListenerWindow' not in globals(command_server):
    #             ListenerWindow = QDialog(mainViewWindow)
    #             my_dialog = ListenerDialog()
    #             my_dialog.setup_ui(ListenerWindow)
    #
    #     command_server.ListenerWindow.show()
    # else:
    #     print "command_server variable not found, can't show window"
    return


class TCPIPThread(threading.Thread):
    def __init__(self, parent, port, send_arrays_binary=0):
        """
        Create a new thread that manages a socket connection
        :param parent: ListenerDialog object (Qt window)
        :param port: tcp port to listen on
        :param send_arrays_binary: 0 (default) sends as string, 1 sends as binary
        :return:
        """
        threading.Thread.__init__(self, group=None, target=None, name='thread_1234')
        self.parent = parent  # Want to bubble messages back to parent. Not ideal to keep ref to parent...
        self.debug = True

        if self.debug: logging.debug('Starting TCP/IP Listener thread')

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        port_number = port
        self.send_arrays_binary = send_arrays_binary


        if self.debug: logging.debug('Trying to bind to port')

        try:
            self.server_socket.bind(("localhost", port_number))

        except socket.error as e:
            raise

        if self.debug: logging.debug('Bound to port %s' % port_number)

        self.server_socket.listen(1)

    def run(self):
        """
        start tcp/ip server, listening for commands:
        :return:
        """
        verb = None

        if self.debug: logging.debug('Starting run loop for tcp thread')

        while 1:

            (clientsocket, address) = self.server_socket.accept()
            if self.debug: logging.debug("New client socket created, description: {0}".format(clientsocket))
            
            data = clientsocket.recv(MSG_LEN) # 数据接收 

            if data in ['quit', 'QUIT', 'Quit', 'Q', 'q']: # 终止 
                if self.debug: logging.debug('Server quit message received, quitting')
                break  # kills while, exits TCP Thread..

            if (len(data) > 4) and (data[:3] == 'cmd'): # cmd命令
                verb = "cmd"
                if self.debug: logging.debug('Found cmd: %s' % data)
                view_cmd = data[3:]
                self.parent.add_view_command(view_cmd)  # 命令添加
                
                while self.parent.runningCommand: # 判断是否运行中
                    # runningCommand flag is set until ListenerDialog has finished issuing command to view..
                    time.sleep(0.002)


            elif (len(data) > 4) and (data[:5] == 'query'): # quert命令
                verb = "query"
                view_exp = data[5:]
                self.parent.add_view_query(view_exp)  # 命令添加

                if self.debug: logging.debug('Added this View query: %s' % view_exp)


            elif (len(data) > 6) and (data[:6] == 'binary'): # 
                tail = data[-3:]
                msg = 'binary transfer mode ON'
                if tail == ' on':
                    self.send_arrays_binary = True
                elif tail == 'off':
                    self.send_arrays_binary = False
                    msg = 'binary transfer mode OFF'
                clientsocket.send(msg)

            if verb == "cmd":
                # Retrieve any error codes from View:
                err_code = self.parent.cmd_result  # Set in timer_event
                zprint(err_code)
                clientsocket.send("cmd: %s" % err_code)

            elif verb == "query":  
                # Loop until we get a query result:
                query_res = None
                while query_res is None:  # query结果获取
                    query_res = self.parent.get_query_result()
                    time.sleep(0.002)

                # Get to here means that query_res has something, show it:
                if self.debug: logging.debug("Thread, run: query_res after waiting has value: {0}".format(query_res))
                if self.debug: logging.debug("Thread, run: query_res type is: {0}".format(type(query_res)))

                # check for error message:
                server_error = False
                if type(query_res).__name__ == 'str': 
                    # query_res类型为string时，判断是否报错
                    if "SERVER_ERROR:" in query_res:
                        socket_response = "SERVER_ERROR"
                        server_error = True
                    else:
                        # 非报错数据, 进行解析
                        var_type, num_elements, size_bytes = self.parent.get_query_type_and_size(query_res)
                        socket_response = unicode("query: %s : %i : %i" % (var_type, num_elements, size_bytes))
                        if self.debug: logging.debug("about to send query response, which is: %s" % socket_response)
                else:
                    # 非字符串结果
                    var_type, num_elements, size_bytes = self.parent.get_query_type_and_size(query_res)
                    socket_response = unicode("query: %s : %i : %i" % (var_type, num_elements, size_bytes))
                    if self.debug: logging.debug("about to send query response, which is: %s" % socket_response)

                # Send query result description to client. Can't exceed MSG_LEN:
                clientsocket.send(socket_response)  # 发送结果数据属性
                # 接受数据
                client_response = clientsocket.recv(MSG_LEN)       # Expect a simple 'OK'

                if client_response == "OK" and not server_error: # 返回'OK' 且不报错
                    # Send the actual data
                    if self.send_arrays_binary and (num_elements > 1):      # binary arrays
                        binary_data = None
                        binary_size = None

                        if var_type == 'int':
                            # pack data as integer byte sequence:
                            int_struct = struct.Struct('%sI' % len(query_res))
                            binary_data = int_struct.pack(*query_res)
                            binary_size = int_struct.size

                        elif var_type == 'float':
                            # pack data as float byte sequence:
                            logging.debug("about to make struct")
                            float_struct = struct.Struct('%sf' % len(query_res))
                            logging.debug("about to pack query_res:")
                            binary_data = float_struct.pack(*query_res)
                            logging.debug("got binary string, about to compute size: ")
                            binary_size = float_struct.size

                        elif var_type == 'str':
                            # join array, send as unicode byte string:
                            uni_bytes = unicode(','.join(query_res))
                            binary_data = uni_bytes
                            binary_size = len(uni_bytes)

                        actual_data = binary_data

                    else:
                        # Send responses as strings:
                        actual_data = '{0}'.format(query_res)
                else:
                    actual_data = "No data from View"

                if self.debug: logging.debug("about to send actual data, which is: {0}".format(actual_data))
                # send out all data:
                clientsocket.send(actual_data)


            if self.debug: logging.debug("About to shut down client socket {0}".format(clientsocket))

            clientsocket.shutdown(socket.SHUT_RDWR)
            clientsocket.close()

        return

class ListenerDialog(QDialog):
    def __init__(self, mainViewWindow, *args, **kwargs):
        """
        :param mainViewWindow:
        :param args:
        :param kwargs:
            tcp_port: port to listen on
            timer_interval: time interval, in milliseconds, at which actions are started
        """

        super(ListenerDialog, self).__init__(mainViewWindow)

        self.tcp_port = kwargs.get('tcp_port', 5002)  # 端口, 如果键的值不存在，则默认 5002
        self.timer_interval = kwargs.get('timer_interval', 10) # 定时间隔, 如果键的值不存在，则默认 10ms
        # workaround for RH7.x (ADMS-35731)
        self.setWindowFlags(QtCore.Qt.Window |
                        QtCore.Qt.WindowCloseButtonHint) # 

        self.__tcp_init__()


    def __tcp_init__(self):
        """
        Initializer..
        :param tcp_port: port to listen on
        :param timer_interval: time interval, in milliseconds, at which actions are started
        :return:
        """

        self.tcp_thread = None  # Initialize the tcp listener thread

        # Instance attributes to be used:
        self.buttonBox = None
        self.textEdit = None
        self.startButton = None
        self.stopButton = None
        self.myTimer = None
        self.commandQueue = None
        self.queryQueue = None
        self.queryResult = None
        self.queryID = 0
        self.runningCommand = None
        self.cmd_result = None  # Result of last cmd call
        self.debug = True
        self.setup_logging()  # 日志记录开始


# def setup_ui(self, dialog):
#     dialog.setObjectName(_fromUtf8("Dialog"))
#     dialog.resize(458, 372)
#     dialog.setModal(False)
#     self.buttonBox = QtGui.QDialogButtonBox(dialog)
#     self.buttonBox.setGeometry(QtCore.QRect(100, 330, 341, 32))
#     self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
#     self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
#     self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
#     self.textEdit = QtGui.QTextEdit(dialog)
#     self.textEdit.setGeometry(QtCore.QRect(20, 20, 421, 231))
#     self.textEdit.setObjectName(_fromUtf8("textEdit"))
#     self.startButton = QtGui.QPushButton(dialog)
#     self.startButton.setGeometry(QtCore.QRect(80, 270, 131, 28))
#     self.startButton.setObjectName(_fromUtf8("startButton"))
#     self.stopButton = QtGui.QPushButton(dialog)
#     self.stopButton.setGeometry(QtCore.QRect(240, 270, 131, 28))
#     self.stopButton.setObjectName(_fromUtf8("stopButton"))
#
#     self.myTimer = QtCore.QTimer(dialog)
#     self.commandQueue = []  # View commands to be issued
#     self.queryQueue = []  # View queries to be run
#
#     self.retranslateUi(dialog)
#     QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dialog.accept)
#     QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dialog.reject)
#     QtCore.QObject.connect(self.startButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.start_clicked)
#     QtCore.QObject.connect(self.stopButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.stop_clicked)
#     QtCore.QMetaObject.connectSlotsByName(dialog)
#
#     self.startButton.setEnabled(True)
#     self.stopButton.setEnabled(False)

    def setup_ui(self): # UI
        self.setObjectName(_fromUtf8("Dialog"))
        self.resize(458, 372)
        self.setModal(False)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(100, 330, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.textEdit = QtGui.QTextEdit(self)
        #self.textEdit = myTextEdit(self)
        self.textEdit.setGeometry(QtCore.QRect(20, 20, 421, 231))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.startButton = QtGui.QPushButton(self)
        self.startButton.setGeometry(QtCore.QRect(80, 270, 131, 28))
        self.startButton.setObjectName(_fromUtf8("startButton"))
        self.stopButton = QtGui.QPushButton(self)
        self.stopButton.setGeometry(QtCore.QRect(240, 270, 131, 28))
        self.stopButton.setObjectName(_fromUtf8("stopButton"))

        self.myTimer = QtCore.QTimer(self)
        self.commandQueue = []  # View commands to be issued
        self.queryQueue = []  # View queries to be run

        self.retranslateUi(self)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)
        QtCore.QObject.connect(self.startButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.start_clicked)
        QtCore.QObject.connect(self.stopButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.stop_clicked)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)

    # def keyPressEvent(self, e):
    #     self.print_message('Got a key press')
    #     # if e.key() == QtCore.Qt.Key_F1:
    #     #     self.show_help()

    def keyReleaseEvent(self, e): # 键位松开事件
        # F1 帮助文档
        if e.key() == QtCore.Qt.Key_F1:
            self.show_help()

    def setup_logging(self): # 日志记录初始设置
        log_format = '%(threadName)s : %(funcName)s : %(message)s'
        logging.basicConfig(filename='mylog.log', level=logging.DEBUG, filemode='w', format=log_format)
        logging.debug('Logging initiated')

    def show_help(self): # HELP调用

        top_dir = os.environ.get('TOPDIR')
        help_file = os.path.join(top_dir, 'help', 'adams_view', 'dialogboxes', 'view_command_server.html')
        if os.path.isfile(help_file):
            os.startfile(help_file)
        else:
            self.print_message('Could not locate help file view_command_server.html')

    def retranslateUi(self, Dialog): # UI
        Dialog.setWindowTitle(_translate("Dialog", "Adams View Command Server", None))
        self.startButton.setText(_translate("Dialog", "Start Server", None))
        self.stopButton.setText(_translate("Dialog", "Stop Server", None))

    def timer_event(self): # 定时调用, 目标命令执行 ---------------------------------------------------------
        """
        Timer callback function. Timer calls this when it fires
        """

        # CMD 命令执行
        while len(self.commandQueue) > 0: 
            self.runningCommand = True  # Notify that View is working..
            cmd = self.commandQueue.pop()
            if self.debug: logging.debug("About to execute: %s" % cmd)

            self.cmd_result = aview_main.execute_cmd(cmd)  # 执行命令
            # if self.cmd_result:

            self.runningCommand = False  # Notify that View is complete

        # Query 命令执行
        while len(self.queryQueue) > 0: 
            self.runningCommand = True  # Notify that View is working..
            cmd = self.queryQueue.pop()

            if self.debug: logging.debug("About to execute query: %s " % cmd)

            try:
                view_answer = aview_main.evaluate_exp(cmd)  # 执行命令
            except ValueError as view_error:
                # view_error.message
                if self.debug: logging.debug("This query failed: {0}".format(cmd))
                view_answer = "SERVER_ERROR: {0}".format(view_error.message)


            # self.queryResults.append(query_result)
            if self.debug: logging.debug("View query result is: {0}".format(view_answer))
            # self.queryResult = '{0}'.format(view_answer)
            self.queryResult = view_answer
            if self.debug: logging.debug("self.queryResult is: {0}".format(self.queryResult))
            self.runningCommand = False  # Notify that View is complete


        return

    def get_query_type_and_size(self, query_result): # query结果数据解析
        """
        Determine type and size of view response
        :param query_result:
        :return:
        """
        if isinstance(query_result, tuple) or isinstance(query_result, list):
            if len(query_result) > 0:
                an_element = query_result[0]
                var_type = type(an_element).__name__
                num_elements = len(query_result)
                if var_type == 'float':
                    packed_data = struct.Struct('%sf' % num_elements)
                    packed_data.pack(*query_result)
                    size_bytes = packed_data.size
                elif var_type == 'int':
                    packed_data = struct.Struct('%si' % num_elements)
                    packed_data.pack(*query_result)
                    size_bytes = packed_data.size
                else:
                    # unsupported type, don't calc a size:
                    # 不支持
                    size_bytes = 0

            else:
                # 空数据
                var_type = None
                num_elements = None
                size_bytes = 0

        else:  # single element:
            var_type = type(query_result).__name__
            num_elements = 1
            size_bytes = 0

        return var_type, num_elements, size_bytes

    def add_view_command(self, cmdString): # 添加 cmd 命令行
        """
        Add a View command to the queue.
        """
        self.print_message('Receive: %s' % cmdString)
        self.runningCommand = True
        # Clear any View errors: 清楚报错数据
        aview_main.execute_cmd("variable set variable=.MDI.ERRNO integ=0")
        aview_main.execute_cmd("variable set variable=.MDI.ERRSTR string='' ")

        self.commandQueue.append(cmdString)

    def add_view_query(self, cmdString): # 添加 query 命令行
        """
        Add a View query to the queue, return result
        """

        if self.debug: logging.debug('Listener: Adding query to queue: %s' % cmdString)
        self.print_message('Query: %s' % cmdString)
        self.queryQueue.append(cmdString)

    def get_view_errors(self): # 判断是否保存 并返回报错数据
        """
        Retrieve contents of message window..
        :return: (True/False, error string)
        """
        temp_file = 'message_window_messages.txt' # 临时文件存储
        if os.path.isfile(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                pass

        logging.debug("Writing msgs to file")
        cmd = "interface field write field_name = message file_name = '%s'" % temp_file 

        aview_main.execute_cmd(cmd)

        logging.debug("Trying to open msg file for reading")
        f_msg = open(temp_file, mode='r')
        all_lines = f_msg.readlines()
        is_error = 'ERROR:' in all_lines

        return is_error, all_lines

    def get_query_result(self): # query结果数据获取
        """
        Called continuously by the TCP thread as it waits
        for query results
        :return: string
        """
        if not (self.queryResult is None):
            ret_value = self.queryResult
            self.queryResult = None         # Need to reset after we've used it
            return ret_value
        else:
            return None


    def start_clicked(self): # command_server start 回调
        """
        User hit start button in GUI - launch TCP server thread
        :return: None
        """

        # Is server already started?
        if self.startButton.isEnabled() == False: # 是否已经Start
            return

        send_arrays_binary = 0          # default: send arrays as text, not binary
        if 'ADAMS_LISTENER_BINARY_ARRAYS' in os.environ:
            send_arrays_binary = 1

        # ----- Start thread listening for tcp/ip commands:
        try:
            # 建立 监听
            self.tcp_thread = TCPIPThread(parent=self, port=self.tcp_port, send_arrays_binary = send_arrays_binary)
        except socket.error:
            # 建立 监听 失败
            s_ret = 'interface field set action = append field_name = .gui.msg_box.message strings="%s\n"' % 'Could not bind to port'
            aview_main.execute_cmd(s_ret)
            self.textEdit.append("Could not bind to port %i, try a different port number." % self.tcp_port)
            return

        self.tcp_thread.start() # 线程启动------------------

        # ----- Timer fires continuously, every 0.03 seconds: 开启定时器
        self.myTimer.timeout.connect(self.timer_event)  # 定时函数
        self.myTimer.start(self.timer_interval)  # 默认10毫秒

        self.textEdit.append("Server is accepting View commands on port: %i" % self.tcp_port) # 显示

        # ----- gui update for this button press: 按钮设置
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)

    def stop_clicked(self): # command_server stop 回调
        """
        Stop thread:
        # thread is blocking, waiting for socket connection. So make
        # connection and issue quit command:
        """

        # Is server already stopped?
        if self.stopButton.isEnabled() == False:
            return

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", self.tcp_port))  # 改
        # client_socket.connect(("localhost", 5002))
        client_socket.send('quit')  # TCPThread will terminate here
        client_socket.close()

        self.tcp_thread = None

        # ------ Stop timer: 停止-定时器
        self.myTimer.stop()
        self.textEdit.append("Server not accepting View commands")

        # ----- gui update for this button press: 按钮设置
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)

    def print_message(self, theMsg): # 数据窗口记录
        """
        Appends message to text box..
        """
        self.textEdit.append(theMsg)



