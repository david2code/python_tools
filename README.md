# 说明
## https_server.py
> https://xz.aliyun.com/t/12605
https server，监听在本地的4443端口，能够处理https请求。
设置会话复用不成功。

访问
```shell
https://127.0.0.1:4443/
```

## cert2
自己生成的证书

## ouryun_ca
公司证书

## lb_test.py
测试负载均衡，请求100次，然后统计各个业务的访问次数

## server.py
http server
用来调试各插件时，模拟业务服务器返回数据
```shell
Usage: server.py [options]

Options:
  -h, --help            show this help message and exit
  -6, --ipv6            run on ipv6
  -m MOCK, --mock=MOCK  run mock: identify, rewrite, weak, big_body,
                        http_server, sendfile
  -p PORT, --port=PORT  listen port
  -c PIECE_CNT, --piece_cnt=PIECE_CNT
                        piece count
  -s PIECE_SIZE, --piece_size=PIECE_SIZE
                        piece size
```
### mock
- identify
user_identify
- rewrite
rewrite_response
- http_server
用于模拟业务服务器返回数据, 分 piece_cnt次响应,每次响应 piece_size 字节,每次响应之间间隔 0.2 秒
- sendfile
用于模拟文件响应,使用sendfile函数发送文件

# regression_testing
回归测试脚本
## filter_test.py
测试envoy插件链不同返回状态
### 使用方法
- 使用 filter_chain_test_d5d5ae72586f07d3eb22253bde513cb479ea423e.patch对 srhino_plugins打补丁
- 准备插件so
在脚本所在目录下执行
~/shell_tools/make_filter_chain_test_so.sh /home/david/srhino_plugins/user-identify/
- 测试引擎容错
设置脚本的 test_fault_tolerant 为 True
```shell
sudo ./filter_test.py -e /home/david/envoy-filters/ -s filter_so/
```
- 测试旧版本
设置脚本的 test_fault_tolerant 为 False
```shell
sudo ./filter_test.py -e /home/david/2envoy-filters/ -s filter_so/
```

