#!/usr/bin/python3
#coding=utf-8

import ssl

try:
    from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
except ImportError:
    import BaseHTTPServer
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("hello")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers();
        self.wfile.write(b"hello");

server_address = ('', 4443)
key_file = "cert2/server-key.pem"
cert_file = "cert2/server-cert.pem"

httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)

#context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(cert_file, key_file)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
#the_session = ssl.SSLSession
#print(the_session.timeout)
#context.session = the_session
#context.session_reused = True
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

#httpd.socket = ssl.wrap_socket(httpd.socket, server_side=True, keyfile=key_file, certfile=cert_file)

httpd.serve_forever()