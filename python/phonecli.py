#-*-coding:utf-8-*-
#!/usr/bin/env python

import socket

ip_port = ('127.0.0.1',8888)
sock = socket.socket()
sock.connect(ip_port)
sock.settimeout(5)

while True:
    data = sock.recv(1024)
    print 'receive:',data
    input_data = raw_input('please input sth:').strip()
    sock.sendall(input_data)
    if input_data == 'exit':
        break
        
sock.close()
    