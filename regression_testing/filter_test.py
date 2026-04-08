#!/bin/python3
import threading
import multiprocessing
import time
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import os
import requests
import socket, socketserver
from optparse import OptionParser
import argparse
import shutil
 
'''
大致流程：
1. 从命令行读取envoy源码目录，插件so目录
2. 启动业务服务，监听在 8000端口
3. 启动 envoy 主进程
4. 开始执行test_mode从0 到18的循环

循环流程如下：
- 关闭 pm 从进程
- 拷贝插件so到 envoy源码目录的 plugins/www.srhino.com
- 启动 pm 从进程
- 向 envoy 监听的 1000端口发送http post请求
- 收集 业务收到的请求和从envoy收到的响应
- 对请求和响应进行校验
'''
test_mode = 0
plugin_name="user-identify.so.1.0.8"
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

def old_envoy_process():
  print("envoy:", os.getpid())
  print("envoy:", multiprocessing.current_process())
  os.chdir(args.envoy_dir)
  os.execl("bazel-bin/envoy", "envoy", "-c config/plugin-loader.yaml", "--component-log-level main:error,http:error,conn_handler:error,plugin:error", "--concurrency 2")

def envoy_process():
  print("envoy:", os.getpid())
  print("envoy:", multiprocessing.current_process())
  os.chdir(args.envoy_dir)
  os.execl("bazel-bin/envoy", "envoy", "-c config/plugin-manager.yaml", "--component-log-level main:error,http:error,conn_handler:error,plugin:error", "--concurrency 2")

def pm_process():
  print("pm:", os.getpid())
  print("pm:", multiprocessing.current_process())
  os.chdir(args.envoy_dir)
  os.execl("bazel-bin/envoy", "envoy", "-c config/plugin-manager.yaml", "--component-log-level main:error,http:error,conn_handler:error,plugin:error", "--concurrency 2", "--base-id 10000", "--enable-plugin-mode")

def update_plugin_so_and_restart_pm(test_mode):
  global pm
  print("kill pm process")
  if pm is not None:
    pm.terminate()
    pm.join()
    pm = None
  print("kill pm done")
  time.sleep(1)

  # set filter so
  src_file = args.so_dir + plugin_name + ".mode" + str(test_mode)
  dst_dir = args.envoy_dir + "plugins/www.srhino.com/user-identify/" + plugin_name
  print(f"src_file: {src_file}")
  print(f"dst_dir: {dst_dir}")
  shutil.copy(src_file, dst_dir)

  print("start pm process")
  pm = multiprocessing.Process(target=pm_process, name="pm_process")
  pm.start()

  # wait pm ready
  time.sleep(5)

def update_plugin_so_and_restart_old_envoy(test_mode):
  global envoy
  print("kill old_envoy process")
  if envoy is not None:
    envoy.terminate()
    envoy.join()
    envoy = None
  print("kill old_envoy done")
  time.sleep(1)

  # set filter so
  src_file = args.so_dir + plugin_name + ".mode" + str(test_mode)
  dst_dir = args.envoy_dir + "plugins/www.srhino.com/user-identify/" + plugin_name
  print(f"src_file: {src_file}")
  print(f"dst_dir: {dst_dir}")
  shutil.copy(src_file, dst_dir)

  print("start old envoy process")
  envoy = multiprocessing.Process(target=old_envoy_process, name="old_envoy_process")
  envoy.start()

  # wait envoy ready
  time.sleep(7)


