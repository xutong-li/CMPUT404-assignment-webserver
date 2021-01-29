# coding: utf-8

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Edited by Xutong Li for CMPUT404 W21 Assignment 1
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
import socketserver
import logging
import os


def get_content(file):
    f = open(file, 'r')
    content = f.read()
    f.close()
    return content


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("Got a request of: %s" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))
        self.method = self.get_method(self.data)
        self.path = self.get_path(self.data)
        self.host = self.get_host(self.data)
        # print(self.method, self.path, self.host)

        # 1. status_code_405
        if self.method != "GET":
            self.status_code_405()
            return

        # path ex: /deep/index.html
        self.localpath = "./www" + self.path
        # handle the path
        css_content, html_content = self.handle_path(self.localpath)

        # handle other status:
        # 2. status_code_301
        if os.path.isdir("./www" + self.path) and self.path[-1] != "/":
            # logging.warning("***")
            self.status_code_301()

        # 3. status_code_200
        elif html_content != "":
            self.status_code_200("html", html_content)

        # 4. status_code_200
        elif css_content != "":
            self.status_code_200("css", css_content)

        # 5. status_code_404
        else:
            self.status_code_404()
            return


    def handle_path(self, local_path):  # local path ex: ./www/deep/...
        css_content = ""
        html_content = ""
        # if the local path directs to files under ./www/deep/
        if os.path.isdir(local_path):
            print("Requesting the local directory: " + str(local_path) + "\n")
            for file in os.listdir(local_path):
                file_name = str(file).lower()
                if file_name[-5:].lower() == '.html' and self.path[-1] == "/":
                    html_file_name = "www" + str(self.path) + file_name
                    html_content = get_content(html_file_name)
                if file_name[-4:].lower() == '.css':
                    css_file_name = "www" + str(self.path) + "/" + file_name
                    css_content = get_content(css_file_name)

        # if the local path directs to files under www/
        elif os.path.isfile(local_path):
            print("Requesting the local file: " + str(local_path) + "\n")
            file_name = str(self.path)
            if file_name[-5:].lower() == '.html':
                html_file_name = "www/" + str(self.path)
                html_content = get_content(html_file_name)
            if file_name[-4:].lower() == '.css':
                css_file_name = "www/" + str(self.path)
                css_content = get_content(css_file_name)

        # return the requested file content
        return css_content, html_content

    # https://pymotw.com/2/socket/binary.html
    # https://www.w3.org/International/articles/http-charset/index
    def status_code_200(self, content_type, content):
        self.request.sendall(bytearray("HTTP/1.1 200 OK\r\n", "utf-8"))
        self.request.sendall(bytearray("Content-Type: text/%s; charset=utf-8\r\n\r\n"
                                       % content_type, 'utf-8'))
        self.request.sendall(bytearray("%s\r\n" % content, 'utf-8'))

    def status_code_405(self):
        self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n", "utf-8"))

    def status_code_301(self):
        self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\n", 'utf-8'))

    def status_code_404(self):
        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n", 'utf-8'))

    def get_method(self, data):
        method = ""
        data = data.decode("utf-8").split("\n")
        method_path = data[0].split(" ")
        method += method_path[0]
        return method

    def get_path(self, data):
        path = ""
        data = data.decode("utf-8").split("\n")
        method_path = data[0].split(" ")
        path += method_path[1]
        return path

    def get_host(self, data):
        data = data.decode("utf-8").split("\n")
        host = data[1].split(" ")[1]
        return host


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
