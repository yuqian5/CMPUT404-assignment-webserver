#  coding: utf-8
import socketserver
from pathlib import Path
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

'''
 <one line to give the program's name and a brief idea of what it does.>
    Copyright (C) <2022>  <Yuqian Cao>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


def get_http_header_request_dir(request):
    start = request.find("GET") + len("GET")
    end = request.find("HTTP/1.1")
    return request[start:end].strip()


def get_http_header_request_method(request):
    parts = request.split(" ")
    return parts[0][2:]


class MyWebServer(socketserver.BaseRequestHandler):
    root = "./www"

    def check_if_file_exist(self, path):
        p = Path(self.root + path)
        abs_path = os.path.abspath(self.root + path)
        if "www" not in abs_path:
            return False, None, None, None
        if p.is_file():
            content_type = ""
            if p.suffix == ".html":
                content_type = "text/html"
            elif p.suffix == ".css":
                content_type = "text/css"
            return True, open(self.root + path, "r"), content_type, 0
        elif p.is_dir():
            return True, open(self.root + path + "/index.html", "r"), "text/html", 1
        else:
            return False, None, None, None

    def parse_http_request(self, request):
        request_list = []

        for item in request.split(b"\r\n"):
            request_list.append(str(item))

        request_object = {}

        # parse request
        request_object["dir"] = get_http_header_request_dir(str(request_list[0]))
        request_object["method"] = get_http_header_request_method(str(request_list[0]))

        return request_object

    def handle(self):
        self.data = self.request.recv(1024).strip()

        # print("******************************************************")
        # print(self.data)
        http_request = self.parse_http_request(self.data)

        # for i in http_request:
        #     print(i, http_request[i])
        # print("******************************************************")

        if http_request["method"] == "GET":
            exist, fd, content_type, dir_type = self.check_if_file_exist(http_request["dir"])
            if dir_type == 1 and http_request["dir"][-1] != "/":
                self.request.sendall(bytearray(f"HTTP/1.1 301 Moved Permanently\r\nLocation: {http_request['dir'] + '/'}\r\nConnection: Close\r\n \r\n", 'utf-8'))
            if exist:
                resp = fd.read().encode()
                length = len(resp)

                self.request.sendall(bytearray(f"HTTP/1.1 200 OK\r\nContent-Type:{content_type}; charset=utf-8\r\nConnection: Close\r\nContent-Length: {length} \r\n\r\n", 'utf-8'))
                self.request.sendall(resp)
            else:
                self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\nConnection: Close\r\n \r\n", 'utf-8'))
        else:
            self.request.sendall(bytearray("HTTP/1.1 405 Not Allowed\r\nConnection: Close\r\n \r\n", 'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
