# -*-coding:utf-8-*-
import optparse
import urllib2
import sys
import json


animallist = ['子鼠', '丑牛', '寅虎', '卯兔', '辰龙', '巳蛇', '午马', '未羊', '申猴', '酉鸡', '戌狗', '亥猪']
constellationlist = ['金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座', '白羊座']
faillist = []


def addToTencent(name):
    url = 'http://wlop.ieodopen.qq.com/AddNewNode.php?iAppId=1104216374&iDirId=1&sName='+name
    # 注意，header中的cookie会失效的，所以事先得手动在浏览器访问上面的URL，然后将cookie复制到这里，然后才可以正常访问
    req_header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Accept-Encoding': 'gzip,deflate,sdch', 'Accept-Language': 'zh-CN,zh;q=0.8',
                  'Connection': 'keep-alive',
                  'Cookie': 'pgv_pvi=9368793088; RK=jf8ycqJfa9; pgv_pvid=3831506045; o_cookie=2880092537; pac_uid=1_2880092537; pgv_info=ssid=s5661450107; pgv_si=s8849454080; _qpsvr_localtk=0.47201871813217644; PHPSESSID=sn3u3sh6gdsdtl54hdvmuc3n06; pt2gguin=o2880092537; uin=o2880092537; skey=@27RVDOdxa; ptisp=ctc; ptcz=b7db4b455b23cb80e0d5eaa312d31acc89e58d0220aeb2058be57ceb09c7197b',
                  'Host': 'wlop.ieodopen.qq.com', 'Upgrade-Insecure-Requests': 1,
                  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    req_timeout = 20
    req = urllib2.Request(url, None, req_header)
    resp = urllib2.urlopen(req, None, req_timeout)
    if resp.getcode() == 200 and json.loads(resp.read().strip().split(' = ')[1])['ret'] != '0':
        print name+' add failed'
        faillist.append(name)
    elif resp.getcode() != 200:
        resp.getcode()
        print name+' request url failed'
        faillist.append(name)


"""
def addToTencent(name):
    print name
"""


def usage():
    print "usage: kaifusimple.py -f 热血服/星座服/生肖服/联盟服,起始服,结束服(星座服和生肖服请填区服名称,热血服和联盟服填区服id)"


def main(funame, begin, end):
    if funame == '联盟服' and int(begin) <= int(end):
        for i in xrange(int(begin),int(end)+1):
            n = i-6000
            name = '联盟'+str(n)+'区'
            addToTencent(name)
    elif funame == '热血服' and int(begin) <= int(end):
        for i in xrange(int(begin),int(end)+1):
            name = '热血'+str(i)+'服'
            addToTencent(name)
    elif funame == '星座服':
        #print begin, end
        #print begin[0:9], end[0:9], len(begin), begin[9:11]
        if constellationlist.index(begin[0:9]) > constellationlist.index(end[0:9]):
            num = begin[9:11]
            for i in xrange(constellationlist.index(begin[0:9]), len(constellationlist)):
                name = constellationlist[i]+num+'服'
                addToTencent(name)
            for j in xrange(0,constellationlist.index(end[0:9])+1):
                name = constellationlist[j]+str(int(num)+1)+'服'
                addToTencent(name)
        else:
            num = begin[9:11]
            for i in xrange(constellationlist.index(begin[0:9]), constellationlist.index(end[0:9]) + 1):
                name = constellationlist[i]+num+'服'
                addToTencent(name)
    elif funame == '生肖服':
        if animallist.index(begin[0:6]) > animallist.index(end[0:6]):
            num = begin[6:8]
            for i in xrange(animallist.index(begin[0:6]), len(animallist)):
                name = animallist[i]+num+'服'
                addToTencent(name)
            for j in xrange(0, animallist.index(end[0:6])+1):
                name = animallist[j]+str(int(num)+1)+'服'
                addToTencent(name)
        else:
            num = begin[6:8]
            for i in xrange(animallist.index(begin[0:6]), animallist.index(end[0:6]) + 1):
                name = animallist[i]+num+'服'
                addToTencent(name)
    else:
        usage()
        sys.exit(1)
    print faillist

if __name__ == '__main__':
    '''
    try:
        while True:
            funame, begin, end = raw_input('请输入 开服类型，起始服，结束服:').strip().split(',')
            main(funame, begin, end)
    except ValueError,e:
        sys.exit(1)
    '''
    parser = optparse.OptionParser()
    parser.add_option('-f', dest='fin', help='输入开服类型及范围')
    option,args=parser.parse_args()
    if option.fin:
        funame, begin, end = option.fin.strip().split(',')
        main(funame, begin, end)
    else:
        usage()
        sys.exit(1)
