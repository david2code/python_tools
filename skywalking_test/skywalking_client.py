from skywalking import agent, config

# ---------- 1. 初始化配置 ----------
config.init(
    agent_collector_backend_services='127.0.0.1:11800',   # OAP gRPC 地址
    agent_name='python-client',                     # 服务名
    agent_instance_name='instance-client',                   # 实例名
)

# ---------- 2. 启动 Agent（必须在 import requests 之前） ----------
agent.start()

# ---------- 3. 正常发请求（会被自动追踪） ----------
import requests

def call_downstream():
    url = 'http://127.0.0.1:1000/'
    # url = 'http://127.0.0.1:1000/get?hello=world'
    headers = {'X-Custom-Header': 'trace-demo'}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        print(f'Status: {resp.status_code}')
        print(f'Body: {resp.text[:200]}...')
    except Exception as e:
        print(f'Request failed: {e}')

if __name__ == '__main__':
    call_downstream()