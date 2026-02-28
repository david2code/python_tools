#!/bin/python3
# SocketTest.py
# -*- coding:utf-8 -*-


import socket
import os
import time


def socketTest():
    while True:
        ret = str(conn.recv(1024), encoding="utf-8")
        print(ret)
        if 'End' in ret:
            print('连接结束-End')
            print('---------------------------------')
            conn.sendall(bytes("收到断开连接信息-End!", encoding="utf-8"))
            conn.close()
            sk.close #不发送fin包
            break
            conn.sendall(bytes("我再发！", encoding="utf-8"))
            conn.sendall(bytes("我再发！", encoding="utf-8"))
            os.system('netstat -nlp | grep %s' % port)
            break
        else:
            print('Not close')
            continue


if __name__ == '__main__':
    while True:
        host = '0.0.0.0'
        port = 9918

        host_name = socket.gethostname()
        print(host_name)
        print("PID = %i" % (os.getpid(),))

        sk = socket.socket()
        sk.bind((host, port))
        sk.listen(60)
        # sk.settimeout(10)
        print('端口监听中...')
        os.system("netstat -nlp|grep :%i" % (port,))
        print('客户端返回连接信息')
        conn, address = sk.accept()
        print('连接中...')
        print('连接来自: ', address)
        print('---------------------------------')
        print("lsof -p %i" % (os.getpid(),))
        os.system("lsof -p %i" % (os.getpid(),))
        print('---------------------------------')
        print('netstat -nlp | grep %s' % port)
        os.system('netstat -nlp | grep %s' % port)
        print('---------------------------------')
        print('ls /proc/%i/fd |wc -l '% (os.getpid(),))
        os.system('ls /proc/%i/fd |wc -l '% (os.getpid(),))
        #time.sleep(4)
        socketTest()