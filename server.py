#!/bin/python3

'''
readme
curl -X GET 127.0.0.1:8000 -v 
'''

from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import time
import socket, socketserver
from optparse import OptionParser
 
parse = OptionParser()
parse.add_option("-6", "--ipv6", action="store_false", dest="ipv6", help="run on ipv6")
parse.add_option("-m", "--mock", default="identify", dest="mock", help="run mock: identify, rewrite, weak, big_body")
parse.add_option("-p", "--port", default="8000", dest="port", help="listen port")
(options, args) = parse.parse_args()
print(options)
port = int(options.port)
host = ('0.0.0.0', port)
if options.ipv6 is not None:
    host = ('::', port)
    socketserver.TCPServer.address_family=socket.AF_INET6

data = {'result': 'this is a test'}
mock = options.mock
content_type = "json"
content_encoding = "none"

big_body_buf=""
if mock == "sensitive":
    content_encoding = "gzip"
#content_encoding = "gzip"
elif mock == "big_body":
    i = 0
    while len(big_body_buf) < 1024 * 1024 * 15:
        str = format(i, '08x')
        i += 8
        #print(str)
        big_body_buf += str
    print(len(big_body_buf))
    #print(big_body_buf)


print("run on: %s, filter: %s, content_type: %s, content_encoding: %s" % (host, mock, content_type, content_encoding))

 
class Resquest(BaseHTTPRequestHandler):
    timeout = 10
    server_version = "Apache"   #设置服务器返回的的响应头 

    def gzipencode(self, content):
        #from io import StringIO
        import io
        import gzip

        print(sys.getsizeof(content));
        c = gzip.compress(content.encode());
        print(sys.getsizeof(c));
        return c

    def resp_202(self):
        print(self.path)
        self.send_response(202)
        self.send_header("content-type","text/html")  #设置服务器响应头
        self.end_headers()

        buf = '''<!DOCTYPE HTML>
        <html>
            <head>
                <title>reload</title>  
                <script>
                    //location.reload(true);
                </script>
            </head>
            <body>
                Path:%s
                The request has been accepted.
            </body>
        </html>''' %(self.path)
        self.wfile.write(buf.encode())  #里面需要传入二进制数据，用encode()函数转换为二进制数据   #设置响应body，即前端页面要展示的数据

    def request_process(self):
        #time.sleep(1);
        #print(self.path)

        #print(self.headers['user-agent'])
        #print(self.headers['content-length'])
        #if self.headers['mock']
        #    mock = self.headers['mock']
        #print("mock %s" % $mock);
        self.send_response(200)
        if mock == "big_body":
            self.send_header("mock_mode", mock)     #设置服务器响应头
            self.send_header("set-cookie","lang=zh-cn; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")     #设置服务器响应头
            self.send_header("content-type","text/html; charset=utf-8")  #设置服务器响应头

            buf = big_body_buf
            self.send_header("content-length", len(buf))  #设置服务器响应头

        elif mock == "identify":
            login_token_position = self.headers['login_token_position']
            login_success = self.headers['login_success']
            print(login_token_position)

            content_type = "text/plain; charset=utf-8"
            buf = '''this is user identify response body'''
            if login_token_position == "header":
                self.send_header("token","eyj0exaioijkv1qilcjhbgcioijiuzi1nij9.eyjsyxqioje3mdq2otk0mdqsim5izii6mtcwndy5otqwncwizxhwijoxnza0nzg1oda0lcj1awqioii1ntailcj0exblijoidxnlciisinjhbmqioiixnza0njk5nda0dmnrztbwcgeifq.tpebdwaih2hemlnjeoytrjplufsdqfd6xnuq-f-6wpi")     #设置服务器响应头
                if login_success == "0":
                    print("set login failed: msg=ok")
                    self.send_header("msg","nok")
                else:
                    print("set login success: msg=ok")
                    self.send_header("msg","ok")
            elif login_token_position == "cookie":
                # login success
                if login_success == "0":
                    print("set login failed: msg=nok")
                    self.send_header("set-cookie","msg=nok; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")
                else:
                    print("set login success: msg=ok")
                    self.send_header("set-cookie","msg=ok; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")

                self.send_header("set-cookie","lang=zh-cn; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")     #设置服务器响应头
                self.send_header("set-cookie","username=davidlss; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")     #设置服务器响应头
                self.send_header("set-cookie","password=davidlss; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")     #设置服务器响应头
                self.send_header("set-cookie","emal=davidlss@126.com; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")     #设置服务器响应头
                self.send_header("set-cookie","token=eyj0exaioijkv1qilcjhbgcioijiuzi1nij9.eyjsyxqioje3mdq2otk0mdqsim5izii6mtcwndy5otqwncwizxhwijoxnza0nzg1oda0lcj1awqioii1ntailcj0exblijoidxnlciisinjhbmqioiixnza0njk5nda0dmnrztbwcgeifq.tpebdwaih2hemlnjeoytrjplufsdqfd6xnuq-f-6wpi; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")     #设置服务器响应头
            elif login_token_position == "xml":
                content_type = "application/xml; charset=utf-8"
                if login_success == "0":
                    print("set login failed: msg=nok")
                    buf = '''<html>
                                <token>j3699x5</token>
                                <password>j3699x5</password>
                                <tel>18576768895</tel>
                                <msg>nok</msg>
                            </html>'''
                else:
                    print("set login success: msg=ok")
                    buf = '''<html>
                                <token>j3699x5</token>
                                <password>j3699x5</password>
                                <tel>18576768895</tel>
                                <msg>ok</msg>
                            </html>'''
            elif login_token_position == "form":
                content_type = "application/x-www-form-urlencoded; charset=utf-8"
                if login_success == "0":
                    print("set login failed: msg=nok")
                    buf = '''account=davidxxx&msg=nok&token=807eac0385f8d1478b347102268543c6&referer=%252Fzentao%252Fmy.html&verifyRand=355530095'''
                else:
                    print("set login success: msg=ok")
                    buf = '''account=davidxxx&msg=ok&token=807eac0385f8d1478b347102268543c6&referer=%252Fzentao%252Fmy.html&verifyRand=355530095'''
            elif login_token_position == "form-data":
                content_type = "application/json; charset=utf-8"
                if login_success == "0":
                    print("set login failed: msg=nok")
                    buf = '''{"msg": "nok", "code":0,"data":{"ID":4,"UserName":"yanfa@ouryun.com.cn","IsEditPasswd":1,"Token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VyIjp7IklEIjoiNCIsIlVzZXJuYW1lIjoieWFuZmFAb3VyeXVuLmNvbS5jbiJ9LCJpc3MiOiJBdXRoX1NlcnZlciIsInN1YiI6InlhbmZhQG91cnl1bi5jb20uY24iLCJhdWQiOlsiV2ViX1NlcnZlciJdLCJleHAiOjE3NDA0NzE1OTEsImlhdCI6MTc0MDQ2NjE5MSwianRpIjoiaVl1NGdXIn0.2kg3GwIu2eJwRLdU0gS0860pEUfutnFOWRWb8VmtG3E"},"message":"ok"}'''
                else:
                    print("set login success: msg=ok")
                    buf = '''{"msg": "ok", "code":0,"data":{"ID":4,"UserName":"yanfa@ouryun.com.cn","IsEditPasswd":1,"Token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VyIjp7IklEIjoiNCIsIlVzZXJuYW1lIjoieWFuZmFAb3VyeXVuLmNvbS5jbiJ9LCJpc3MiOiJBdXRoX1NlcnZlciIsInN1YiI6InlhbmZhQG91cnl1bi5jb20uY24iLCJhdWQiOlsiV2ViX1NlcnZlciJdLCJleHAiOjE3NDA0NzE1OTEsImlhdCI6MTc0MDQ2NjE5MSwianRpIjoiaVl1NGdXIn0.2kg3GwIu2eJwRLdU0gS0860pEUfutnFOWRWb8VmtG3E"},"message":"ok"}'''
            else:
                content_type = "application/json; charset=utf-8"
                if login_success == "0":
                    print("set login failed: msg=nok")
                    buf = '''{"code":"200","msg":"nok","data":{"user_id":"550","username":"é²éªéª","email":"lushanshan@ouryun.com.cn","type":"user","rand":"1704699404vcke0ppa","mobile":"18576723035","token":"jcyj0exaioijkv1qilcjhbgcioijiuzi1nij9.eyjsyxqioje3mdq2otk0mdqsim5izii6mtcwndy5otqwncwizxhwijoxnza0nzg1oda0lcj1awqioii1ntailcj0exblijoidxnlciisinjhbmqioiixnza0njk5nda0dmnrztbwcgeifq.tpebdwaih2hemlnjeoytrjplufsdqfd6xnuq-f-6wpi","default_password":0,"change_password_days":"28","change_password_tips":""}}'''
                else:
                    print("set login success: msg=ok")
                    buf = '''{"code":"200","msg":"ok","data":{"user_id":"550","username":"é²éªéª","email":"lushanshan@ouryun.com.cn","type":"user","rand":"1704699404vcke0ppa","mobile":"18576723035","token":"jcyj0exaioijkv1qilcjhbgcioijiuzi1nij9.eyjsyxqioje3mdq2otk0mdqsim5izii6mtcwndy5otqwncwizxhwijoxnza0nzg1oda0lcj1awqioii1ntailcj0exblijoidxnlciisinjhbmqioiixnza0njk5nda0dmnrztbwcgeifq.tpebdwaih2hemlnjeoytrjplufsdqfd6xnuq-f-6wpi","default_password":0,"change_password_days":"28","change_password_tips":""}}'''

            self.send_header("content-type", content_type)  #设置服务器响应头

        elif mock == "weak":
            #self.send_header("test1","this is test!")     #设置服务器响应头
            #self.send_header("set-cookie","lang=zh-cn; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")     #设置服务器响应头
            #self.send_header("set-cookie","username=davidlss; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")     #设置服务器响应头
            #self.send_header("set-cookie","password=davidlss; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")     #设置服务器响应头
            #self.send_header("set-cookie","emal=davidlss@126.com; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")     #设置服务器响应头
            #self.send_header("content-type","application/json; charset=utf-8")  #设置服务器响应头
            #self.send_header("set-cookie","token=eyj0exaioijkv1qilcjhbgcioijiuzi1nij9.eyjsyxqioje3mdq2otk0mdqsim5izii6mtcwndy5otqwncwizxhwijoxnza0nzg1oda0lcj1awqioii1ntailcj0exblijoidxnlciisinjhbmqioiixnza0njk5nda0dmnrztbwcgeifq.tpebdwaih2hemlnjeoytrjplufsdqfd6xnuq-f-6wpi; expires=wed, 07-feb-2024 07:27:44 gmt; max-age=2592000; path=/zentao/")     #设置服务器响应头
            #buf = '''{"code":"200","msg":"ok","data":{"user_id":"550","username":"é²éªéª","email":"lushanshan@ouryun.com.cn","type":"user","rand":"1704699404vcke0ppa","mobile":"18576723035","token":"jcyj0exaioijkv1qilcjhbgcioijiuzi1nij9.eyjsyxqioje3mdq2otk0mdqsim5izii6mtcwndy5otqwncwizxhwijoxnza0nzg1oda0lcj1awqioii1ntailcj0exblijoidxnlciisinjhbmqioiixnza0njk5nda0dmnrztbwcgeifq.tpebdwaih2hemlnjeoytrjplufsdqfd6xnuq-f-6wpi","default_password":0,"change_password_days":"28","change_password_tips":""}}'''
            self.send_header("cache-control","no-cache")     #设置服务器响应头
            self.send_header("content-encoding","gzip")     #设置服务器响应头
            self.send_header("content-language","zh-CN")     #设置服务器响应头
            self.send_header("content-security-policy","object-src 'none';")     #设置服务器响应头
            self.send_header("content-type","text/javascript;charset=UTF-8")     #设置服务器响应头
            self.send_header("date", "Wed, 17 Apr 2024 09:18:14 GMT")
            self.send_header("pragma", "no-cache")
            self.send_header("server", "stone rhino")
            self.send_header("set-cookie", "rememberMe=deleteMe; Path=/; Max-Age=0; Expires=Tue, 16-Apr-2024 09:18:14 GMT; SameSite=lax")
            self.send_header("set-cookie", "rememberMe=deleteMe; Path=/; Max-Age=0; Expires=Tue, 16-Apr-2024 09:18:14 GMT; SameSite=lax")
            self.send_header("strict-transport-security", "max-age=31536000; includeSubDomains; preload")
            self.send_header("vary", "Accept-Encoding")
            self.send_header("x-content-type-options", "nosniff")
            buf = '''\r\n\r\n\r\n\r\n\r\n\r\n\r\n<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">\r\n<html>\r\n<head>\r\n    <meta charset=\"UTF-8\" http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">\r\n    <meta name=\"viewport\"\r\n          content=\"width=device-width,height=device-height,initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no\">\r\n    <title>深圳市疾病预防管理系统 </title>\r\n    \n\n\n\n\n\n\n<!-- easyui皮肤 -->\n<link href=\"/plugins/easyui/jquery-easyui-theme/default/easyui.css\" rel=\"stylesheet\" type=\"text/css\" />\n<link href=\"/plugins/easyui/jquery-easyui-theme/icon.css\" rel=\"stylesheet\" type=\"text/css\" />\n<link href=\"/plugins/easyui/icons/icon-all.css\" rel=\"stylesheet\" type=\"text/css\" />\n<!-- ztree样式 -->\n<link href=\"/plugins/ztree/css/zTreeStyle/zTreeStyle.css\" rel=\"stylesheet\" type=\"text/css\" />\n\n<script src=\"/plugins/easyui/jquery/jquery-3.6.4.min.js\"></script>\n\n<script src=\"/plugins/easyui/jquery-easyui-1.3.6/jquery.easyui.min.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jquery-easyui-1.3.6/locale/easyui-lang-zh_CN.js\" type=\"text/javascript\"></script>\n\n<!-- jquery扩展 -->\n<script src=\"/plugins/easyui/release/jquery.jdirk.min.js\"></script>\n\n<!-- easyui扩展 -->\n<link href=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.css\" rel=\"stylesheet\" type=\"text/css\" />\n\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.progressbar.js\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.slider.js\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.linkbutton.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.validatebox.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.combo.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.combobox.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.menu.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.searchbox.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.panel.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.window.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.dialog.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.layout.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.tree.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.datagrid.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.treegrid.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.combogrid.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.combotree.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.tabs.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.theme.js\" type=\"text/javascript\"></script>\n\n<!--<script src=\"/plugins/easyui/release/jeasyui.extensions.all.min.js\"></script>-->\n\n<script src=\"/plugins/easyui/icons/jeasyui.icons.all.js\" type=\"text/javascript\"></script>\n<!--<script src=\"/plugins/easyui/release/jeasyui.icons.all.min.js\"></script>-->\n\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.icons.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.gridselector.js\" type=\"text/javascript\"></script>\n\n<script src=\"/plugins/easyui/jeasyui-extensions/jquery.toolbar.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jquery.comboicons.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jquery.comboselector.js\" type=\"text/javascript\"></script>\n\n<script src=\"/plugins/easyui/jeasyui-extensions/jquery.portal.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jquery.my97.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/jeasyui.extensions.ty.js\"></script>\n<script src=\"/plugins/easyui/jeasyui-extensions/datagrid-detailview.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/echarts/echarts.min.js\"></script>\n<!-- ztree扩展 -->\n<script type=\"text/javascript\" src=\"/plugins/ztree/js/jquery.ztree.core-3.5.js\"></script>\n<script type=\"text/javascript\" src=\"/plugins/ztree/js/jquery.ztree.excheck-3.5.js\"></script>\n<script type=\"text/javascript\" src=\"/plugins/ztree/js/jquery.ztree.exedit.js\"></script>\n\n<link rel=\"stylesheet\" href=\"/plugins/easyui/common/other.css\"></link>\n<link rel=\"stylesheet\" href=\"/plugins/radio-checkbox/css/jquery-labelauty.css\"></link>\n<!-- filedset -->\n<link rel=\"stylesheet\" type=\"text/css\" href=\"/plugins/easyui/fieldset/fieldset.css\" />\n<script type=\"text/javascript\" src=\"/plugins/easyui/fieldset/fieldset.js\"></script>\n<script src=\"/plugins/My97DatePicker/WdatePicker.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/radio-checkbox/js/jquery-labelauty.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/commonJs/sinoUtil.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/commonJs/sinoCBX.js\" type=\"text/javascript\"></script>\n<script src=\"/js/fmtJs.js\" type=\"text/javascript\"></script>\n<script src=\"/plugins/commonJs/pinyin.js\" type=\"text/javascript\"></script>\n<script type=\"text/javascript\" src=\"//api.map.baidu.com/api?v=2.0&ak=znjGwg6cpOGitHF4XT9e43dPtS96D82x\"></script>\n\n<script>\nvar project=\"\";\nvar orgLevel = \"\";\nvar pCode=\"\",cCode=\"\",dCode=\"\",_orgCode=\"\",$orgId=\"\",$orgName=\"\";\nif(orgLevel==\"1\"){\n\tpCode=\"\".substring(0,2)+\"000000\";\n\tcCode=\"\".substring(0,4)+\"0000\";\n\t$orgName=\"\";\n}else if(orgLevel==\"2\"){\n\tpCode=\"\".substring(0,2)+\"000000\";\n\tcCode=\"\".substring(0,4)+\"0000\";\n\tdCode=\"\";\n\t$orgName=\"\";\n}else if(orgLevel==\"3\"){\n\tpCode=\"\".substring(0,2)+\"000000\";\n\tcCode=\"\".substring(0,4)+\"0000\";\n\tdCode=\"\";\n}else if(orgLevel==\"4\"){\n\tpCode=\"\";\n\tcCode=\"\";\n\tdCode=\"\";\n\torgLevel=\"4\";\n}else{\n\tpCode=\"\";\n\tcCode=\"\";\n\tdCode=\"\";\n\torgLevel=\"5\";\n}\n//全局的AJAX访问，处理AJAX清求时SESSION超时\n$.ajaxSetup({\n    contentType:\"application/x-www-form-urlencoded;charset=utf-8\",\n    complete:function(XMLHttpRequest,textStatus){\n          //通过XMLHttpRequest取得响应头，sessionstatus\n          var sessionstatus=XMLHttpRequest.getResponseHeader(\"sessionstatus\");\n          if(sessionstatus==\"timeout\"){\n               //跳转的登录页\n               parent.location.replace('/goto');\n       \t\t}\n    }\n});\n\n\n/**\n * 所有ajax请求url加上 随机数\n */\n$(document).ajaxSend(function(evt, request, settings) {\n\tif(settings.url && settings.url.indexOf('?') != -1) {\n\t\tsettings.url = settings.url.replace('?', '?' + Math.random() + '&');\n\t} else {\n\t\tsettings.url += '?' + Math.random();\n\t}\n});\n\nvar is360 = _mime(\"type\", \"application/vnd.chromium.remoting-viewer\");\n//判断mime\nfunction _mime(option, value) {\n  //debugger;\n  let mimeTypes = navigator.mimeTypes;\n  for (var mt in mimeTypes) {\n    console.log('type:',mimeTypes[mt][option]);\n    if (mimeTypes[mt][option] == value) {\n      return true;\n    }\n  }\n  return false;\n}\n\n\tfunction myBrowser() {\n\t\tvar userAgent = navigator.userAgent; //取得浏览器的userAgent字符串\n\t\tvar isOpera = userAgent.indexOf(\"Opera\") > -1; //判断是否Opera浏览器\n\t\tvar isIE = (userAgent.indexOf(\"compatible\") > -1\n\t\t\t\t&& userAgent.indexOf(\"MSIE\") > -1 && !isOpera); //判断是否IE浏览器\n\t\tvar isEdge = userAgent.indexOf(\"Edge\") > -1; //判断是否IE的Edge浏览器\n\t\tvar isFF = userAgent.indexOf(\"Firefox\") > -1; //判断是否Firefox浏览器\n\t\tvar isSafari = userAgent.indexOf(\"Safari\") > -1\n\t\t\t\t&& userAgent.indexOf(\"Chrome\") == -1; //判断是否Safari浏览器\n\t\tvar isChrome = userAgent.indexOf(\"Chrome\") > -1\n\t\t\t\t&& userAgent.indexOf(\"Safari\") > -1; //判断Chrome浏览器\n\t\tif (isIE) {\n\t\t\tvar reIE = new RegExp(\"MSIE (\\\\d+\\\\.\\\\d+);\");\n\t\t\treIE.test(userAgent);\n\t\t\tvar fIEVersion = parseFloat(RegExp[\"$1\"]);\n\t\t\tif (fIEVersion == 7) {\n\t\t\t\treturn \"IE7\";\n\t\t\t} else if (fIEVersion == 8) {\n\t\t\t\treturn \"IE8\";\n\t\t\t} else if (fIEVersion == 9) {\n\t\t\t\treturn \"IE9\";\n\t\t\t} else if (fIEVersion == 10) {\n\t\t\t\treturn \"IE10\";\n\t\t\t} else if (fIEVersion == 11) {\n\t\t\t\treturn \"IE11\";\n\t\t\t} else {\n\t\t\t\treturn \"0\";\n\t\t\t}//IE版本过低\n\t\t\treturn \"IE\";\n\t\t}\n\t\tif (isOpera) {\n\t\t\treturn \"Opera\";\n\t\t}\n\t\tif (isEdge) {\n\t\t\treturn \"Edge\";\n\t\t}\n\t\tif (isFF) {\n\t\t\treturn \"FF\";\n\t\t}\n\t\tif (isSafari) {\n\t\t\treturn \"Safari\";\n\t\t}\n\t\tif (isChrome) {\n\t\t\treturn \"Chrome\";\n\t\t}\n\n\t}\n\tif (!is360&&myBrowser()!='Chrome') {\n\t\twindow.location = \"/webbrowser\"\n\t}\n\n\t//hex 加密解密\n\tvar digitArray = new Array('0', '1', '2', '3', '4', '5', '6', '7', '8',\n\t\t\t'9', 'a', 'b', 'c', 'd', 'e', 'f');\n\tfunction toHex(n) {\n\t\tvar result = ''\n\t\tvar start = true;\n\t\tfor (var i = 32; i > 0;) {\n\t\t\ti -= 4;\n\t\t\tvar digit = (n >> i) & 0xf;\n\t\t\tif (!start || digit != 0) {\n\t\t\t\tstart = false;\n\t\t\t\tresult += digitArray[digit];\n\t\t\t}\n\t\t}\n\t\treturn (result == '' ? '0' : result);\n\t}\n\tfunction pad(str, len, pad) {\n\t\tvar result = str;\n\t\tfor (var i = str.length; i < len; i++) {\n\t\t\tresult = pad + result;\n\t\t}\n\t\treturn result;\n\t}\n\tfunction encodeHex(str) {\n\t\tvar result = \"\";\n\t\tfor (var i = 0; i < str.length; i++) {\n\t\t\tresult += pad(toHex(str.charCodeAt(i) & 0xff), 2, '0');\n\t\t}\n\t\treturn result;\n\t}\n\n\tfunction ntos(n) {\n\n\t\tn = n.toString(16);\n\n\t\tif (n.length == 1)\n\t\t\tn = \"0\" + n;\n\n\t\tn = \"%\" + n;\n\n\t\treturn unescape(n);\n\n\t}\n\n\tfunction decodeHex(str) {\n\t\tstr = str.replace(new RegExp(\"s/[^0-9a-zA-Z]//g\"));\n\t\tvar result = \"\";\n\t\tvar nextchar = \"\";\n\n\t\tfor (var i = 0; i < str.length; i++) {\n\t\t\tnextchar += str.charAt(i);\n\t\t\tif (nextchar.length == 2) {\n\t\t\t\tresult += ntos(eval('0x' + nextchar));\n\t\t\t\tnextchar = \"\";\n\t\t\t}\n\t\t}\n\t\treturn result;\n\t}\n</script>\n\r\n    <link href=\"/css/index.css\" rel=\"stylesheet\">\r\n    <link href=\"/css/style.css\" rel=\"stylesheet\">\r\n\r\n    <script>\r\n        function refreshCaptcha() {\r\n            document.getElementById(\"img_captcha\").src = \"/images/kaptcha.jpg?t=\" + Math.random();\r\n        }\r\n\r\n    </script>\r\n</head>\r\n\r\n\r\n<body>\r\n<form id='loginForm' name=\"loginForm\" action=\"/goto/blogin\" method=\"post\">\r\n\r\n    <div class=\"body-middle-new\">\r\n        <div class=\"logobj-new\">\r\n            <div class=\"logo-new\"><img src=\"/images/logo_03.png\"></div>\r\n        </div>\r\n        <div class=\"content-new bj\">\r\n            <div class=\"cont_right-new\">\r\n                <h2 class=\"form-title-new\">用户中心</h2>\r\n                <div class=\"input_box-new\">\r\n                    <div class=\"title-new\">账号：</div>\r\n                    <input id=\"uname\" name=\"username\" type=\"text\" placeholder=\"请输入用户名\"/>\r\n                    <div class=\"clear\"></div>\r\n                    <span class=\"err-new\" id=\"uname_text\"></span>\r\n                </div>\r\n                <div class=\"input_box-new\">\r\n                    <div class=\"title-new\">密码：</div>\r\n                    <input id=\"upass\" type=\"password\" name=\"password\" autocomplete=\"off\" placeholder=\"请输入密码\"/>\r\n                    <div class=\"clear\"></div>\r\n                    <span class=\"err-new\" id=\"upass_text\"></span>\r\n                </div>\r\n                <!-- <span id=\"bindPhone\"></span> -->\r\n                <div class=\"input_box-new\">\r\n                    <div class=\"title-new\">验证码：</div>\r\n                    <input id=\"verify\" type=\"text\" name=\"captcha\" placeholder=\"请输入验证码\" onKeyUp=\"verifyCodeLength(this.value)\"/>\r\n                    <div class=\"yzm-new\">\r\n                        <img src=\"/images/kaptcha.jpg\" width=\"130px\" height=\"42px\" title=\"点击更换\" id=\"img_captcha\"\r\n                             onclick=\"javascript:refreshCaptcha();\"/>\r\n                    </div>\r\n                    <div class=\"clear\"></div>\r\n                    <span class=\"err-new\" id=\"verify_text\">验证码错误！</span>\r\n                </div>\r\n                <div id=\"sbmitbtn\" class=\"input_boxan\">\r\n                    <button type=\"button\" class=\"btn btn-primary-new\" id=\"login_submit\" onclick=\"sub()\">登 录</button>\r\n                </div>\r\n\r\n            </div>\r\n        </div>\r\n    </div>\r\n</form>\r\n<form id='resetPwdForm' action=\"/goto/resetPwd\" method='get'></form>\r\n\r\n<!-- 验证 -->\r\n\r\n    \r\n    \r\n    \r\n    \r\n    \r\n    \r\n    \r\n\r\n\r\n<!-- 验证 end -->\r\n</body>\r\n\r\n<script src=\"/js/des.js?v=1.2\"></script>\r\n<script type=\"text/javascript\">\r\n    $(document).ready(function () {\r\n        $(\".js_form_input li input\").focus(function () {\r\n            $(this).parent(\".dbox\").addClass(\"dboxselect\").parents(\"li\").siblings().find(\".dbox\").removeClass(\"dboxselect\");\r\n            $(this).parents(\"li\").addClass(\"li-select\").siblings(\"li\").removeClass(\"li-select\");\r\n            $(this).css({\r\n                \"color\": \"#333\"\r\n            })\r\n        })\r\n        $(\".js_form_input li input\").blur(function () {\r\n            $(this).parent(\".dbox\").removeClass(\"dboxselect\");\r\n            $(this).parents(\"li\").removeClass(\"li-select\");\r\n        })\r\n    })\r\n\r\n    // 404：账户名不存在  200：操作成功   500：用户名或密码不正确\r\n    //\t$(\"#uname_text\").html(\"绑定手机号码成功，请重新登录！\");\r\n    /* //ajax方式提交绑定手机号\r\n    function bindPhoneForm() {\r\n        var data = $(\"#loginForm\").serializeObject();\r\n        $.post(\r\n            \"/goto/bindPhone\", //url\r\n\t\t\tdata, //data\r\n\t\t\tfunction(data) {//回调\r\n\t\t\t\tif (data.code == '200') {\r\n\t\t\t\t\t$(\"#sbmitbtn\").html('<button type=\"button\" class=\"btn btn-primary-new\"  id=\"login_submit\" onclick=\"sub()\">登   录</button>');\r\n\t\t\t\t\t$(\"#bindPhone\").html('');\r\n\t\t\t\t\talert(\"绑定手机号码成功，请重新登录！\");\r\n\t\t\t\t\t//location.href=\"/goto\";\r\n\t\t\t\t}else {\r\n\t\t\t\t\tdata.code == '404' ? alert(\"用户名或密码不正确1\"):alert(\"用户名或密码不正确2\");\r\n\t\t\t\t}\t\t\t\t\r\n\t\t\t}\r\n\t\t);\r\n\t} */\r\n\r\n    //表单提交方式登录\r\n    function sub() {\r\n        if ($('#uname').val() == '') {\r\n            $(\".login_main_errortip\").html(\"账号为空，请输入\");\r\n            $('#username').focus();\r\n            return;\r\n        } else if ($('#upass').val() == '') {\r\n            $(\".login_main_errortip\").html(\"密码为空，请输入\");\r\n            $('#upass').focus();\r\n            return;\r\n        } else {\r\n\t\t\t$(\"#upass\").val(strEnc($(\"#upass\").val()));\r\n            $('#loginForm').submit();\r\n        }\r\n    }\r\n\r\n    //回车时，默认是登陆\r\n    // function KeyDown() {\r\n    //     if (window.event.keyCode == 13) {\r\n    //         sub();\r\n    //     }\r\n    // }\r\n\r\n    $(function () {\r\n        $('body').height($(window).height());\r\n    });\r\n\r\n    var isLogin=true;\r\n    function verifyCodeLength(val) {\r\n        if (val.length == 5) {\r\n            if(isLogin){\r\n                isLogin=false;\r\n                sub();\r\n            }\r\n            // sub();  // auto-login prevention\r\n        }\r\n    }\r\n\r\n    function downBrowser() {\r\n        window.open(\"/plugins/file/77.0.3865.120_chrome_installer_32.exe\");\r\n// \t\twindow.location.href=\"\" \r\n    }\r\n\r\n</script>\r\n</html>\r\n'''
            if content_encoding == "gzip":
                buf = self.gzipencode(buf);

        elif mock == "rewrite":
            if content_type == "json":
                #self.send_header("Content-type","application/json")  #设置服务器响应头
                #self.send_header("Content-type","application/json; charset=utf-8")  #设置服务器响应头
                buf = '''
{
  "code": "200",
  "data": [
    {
      "card_number": "801965560726863160",
      "id": 1,
      "id_card": "430211197003276638",
      "name": "李志强",
      "password": "9P8RkhKU",
      "phone": "13277946127"
    },
    {
      "card_number": "883556997566547253",
      "id": 2,
      "id_card": "320703196112238427",
      "name": "刘刚",
      "password": "S336Pgwk",
      "phone": "18114911186"
    },
    {
      "card_number": "628834773563676902",
      "id": 3,
      "id_card": "450221196810193072",
      "name": "黄桂珍",
      "password": "45rkMkzN",
      "phone": "15054361089"
    },
    {
      "card_number": "65174779994373309",
      "id": 4,
      "id_card": "620800197611272285",
      "name": "孟桂芳",
      "password": "iIk3I9Gj",
      "phone": "13880147064"
    },
    {
      "card_number": "393958220775846404",
      "id": 5,
      "id_card": "331126198403177728",
      "name": "张梅",
      "password": "J9fCnsn1",
      "phone": "13827039177"
    },
    {
      "card_number": "46588861249588147",
      "id": 6,
      "id_card": "371203195909226165",
      "name": "鞠强",
      "password": "1Fl20Fc9",
      "phone": "13388211463"
    },
    {
      "card_number": "172448622447912426",
      "id": 7,
      "id_card": "340302196203244780",
      "name": "张楠",
      "password": "A04ZPw6j",
      "phone": "15641365823"
    },
    {
      "card_number": "237346033389661434",
      "id": 8,
      "id_card": "370401199609050415",
      "name": "王鹏",
      "password": "Q3vcNnme",
      "phone": "15090090722"
    },
    {
      "card_number": "749437687615447075",
      "id": 9,
      "id_card": "150521194908014120",
      "name": "刘瑞",
      "password": "6kkVeJ5J",
      "phone": "13466779692"
    },
    {
      "card_number": "311117161006230926",
      "id": 10,
      "id_card": "469029193608209292",
      "name": "徐秀英",
      "password": "OG6IcKOb",
      "phone": "15247797951"
    }
  ],
  "msg": "操作成功"
}

'''
        elif mock == "sensitive":
            self.send_header("Content-type","text/html")  #设置服务器响应头
            buf = '''
<!DOCTYPE HTML>
<html>
    <head>
        <title>Get page</title>
    </head>
    <body>
        <form action="post_page" method="post">
            username: <input type="text" name="username" /><br />
            password: <input type="text" name="password" /><br />
            <input type="submit" value="POST" />
            <text>some sensitive words</text>
            <br/>
            <phone> 18576723035 </phone>
        </form>
    </body>
</html>
'''
            if content_encoding == "gzip":
                buf = self.gzipencode(buf);
                self.send_header("Content-Encoding","gzip")
                self.send_header("Content-Length", sys.getsizeof(buf));
                
        else:
            #获取post提交的数据
            self.send_header("Content-type","text/html")  #设置服务器响应头
            datas = self.rfile.read(int(self.headers['content-length']))    #固定格式，获取表单提交的数据
            #datas = urllib.unquote(datas).decode("utf-8", 'ignore')
     
            buf = '''<!DOCTYPE HTML>
            <html>
                <head>
                    <title>Post page</title>  
                </head>
                <body>
                    Path:%s
                    Post Data:%s  <br />
                </body>
            </html>''' %(self.path, datas)


        self.end_headers()
        if content_encoding == "gzip":
            self.wfile.write(buf)  #里面需要传入二进制数据，用encode()函数转换为二进制数据   #设置响应body，即前端页面要展示的数据
        else:
            self.wfile.write(buf.encode())  #里面需要传入二进制数据，用encode()函数转换为二进制数据   #设置响应body，即前端页面要展示的数据

    def do_GET(self):
        print('----- headers start ----')
        print(self.headers)
        print('----- headers end ----')

        self.request_process();
        #self.resp_202();
 
    def do_POST(self):
        datas = self.rfile.read(int(self.headers['content-length']))
        print("\ndo post: %s, client_address: %s" % (self.path, self.client_address))

        print('----- headers start ----')
        print(self.headers)
        print('----- headers end ----')

        print('----- request body start ----')
        print(datas)
        print('----- request body end ----')

        self.request_process();
 
if __name__ == '__main__':

    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()