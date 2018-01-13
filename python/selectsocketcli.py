#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author：King

import socket
import select

ip_port = ('127.0.0.1', 8080)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(ip_port)
sock.setblocking(0)

tag = 0
i = 0

while True:
    readlist, writelist, errorlist = select.select([sock], [sock], [sock], 1)
    # print len(readlist), len(writelist)
    if len(writelist) and tag == 0:
        print len(readlist), len(writelist)
        print "writing %s" % i
        print "you can start send data"
        tag = 1
        input_data = raw_input().strip()
        writelist[0].sendall(input_data)
        writelist.pop(0)
        # continue

    if tag == 1 and len(readlist):
        print "reading %s" % i
        print len(readlist), len(writelist)
        data = sock.recv(1024)
        tag = 0
        if data:
            print "received [%s] data from server" % data
        else:
            print "connection closed by server"
            break
    i += 1
sock.close()
