#!/bin/python3
# SocketTestClient
# -*- coding:utf-8 -*-
 
import socket
import os
import subprocess
import time
 
host = '0.0.0.0'
port = 9918
 
host = socket.gethostname()
print('客户端host = ',host)
print("客户端请求PID = %i" % (os.getpid(),))
obj = socket.socket()
obj.connect((host, port))
print('netstat -nlp | grep %s' % port)
os.system('netstat -nlp | grep %s' % port)
j = 0
while True:
    obj.send(bytes("这是客户端第 %s 条消息！ " % j, encoding="utf-8"))
    #time.sleep(5)
    j = j + 1
    print("发送了 %s 条！" %j)
    if j == 5:
        obj.send(bytes("End", encoding="utf-8"))
        ret = str(obj.recv(1024), encoding="utf-8")
        print('ret = ',ret)
        if ret == 'Finish!':
            obj.close()
            break
    else:
        continue