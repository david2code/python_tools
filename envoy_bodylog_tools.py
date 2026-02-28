#!/usr/bin/python3
#coding=utf-8
from optparse import OptionParser
import sys
import tty, termios
import os
import json
import re
from full_access_log_pb2 import FullAccessLog
import chardet

# 此脚本用于读取并分析body.log
# 将结果输出
# TODO 支持按request_id搜索

class SearchLog: 
    def __init__(self, filename):
        self.filename_ = filename

    def getch(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


    def printBody(self, body):
        if len(body) >= 1 and len(body[0]) != 0:
            body_length=len(body[0])
            det = chardet.detect(body[0])
            s_data = body[0][:1500]
            encoding = det['encoding']
            print(encoding)
            print("body length: ", body_length)
            if encoding:
                try:
                    s_data = s_data.decode(det['encoding'], errors='replace')
                except:
                    print("decode error")
            else:
                print("unknown encoding")
            print(repr(s_data))

    def show_proto(self, proto_data):
        log = FullAccessLog()
        log.ParseFromString(proto_data)

        os.system("clear")
        print(f"-------------------------proto start----------------------------------------------")
        print(f"request_id:\t {log.request_id}")
        print(f"node_id:\t {log.node_id}")
        print(f"engine_type:\t {log.engine_type}")
        print(f"plugin_hit:\t {log.plugin_hit}")

        print(f"-------------------------connection info start")
        print(f"downstream_remote_address:\t\t {log.connection_info.downstream_remote_address}")
        print(f"downstream_local_address:\t\t {log.connection_info.downstream_local_address}")
        print(f"downstream_direct_remote_address:\t {log.connection_info.downstream_direct_remote_address}")
        print(f"upstream_host:\t\t\t {log.connection_info.upstream_host}")
        print(f"upstream_local_address:\t\t {log.connection_info.upstream_local_address}")
        print(f"virtual_cluster_name:\t\t {log.connection_info.virtual_cluster_name}")
        print(f"route_name:\t\t\t {log.connection_info.route_name}")
        print(f"upstream_cluster:\t\t {log.connection_info.upstream_cluster}")
        print(f"start_time:\t\t\t {log.connection_info.start_time}")
        print(f"duration:\t\t\t {log.connection_info.duration}")
        print(f"request_duration:\t\t {log.connection_info.request_duration}")
        print(f"request_tx_duration:\t\t {log.connection_info.request_tx_duration}")
        print(f"response_duration:\t\t {log.connection_info.response_duration}")
        print(f"response_tx_duration:\t\t {log.connection_info.response_tx_duration}")
        print(f"bytes_received:\t\t {log.connection_info.bytes_received}")
        print(f"bytes_sent:\t\t {log.connection_info.bytes_sent}")
        print(f"listener_stat_prefix:\t\t {log.connection_info.listener_stat_prefix}")
        print(f"origin_host:\t\t {log.connection_info.origin_host}")

        print(f"-------------------------user_info start")
        print(f"unique_id:\t\t {log.user_info.unique_id}")
        print(f"name:\t\t {log.user_info.name}")
        print(f"app_id:\t\t {log.user_info.app_id}")
        print(f"rule_id:\t\t {log.user_info.rule_id}")
        print(f"-------------------------request start")
        print(f"{log.request.raw_start_line}")
        print(f"{log.request.raw_headers}")
        self.printBody(log.request.raw_body)

        print(f"-------------------------response start")
        print(f"{log.response.raw_start_line}")
        print(f"{log.response.raw_headers}")
        self.printBody(log.response.raw_body)

        print(f"-------------------------proto end----------------------------------------------")
        print("")

    def process(self):
        quit = False
        with open(self.filename_, 'rb') as file:
            while True:
                length_data = file.read(4)
                length = int.from_bytes(length_data, byteorder='big', signed=False)
                #length = 2147483653
                #print("length: %d" % length)
                if length <= 0:
                    break
                if length & 0x80000000:
                    print("slice")
                    i = 0
                    proto_data = b""
                    length -= 0x80000000
                    print("length: ", length)
                    while True:
                        if i != 0:
                            print("file pos: ", file.tell())
                            length_data = file.read(4)
                            length = int.from_bytes(length_data, byteorder='big', signed=False)
                            length -= 0x80000000
                            print("other_length: ", length)

                        id = file.read(16)
                        print("id: ", id)
                        total_slices_data = file.read(2)
                        total_slices = int.from_bytes(total_slices_data, byteorder='big', signed=False)
                        print("total_slices: ", total_slices)
                        cur_slices_data = file.read(2)
                        cur_slices = int.from_bytes(cur_slices_data, byteorder='big', signed=False)
                        print("cur_slices: ", cur_slices)
                        proto_data += file.read(length)
                        i += 1

                        if cur_slices + 1 >= total_slices:
                            print("last one")
                            break
                else:
                    proto_data = file.read(length)
                #print("proto len: %d" % len(proto_data))
                self.show_proto(proto_data)
                ch = self.getch()

                if ch == 'q':
                    return
            return

if __name__ == '__main__':
    parse = OptionParser()
    parse.add_option("-f", "--file", dest="filename", help="path to body log file", metavar="FILE")
    (options, args) = parse.parse_args()
    #print(options)
    #print(args)
    if options.filename is None:
        parse.print_help()
        sys.exit()
    if not os.path.exists(options.filename):
        print("record file: %s not exists" % options.filename);
        sys.exit()

    search = SearchLog(options.filename);
    search.process();

