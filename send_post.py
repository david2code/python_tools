#!/bin/python3
import requests
import json
 
# 用于发送POST请求，请求body是一个文件的内容
# TODO 按并发循环发送
#url = 'http://127.0.0.1:1000'
url = 'http://192.192.101.76:20010'
data = {
 'key1': 'value1',
 'key2': 'value2'
}
# 将字典转换为JSON字符串
#json_data = json.dumps(data)

with open("/home/david/python_server/a.json", "r") as file:
    json_data = file.read()
    json_data = json_data.encode('utf-8')

#print(json_data)
print(len(json_data))
headers = {'Content-Type': 'application/json'}  # 设置正确的Content-Type头部
response = requests.post(url, data=json_data, headers=headers)

# 打印响应内容
print(response.text)

