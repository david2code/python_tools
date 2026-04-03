#!/bin/python3
import httpx
import asyncio
import subprocess

async def test_http2_post():
    print("Testing HTTP/2 POST request with httpx...")
    
    # 创建支持 HTTP/2 的客户端
    # httpx 的 http2=True 会自动处理 HTTP/2 升级
    async with httpx.AsyncClient(http2=True) as client:
        # 首先发送一个 GET 请求来建立连接
        # 这样可以确保连接被正确升级到 HTTP/2
        print("\n1. Sending initial GET request to establish connection...")
        get_response = await client.get("https://localhost:8443/", verify=False)
        print(f"GET Status code: {get_response.status_code}")
        print(f"GET HTTP version: {get_response.http_version}")
        
        # 然后发送 POST 请求
        print("\n2. Sending POST request...")
        response = await client.post(
            "https://localhost:8443/api/test",
            json={"name": "test", "value": 123},
            headers={"Content-Type": "application/json"},
            verify=False
        )
        
        # 打印响应信息
        print(f"POST Status code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text}")
        print(f"HTTP version: {response.http_version}")
        
        # 检查是否使用了 HTTP/2
        if response.http_version == "HTTP/2":
            print("✓ Successfully used HTTP/2 protocol!")
        else:
            print("✗ Used HTTP/1.1 instead of HTTP/2")
            print("\nNote: httpx may not use HTTP/2 for plain HTTP connections")
    
    # 使用 curl 测试 HTTP/2 支持
    print("\n3. Testing HTTP/2 POST request with curl...")
    curl_command = [
        "curl", "-v", "--http2-prior-knowledge",
        "http://localhost:8000/api/test",
        "-d", '11122233344455566778899',
        "-H", "Content-Type: application/json",
        "-H", 'Host: 127.0.0.1',
        "-H",  'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        "-H",  'content-type: text/html',
        "-H",  'accept: */*',
        "-H",  'accept-encoding: gzip, deflate',
        "-H",  'accept-language: zh-CN,zh;q=0.9',
        "-H",  'header-to-modify: 1234567',
        "-H",  'header-to-remove: 0000000',
        "-H",  'cookie: zentaosid=7ca1envmh22ea7a9bdmap1c9b4; lang=zh-cn; vision=rnd; device=desktop; theme=default; preProductID=158; preBranch=all; caseModule=2976; hideMenu=false; tab=qa',
    ]
    
  # url = 'http://127.0.0.1:1000/zentao/testcase-showImport-158-0.html?zin=1'

    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=False)
        print("Curl output:")
        print(result.stdout)
        if result.stderr:
            print("Curl error:")
            print(result.stderr)
        
        # 检查输出中是否包含 HTTP/2
        if "HTTP/2 200" in result.stdout:
            print("\n✓ Successfully used HTTP/2 protocol with curl!")
        else:
            print("\n✗ Failed to use HTTP/2 protocol with curl")
    except Exception as e:
        print(f"Error running curl: {e}")

if __name__ == "__main__":
  # 创建支持 HTTP/2 的客户端                                              
  with httpx.Client(http2=True, verify=False) as client:                               
      # 发送请求                                                          
      response = client.get('https://127.0.0.1:8443/')                   
      # 打印响应信息                                                      
      print(response.status_code)          # 200                          
      print(response.http_version)         # 'HTTP/2'，确认使用的协议版本
      print(response.text)                 # 响应正文                     

  # asyncio.run(test_http2_post())
