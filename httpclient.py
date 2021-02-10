#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def __init__(self):
        self.code_desc = {
            200: "OK",
            301: "Moved Permanently",
            404: "Not Found"
        }

    def get_host_port(self, url):
        host_port = urllib.parse.urlparse(url)
        host = host_port.hostname
        port = host_port.port

        if port is None:
            return (host, 80)
        else:
            return (host, port)

    def get_path(self, url):
        path = urllib.parse.urlparse(url).path
        if len(path) == 0:
            return "/"
        else:
            return path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def print_response(self, code, headers, body):
        print(f"HTTP/1.1 {code} {self.code_desc.get(code, '')}")
        for k, v in headers.items():
            print(f"{k}: {v}")
        print()
        print(body)

    def get_code(self, data):
        return int(data.split("\r\n")[0].split(" ")[1])

    def get_headers(self, data):
        headers = dict()
        first_line = True
        for line in data.split("\r\n"):
            if line == "":
                break
            elif first_line:
                first_line = False
                continue

            k, v = line.split(": ")
            headers[k.strip()] = v.strip()
        return headers

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def send_request(self, request_arr, body=""):
        request = "\r\n".join(request_arr) + "\r\n\r\n" + body
        self.sendall(request)

        data = self.recvall(self.socket)
        self.close()

        code = self.get_code(data)
        headers = self.get_headers(data)
        body = self.get_body(data)

        self.print_response(code, headers, body)

        return HTTPResponse(code, body)

    def GET(self, url, args=None):
        host, port = self.get_host_port(url)
        self.connect(host, port)

        request_arr = [
            f"GET {self.get_path(url)} HTTP/1.1",
            f"Host: {host}",
            f"Connection: close"
        ]

        return self.send_request(request_arr)

    def POST(self, url, args=None):
        host, port = self.get_host_port(url)
        self.connect(host, port)

        body = ""
        if args is not None:
            # Code from user João Almeida https://stackoverflow.com/u/4141980, 
            # at https://stackoverflow.com/a/53865188
            for i, (k, v) in enumerate(args.items()):
                body += f"{k}={v}"
                if i < len(args.items()) - 1:
                    body += "&"

        request_arr = [
            f"POST {self.get_path(url)} HTTP/1.1",
            f"Host: {host}",
            f"Content-Type: application/x-www-form-urlencoded",
            # Code from user Kris https://stackoverflow.com/u/3783770, 
            # at https://stackoverflow.com/a/30686735
            f"Content-Length: {len(body.encode('utf-8'))}",
            f"Connection: close"
        ]

        return self.send_request(request_arr, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        client.command( sys.argv[2], sys.argv[1] )
    else:
        client.command( sys.argv[1] )