if __name__ == '__main__':
  # 测试引擎容错机制
  test_fault_tolerant = True

  parser = argparse.ArgumentParser(description="envoy filter test program")
  parser.add_argument("-e", "--envoy_dir", help="envoy-filters dir")
  parser.add_argument("-s", "--so_dir", help="filter so dir")

  args = parser.parse_args()
  print(f"envoy-filters dir: {args.envoy_dir}")
  print(f"so dir: {args.so_dir}")

  print("main:", os.getpid())
  print("main:", multiprocessing.current_process())

  host = ('0.0.0.0', 8000)
  server = HTTPServer(host, Resquest)
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)
  server_thread = threading.Thread(target=server_worker, args=(server, 2))

  server_thread.start()
  # wait server prepare
  time.sleep(1)

  pm = None
  envoy = None
  if test_fault_tolerant is True:
    envoy = multiprocessing.Process(target=envoy_process, name="envoy_process")
    envoy.start()
    print("start envoy process")
    time.sleep(1)

  # for test_mode in range(3, 4):
  for test_mode in range(0, 21):

    # prepare plugin so
    if test_fault_tolerant is True:
      update_plugin_so_and_restart_pm(test_mode)
    else:
      update_plugin_so_and_restart_old_envoy(test_mode)

    # clear global value
    server_side_req_body = None
    server_side_req_header = None
    # send post
    resp_status_code, resp_headers, resp_body = send_post()

    print("testmode: %d begin" % test_mode)
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
      assert server_side_req_header["Header-To-Modify"] == "1234567_plugin_modified_onDecodeHeader_Continue", "test failed"
      assert server_side_req_header.get("Header-To-Remove") == None, "test_faled"

      assert resp_headers["Header-To-Add"] == "plugin add header", "test failed"
      assert resp_headers["Header-To-Modify"] == "1234567_plugin_modified_onEncodeHeader_Continue", "test failed"
      assert resp_headers.get("Header-To-Remove") == None, "test_faled"
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
      assert server_side_req_header["Header-To-Modify"] == "1234567_plugin_modified_onDecodeHeader_Break", "test failed"
      assert server_side_req_header.get("Header-To-Remove") == None, "test_faled"
    # onDecodeHeader Pause then continue
    elif test_mode == 3:
      # check header modify
      assert resp_status_code == 200, "test failed"
      assert server_side_req_header["Header-To-Add"] == "plugin add header", "test failed"
      assert server_side_req_header["Header-To-Modify"] == "1234567_plugin_modified_onDecodeHeader_Pause_then_Continue", "test failed"
      assert server_side_req_header.get("Header-To-Remove") == None, "test_faled"
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
      assert server_side_req_header.get("Header-To-Remove") == None, "test_faled"
    # onDecodeData Pause then DirectResponse
    elif test_mode == 9:
      assert resp_status_code == 200, "test failed"
      assert server_side_req_body == "request body modify onDecodeData pause then modify body", "test failed"
    elif test_mode == 10:
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onDecodeData", "test failed"

    # onEncodeHeader DirectResponse
    elif test_mode == 11: 
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onEncodeHeader", "test failed"
    # onEncodeHeader Break
    elif test_mode == 12:
      # check header modify
      assert resp_status_code == 200, "test failed"
      assert resp_headers["Header-To-Add"] == "plugin add header", "test failed"
      assert resp_headers["Header-To-Modify"] == "1234567_plugin_modified_onEncodeHeader_Break", "test failed"
      assert resp_headers.get("Header-To-Remove") == None, "test_faled"
    # onEncodeHeader Pause then continue
    elif test_mode == 13:
      # check header modify
      assert resp_status_code == 200, "test failed"
      assert resp_headers["Header-To-Add"] == "plugin add header", "test failed"
      assert resp_headers["Header-To-Modify"] == "1234567_plugin_modified_onEncodeHeader_Pause_then_Continue", "test failed"
      assert resp_headers.get("Header-To-Remove") == None, "test_faled"
    # onEncodeHeader Pause then DirectResponse
    elif test_mode == 14:
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onEncodeHeader", "test failed"

    # onEncodeData WaitForBody
    elif test_mode == 15:
      assert resp_status_code == 200, "test failed"
      assert resp_body == "response body modify onEncodeData wait for body", "test failed"
    # onEncodeData tryWaitForBody
    elif test_mode == 16:
      assert resp_status_code == 200, "test failed"
      assert resp_body == "response body modify onEncodeData try wait for body", "test failed"
    # onEncodeData DirectResponse
    elif test_mode == 17:
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onEncodeData", "test failed"
    # onEncodeData Pause then continue
    elif test_mode == 18:
      # check header modify
      assert resp_status_code == 200, "test failed"
      assert resp_headers["Header-To-Add"] == "plugin add header", "test failed"
      assert resp_headers["Header-To-Modify"] == "1234567_plugin_modified_onEncodeData_Pause_then_Continue", "test failed"
      assert resp_headers.get("Header-To-Remove") == None, "test_faled"
    elif test_mode == 19:
      # check header modify
      assert resp_status_code == 200, "test failed"
      assert resp_body == "response body modify onEncodeData pause then modify body", "test failed"
    # onEncodeData Pause then DirectResponse
    elif test_mode == 20:
      assert resp_status_code == 403, "test failed"
      assert resp_body == "DirectResponse onEncodeData", "test failed"

    else:
      print(resp_status_code)
      assert False, "uknown test mode"

    print("testmode: %d passed\n" % test_mode)


  envoy.terminate()
  envoy.join()

  server_thread.join()
  # t2.join()