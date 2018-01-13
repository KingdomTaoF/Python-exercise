#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-22

import select
import socket
import sys
import Queue

ip_port = ('127.0.0.1', 8080)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(0)
print >>sys.stderr, 'starting listen on %s' % str(ip_port)
print >>sys.stderr, 'waiting for next event'
sock.bind(ip_port)
sock.listen(5)

inputs = [sock]
outputs = []
message_queue = {}

while True:
    # select监控是否有文件句柄可读，可写，异常
    readlist, writelist, errorlist = select.select(inputs, outputs, inputs, 1)

    for r in readlist:
        # 新连接请求添加到 inputs 轮训列表中，并为新的连接请求创建queue队列
        if r is sock:
            conn, address = r.accept()
            print >>sys.stderr, 'connection from ', address
            conn.setblocking(0)
            inputs.append(conn)
            message_queue[conn] = Queue.Queue()
        # 连接的状态改变有两种情况，一种是有发新的数据过来，另外就是client断开
        else:
            data = r.recv(1024)
            client = str(r.getpeername())
            if data:
                print >>sys.stderr, 'recvied %s from %s' % (data, client)
                message_queue[r].put(data)
                if r not in outputs:
                    outputs.append(r)
            else:
                print >>sys.stderr, 'closing connection from %s' % client
                if r in outputs:
                    outputs.remove(r)
                inputs.remove(r)
                r.close()
                del message_queue[r]

    # 将接受到数据回送给client
    for w in writelist:
        try:
            # 非阻塞读queue中的数据，读不到就立即跳过
            # 获取可写socket的queue中的内容，
            # 如果为空将其从 outputs 中剔除
            next_message = message_queue[w].get_nowait()
        except Queue.Empty:
            print >>sys.stderr, ' ', w.getpeername(), 'queue empty'
            outputs.remove(w)
        else:
            print >>sys.stderr, 'sending %s to %s' % (next_message, w.getpeername())
            w.send(next_message)

    for e in errorlist:
        print >> sys.stderr, 'error condtion on', e.getpeername()
        inputs.remove(e)
        if e in outputs:
            outputs.remove(e)
        e.close()
        del message_queue[e]
