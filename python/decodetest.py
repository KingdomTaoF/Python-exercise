#-*-coding:utf-8-*-
s = '王锦韬'

print s,type(s)

s2 = s.decode('utf-8')
print s2,type(s2)

s3 = s2.encode("GBK")
print s3,type(s3)