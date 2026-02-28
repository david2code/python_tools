#!/bin/python3
from optparse import OptionParser
import sys
import os
import time
import base64
from haralyzer import HarParser
from http.client import HTTPConnection
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote
server_host = ('0.0.0.0', 8000)
server_response_map = {}

class Request(BaseHTTPRequestHandler):
    timeout = 5
    server_version = "Apache"   #设置服务器返回的的响应头 
    def gzipencode(self, content):
        #from io import StringIO
        import io
        import gzip

        #print(sys.getsizeof(content));
        c = gzip.compress(content);
        #print(sys.getsizeof(c));
        return c
    def request_process(self, method):
        path = self.path
        #print(self.path)
        #print(method)
        item = server_response_map.get(method + "_" + path)
        if not item:
            print("request: %s %s not found" % (method, path))
            self.send_response(404)
            self.send_header("Content-type","text/html")  #设置服务器响应头
            self.end_headers()
            buf = "request path not found"
            self.wfile.write(buf.encode())
        else:
            self.send_response(item['status'])

            encoding = None
            for header in item['headers']:
                name = header['name']
                if name == "content-encoding":
                    encoding = header['value']
                self.send_header(name.title(), header['value'])

            self.end_headers()

            buf = item['content']
            #print(type(buf))
            if encoding == "gzip":
                buf = self.gzipencode(buf);
            self.wfile.write(buf)

    def do_GET(self):
        self.request_process("GET");
 
    def do_POST(self):
        self.request_process("POST");

def server_process(entries):
    for entry in  entries:
        url = entry['request']['url']
        parsed_url = urlparse(url)
        #print("scheme: ", parsed_url.scheme)
        #print("netloc: ", parsed_url.netloc)
        #print("path: ", parsed_url.path)
        #print("params: ", parsed_url.params)
        #print("query: ", parsed_url.query)
        method = entry['request']['method']
        path = parsed_url.path 
        query = parsed_url.query
        if query:
            path += "?" + parsed_url.query
        headers = {}
        # headers
        for header in entry['request']['headers']:
            #print(header)
            name = header['name']
            if name == ":method":
                method = header['value']
            elif name == ":path":
                path = header['value']

            if not method and not path:
                break

        item = {}
        item['status'] = entry['response']['status']
        item["headers"] = entry['response']['headers']
        content = ""
        content_encoding = None
        if entry['response']['content']:
            content = entry['response']['content'].get('text')
            content_encoding = entry['response']["content"].get("encoding")
        if content and content_encoding == "base64":
            item["content"] = base64.b64decode(content)
        else:
            if not content:
                content = ""
            item["content"] = content.encode()

        server_response_map[method + "_" + path] = item;


    #print(server_response_map)
    #quit()
    server = HTTPServer(server_host, Request)
    print("Starting server, listen at: %s:%s" % server_host)
    server.serve_forever()
    print()

def http_request(host, port, method, path, body, headers):
    print("request: ", method, "", path);
    if body:
        print("   body:", body)
    conn = HTTPConnection(host, port)
    conn.request(method, path, body=body, headers=headers)
    response = conn.getresponse()
    conn.close()
    #time.sleep(1)
    print("response: ", response.status, response.reason)
    print()

def client_process(entries):
    index = 1
    for entry in  entries:
        #print(entry['connection'])
        #if entry['connection'] != "136736":
        #    continue
        print("Request ", index)
        index += 1
        url = entry['request']['url']
        parsed_url = urlparse(url)
        #print("scheme: ", parsed_url.scheme)
        #print("netloc: ", parsed_url.netloc)
        #print("path: ", parsed_url.path)
        #print("params: ", parsed_url.params)
        #print("query: ", parsed_url.query)
        method = entry['request']['method']
        path = parsed_url.path 
        query = parsed_url.query
        # for debug
        #if path != "/images/blank.gif":
        #if path != "/heicha/mw/abclite-2063-s.original.js":
        #    continue
        if query:
            path += "?" + parsed_url.query
        headers = {}
        # headers
        for header in entry['request']['headers']:
            #print(header)
            name = header['name']
            if name[0:1] != ":":
                #print(header['value'])
                headers[name.title()] = header['value']
            #print(header['name'])
            #print(header.value)
        # TODO queryString
        # cookies
        #cookie_str=""
        #for cookie in entry['request']['cookies']:
        #    ck = cookie['name'] + "=" + cookie['value']
        #    if not cookie_str:
        #        cookie_str = ck
        #    else:
        #        cookie_str += "; " + ck
        #print(cookie_str)
        #if not cookie_str:

        body = None
        if method == "POST":
            body = entry['request']['postData']['text']

        http_request(host, port, method, path, body, headers)
        #time.sleep(1)
        #print(headers)

if __name__ == '__main__':
    parse = OptionParser()
    parse.add_option("-f", "--file", dest="filename", help="path to har file", metavar="FILE")
    parse.add_option("-s", "--server", action="store_true", dest="server", default=False, help="run as server")
    (options, args) = parse.parse_args()
    print(options)
    #print(args)
    if options.filename is None or options.server is None:
        parse.print_help()
        quit()
    if not os.path.exists(options.filename):
        print("har file: %s not exists" % options.filename);
        quit()

    har_parser = HarParser.from_file(options.filename)
    har_data = har_parser.har_data
    host = "127.0.0.1"
    port = 8000
    print("total requests: ", len(har_data['entries']))

    if options.server:
        server_process(har_data['entries'])
    else:
        client_process(har_data['entries'])

        #quit()
