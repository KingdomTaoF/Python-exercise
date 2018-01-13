#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-27 15:27:43

import socket

ip_port = ('127.0.0.1', 8009)
sock = socket.socket()
sock.connect(ip_port)
sock.settimeout(10)

while True:
    try:
        data = sock.recv(1024)
        print 'recevied data:%s' % data
        input_data = raw_input('please input:')
        sock.sendall(input_data)
        if input_data == 'exit':
            break
    except socket.timeout:
        print "socket 超时，退出client"
        break

sock.close()

