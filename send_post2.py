#!/bin/python3
import requests
import json
 
# 用于发送POST请求，请求body是一个文件的内容
# TODO 按并发循环发送
#url = 'http://127.0.0.1:1000'
url = 'http://127.0.0.1:1000/zentao/testcase-showImport-158-0.html?zin=1'
data = {
 'key1': 'value1',
 'key2': 'value2'
}
# 将字典转换为JSON字符串
#json_data = json.dumps(data)

with open("/home/david/python_server/post.data", "r") as file:
    json_data = file.read()

#print(json_data)
print(len(json_data))
headers = {
        'Host': 'zt.ouryun.cn',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary2c8EQzDVHvLpZucU',
        'content-length': '16062',
        'x-requested-with': 'XMLHttpRequest',
        'accept': '*/*',
        'origin': 'http://zt.ouryun.cn',
        'referer': 'http://zt.ouryun.cn/zentao/index-index-L3plbnRhby90ZXN0Y2FzZS1icm93c2UtMTU4LWFsbC1ieU1vZHVsZS0yOTc2Lmh0bWw=.html',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9',
        'x-forwarded-for': '172.16.0.90',
        'x-forwarded-proto': 'http',
        'x-request-id': 'b09c2f8c-41b0-41af-95a8-eb993bc79a45',
        'sr-vsmatched': 'false',
        'sr_fp_value': 'af1aa36738cfaf158af62d69bbbd7f03',
        'cookie': 'zentaosid=7ca1envmh22ea7a9bdmap1c9b4; lang=zh-cn; vision=rnd; device=desktop; theme=default; preProductID=158; preBranch=all; caseModule=2976; hideMenu=false; tab=qa',
}  # 设置正确的Content-Type头部
response = requests.post(url, data=json_data.encode('utf-8'), headers=headers)

# 打印响应内容
print(response.text)

