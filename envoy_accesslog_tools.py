#!/usr/bin/python3
#coding=utf-8
from optparse import OptionParser
import sys
import tty, termios
import os
import requests
import json
import re
import subprocess

# 此脚本用于读取并分析过滤access.log
# 将结果输出

class SearchLog: 
    def __init__(self, filename):
        self.log_key_list_ = []
        self.search_key_info_ = dict()
        self.filename_ = filename
        self.init()

    def init(self):
        ## 如果envoy配置access_log有修改，则复制过来
        json_template = """
{
    "l": [
                  [
                   "%START_TIME(%s.%9f)%",
                   "%PROTOCOL%",
                   "%REQ(:SCHEME)%",
                   "%REQ(:METHOD)%",
                   "%REQ(HOST)%",
                   "%REQ(:AUTHORITY)%",
                   "%REQ(:PATH)%",
                   "%REQ(USER-AGENT)%",
                   "%REQ(X-ENVOY-ORIGINAL-PATH)%",
                   "%REQ(REFERER)%",
                   "%REQ(X-FORWARDED-FOR)%",
                   "%REQ(X-FORWARDED-HOST)%",
                   "%REQ(CONTENT-TYPE)%",
                   "%REQ(ACCEPT)%",
                   "%REQUEST_HEADERS_BYTES%",
                   "%BYTES_RECEIVED%",
                   "%REQ(x-request-id)%"
                  ],
                  [
                   "%RESPONSE_CODE%",
                   "%RESPONSE_CODE_DETAILS%",
                   "%RESP(CONTENT-TYPE)%",
                   "%RESPONSE_HEADERS_BYTES%",
                   "%BYTES_SENT%",
                   "%RESPONSE_TRAILERS_BYTES%"
                  ],
                  [
                   "%DOWNSTREAM_REMOTE_ADDRESS%",
                   "%DOWNSTREAM_LOCAL_ADDRESS%",
                   "%DOWNSTREAM_DIRECT_REMOTE_ADDRESS%",
                   "%UPSTREAM_HOST%",
                   "%UPSTREAM_LOCAL_ADDRESS%",
                   "%DURATION%",
                   "%VIRTUAL_CLUSTER_NAME%",
                   "%ROUTE_NAME%",
                   "%UPSTREAM_CLUSTER%",
                   "%DYNAMIC_METADATA(envoy.access_loggers.grpc.filter_access_log)%",
                   "%REQUEST_DURATION%",
                   "%REQUEST_TX_DURATION%",
                   "%RESPONSE_DURATION%",
                   "%RESPONSE_TX_DURATION%"
                  ]
     ]
 }
 """

        template = json.loads(json_template)
        template = template["l"]
        max_len = 0
        for i in range(len(template)):
            lst = []
            for j in range(len(template[i])):
                key = template[i][j]
                #print(key)
                if key.find("START_TIME") != -1:
                    key = "START_TIME"
                else:
                    pattern = r"\((.*)\)"
                    match = re.search(pattern, key)
                    if match:
                        #print("match start: ", match.group(1))
                        key = match.group(1)
                    else:
                        pattern = r"%(.*)%"
                        match = re.search(pattern, key)
                        if match:
                            #print("match start: ", match.group(1))
                            key = match.group(1)
                        else:
                            print("template parse error")
                            return

                lst.append(key)
                if len(key) > max_len:
                    max_len = len(key)
            self.log_key_list_.append(lst)

        for i in range(len(self.log_key_list_)):
            for j in range(len(self.log_key_list_[i])):
                key = self.log_key_list_[i][j]
                if key == "HOST":
                    self.search_key_info_["host"] = {"xpos" : i, "ypos" : j, "value" : ""}
                elif key == "DOWNSTREAM_REMOTE_ADDRESS":
                    self.search_key_info_["downstream_ip"] = {"xpos" : i, "ypos" : j, "value" : ""}

                if len(key) < max_len:
                    self.log_key_list_[i][j] = key + ' ' * (max_len - len(key))

    def getch(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


    def update_search_key(self):
        while True:
            os.system("clear")
            print("根据如下条件过滤日志(各条件之间是与关系，如果为空，则不生效):")
            print("1. 客户端ip(%s)" % self.search_key_info_["downstream_ip"]["value"])
            print("2. 应用Host(%s)" % self.search_key_info_["host"]["value"])
            print("q. 退出")
            print("输入数字，进行输入或编辑")
            ch = self.getch()
            if ch == '1':
                print("输入客户端ip:")
                self.search_key_info_["downstream_ip"]["value"] = input()
            elif ch == '2':
                print("输入应用Host:")
                self.search_key_info_["host"]["value"] = input()
            elif ch == 'q':
                break;

    def print_search_info(self):
        if self.search_key_info_['downstream_ip']['value']:
            print(f"匹配客户端ip: {self.search_key_info_['downstream_ip']['value']}")
        if self.search_key_info_['host']['value']:
            print(f"匹配Host: {self.search_key_info_['host']['value']}")
        print(f"当前行号 (%d / %d)" % (self.current_line_ + 1, self.total_lines_))


    def single_match(self, record, key):
        value = self.search_key_info_[key]["value"]
        if value:
            #print(value)
            xpos = self.search_key_info_[key]["xpos"]
            ypos = self.search_key_info_[key]["ypos"]
            if record[xpos][ypos] is None or record[xpos][ypos].find(value) == -1:
                return False
        return True

    def match(self, record):
        if not self.single_match(record, "downstream_ip"):
            return False
        if not self.single_match(record, "host"):
            return False
        return True

    def check_and_display(self, line):
        line = line.strip();
        record = json.loads(line)
        #print(line)
        record = record["l"]

        if not self.match(record):
            #print("not match")
            return "next"

        if len(record) != len(self.log_key_list_):
            print("error, log message not match")
            return "error"
        for i in range(len(record)):
            if len(record[i]) != len(self.log_key_list_[i]):
                print("error, log message not match")
                return "error"
            for j in range(len(record[i])):
                if record[i][j] is None :
                    record[i][j] = self.log_key_list_[i][j] + ": null"
                else:
                    record[i][j] = self.log_key_list_[i][j] + ": " +  str(record[i][j])

        os.system("clear")
        self.print_search_info()
        print(json.dumps(record, indent=2));
        return "input"

    def print_help(self):
        os.system("clear")
        print("用法提示: ")
        print("  n:  跳至下一个匹配行")
        print("  p:  跳至上一个匹配行")
        print("  /:  设置过滤条件")
        print("  q:  退出软件")
        print("  h:  输出用法")
        print("  输入任意字符退出本提示")
        self.getch()

    def process(self):
        line_pos = [0]
        self.current_line_ = 0

        quit = False
        last_find_line = 0
        side_find = False
        self.print_help()
        #print(log_key_list)

        cmd = "cat {} | wc -l".format(self.filename_)
        output = subprocess.check_output(cmd, shell=True)
        output = output.strip()
        self.total_lines_ = int(output.decode('utf-8'))

        with open(self.filename_, 'r') as file:
            file.seek(0, 2)
            file_end_pos = file.tell()
            direction = 'n'
            while True:
                if self.current_line_ < len(line_pos):
                    pos = line_pos[self.current_line_]
                else:
                    print("self.current_line_ error: %d, line_pos length: %d", self.current_line_, len(line_pos))
                    return

                #print("file pos: ", pos)
                file.seek(pos)
                line = file.readline()
                #print(line)
                if (self.current_line_ + 1) == len(line_pos):
                    next_pos = file.tell()
                    #print("file now pos: ", next_pos)
                    if next_pos != file_end_pos:
                        line_pos.append(next_pos)
                ret = self.check_and_display(line)
                if side_find:
                    print("Last find!!!")
                    ret = "input"

                if ret == "error":
                    return
                elif ret == "next":
                    ch = direction
                elif ret == "input":
                    ch = self.getch()
                    last_find_line = self.current_line_

                #print(ch)
                if ch == 'n':
                    #print("next")
                    direction = ch
                    side_find = False
                    if (self.current_line_ + 1) == self.total_lines_:
                        self.current_line_ = last_find_line
                        side_find = True
                        #input()
                    else:
                        self.current_line_ += 1
                    #print(self.current_line_)
                elif ch == 'p':
                    direction = ch
                    side_find = False
                    #print("previous")
                    if self.current_line_ == 0:
                        #print("At the file start line!!!!")
                        self.current_line_ = last_find_line
                        side_find = True
                        #input()
                    else:
                        self.current_line_ -= 1
                elif ch == '/':
                    self.update_search_key()
                elif ch == 'h':
                    self.print_help()
                elif ch == 'q':
                    return
            return

if __name__ == '__main__':
    parse = OptionParser()
    parse.add_option("-f", "--file", dest="filename", help="path to access log file", metavar="FILE")
    (options, args) = parse.parse_args()
    #print(options)
    #print(args)
    if options.filename is None:
        parse.print_help()
        quit()
    if not os.path.exists(options.filename):
        print("record file: %s not exists" % options.filename);
        quit()

    search = SearchLog(options.filename);
    search.process();

