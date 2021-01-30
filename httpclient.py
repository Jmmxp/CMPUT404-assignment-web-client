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
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return data.split("\r\n")[0].split(" ")[1]

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
        after_headers = False
        body = ""
        for line in data.split("\r\n"):
            if after_headers:
                body += line + "\r\n"
            elif line == "":
                after_headers = True
                continue
            
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        buffer_size = 1024
        while True:
            part = sock.recv(buffer_size)
            # Modified this loop to properly receive socket data by basing it off of
            # StackOverflow user yoniLavi: https://stackoverflow.com/u/493553
            # Link to code: https://stackoverflow.com/a/34236030
            if len(part) < buffer_size:
                break
            
            if (part):
                buffer.extend(part)
            else:
                break
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        self.connect(url, 80)

        request = [
            "GET / HTTP/1.1",
            f"Host: {url}",
        ]

        stringify = "\r\n".join(request) + "\r\n\r\n"
        self.sendall(stringify)
        
        data = self.recvall(self.socket)
        self.close()

        code = self.get_code(data)
        headers = self.get_headers(data)
        body = self.get_body(data)

        # print(code)
        # print(headers)
        # print(body)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        return HTTPResponse(code, body)

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
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
