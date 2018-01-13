from socket import *
from time import ctime

host = ''
port = 21567
bufsize = 1024
addr = (host, port)

tcpsock = socket(AF_INET, SOCK_STREAM)
tcpsock.bind(addr)
tcpsock.listen(5)

while True:
    print "waiting for connection"
    tcpclisock, Addr = tcpsock.accept()
    print "connect from:" Addr
    
    while True:
        data = tcpclisock.recv(bufsize)
        if not data:
            break
        tcpclisock.send('[%s] %s' % (ctime(), data))
        tcpclisock.close()
tcpsock.close()
        