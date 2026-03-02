#!/bin/python3
import threading
import time
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import requests
import socket, socketserver
from optparse import OptionParser
 
test_mode = 0
# server测收到的请求header
server_side_req_header = None
# server测收到的请求body
server_side_req_body = None
# server测发送的响应header
server_side_resp_header = None
# server测发送的响应body
server_side_resp_body = None

class Resquest(BaseHTTPRequestHandler):
    server_version = "Apache"   #设置服务器返回的的响应头 

    def request_process(self):
        buf = "http server response body"
        self.send_response(200)

        self.send_header("test-mode", test_mode)     #设置服务器响应头
        self.send_header("set-cookie","lang=zh-cn; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")     #设置服务器响应头
        self.send_header("content-type","text/html; charset=utf-8")  #设置服务器响应头
        self.send_header("header-to-modify", "1234567")
        self.send_header("header-to-remove", "0000000")
        self.send_header("content-length", len(buf))  #设置服务器响应头
        self.end_headers()

        self.wfile.write(buf.encode())  #里面需要传入二进制数据，用encode()函数转换为二进制数据   #设置响应body，即前端页面要展示的数据

    def do_GET(self):
        print('----- headers start ----')
        print(self.headers)
        print('----- headers end ----')

        self.request_process()
        #self.resp_202();
 
    def do_POST(self):
        global server_side_req_header
        global server_side_req_body
        # datas = self.rfile.read(int(self.headers['content-length']))
        server_side_req_header = self.headers
        server_side_req_body = self.rfile.read(int(self.headers['content-length'])).decode()
        # print("\ndo post: %s, client_address: %s" % (self.path, self.client_address))
        self.request_process()
 


def server_worker(server, delay):
  print("Starting server, listen at: %s:%s" % host)
  server.serve_forever()

def signal_handler(sig, frame):
  print("signal: {sig} received, exiting")
  shutdown_thread = threading.Thread(target=server.shutdown, daemon=True)
  shutdown_thread.start()

def send_post():
  global server_side_req_header
  global server_side_req_body
  url = 'http://127.0.0.1:1000/zentao/testcase-showImport-158-0.html?zin=1'
  data = "11122233344455566778899"

  headers = {
          'Host': '127.0.0.1',
          'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
          'content-type': 'text/html',
          'accept': '*/*',
          'accept-encoding': 'gzip, deflate',
          'accept-language': 'zh-CN,zh;q=0.9',
          'header-to-modify': "1234567",
          'header-to-remove': "0000000",
          'cookie': 'zentaosid=7ca1envmh22ea7a9bdmap1c9b4; lang=zh-cn; vision=rnd; device=desktop; theme=default; preProductID=158; preBranch=all; caseModule=2976; hideMenu=false; tab=qa',
  }  # 设置正确的Content-Type头部
  response = requests.post(url, data, headers=headers)
  return response.status_code, response.headers, response.text

