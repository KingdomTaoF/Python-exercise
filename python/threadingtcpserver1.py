#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-27

'''
SocketServer模块部分结构图：
实例化ThreadingTCPServer的过程(类似的还有 ForkingTCPServer)
server=ThreadingTCPServer(ThreadingMixIn, TCPServer)
    --> TCPServer(BaseServer).__init__()调用下面的
    --> BaseServer.__init__()
    --> self.RequestHandlerClass=SocketServer.BaseRequestHandler()
server.serve_forever()
    --> BaseServer.serve_forever()
    --> select轮训等待请求到来
    --> self._handle_request_noblock()
    --> ThreadingMixIn.process_request()(覆盖了BaseServer中的process_request)
        为每个请求创建一个线程来处理，每个线程都执行ThreadingMixIn.process_request_thread()
    --> ThreadingMixIn.process_request_thread()
    --> BaseServer.finish_request()
    --> self.RequestHandlerClass(request, client_class, self)
        也就是我们传进去的 handlerclass，用来真正处理请求
本质上就是利用select监听server的socket，然后如果从socket上获取到请求时，
就为每个请求创建一个独立线程，该线程执行一个函数处理请求
'''
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
    server = SocketServer.ThreadingTCPServer(('127.0.0.1', 8009), MyServer)
    server.serve_forever()
