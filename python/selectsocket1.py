#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:king

import socket
import select

ip_port = ('127.0.0.1', 8080)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(ip_port)
sock.listen(5)
sock.setblocking(0)  # 设置socket为非阻塞工作方式


inputs = {sock: ip_port}

while True:
    # select监控所有socket，看是否有被激活的
    readlist, writelist, errorlist = select.select(inputs.keys(), [], [], 1)
    for r in readlist:
        # 当有新的client连接的时候，添加到select列表句柄中进行轮训
        if sock == r:
            request, address = r.accept()
            print 'accept request,client:%s' % str(address)
            request.setblocking(0)
            inputs[request] = address
        # 如果是已经存在的连接（也就是非服务器的socket），
        # 就直接获取输入，没有输入就表示该socket断开连接了
        else:
            received_data = r.recv(1024)
            print r.getpeername()
            if received_data:
                print 'received from %s data: %s' % (str(inputs[r]), received_data)
            else:
                inputs.remove(r)

sock.close()
