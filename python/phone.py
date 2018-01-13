#-*-coding:utf-8-*-
#!/usr/bin/env python

import socket

ip_port = ('127.0.0.1',8888)
sock = socket.socket()
sock.bind(ip_port)
sock.listen(5)

while True:
    conn,address = sock.accept()
    conn.sendall('welcome....')
    Flag = True
    while Flag:
        data = conn.recv(1024)
        if data == 'exit':
            Flag = False
        elif data == '0':
            conn.sendall('start phone....')
        else:
            conn.sendall('wrong input,again')
    conn.close()