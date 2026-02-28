# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     add_bs_one
   Description :   
   Author :       世豪
   date：          2024/10/21
-------------------------------------------------
   Change Activity:
                   2024/10/21 下午7:13: 
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
# from templates.load.load_test import LoadTest
import asyncio
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


    def rsa_encrypt(self, password: str, publickey):
        """校验RSA加密 使用公钥进行加密"""
        public_key = publickey
        cipher = PKCS1_cipher.new(RSA.importKey(public_key))
        cipher_text = base64.b64encode(cipher.encrypt(password.encode())).decode()
        return cipher_text


    def user_login(self, ssh_ip, username, password):
        """
        新版本
        Returns:

        """
        # 获取uuid

        url = f"https://{ssh_ip}/api/v1.2/randString"

        payload = ""
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload, verify=False)

        # print(response.text)
        rand = json.loads(response.text)['data']['rand']
        if rand:
            # md5密码
            md5pwd = self.md5enc(password)
            # 组装json
            pre_enc_str = {
                'username': username,
                'password': md5pwd,
                'uuid': rand
            }
            # print(pre_enc_str)
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

    def hello(self):
        try:
            ulids = []
            for i in range(1, 6):
                uid = ulid.new()
                lowercase_ulid = str(uid).lower()
                ulids.append({"id": i, "ulid": lowercase_ulid})
            print(ulids)

            return ulids
        except Exception as e:
            print(e)
    def check(self,uid,check_path,check_code):
        token = self.user_login(self.sc_ip, self.user, self.sc_pwd)
        url = f"https://{self.sc_ip}/api/v1/healthCheck/{self.engine_id}"

        payload = json.dumps({
            "apiVersion": "dam.ouryun.com.cn/v1",
            "kind": "HealthCheck",
            "metadata": {
                "name": uid,
                "namespace": "default",
                "annotations": {
                    "username": "admin"
                }
            },
            "spec": {
                "commonInfo": {
                    "name": self.name,
                    "disabled": False,
                    "source": 0
                },
                "healthCheckSpecifier": {
                    "httpHealthCheck": {
                        "httpType": "HTTP1",
                        "path": check_path,
                        "expectedStatuses": check_code
                    },
                    "tcpHealthCheck": {},
                    "type": 2
                },
                "interval": 5,
                "timeout": 5,
                "unhealthyThreshold": 3,
                "healthyThreshold": 1
            }
        })
        headers = {
            'token': token,
            'Content-Type': 'application/json',
            'sr-engine-key':f'{self.engine_id}'
        }
        print(headers)

        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        print(json.loads(response.text))
        data1 = json.loads(response.text)
        if data1["code"] == 200:
            print("新增健康检查成功")

            return uid
        else:
            print(f"新增健康检查失败：{data1['message']}")

    def upstream(self,uid,uid1):
        token = self.user_login(self.sc_ip, self.user, self.sc_pwd)
        url = f"https://{self.sc_ip}/api/v1/upstream/{self.engine_id}"
        payload = json.dumps({
                  "apiVersion": "dam.ouryun.com.cn/v1",
                  "kind": "Upstream",
                  "metadata": {
                    "name": uid,
                    "namespace": "default",
                    "annotations": {
                      "type": "HTTP",
                      "service": "false",
                      "username": "admin",
                      "plugin": "false",
                      "lbAlg": "random"
                    },
                    "resourceVersion": "",
                    "labels": {}
                  },
                  "spec": {
                    "commonInfo": {
                      "description": "",
                      "disabled": False,
                      "name": self.name,
                      "modifier": 0
                    },
                    "connPoll": {
                      "maxConnections": -1,
                      "maxPendingRequests": -1,
                      "maxRequests": -1,
                      "maxRequestsPerConnection": 0,
                      "outboundSourceAddress": ""
                    },
                    "healthCheckRef": {
                      "name": uid1,
                      "namespace": "default",
                      "group": "dam.ouryun.com.cn",
                      "version": "v1",
                      "kind": "HealthCheck",
                      "resource": "healthchecks"
                    },
                    "runtimeStats": {
                      "status": 0,
                      "membershipHealthy": 1,
                      "membershipTotal": 1
                    },
                    "endpoints": [
                      {
                        "address": f"{self.bs_ip}",
                        "port": self.bs_port
                      }
                    ],
                    "lbAlg": 3,
                    "sslConfigurations": {
                      "allowRenegotiation": False,
                      "tlsMode": 0
                    },
                    "dnsResolver": {
                      "address": [],
                      "respectDnsTtl": False,
                      "dnsRefreshRate": 0
                    }
                  }
                })
        headers = {
            'token': token,
            'Sr-Engine-Key': f'{self.engine_id}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        data1 = json.loads(response.text)
        if data1["code"] == 200:
            print(f"新增业务成功")
            return uid
        else:
            print(f"新增业务失败：{data1['message']}")
    def vs(self,uid,uid1):
        token = self.user_login(self.sc_ip, self.user, self.sc_pwd)
        url = f"https://{self.sc_ip}/api/v1/vs/{self.engine_id}"
        count = 0
        form = json.dumps({
                        "disabled": False,
                        "isUp": True,
                        "name": "路由策略",
                        "play": True,
                        "behavior": "forwardAction",
                        "timeout": 0,
                        "caseSensitive": True,
                        "httpsRedirect": True,
                        "stripQuery": True,
                        "auto": True,
                        "responseCode": "2",
                        "redirect_val": "",
                        "Host_rewrite": "auto",
                        "upstreamGroupName": "",
                        "upstream": uid1,
                        "requestList": [],
                        "responseList": [],
                        "matchersForm": [
                            {
                                "caseSensitive": True,
                                "path_value": "/",
                                "methods": [],
                                "path_matchers": "prefix",
                                "parameterList": [],
                                "headList": []
                            }
                        ],
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
                        "id": 1268292976
                    }
                    )
        payload = json.dumps({
            "apiVersion": "dam.ouryun.com.cn/v1",
            "kind": "VirtualService",
            "metadata": {
                "annotations": {
                    "form": f"[{form}]",
                    "type": "HTTP",
                    "username": "admin"
                },
                "name": uid,
                "namespace": "default"
            },
            "spec": {
                "commonInfo": {
                    "disabled": False,
                    "name": self.name,
                },
                "domains": [
                    f"{self.gw_ip}:{self.gw_port}"
                ],
                "routes": [
                    {
                        "name": "01hvtk71gg7p7mw0mgcqk4h36f",
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
                        "headerManipulation": {},
                        "behavior": "forwardAction",
                        "id": 1268292976,
                        "disabled": False,
                        "commonInfo": {
                            "disabled": False,
                            "name": "路由策略"
                        },
                        "actionSpecifier": {
                            "forwardAction": {
                                "timeout": 0,
                                "hostRewriteSpecifier": {
                                    "type": 2,
                                    "auto": True
                                },
                                "pathRewriteSpecifier": {
                                    "type": 0
                                },
                                "upstreamSpecifier": {
                                    "type": 1,
                                    "upstreamRef": {
                                        "name": uid1,
                                        "namespace": "default",
                                        "group": "dam.ouryun.com.cn",
                                        "version": "v1",
                                        "kind": "Upstream",
                                        "resource": "upstreams"
                                    },
                                    "upstreamGroupRef": {
                                        "name": "",
                                        "namespace": "default",
                                        "group": "dam.ouryun.com.cn",
                                        "version": "v1",
                                        "kind": "UpstreamGroup",
                                        "resource": "upstreamgroups"
                                    }
                                }
                            },
                            "redirectAction": {},
                            "directResponseAction": {},
                            "type": 1
                        }
                    }
                ]
            }
        })
        headers = {
            'token': token,
            'Sr-Engine-Key': f'{self.engine_id}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        data1 = json.loads(response.text)
        if data1["code"] == 200:
            print("新增虚拟服务成功")
            return uid
        else:
            print(f"新增业务失败：{data1['message']}")
    def gw(self,uid,uid1):
        token = self.user_login(self.sc_ip, self.user, self.sc_pwd)
        url = f"https://{self.sc_ip}/api/v1/gw/{self.engine_id}"
        count = 0
        form = json.dumps({
                          "names": ["local"],
                          "disabled": False,
                          "version": "",
                          "name": self.name,
                          "description": "",
                          "listeners": [
                            {
                              "bindToPort": True,
                              "bindAddress": f"{self.gw_ip}",
                              "serverList": [
                                {
                                  "para": 0,
                                  "version": "TLS_AUTO",
                                  "requireClientCertificate": True,
                                  "virtualServices": [f"{uid1}"],
                                  "cipherSuites": [
                                    "[ECDHE-ECDSA-AES128-GCM-SHA256|ECDHE-ECDSA-CHACHA20-POLY1305]",
                                    "[ECDHE-RSA-AES128-GCM-SHA256|ECDHE-RSA-CHACHA20-POLY1305]",
                                    "ECDHE-ECDSA-AES128-SHA",
                                    "ECDHE-RSA-AES128-SHA",
                                    "AES128-GCM-SHA256",
                                    "AES128-SHA",
                                    "ECDHE-ECDSA-AES256-GCM-SHA384",
                                    "ECDHE-RSA-AES256-GCM-SHA384",
                                    "ECDHE-ECDSA-AES256-SHA",
                                    "ECDHE-RSA-AES256-SHA",
                                    "AES256-GCM-SHA384",
                                    "AES256-SHA"
                                  ],
                                  "sniDomains": [],
                                  "mergeSlashes": False,
                                  "skipXffAppend": False,
                                  "forward1": "HTTP",
                                  "forward2": "HTTP option",
                                  "plugin": "",
                                  "isPlugin": False,
                                  "timeoutDisable": False,
                                  "streamIdleTimeout": 300,
                                  "requestTimeout": 300,
                                  "requestHeadersTimeout": 30,
                                  "idleTimeout": 600,
                                  "maxConnectionDuration": "",
                                  "maxConnectionDurationType": "S"
                                }
                              ],
                              "tracingUpstreamName": "",
                              "accessLogUpstreamName": True,
                              "perConnectionBufferLimitBytes": "",
                              "perConnectionBufferLimitBytesType": "KB",
                              "bindPort": f"{self.gw_port}",
                              "caCertRef": ""
                            }
                          ]
                        }
                        )
        payload = json.dumps({
                          "apiVersion": "dam.ouryun.com.cn/v1",
                          "kind": "Gateway",
                          "metadata": {
                            "annotations": {
                              "form": f"{form}",
                              "username": "admin",
                              "description": ""},
                            "name": uid,
                            "namespace": "default"
                          },
                          "spec": {
                            "commonInfo": {
                              "description": "",
                              "disabled": False,
                              "name": self.name
                            },
                            "listeners": [
                              {
                                "bindPort": self.gw_port,
                                "bindToPort": True,
                                "bindAddress": f"{self.gw_ip}",
                                "mask": 0,
                                "options": {
                                  "perConnectionBufferLimitBytes": 1024
                                },
                                "gatewayServers": [
                                  {
                                    "id": 2112480183,
                                    "serverSpecifier": {
                                      "httpServer": {
                                        "accessLog": {
                                          "account": "admin",
                                          "upstreamRef": {
                                            "name": "access-log-service-upstream",
                                            "namespace": "default",
                                            "group": "dam.ouryun.com.cn",
                                            "version": "v1",
                                            "kind": "Upstream",
                                            "resource": "upstreams"
                                          }
                                        },
                                        "options": {
                                          "mergeSlashes": False,
                                          "xffClientSrcIPSource": 4,
                                          "xffAppendMode": 2,
                                          "timeoutDisable": False,
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
                                          }
                                        },
                                        "virtualServiceRefs": [
                                          {
                                            "name": uid1,
                                            "namespace": "default",
                                            "group": "dam.ouryun.com.cn",
                                            "version": "v1",
                                            "kind": "VirtualService",
                                            "resource": "virtualservices"
                                          }
                                        ]
                                      },
                                      "tcpServer": {},
                                      "type": 2
                                    },
                                    "sslConfigurations": {
                                      "requireClientCertificate": True,
                                      "tlsMode": 0,
                                      "sniDomains": []
                                    }
                                  }
                                ]
                              }
                            ],
                            "proxyNames": [
                              "default"
                            ],
                            "names": [
                              "local"
                            ]
                          }
                        }
                        )
        headers = {
            'token': token,
            'Sr-Engine-Key': f'{self.engine_id}',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        data1 = json.loads(response.text)
        if data1["code"] == 200:
            print("新增网关成功")
        else:
            print(f"新增网关失败：{data1['message']}")

    def recover(self):
        token = self.user_login(self.sc_ip, self.user, self.sc_pwd)
        url = f"https://{self.sc_ip}/api/v1/system/backup/recover?backup_id=1"

        payload = json.dumps({
            "backup_id": 1,
            "backup_type": 2
        })
        headers = {
            'token': token,
            'Content-Type': 'application/json'
        }
        try:
            response = requests.request("PUT", url, headers=headers, data=payload, verify=False)

            print(response.text)
            return json.loads(response.text)["data"]["backup_sn"]
        except Exception as e:
            print(e)
    def backup_process(self,sn):
        token = self.user_login(self.sc_ip, self.user, self.sc_pwd)

        url = f"https://{self.sc_ip}/api/v1/system/backup/recover/progress?backup_sn={sn}&source_type=2"

        payload = {}
        headers = {
            'token': token
        }
        try:
            while True:
                response = requests.request("GET", url, headers=headers, data=payload, verify=False)

                print(response.text)
                a=json.loads(response.text)["data"]["progress"]
                print(a)
                if a<100:
                    print(f"备份恢复进度{a}")
                    time.sleep(1)
                else:
                    return  False
        except Exception as e:
            print(e)
            return False

    def test(self):
            #获取uuid
            uuid = self.hello()
            print(uuid)
            #新增健康检查
            check_uid = self.check(uuid[0]['ulid'],self.check_path,self.check_code)
            # 新增业务
            upstream_uid = self.upstream(uuid[1]['ulid'], check_uid)
            #新增虚拟服务
            vs_uid = self.vs(uuid[2]['ulid'],upstream_uid)
            #新增网关
            self.gw(uuid[3]['ulid'],vs_uid)
            # for i in range(1,2):
            #     res = requests.get(f'http://{self.gw_ip}:{self.gw_port}/')
            #     print(res.text)
            url_request_map = {
                f"http://{self.gw_ip}:{self.gw_port}/json": 100,  # 第一个 URL 压测 5000 次
            }

            load_test =  LoadTest(
                            url_request_map=url_request_map,  # 传入 URL 和请求数的映射
                            method="GET",  # 请求方法
                            concurrent_users=20,  # 并发用户数
                            add_random_path=True  # 启用随机路径
                        )
            # 使用 asyncio 运行异步任务
            asyncio.run(load_test.run())


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

    ## 生成测试数据--单接口
    #res = {
    #    "sc_ip": "172.16.88.201",
    #    "sc_user":"admin",
    #    "sc_password":"root123.",
    #    "engine_id":1,
    #    "bs_ip":"192.192.101.155",  #业务ip
    #    "bs_port":8000, #业务端口
    #    "gw_ip":"172.16.88.159", #网关ip
    #    "gw_port":20001, #网关端口
    #    'name':'资产应用-拆分2', #业务名称
    #    'check_path': "/", #健康检查路径
    #    'check_code': [200,404]

    #}

    # 生成测试数据--单接口
    res = {
        "sc_ip": "192.168.11.11",
        "sc_user":"admin",
        "sc_password":"root123.",
        "engine_id":1,
        "bs_ip":"192.192.101.155",  #业务ip
        "bs_port":8000, #业务端口
        "gw_ip":"192.168.2.200", #网关ip
        "gw_port":20001, #网关端口
        'name':'资产应用-拆分2', #业务名称
        'check_path': "/", #健康检查路径
        'check_code': [200,404]
    }

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
        print(res)


    # 创建线程池，最大线程数为 20（可以根据实际情况调整）
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(run_test, range(1, 40))