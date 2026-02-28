const http = require('http');

const server = http.createServer((req, res) => {
    // 对于SSE请求，需要设置正确的Content-Type和Cache-Control
    // 设置Content-Type头为text/event-stream，这是SSE所需的。
    // 设置Cache-Control头为no-cache，这将防止客户端缓存事件流。
    // 使用Connection: keep-alive，这将保持连接打开，直到服务器明确地关闭连接。
    res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Credentials': true,
        'Access-Control-Allow-Origin': '*'
    });

    // 每隔一定时间发送一次消息
    // 使用res.write()方法将新的数据发送到客户端。
    // 我们在数据前添加了data:前缀，这是SSE事件流所需的。
    // 最后，我们在每个事件之间添加了一个空行，这是SSE事件流规范要求的，以便客户端可以正确解析事件流
    setInterval(() => {
        const data = `data: ${new Date().toISOString()}`;
        res.write(data);
    }, 1000);

    // 当客户端断开连接时，清理资源
    req.on('close', () => {
        clearInterval(); // 清除定时器
        res.end(); // 结束响应
    });
});

server.listen(3000, () => {
    console.log('Server is running on port 3000');
});
