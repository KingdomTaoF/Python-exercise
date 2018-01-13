import ftplib
import os
import socket

host = 'ftp.mozilla.org'
dirn = 'pub/mozilla.org/webtools'
file = 'bugzilla-LATEST.tar.gz'

def main():
    try:
        f = ftplib.FTP(host)
    except (socket.error, socket.gaierror),e:
        print "error: cannot reach %s" % host
        return
    print "connect to host %s" % host
    
    try:
        f.login()
    except ftplib.error_perm:
        print "cannot login"
        f.quit()
        return
    
    try:
        f.cwd(dirn)
    except ftplib.error_perm:
        print "cannot cd to %s" % dirn
        f.quit()
        return
    print "cd to %s" % dirn

    try:
        f.retrbinary('retr %s' % file, open(file,'wb').write)
    except ftplib.error_perm:
        print "cannot read file:%s" % file
        f.quit()
        return
    print "download %s to CWD" % file
    f.quit()
    return
    
if __name__ == "__main__":
    main()