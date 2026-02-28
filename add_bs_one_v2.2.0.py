# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     add_bs_one_v2.2.0
   Description :   
   Author :       世豪
   date：          2025/6/18
-------------------------------------------------
   Change Activity:
                   2025/6/18 下午5:40: 
-------------------------------------------------
"""
__author__ = '世豪'
import requests
import ulid
import json
import base64
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
import urllib3
import time
import random
from concurrent.futures import ThreadPoolExecutor
import queue
urllib3.disable_warnings()
#from templates.load.load_test import LoadTest
import asyncio
import uuid
import os
import sys
import base64
from ddddocr import DdddOcr
from faker import Faker
fake_en = Faker('en_US')  # 英文Faker实例
fake_zh = Faker('zh_CN')  # 中文Faker实例
class Bs:
    def __init__(self, sc_ip, sc_user,sc_pwd,engine_id,bs_ip,bs_port,gw_ip,gw_port,name,check_path,check_code):
        self.public_key = """-----BEGIN PUBLIC KEY-----
        MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcu1sLod7mIz0EaYW7iM/glFNL
        kTFI5n87pFW/0Xv2UFUiPoFKiBagZ0NsBtPTKzFFimmqEdbj0W0O7wwoQ1bupTo8
        1qYm1EJ+Qc3REzmPyEJn9wof7vHvSlNdcIff6wJOOZ+Vqq08qK4p9HG73/8oKgVx
        Nw4cEJUnmqUqtAP31wIDAQAB
        -----END PUBLIC KEY-----"""

        self.sc_ip = sc_ip
        self.user = sc_user
        self.sc_pwd = sc_pwd
        self.engine_id = engine_id
        self.bs_ip = bs_ip
        self.bs_port = bs_port
        self.gw_ip = gw_ip
        self.gw_port = gw_port
        self.name = name
        self.check_path = check_path
        self.check_code = check_code


        pass


    def md5enc(self, in_str):
        """
        字符串MD5加密
        """
        md5 = hashlib.md5()
        md5.update(in_str.encode("utf8"))
        return md5.hexdigest()


    def rsa_encrypt(self, msg: str, publickey, max_length=100):
        """校验RSA加密 使用公钥进行加密"""
        cipher = PKCS1_cipher.new(RSA.importKey(publickey))
        res_byte = bytes()
        for i in range(0, len(msg), max_length):
            res_byte += cipher.encrypt(msg[i:i + max_length].encode('utf-8'))
        # cipher_text = base64.b64encode(cipher.encrypt(password.encode())).decode()
        return base64.b64encode(res_byte).decode('utf-8')
    def recognize_captcha_from_base64(self,base64_data):
        """
        识别base64，转换成具体验证码
        """

        # 从逗号处截取后面的base64字符串
        pure_base64 = base64_data.split(",")[1] if "," in base64_data else base64_data

        try:
            image_data = base64.b64decode(pure_base64)

            with open(os.devnull, 'w') as f:
                sys.stdout = f
                ocr = DdddOcr()
                sys.stdout = sys.__stdout__

            result = ocr.classification(image_data)
            return result

        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None
    def get_login_captcha_info(self,sc_ip):
        resposne = requests.get("https://{}/api/v1.2/captcha".format(sc_ip), verify=False)
        data = resposne.json()['data']
        return data['captcha'], data['id']

    def user_login(self, ssh_ip, username, password):
        """
        新版本
        Returns:

        """
        # 获取uuid
        try:

            url = f"https://{ssh_ip}/api/v1.2/randString"

            payload = ""
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload, verify=False)

            # print(response.text)
            rand = json.loads(response.text)['data']['rand']
            if rand:
                # md5密码
                md5pwd = self.md5enc(password)
                captcha_base64, captcha_id = self.get_login_captcha_info(self.sc_ip)
                captcha_code = self.recognize_captcha_from_base64(captcha_base64)
                # 组装json
                pre_enc_str = {
                    'username': username,
                    'password': md5pwd,
                    'uuid': rand,
                    "captcha": captcha_code,
                    "captchaId": captcha_id
                }
                # 公钥加密json
                res = self.rsa_encrypt(json.dumps(pre_enc_str), self.public_key)
                # print(res)
                url_login = "https://{}/api/v1.2/login".format(ssh_ip)
                payload = json.dumps(
                    {"info": res}
                )
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url_login, headers=headers, data=payload, verify=False)
                print(json.loads(response.text)['data']['token'])
                return json.loads(response.text)['data']['token']
                # if json.loads(response.text)['code'] == 200:
                #     print('登录成功')
                #     return json.loads(response.text)['data']['token']
                # else:
                #     return False
        except Exception as e:
            print(f"Error processing user: {str(e)}")


    def get_http_check(self):
        try:
            token = self.user_login(self.sc_ip, self.user, self.sc_pwd)
            url = f"https://{self.sc_ip}/api/v1/object/healthcheck/list?page=1&size=10000&order_direct=1&order_by=updated_at"
            payload = {}
            headers = {
                'token': token
            }

            response = requests.request("GET", url, headers=headers, data=payload, verify=False)
            id=[]

            data = json.loads(response.text)['data']['list']
            for i in data:
                if i['name'] ==  "HTTP健康检查（内置）":
                    id.append(i['ulid'])
            return id
        except Exception as e:
            print(e)


    def get_uuid_str(self):
        uuid4 = uuid.uuid4()  # 生成随机 UUID
        uuid_str = str(uuid4).replace('-', '')[:23]  # 去除 UUID 中的连字符并转换为字符串
        return "01j" + uuid_str


    def add_check(self,token):
        url = "https://192.192.101.16/api/v1/object/healthcheck"
        payload = json.dumps({
            "healthy_threshold": 3,
            "interval": 10,
            "kind": 2,
            "name": f"自动创建健康检查发布{fake_en.uuid4()}",
            "timeout": 10,
            "unhealthy_threshold": 3,
            "http_info": {
                "http_kind": 1,
                "path": "/",
                "expected_statuses": "200"
            }
        })
        headers = {
            'token': token,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload,verify=False)

        print(response.text)

    def create_app_proxy(self,sc_ip, token,engine_id, b_address='', b_port=0, l_ip='', l_port=0, app_name=None):
        """
        创建应用代理
        :param sc_ip: 总控ip 必填
        :param token: token 必填
        :param engine_id: 操作的引擎id 必填
        :param b_address: 业务ip 必填
        :param b_port: 业务端口 必填
        :param l_ip: 代理ip 必填
        :param l_port: 代理端口 必填
        :param app_name: 应用名称 不必填
        :return: 创建返回的应用代理IP，None就是没创建成功
        """

        url = f"https://{sc_ip}/app-proxies/app-proxy/create"
        app_id = self.get_uuid_str()
        check_id =self.get_http_check()
        payload = json.dumps({
            "app_id": app_id,
            "app_name": f"自动创建应用发布{fake_en.uuid4()}" if app_name is None else app_name,
            "mode": "ip",
            "upstream": {
                "endpoints": [
                    {
                        "address": str(b_address),
                        "port": int(b_port)
                    }
                ],
                "lb_alg": 1,
                "tls_options": {
                    "tls_mode": 0
                },
                "conn_options": {
                    "maxRequestsPerConnection": 0,
                    "maxConnections": 0,
                    "maxRequests": 0,
                    "maxPendingRequests": 0
                },
                "cors": {
                    "enabled": False
                },
                "health_check": check_id[0],
                "response_rewrite": {
                    "enabled": False,
                    "mode": 1,
                    "rules": [
                        {}
                    ]
                }
            },
            "listener": {
                "ip": str(l_ip),
                "port": int(l_port),
                "http_options": {
                    "mergeSlashes": True,
                    "streamIdleTimeout": {
                        "seconds": 300
                    },
                    "requestTimeout": {
                        "seconds": 300
                    },
                    "requestHeadersTimeout": {
                        "seconds": 30
                    },
                    "idleTimeout": {
                        "seconds": 600
                    },
                    "maxConnectionDuration": {
                        "seconds": 0
                    },
                    "timeoutDisable": True,
                    "xffClientSrcIPSource": 4,
                    "xffAppendMode": 2
                },
                "tls_options": {
                    "tls_mode": 0
                },
                "redirect_https": {
                    "enabled": False
                },
                "gateway_name": ""
            },
            "virtual_service": {
                "routes": [
                    {
                        "id": 0,
                        "name": fake_en.uuid4(),
                        "commonInfo": {
                            "name": f"路由转发{fake_en.uuid4()}",
                            "disabled": False
                        },
                        "matchers": [
                            {
                                "caseSensitive": True,
                                "pathSpecifier": {
                                    "type": 1,
                                    "prefix": "/"
                                },
                                "methods": [],
                                "headers": [],
                                "queryParameters": []
                            }
                        ],
                        "actionSpecifier": {
                            "type": 1,
                            "forwardAction": {
                                "timeout": 0,
                                "pathRewriteSpecifier": {},
                                "hostRewriteSpecifier": {}
                            }
                        },
                        "headerManipulation": {
                            "requestHeadersToRemove": [],
                            "responseHeadersToRemove": [],
                            "requestHeadersToAdd": [],
                            "responseHeadersToAdd": []
                        }
                    }
                ],
                "domains": [
                    f"{l_ip}:{l_port}"
                ]
            }
        })
        headers = {
            'token': token,
            'sr-engine-key': f'{engine_id}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload,verify=False)
            if response.status_code == 200:
                res = json.loads(response.text)
                if res['code'] == 200:
                    print(f'新增业务{self.name}成功，业务访问地址为{self.gw_ip}:{self.gw_port}')
                    return res['data']['app_id']
                else:
                    print(f'创建应用发布失败,原因：{res["message"]}')
                    return None

        except Exception as e:
            print(f"创建应用发布异常,原因：{e}")
            return None

    def test(self):
            token = self.user_login(self.sc_ip, self.user, self.sc_pwd)
            self.create_app_proxy(self.sc_ip,token,self.engine_id,self.bs_ip,self.bs_port,self.gw_ip,self.gw_port,self.name)
            # self.add_check(token)
            # for i in range(1,2):
            #     res = requests.get(f'http://{self.gw_ip}:{self.gw_port}/')
            #     print(res.text)
            # url_request_map = {
            #     f"http://{self.gw_ip}:{self.gw_port}/code/201": 1,  # 第一个 URL 压测 5000 次
            # }
            #
            # load_test =  LoadTest(
            #                 url_request_map=url_request_map,  # 传入 URL 和请求数的映射
            #                 method="GET",  # 请求方法
            #                 concurrent_users=20,  # 并发用户数
            #                 add_random_path=False  # 启用随机路径
            #             )
            # # 使用 asyncio 运行异步任务
            # asyncio.run(load_test.run())


if __name__ == '__main__':
    # scip = input("请输入你的总控ip：")
    # engine_id = input("请输入你的引擎id")
    # gw_ip = input("请输入你的网关ip")
    # 定义可能的词汇
    # 定义可能的词汇
    prefixes = [
        "CRM", "ERP", "HRM", "OA", "IMS", "SCM", "WMS", "TMS", "BPM", "CIMS", "EAM", "SaaS", "PaaS", "IaaS",
        "HRIS", "LMS", "TMS", "FSMS", "TAS", "EHR", "PMS", "QMS", "GRC", "WFM", "EDMS", "PMIS", "MMS", "VMS",
        "RMS", "FMS", "EAMS", "FSIS", "GSS", "KMS", "BRS", "SPS", "CCS", "SSO", "API", "DMS", "IMS", "BPS",
        "DSS", "FSS", "NMS", "BIM", "PIMS", "ITMS", "V2X", "LIMS", "RIS", "CMS", "DCS", "CPS", "ISMS", "WFS",
        "SIMS", "TAS", "BFS", "BES", "AMS", "PDS", "PDSMS", "RDS", "SHRMS", "QAS", "TAS", "VSS", "SMS",
        "RPA", "ERPIS", "HCM", "FAM", "CRMS", "HRDMS", "CCMIS", "EDSS", "ESS", "RMS", "CRMIS", "HRO",
        "S4HANA", "CPMS", "BMIS", "SDS", "TMA", "CMMI", "EDMS", "AMR", "WFA", "QIS", "S2P", "VST", "WCS"
    ]

    main_words = [
        "人力资源", "员工管理", "人事", "绩效考核", "人才招聘", "企业管理", "员工考勤", "薪资管理", "员工培训",
        "人事档案", "职位管理", "招聘管理", "薪酬福利", "工作流", "工作调度", "员工关系", "任务管理",
        "团队协作", "智能办公", "员工自助", "合同管理", "招聘计划", "考勤管理", "企业沟通", "员工满意度",
        "人事事务", "项目管理", "领导力管理", "培训课程", "职业发展", "工作效率", "员工健康", "劳动法管理",
        "招聘系统", "工作分配", "考核系统", "出勤管理", "工资结算", "组织结构", "数据分析", "离职管理",
        "异动管理", "绩效评估", "生产管理", "供应链管理", "采购管理", "信息安全", "员工服务", "知识管理",
        "跨部门协作", "智能调度", "生产调度", "安全管理", "质量控制", "调薪系统", "薪酬规划", "离职分析",
        "员工关系管理", "企业文化", "培训需求", "年度计划", "招聘流程", "员工心态", "预算管理", "工作规划",
        "决策支持", "人力分析", "绩效改进", "技能管理", "人才库", "业务流程", "团队绩效", "项目协作",
        "职业路径", "岗位分析", "智能诊断", "目标达成", "员工关怀", "企业沟通平台", "任务分配系统",
        "客户管理", "供应商管理", "产品研发", "数据流管理", "团队建设", "企业组织", "智能排班",
        "质量管理", "需求管理", "多层次管理", "员工自评", "招聘分析", "工时管理", "团队协作系统"
    ]

    suffixes = [
        "管理系统", "服务平台", "应用", "信息系统", "智能平台", "数据平台", "云平台", "决策支持系统",
        "流程管理系统", "工具", "助手", "工作平台", "在线平台", "数字化平台", "分析平台", "解决方案",
        "工作系统", "协同平台", "运营平台", "监控系统", "管理平台", "智能解决方案", "办公系统", "平台系统",
        "系统工具", "技术平台", "企业解决方案", "信息化系统", "资源管理系统", "数字系统", "云端平台",
        "移动平台", "智能管理", "线上平台", "资源配置平台", "绩效平台", "决策平台", "运营系统",
        "综合管理系统", "多功能平台", "大数据平台", "文档管理系统", "通讯平台", "系统平台", "智慧平台",
        "协同办公平台", "人事平台", "员工服务平台", "绩效管理平台", "任务协作平台", "服务管理系统",
        "财务管理系统", "资产管理平台", "人才发展平台", "数字工作平台", "业务管理系统", "智能办公系统",
        "数据分析系统", "企业信息系统", "统计平台", "职场工具", "办公自动化系统", "流程优化系统",
        "绩效考核系统", "智能服务平台", "管理支持平台", "绩效评估平台", "人力信息系统", "决策辅助平台",
        "数字化服务平台", "人员调度系统", "企业服务平台", "知识库系统", "多语言平台", "企业绩效平台",
        "在线服务平台", "任务调度系统", "多维分析平台", "智慧办公平台", "实时监控平台", "协同工作系统",
        "跨平台系统", "自动化系统", "招聘系统", "数据收集平台", "云计算平台", "团队管理平台"
    ]


    # 随机生成100个名称
    def generate_names(num=10000):
        names = []
        for _ in range(num):
            prefix = random.choice(prefixes)
            main_word = random.choice(main_words)
            suffix = random.choice(suffixes)
            name = f"{prefix}{main_word}{suffix}"
            names.append(name)
        return names


    generated_names = generate_names()

    # 生成测试数据--单接口
    #res = {
    #    "sc_ip": "192.168.11.11",
    #    "sc_user":"admin",
    #    "sc_password":"root123.",
    #    "engine_id":1,
    #    "bs_ip":"192.192.101.155",  #业务ip
    #    "bs_port":8000, #业务端口
    #    "gw_ip":"192.168.2.200", #网关ip
    #    "gw_port":20001, #网关端口
    #    'name':'资产应用-拆分2', #业务名称
    #    'check_path': "/", #健康检查路径
    #    'check_code': [200,404]
    #}

    # 生成测试数据--单接口
    res = {
        "sc_ip": "172.16.88.201",
        "sc_user":"admin",
        "sc_password":"root123.",
        "engine_id":1,
        "bs_ip":"192.192.101.104",  #业务ip
        "bs_port":20011, #业务端口
        "gw_ip":"192.168.2.200", #网关ip
        "gw_port":20100, #网关端口
        'name':'资产应用-拆分2', #业务名称
        'check_path': "/", #健康检查路径
        'check_code': [200,404]
    }

    ### 生成测试数据--单接口
    ##res = {
    ##    "sc_ip": "192.192.101.16",
    ##    "sc_user":"admin",
    ##    "sc_password":"root123.",
    ##    "engine_id":1,
    ##    "bs_ip":"192.192.101.16",  #业务ip
    ##    "bs_port":7005, #业务端口
    ##    "gw_ip":"192.192.100.191", #网关ip
    ##    'check_path': "/", #健康检查路径
    ##    'check_code': [200,404]

    ##}

    # 使用多线程并发处理
    # 创建一个队列来存储端口号，初始化时将一定范围的端口号放入队列中
    port_queue = queue.Queue()
    # 假设需要生成 多个端口号
    for i in range(20001, 20001+ 5000):
        port_queue.put(i)
    def run_test(i):
        # 从队列中获取一个端口号
        gw_port = port_queue.get()
        a = Bs(res["sc_ip"], res["sc_user"], res["sc_password"], res["engine_id"], res["bs_ip"], res["bs_port"],
               res["gw_ip"], gw_port, generated_names[i], res['check_path'], res['check_code'])
        a.test()



    # 创建线程池，最大线程数为 20（可以根据实际情况调整）
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(run_test, range(1, 5))