if __name__ == '__main__':
  host = ('0.0.0.0', 8000)
  server = HTTPServer(host, Resquest)
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)
  server_thread = threading.Thread(target=server_worker, args=(server, 2))
  # t2 = threading.Thread(target=worker, args=("B", 2))

  server_thread.start()
  # wait server prepare
  time.sleep(2)
  # t2.start()

  for test_mode in range(18, 20):
    print("testmode: %d begin" % test_mode)
    # prepare plugin so

    # clear global value
    server_side_req_body = None
    server_side_req_header = None
    # send post
    resp_status_code, resp_headers, resp_body = send_post()

    print(server_side_req_header)
    print(server_side_req_body)
    print("resp headers: ")
    print(resp_headers)
    print(resp_body)
    # print(server_side_req_body.decode())

    # check result
    # continue
    if test_mode == 0:
      # check header modify
      assert resp_status_code == 200, "test failed"
      assert server_side_req_header["Header-To-Add"] == "plugin add header", "test failed"
      assert server_side_req_header["Header-To-Modify"] == "1234567_plugin_modified", "test failed"
      assert server_side_req_header["Header-To-Remove"] == None, "test_faled"

      assert resp_headers["Header-To-Add"] == "plugin add header", "test failed"
      assert resp_headers["Header-To-Modify"] == "1234567_plugin_modified_onEncodeHeader_Continue", "test failed"
      assert resp_headers["Header-To-Remove"] == None, "test_faled"
    # onDecodeHeader DirectResponse
    elif test_mode == 1: 
      # print(resp_status_code)
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onDecodeHeader", "test failed"
    # onDecodeHeader Break
    elif test_mode == 2:
      # check header modify
      assert resp_status_code == 200, "test failed"
      assert server_side_req_header["Header-To-Add"] == "plugin add header", "test failed"
      assert server_side_req_header["Header-To-Modify"] == "1234567_plugin_modified", "test failed"
      assert server_side_req_header["Header-To-Remove"] == None, "test_faled"
    # onDecodeHeader Pause then continue
    elif test_mode == 3:
      # check header modify
      assert resp_status_code == 200, "test failed"
      assert server_side_req_header["Header-To-Add"] == "plugin add header", "test failed"
      assert server_side_req_header["Header-To-Modify"] == "1234567_plugin_modified_onDecodeHeader_Pause_then_Continue", "test failed"
      assert server_side_req_header["Header-To-Remove"] == None, "test_faled"
    # onDecodeHeader Pause then DirectResponse
    elif test_mode == 4:
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onDecodeHeader", "test failed"

    # onDecodeData WaitForBody
    elif test_mode == 5:
      assert resp_status_code == 200, "test failed"
      assert server_side_req_body == "request body modify onDecodeData wait for body", "test failed"
    # onDecodeData tryWaitForBody
    elif test_mode == 6:
      assert resp_status_code == 200, "test failed"
      assert server_side_req_body == "request body modify onDecodeData try wait for body", "test failed"
    # onDecodeData DirectResponse
    elif test_mode == 7:
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onDecodeData", "test failed"
    # onDecodeData Pause then continue
    elif test_mode == 8:
      # check header modify
      assert resp_status_code == 200, "test failed"
      assert server_side_req_header["Header-To-Add"] == "plugin add header", "test failed"
      assert server_side_req_header["Header-To-Modify"] == "1234567_plugin_modified_onDecodeData_Pause_then_Continue", "test failed"
      assert server_side_req_header["Header-To-Remove"] == None, "test_faled"
    # onDecodeData Pause then DirectResponse
    elif test_mode == 9:
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onDecodeData", "test failed"

    # onEncodeHeader DirectResponse
    elif test_mode == 10: 
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onEncodeHeader", "test failed"
    # onEncodeHeader Break
    elif test_mode == 11:
      # check header modify
      assert resp_status_code == 200, "test failed"
      assert resp_headers["Header-To-Add"] == "plugin add header", "test failed"
      assert resp_headers["Header-To-Modify"] == "1234567_plugin_modified_onEncodeHeader_Break", "test failed"
      assert resp_headers.get("Header-To-Remove") == None, "test_faled"
    # onEncodeHeader Pause then continue
    elif test_mode == 12:
      # check header modify
      assert resp_status_code == 200, "test failed"
      assert resp_headers["Header-To-Add"] == "plugin add header", "test failed"
      assert resp_headers["Header-To-Modify"] == "1234567_plugin_modified_onEncodeHeader_Pause_then_Continue", "test failed"
      assert resp_headers.get("Header-To-Remove") == None, "test_faled"
    # onEncodeHeader Pause then DirectResponse
    elif test_mode == 13:
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onEncodeHeader", "test failed"

    # onEncodeData WaitForBody
    elif test_mode == 14:
      assert resp_status_code == 200, "test failed"
      assert resp_body == "response body modify onEncodeData wait for body", "test failed"
    # onEncodeData tryWaitForBody
    elif test_mode == 15:
      assert resp_status_code == 200, "test failed"
      assert resp_body == "response body modify onEncodeData try wait for body", "test failed"
    # onEncodeData DirectResponse
    elif test_mode == 16:
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onEncodeData", "test failed"
    # onEncodeData Pause then continue
    elif test_mode == 17:
      # check header modify
      assert resp_status_code == 200, "test failed"
      assert resp_headers["Header-To-Add"] == "plugin add header", "test failed"
      assert resp_headers["Header-To-Modify"] == "1234567_plugin_modified_onEncodeData_Pause_then_Continue", "test failed"
      assert resp_headers.get("Header-To-Remove") == None, "test_faled"
    # onEncodeData Pause then DirectResponse
    elif test_mode == 18:
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onEncodeData", "test failed"

    else:
      print(resp_status_code)
      assert False, "uknown test mode"

    print("testmode: %d passed\n" % test_mode)
    break


  server_thread.join()
  # t2.join()