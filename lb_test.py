#!/usr/bin/python3
#coding=utf-8
import requests

# 此脚本用于测试负载均衡
# 多次请求负载均衡，然后根据返回的数据统计都路由到了哪些业务上

LB_URL = "http://172.16.89.200:20200/"
CNT = 300;

def request_url(): 

    hint = dict()
    i = 0
    while i < CNT:
        i = i + 1

        response = requests.get(LB_URL)
        resp_json = response.json();
        ip = resp_json['data']['ip']
        port = resp_json['data']['port']
        key = '%s:%d' % (ip, port)
        # print(key)
        print(i, ":", key, " set-cookie: ", response.headers.get('set-cookie'))
        if key in hint:
            hint[key] = hint[key] + 1
        else:
            hint[key] = 1

    for key in hint:
        print(key, hint[key])


 
if __name__ == '__main__':
    request_url()