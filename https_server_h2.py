#!/bin/python3
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

async def handle_all_requests(request):
    # 从请求中获取查询参数
    status_code = int(request.query_params.get("status", 200))
    
    # 构建响应头
    headers = {
        "X-Custom-Header": "HTTP/2 Server",
        "Content-Type": "text/plain; charset=utf-8"
    }
    
    # 构建响应内容
    content = "http server response body"
    # content = f"Hello, HTTP/2 World!\n"
    # content += f"Request path: {request.url.path}\n"
    # content += f"Status code: {status_code}\n"
    
    return PlainTextResponse(
        content=content,
        status_code=status_code,
        headers=headers
    )

app = Starlette(routes=[
    Route("/{path:path}", handle_all_requests, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
])

if __name__ == "__main__":
    import hypercorn.config
    from hypercorn.asyncio import serve
    import asyncio
    
    config = hypercorn.config.Config()
    # 配置 TLS
    config.bind = ['[::1]:8443', '0.0.0.0:8443']  # 使用 8443 端口进行 HTTPS
    config.certfile = 'cert2/server-cert.pem'  # 证书文件
    config.keyfile = 'cert2/server-key.pem'  # 私钥文件
    # 配置 HTTP/2 支持
    config.alpn_protocols = ['h2', 'http/1.1']  # 优先使用 HTTP/2
    config.h2_max_concurrent_streams = 200  # 提高并发流数
    config.http2 = True  # 明确启用 HTTP/2
    
    asyncio.run(serve(app, config))
