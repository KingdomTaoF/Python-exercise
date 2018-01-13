from socket import *

host = 'localhost'
port = 21567
bufsiz = 1024
addr = (host, port)

tcpclisock = socket(AF_INET, SOCK_STREAM)
tcpclisock.connect(addr)

while True:
    data = raw_input('>')
    if not data:
        break
    tcpclisock.send(data)
    data = tcpclisock.recv(bufsiz)
    
    if not data:
        break
    print data
    
tcpclisock.close()