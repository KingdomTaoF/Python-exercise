#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-06 15:40:43

import SocketServer
import socket


class MyServer(SocketServer.BaseRequestHandler):
    def handle(self):
        conn = self.request
        print self.client_address
        conn.sendall('欢迎')
        flag = True
        while flag:
            try:
                data = conn.recv(1024)
                if data == 'exit':
                    flag = False
                elif data == '0':
                    conn.sendall('recording')
                elif data != '':
                    print "recevied %s from %s" % (data, self.client_address)
                else:
                    conn.sendall('please input again')
            except socket.error:
                print "socket error,close connection"
                break


if __name__ == '__main__':
    server = SocketServer.ForkingTCPServer(('127.0.0.1', 8009), MyServer)
    server.serve_forever()
