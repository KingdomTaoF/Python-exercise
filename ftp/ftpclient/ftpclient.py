#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-07 15:14:20


import socket
import sys
import select
import re
import os
import hashlib
# import time


status_code = {
    '200': '用户名密码验证成功',
    '201': '用户注册成功',
    '203': '命令执行成功',
    '400': '用户名和密码不相符',
    '401': '用户注册失败,用户已存在',
    '402': '用户不存在',
    '403': '命令执行失败',
    '404': '不支持该操作',
    '405': '命令用法不正确',
    '406': '目标文件存在',
    '407': '目标文件不存在',
    '408': '服务端未知错误',
    '409': '非法路径(超出用户家目录范围)',
    '410': '用户剩余空间不足，无法上传',
}


class MyClient(object):
    def __init__(self, ip_port):
        self.ip_port = ip_port
        self.cmdflag = 0

    def connect(self):
        '''连接到ftpserver'''
        self.sock = socket.socket()
        self.sock.connect(self.ip_port)

    def start(self):
        self.connect()
        print("connected to server:%s" % str(self.ip_port))
        print(str(self.sock.recv(1024)))
        self.flag = raw_input("login 还是 register：").strip()
        self.username = raw_input("用户名:").strip()
        self.password = raw_input("密码:").strip()
        if len(self.flag) == 0 or len(self.username) == 0 or len(self.password) == 0:
            print('操作类型，用户名，密码为必须项，不能为空')
            sys.exit(1)
        if self.flag == 'register':
            self.home_dir = raw_input('家目录名:')
            self.disk_quota = raw_input('磁盘配额:')
            self.userinfo = ("%s,%s,%s,%s,%s" % (self.flag, self.username, self.password, self.home_dir, self.disk_quota))
        elif self.flag == 'login':
            self.userinfo = ("%s,%s,%s" % (self.flag, self.username, self.password))
        else:
            print('%s 为未知的操作' % self.flag)
            sys.exit(1)
        print(self.userinfo)
        # 发送用户名和密码
        self.sock.sendall(self.userinfo)
        # 获取验证状态
        self.status_info = self.sock.recv(1024)
        if self.status_info.strip().split(' ')[0].startswith('40'):
            print(self.status_info)
            sys.exit(1)
        else:
            print(self.status_info)
        # put_reobj = re.compile('^put')
        # get_reobj = re.compile('^get')
        spe_action = {
            'get': self.action_get,
            'put': self.action_put,
            'rm': self.actionRm,
            'mv': self.actionMv,
            'help': self.Help,
            'passwd': self.resetPasswd,
            'useradd': self.manageUser,
            'userdel': self.manageUser,
            'usermod': self.manageUser,
            'show': self.manageUser,
        }
        uni_action = ['ls', 'pwd', 'cd', 'mkdir']
        while True:
            cmdstring = raw_input("%s>" % self.username).strip()
            print(cmdstring)
            if cmdstring == '':
                continue
            elif cmdstring == 'exit':
                sys.exit(1)
            elif cmdstring.split(' ')[0] in spe_action:
                print('开始执行命令 %s' % cmdstring)
                result = spe_action[cmdstring.split(' ')[0]](cmdstring)
                print('\n%s %s\n%s' % (result[0], status_code[result[0]], result[1]))
            else:
                result = self.interact(cmdstring)
                if result == '':
                    # print '出现错误'
                    continue
                elif result == '1':
                    continue
                else:
                    if cmdstring.split(' ')[0] == 'ls':
                        self.color_print_dir(result)
                    else:
                        print(result)

    def Help(self, cmdstring):
        try:
            help_cmd = cmdstring.strip().split(' ')[1]
        except IndexError:
            help_cmd = 'help'
        help_dict = {
            'cd': 'cd path',
            'ls': 'ls path/file',
            'mkdir': 'mkdir dirname',
            'get': 'get filename',
            'put': 'put filename',
            'rm': 'rm filename',
            'mv': 'mv src dest',
            'pwd': 'show potential work dir',
        }
        if help_cmd == 'help':
            printstring = ''
            for i in help_dict:
                printstring += '%s:%s\n' % (i, help_dict[i])
            return ['203', printstring]
        elif help_cmd in help_dict:
            return ['203', '%s:%s' % (help_cmd, help_dict[help_cmd])]
        else:
            return ['404', '不支持 %s 操作' % help_cmd]

    def manageUser(self, cmdstring):
        args = cmdstring.strip().split(' ')
        print(str(args))
        if args[0] != 'show' and self.username != 'admin':
            return ['403', '当前用户非admin,无法执行此操作']
        else:
            action_list = {
                'useradd': self.useradd,
                'userdel': self.userdel,
                'usermod': self.usermod,
                'show': self.showUser,
            }
            return action_list[args[0]](args[1:])

    def useradd(self, args):
        username = raw_input("用户名:").strip()
        password = raw_input("密码:").strip()
        home_dir = raw_input('家目录名:')
        disk_quota = raw_input('磁盘配额:')
        if len(username) == 0 or len(password) == 0:
            return ['403', '用户名或密码不能为空']
        userinfo = "%s ,%s ,%s ,%s" % (username, password, home_dir, disk_quota)
        cmd = '%s ,%s' % ('useradd', userinfo)
        print(cmd)
        self.sock.sendall(cmd)
        result = self.sock.recv(1024).strip().split(':')
        return result

    def userdel(self, args):
        # cmd = '%s %s' % ('userdel', args[0])
        rm_dir = raw_input('是否删除用户的目录(Y/N):').strip()
        if rm_dir == 'Y' or rm_dir == 'y':
            cmd = '%s %s -r' % ('userdel', args[0])
        elif rm_dir == 'N' or rm_dir =='n':
            cmd = '%s %s' % ('userdel', args[0])
        else:
            return ['403', '%s 无效的输入' % rm_dir]
        self.sock.sendall(cmd)
        ret = self.sock.recv(1024).strip().split(":")
        return ret

    def showUser(self, args):
        # print(len(args))
        if len(args) == 1:
            if args[0] == self.username or self.username == 'admin':
                cmd = 'show %s' % args[0]
            else:
                return ['403', '没有权限查看 %s 的信息' % args[0]]
        elif len(args) == 0:
            if self.username == 'admin':
                cmd = 'show all'
            else:
                cmd = 'show %s' % self.username
        else:
            return ['405', '参数个数过多']
        self.sock.sendall(cmd)
        ret = self.sock.recv(1024).strip().split(':')
        return ret

    def usermod(self, args):
        print('执行usermod')
        '''
        -q
        -d -n
        '''
        options_dict = {}
        options = ['-n', '-q', '-d']
        for i in xrange(0, len(args) - 1):
            if args[i] == '-n':
                options_dict[args[i]] = ''
            elif i == len(args) - 1:
                if args[i].strip().startswith('-'):
                    options_dict(args[i]) == ''
                else:
                    break
            elif args[i].strip().startswith('-') and not args[i+1].strip().startswith('-') and args[i].strip() in options:
                options_dict[args[i]] = args[i + 1]
            elif args[i].strip().startswith('-') and args[i+1].strip().startswith('-') and args[i].strip() in options:
                options_dict[args[i]] = ''
            else:
            # not args[i].strip().startswith('-') and args[i+1].strip().startswith('-'):
                continue
        print(str(options_dict))
        if '-n' in options_dict:
            if len(options_dict) * 2 - 1 == len(args) - 1:
                '''
                cmd = ''
                for i in options_dict:
                    cmd += '%s %s ' % (i, options_dict[i])
                '''
                self.sock.sendall('usermod %s %s' % (args[-1], str(options_dict)))
                # return ['203', '用法正确,%s' % cmd]
            else:
                return ['403', '用法不正确']
        else:
            if len(options_dict) * 2 == len(args) - 1:
                '''
                cmd = ''
                for i in options_dict:
                    cmd += '%s %s' % (i, options_dict[i])
                '''
                self.sock.sendall('usermod %s %s' % (args[-1], str(options_dict)))
                # return ['203', '用法正确,%s' % cmd]
            else:
                return ['403', '用法不正确']
        return self.sock.recv(2048).strip().split(':')

    def resetPasswd(self, cmdstring):
        args = cmdstring.strip().split(' ')
        if self.username == 'admin':
            new_password1 = raw_input('请输入新的密码:').strip()
            new_password2 = raw_input('请再输入一遍:').strip()
            if new_password1 != new_password2 or len(new_password1) == 0:
                return ['403', '两次输入的密码不一致，修改密码失败']
            else:
                if len(args) == 1:
                    self.sock.sendall('%s %s %s' % ('passwd', 'admin', new_password1))
                    return self.sock.recv(1024).strip().split(':')
                elif len(args) == 2:
                    self.sock.sendall('%s %s %s' % ('passwd', args[1], new_password1))
                    return self.sock.recv(1024).strip().split(':')
                else:
                    return ['405', '只能接收最多一个参数']
        else:
            if len(args) == 1 or args[1] == self.username:
                new_password1 = raw_input('请输入新的密码:').strip()
                new_password2 = raw_input('请再输入一遍:').strip()
                if new_password1 != new_password2 or len(new_password1) == 0:
                    return ['403', '两次输入的密码不一致，修改密码失败']
                else:
                    self.sock.sendall('%s %s %s' % ('passwd', self.username, new_password1))
                    return self.sock.recv(1024).strip().split(':')
            else:
                return ['403', '非admin用户只能修改自己的密码，无法修改其他用户密码']

    def actionMv(self, cmdstring):
        args = cmdstring.strip().split(' ')
        if len(args) != 3:
            return ['405', 'usage: mv srcfile destfile']
        else:
            self.sock.sendall(cmdstring)
            ret = self.sock.recv(1024).strip().split(':')
            if ret[0] == '403' or ret[0] == '203' or ret[0] == '408' or ret[0] == '409':
                return [ret[0], ret[1]]
            elif ret[0] == '406':
                print('%s:%s\n%s' % (ret[0], status_code[ret[0]], ret[1]))
                while True:
                    choice = raw_input('choice:').strip()
                    if choice == 'y' or choice == 'Y':
                        self.sock.sendall(choice)
                        override_status = self.sock.recv(1024).strip().split(':')
                        return [override_status[0], override_status[1]]
                    elif choice == 'N' or choice == 'n':
                        self.sock.sendall(choice)
                        return ['403', '%s 已存在，并取消覆盖' % args[2]]
                    else:
                        print('错误的输入')
                        continue
            else:
                return ['408', 'error']

    def actionRm(self, cmdstring):
        self.sock.sendall(cmdstring)
        result = self.sock.recv(1024).strip().split(':')
        while True:
            if len(result) == 2:
                return result
            else:
                result = self.sock.recv(1024).strip().split(':')
                continue

    def color_print_dir(self, retstring):
        # print("开始打印")
        itemlist = retstring.strip('\n').split('\n')
        print(itemlist[0])
        pattern1 = re.compile('^total.*')
        if pattern1.match(itemlist[1]):
            print(itemlist[1])
            itemlist.pop(1)
        pattern2 = re.compile('^d.*')
        for i in itemlist[1:]:
            if pattern2.match(i):
                print('\033[1;34m%s\033[0m' % i)
            else:
                print(i)
        '''
        dirlist = pattern.findall(retstring)
        for i in dirlist:
            print('\033[1;34m%s\033[0m' % i)
        '''

    def processBar(self, trans_size, file_size, mode):
        rows, columns = os.popen('stty size', 'r').read().split()
        bar_length = int(columns) - len(mode) * 2 - 19
        percent = float(trans_size) / float(file_size)
        hashes = '=' * int(percent * bar_length)
        spaces = ' ' * (bar_length - len(hashes))
        change = float(1048576)
        sys.stdout.write('\r%s:%.2fM/%.2fM %d%% [%s]' % (mode, trans_size / change, file_size / change, percent * 100, hashes + spaces))
        # time.sleep(1)
        sys.stdout.flush()

    def action_get(self, cmdstring):
        '''
        server有目标文件-- 406
            client本地存在目标文件：
                1、filesize一致，接着验证md5是否一致，不一致直接覆盖同步
                   一致的话就不同步
                2、filesize不一致，增量同步。同步完后验证md5是否一致
                            md5不一致：重新进行完全同步
                            md5一致：跳过
                   如果client的文件大小大于server端的，就询问是否覆盖同步
                   同步完后再次对比md5是否一致，
                         一致就继续，
                        不一致就再次同步
            client本地不存在目标文件：
                直接完全同步，同步完后对比md5
                    一致就ok
                    不一致就重新同步
        server木有目标文件：407
            直接返回client错误
        '''
        args = cmdstring.strip().split(' ')
        if len(args) == 1:
            return ['403', '命令用法错误，usage：get filename']
        else:
            # 先暂时只接收一个参数（只能一次下载一个文件）
            filename = args[1]
            self.sock.sendall(cmdstring)
            # server 根据用户想获取的文件，看server是否存在该文件
            # 有返回 406，无则返回 407
            server_exist_ornot = self.sock.recv(1024).strip()
            if server_exist_ornot == '406':
                # server端存在此文件
                result = self.writeFile(filename)
                if result[0] == '403':
                    self.sock.sendall('403')
                    choice = raw_input('%s 文件md5不一致，是否重新覆盖：' % filename).strip()
                    print('你的选择为:%s' % choice)
                    self.sock.sendall(choice)
                    if choice == 'y' or choice == 'y':
                        return_status = os.system('> ./%s' % filename)
                        if return_status == 0:
                            return_code = self.writeFile(filename, reflag=1)
                            if return_code[0] == '203':
                                return ['203', '重新同步文件 %s 成功' % filename]
                            else:
                                return ['403', '重新同步文件 %s 失败' % filename]
                        else:
                            return ['403', '清除文件内容错误']
                    elif choice == 'N' or choice == 'n':
                        return ['403', '%s md5不一致，并取消同步']
                    else:
                        return ['403', '无效的选项']
                else:
                    self.sock.sendall('203')
                    return result
                '''
                if os.path.isfile('./%s' % filename):
                    client_file_size = os.stat(filename).st_size
                    self.sock.sendall('%s:%d' % (filename, client_file_size))
                    # 获取server端文件的大小
                    server_file_size_list = self.sock.recv(1024).strip().split(':')
                    server_file_size = int(server_file_size_list[1])
                    print('%s:%s\n%s:%s' % ('client', client_file_size, 'server', server_file_size))
                    current_file_size = client_file_size
                    print('开始下载文件')
                    if server_file_size < client_file_size:
                        mode = 'wb'
                        current_file_size = 0
                    else:
                        mode = 'ab'
                    with open(filename, mode) as dfile:
                        while current_file_size < server_file_size:
                            if server_file_size - current_file_size < 1024:
                                size = server_file_size - current_file_size
                            else:
                                size = 1024
                            data = self.sock.recv(size)
                            print(data)
                            dfile.write(data)
                            current_file_size += len(data)
                    server_file_md5 = self.sock.recv(1024).strip()
                    client_file_md5 = self.calcFileMD5(filename)
                    if server_file_md5 == client_file_md5:
                        return ['203', '%s 下载完成' % filename]
                    else:
                        return ['403', '%s 文件md5不一致' % filename]
                # client本地不存在此文件
                else:
                    # self.sock.sendall('%s:%d' % (filename, 0))
                    # 开始接收文件
                    return self.writeFile(filename)
                '''
            elif server_exist_ornot == '407':
                # 文件不存在，返回错误
                return ['407', '%s 不存在' % filename]
            else:
                return ['408', '错误的返回码']

    def writeFile(self, filename, reflag=0):
        if os.path.isfile('./%s' % filename):
            current_file_size = os.stat('./%s' % filename).st_size
        else:
            current_file_size = 0
        if reflag == 0:
            self.sock.sendall('%s:%d' % (filename, current_file_size))
            self.server_file_info = self.sock.recv(1024).strip().split(':')
            server_file_size = int(self.server_file_info[1])
        else:
            server_file_size = int(self.server_file_info[1])
        if server_file_size < current_file_size:
            current_file_size = 0
            mode = 'wb'
        else:
            mode = 'ab'
        with open(filename, mode) as f:
            while current_file_size < server_file_size:
                if server_file_size - current_file_size < 1024:
                    size = server_file_size - current_file_size
                else:
                    size = 1024
                data = self.sock.recv(size)
                # print(data)
                f.write(data)
                current_file_size += len(data)
                self.processBar(current_file_size, server_file_size, '下载文件')
        server_file_md5 = self.sock.recv(1024).strip()
        client_file_md5 = self.calcFileMD5(filename)
        if server_file_md5 == client_file_md5:
            return ['203', '%s 下载完成' % filename]
        else:
            return ['403', '%s 文件md5不一致' % filename]

    def calcFileMD5(self, destfile):
        m = hashlib.md5()
        if os.path.isfile(destfile):
            with open(destfile, 'rb') as f:
                for line in f:
                    m.update(line)
            return m.hexdigest()
        else:
            return 'error'

    def action_put(self, cmdstring):
        args = cmdstring.strip().split(' ')
        if len(args) == 1:
            return ['405', '用法：put filename']
        else:
            if args[1].startswith('/'):
                dest_file = args[1]
            else:
                dest_file = './%s' % args[1]
            if not os.path.isfile(dest_file):
                return ['407', '要上传的 %s 不存在' % args[1]]
            else:
                print('开始上传文件 %s' % dest_file)
                # 和server端目标文件大小以及client端本地目标文件大小
                self.sock.sendall(cmdstring)
                server_recv_file_size = int(self.sock.recv(1024).strip().split(':')[1])
                client_send_file_size = os.stat(dest_file).st_size
                self.sock.sendall('%s:%d' % (dest_file, client_send_file_size))
                print('server:%s\nclient:%s' % (server_recv_file_size, client_send_file_size))
                disk_quota_ornot = self.sock.recv(1024).strip()
                if disk_quota_ornot == '410':
                    return ['410', '上传失败']
                if client_send_file_size < server_recv_file_size:
                    print('开始覆盖传输')
                    self.sendFile(dest_file, 0)
                    return self.checkPutConsistency(dest_file)
                elif client_send_file_size == server_recv_file_size:
                    return self.checkPutConsistency(dest_file)
                else:
                    print('开始断点传输')
                    self.sendFile(dest_file, server_recv_file_size)
                    return self.checkPutConsistency(dest_file)

    def sendFile(self, dest_file, begin):
        file_size = os.stat(dest_file).st_size
        with open(dest_file, 'rb') as f:
            f.seek(begin)
            trans_size = begin
            for line in f:
                # print(line)
                self.sock.sendall(line)
                trans_size += len(line)
                self.processBar(trans_size, file_size, '上传文件')

    def checkPutConsistency(self, dest_file):
        # 上传完文件后，获取两端的md5进行比较
        server_recv_file_md5 = self.sock.recv(1024).strip()
        client_send_file_md5 = self.calcFileMD5(dest_file)
        print('\n开始验证md5:\nserver:%s\nclient:%s' % (server_recv_file_md5, client_send_file_md5))
        if server_recv_file_md5 == client_send_file_md5:
            self.sock.sendall('203')
            return ['203', 'md5一致,%s 上传成功' % dest_file]
        else:
            choice = raw_input('%s 的md5不一致，是否重新完全同步(Y/N):').strip()
            while True:
                if choice == 'Y' or choice == 'y':
                    self.sock.sendall('403:y')
                    self.sendFile(dest_file, 0)
                    new_server_recv_file_md5 = self.sock.recv(1024).strip()
                    if new_server_recv_file_md5 == client_send_file_md5:
                        return ['203', '重新同步 %s 成功，md5一致' % dest_file]
                    else:
                        return ['403', '重新同步完成，但是未知原因导致 %s md5不一致' % dest_file]
                elif choice == 'N' or choice == 'n':
                    self.sock.sendall('403:n')
                    return ['403', '%s 文件md5不一致，并取消重传']
                else:
                    choice = raw_input('无效的选项，是否重新完全同步(Y/N):').strip()
                    continue
                    # return ['403', '输入选项错误']

    def interact(self, cmdstring):
        print("开始交互")
        rlist, wlist, elist = select.select([self.sock], [self.sock], [self.sock])
        if len(wlist) > 0 and self.cmdflag == 0:
            print("发送命令 %s" % cmdstring)
            wlist[0].sendall(cmdstring)
            self.cmdflag = 1
        if self.cmdflag == 1:
            print("获取命令执行结果")
            retstring = self.sock.recv(1024)
            if retstring == '':
                return ''
            else:
                self.cmdflag = 0
                return retstring
        return '1'


if __name__ == '__main__':
    ip_port = ('127.0.0.1', 9999)
    client = MyClient(ip_port)
    client.start()
