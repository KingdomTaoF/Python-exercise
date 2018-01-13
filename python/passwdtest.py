#-*-coding:utf-8-*-
import  MySQLdb
import getpass

conn = MySQLdb.connect(host='127.0.0.1',user='root',db='gdut')
cur = conn.cursor()
wrong_times = {}

while True:
    username = raw_input('username:').strip()
    #password = raw_input('password:').strip()
    password = getpass.getpass('password:').strip()
    
    if cur.execute('select * from user where name="%s"' % username) == 0:
        print "%s is not exist" % username
        break
    
    data = cur.fetchall()
    if data[0][3] == "1":
        print "%s is locked,cannot login" % username
        break
        
    if password != data[0][2]:
        if username not in wrong_times.keys():
            wrong_times[username] = 1
        else:
            wrong_times[username] += 1
        
        if wrong_times[username] == 3: 
            print "%s enter wrong password for 3 times,lock user" % username
            cur.execute('update user set status=1 where name="%s"' % username)
            break
        print "%s enter wrong password for %s times" % (username,wrong_times[username])
        continue
    else:
        print "%s login successfully" % username
    

cur.close()
conn.commit()
conn.close()
