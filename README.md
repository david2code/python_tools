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
- user_identify
- rewrite_response

# regression_testing
回归测试脚本
## envoy_filter_test.py
测试envoy插件链不同返回状态
