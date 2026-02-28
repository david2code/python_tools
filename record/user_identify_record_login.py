#!/usr/bin/python3
#coding=utf-8
from optparse import OptionParser
import sys
import tty, termios
import os
import requests
import ata_parse

# 此脚本用于向ata查询数据
# 通过从文件中读取request_id和storage_time，然后构造 url 向ata进行查询
# 将查询结果进行解析，然后在终端展示

# curl "http://127.0.0.1:9903/query_raw?request_id=de9b778e-3f6b-459a-a531-887bc33f51a3&storage_time=1741338484"
ATA_URL = "http://127.0.0.1:9903/query_raw?"

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def process_file(filename):
    app_dict = dict()
    total_records = 0
    with open(filename, 'r') as file:
        for line in file:
            total_records += 1
            print(line)
            line = line.strip();
            lst = line.split(" ");
            print(lst);
            app_address = lst[0];
            downstream_ip = lst[1];
            value = { "request_id" : lst[2], "storage_time" : lst[3] }
            if app_address in app_dict:
                if downstream_ip in app_dict[app_address]:
                    app_dict[app_address][downstream_ip].append(value);
                else:
                    app_dict[app_address][downstream_ip] = [value]
                #print(app_address)
                #app_dict[app_address].append(value)
            else:
                app_dict[app_address] = { downstream_ip : [value] }

    
    print("total records: ", total_records)
    input()
    app_size = len(app_dict)
    app_pos = 0
    quit = False
    quit_app = False
    quit_ip = False
    for app_address, ip_dict in app_dict.items():
        #print("app_address: ", app_address)
        app_pos += 1
        ip_size = len(ip_dict)
        ip_pos = 0
        #input()
        for downstream_ip, lst in ip_dict.items():
            #print("  downstream_ip: ", downstream_ip)
            ip_pos += 1

            lst_size = len(lst)
            lst_pos = 0

            for item in lst:
                request_id = item["request_id"]
                storage_time = item["storage_time"]
                url = ATA_URL + "request_id=" + request_id + "&storage_time=" + storage_time
                lst_pos += 1

                os.system("clear")
                print("app_address: %s, (%d / %d)" % (app_address, app_pos, app_size))
                print("downstream_ip: %s, (%d / %d)" % (downstream_ip, ip_pos, ip_size))
                print("request_id: %s, storage_time: %s, (%d / %d)" % (request_id, storage_time, lst_pos, lst_size))
                print("url: ", url)

                response = requests.get(url)
                if response.status_code != 200:
                    print("query ata failed")
                else:
                    #print(response.status_code)
                    #print(response.url)
                    #print(response.content)
                    ata_parse.parseAtaResult(response.content)
                #print("\033[0;5H", end="")
                #sys.stdout.write("\033[5;10H")
                #sys.stdout.flush()

                ch = getch()
                #print(ch)
                if ch == 'j':
                    print("next")
                elif ch == 'k':
                    quit_ip = True
                elif ch == 'l':
                    quit_ip = True
                    quit_app = True
                elif ch == 'q':
                    quit = True
                    quit_ip = True
                    quit_app = True

                if quit_ip:
                    quit_ip = False
                    break
            if quit_app:
                quit_app = False
                break

        if quit:
            quit = False
            break

 
if __name__ == '__main__':
    parse = OptionParser()
    parse.add_option("-f", "--file", dest="filename", help="path to record file", metavar="FILE")
    (options, args) = parse.parse_args()
    #print(options)
    #print(args)
    if options.filename is None:
        parse.print_help()
        quit()
    if not os.path.exists(options.filename):
        print("record file: %s not exists" % options.filename);
        quit()
    process_file(options.filename);

