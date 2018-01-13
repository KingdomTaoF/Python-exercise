#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-07 18:01:57

import SocketServer
import pickle
import hashlib
import select
import subprocess
import os
import os.path
import sys
import re
import json


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
    '410': '用户剩余空间不足，无法上传'
}


class MyServer(SocketServer.BaseRequestHandler):

    base_home_dir = '/var/ftp/pub'
    '''
    self.action_list = {
        'ls': self.action_ls,
        'cd': self.action_cd,
        'mkdir': self.mkdir,
        'pwd': self.pwd,
        'put': self.action_put,
        'get': self.action_get,
    }
    '''

    def auth_or_register(self, loginInfo):
        userinfo = loginInfo.strip().split(',')
        self.auth_info = userinfo
        print(userinfo)
        if len(userinfo) == 3:
            flag, username, password = userinfo
        elif len(userinfo) == 5:
            flag, username, password, home_dir, disk_quota = userinfo
            # print(userinfo)
            if len(home_dir) == 0:
                home_dir = "%s/%s" % (self.base_home_dir, username)
            if len(disk_quota) == 0:
                disk_quota = '1GB'
        else:
            return '408'
        '''
        try:
            flag, username, password, home_dir, disk_quota = loginInfo.strip().split(',')
        except ValueError:
            flag, username, password = loginInfo.strip().split(',')
            home_dir = "%s/%s" % (self.base_home_dir, username)
            disk_quota = '1GB'
        '''
        if flag == 'login':
            ret = self.auth(username, password)
            return ret
        elif flag == 'register':
            ret = self.register(username, password, home_dir, disk_quota)
            return ret
        else:
            return '404'

    def auth(self, username, password):
        self.userinfo = self.read_from_db(username)
        if self.userinfo == '1':
            return '402'
        else:
            if self.md5(password) == self.userinfo['password']:
                self.current_dir = self.userinfo['home_dir']
                return '200'
            else:
                return '400'

    def register(self, username, password, home_dir, disk_quota):
        ret = self.read_from_db(username)
        if ret != '1':
            return '401'
        else:
            # d = {username: {'password': self.md5(password)}}
            userinfo = self.load_db()
            userinfo[username] = {
                'password': self.md5(password),
                'home_dir': home_dir,
                'disk_quota': disk_quota
            }
            self.userinfo = userinfo[username]
            ret = self.write_to_db(userinfo)
            if ret == '写入错误':
                return '401'
            else:
                self.current_dir = home_dir
                if not os.path.isdir(home_dir):
                    os.mkdir(home_dir)
                return '201'

    def md5(self, password):
        hashobj = hashlib.md5()
        hashobj.update(password)
        return hashobj.hexdigest()

    def write_to_db(self, d):
        '''
        存储用户信息的结构为
        {username1:{password:PASSWORD,home_dir:HOME,disk_quota:n单位}}
        '''
        f = open('password.db', 'wb')
        try:
            pickle.dump(d, f)
        except pickle.PicklingError:
            return '写入错误'
        finally:
            f.close()

    def load_db(self):
        try:
            f = open('password.db', 'rb')
            d = pickle.load(f)
        except IOError:
            f = open('password.db', 'wb')
            f.close()
            f = open('password.db', 'rb')
            try:
                d = pickle.load(f)
            except EOFError:
                d = {}
        except EOFError:
            d = {}
        finally:
            f.close()
            return d

    def read_from_db(self, username):
        try:
            d = self.load_db()
            return d[username]
        except KeyError:
            return '1'

    def interact(self, commandstring):
        # username = loginInfo.strip().split(',')[1]
        self.action_list = {
            'ls': self.action_ls,
            'cd': self.action_cd,
            'mkdir': self.mkdir,
            'pwd': self.pwd,
            # 'put': self.action_put,
            # 'get': self.action_get,
        }
        while True:
            tmp_list = commandstring.strip().split(' ')
            if tmp_list[0] not in self.action_list:
                return ['404', '']
            else:
                print('开始执行命令 %s' % tmp_list[0])
                ret = self.action_list[tmp_list[0]](tmp_list[1:])
                # print(str(ret))
                return ret

    def getDirSize(self, dir_path):
        size = 0
        for dirpaths, dirnames, filenames in os.walk(dir_path):
            for f in filenames:
                size += os.path.getsize(os.path.join(dirpaths, f))
        return size

    def changeToByte(self, size):
        '''
        reobj_G = re.compile('GB$')
        reobj_M = re.compile('MB$')
        reobj_K = re.compile('KB$')
        '''
        size = size.strip('B')
        if size.endswith('GB') or size.endswith('G'):
            return float(size.strip('G')) * 1024 * 1024 * 1024
        elif size.endswith('MB') or size.endswith('M'):
            return float(size.strip('M')) * 1024 * 1024
        elif size.endswith('KB') or size.endswith('K'):
            return float(size.strip('K')) * 1024
        else:
            return float(size)

    def autoChangeSize(self, size):
        '''
        自动将 byte 单位转换为方便显示的单位，如KB,MB,GB等
        '''
        size = float(size)
        if size / 1024 < 1:
            return '%.2fB' % size
        elif size / (1024 * 1024) < 1:
            return '%.2fKB' % (size / 1024)
        elif size / (1024 * 1024 * 1024) < 1:
            return '%.2fMB' % (size / (1024 * 1024))
        elif size / (1024 * 1024 * 1024 * 1024) < 1:
            return '%.2fGB' % (size / (1024 * 1024 * 1024))
        else:
            return '%.2fTB' % (size / (1024 * 1024 * 1024 * 1024))

    def action_put(self, args):
        # 检查server是否包含目标文件
        conn = self.request
        dest_file = '%s/%s' % (self.current_dir, args[0])
        quota_ornot = self.writeFile(dest_file)
        if type(quota_ornot) == list:
            return quota_ornot
        result = conn.recv(1024).strip().split(':')
        print(result)
        while True:
            if result[0] == '203':
                return ['203', '%s 上传成功' % dest_file]
            elif result[0] == '403' and result[1] == 'y':
                # return ['203', '%s 覆盖上传成功' % dest_file]
                return_status = os.system('> %s' % dest_file)
                if return_status == 0:
                    self.writeFile(dest_file, reflag=1)
                    return ['203', '%s 完全同步成功，md5一致' % dest_file]
                else:
                    return ['403', '未知错误']
            elif result[0] == '403' and result[2] == 'n':
                return ['403', '%s md5不一致，并取消重新上传' % dest_file]
            else:
                result = conn.recv(1024).strip().split(':')

        '''
        if os.path.isfile(dest_file):
            current_recv_file_size = os.stat(dest_file).st_size
            conn.sendall('%s:%d' % (args[0], current_recv_file_size))
            client_put_file_size = conn.recv(1024).strip().split(':')[1]
        else:
            pass
        '''

    def writeFile(self, dest_file, reflag=0):
        conn = self.request
        if os.path.isfile(dest_file):
            current_recv_file_size = os.stat(dest_file).st_size
        else:
            current_recv_file_size = 0
        if reflag == 0:
            conn.sendall('%s:%d' % (dest_file, current_recv_file_size))
            self.client_put_file_size = int(conn.recv(1024).strip().split(':')[1])
            client_put_file_size = self.client_put_file_size
        else:
            client_put_file_size = self.client_put_file_size
        print('server:%s\nclient:%s' % (current_recv_file_size, client_put_file_size))
        # 比较用户上传文件之后是否会超过用户的磁盘配额
        if self.getDirSize(self.userinfo['home_dir']) + client_put_file_size > self.changeToByte(self.userinfo['disk_quota']):
            conn.sendall('410')
            return ['410', '大于用户可用空间，无法上传 %s' % dest_file]
        else:
            conn.sendall('203')
        if current_recv_file_size > client_put_file_size:
            current_recv_file_size = 0
            mode = 'wb'
        else:
            mode = 'ab'
        with open(dest_file, mode) as f:
            while current_recv_file_size < client_put_file_size:
                if client_put_file_size - current_recv_file_size < 1024:
                    size = client_put_file_size - current_recv_file_size
                else:
                    size = 1024
                data = conn.recv(size)
                # print(data)
                f.write(data)
                current_recv_file_size += len(data)
        server_file_md5 = self.calcFileMD5(dest_file)
        conn.sendall(server_file_md5)
        return 'continue'
        # client_file_md5 = conn.recv(1024).strip()
        '''
        if server_file_md5 == client_file_md5:
            return ['203', '%s 上传成功' % dest_file]
        else:
            return ['403', '%s 文件md5不一致' % dest_file]
        '''

    def action_get(self, args):
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
        '''
        # 这里是实现同时get多个文件的操作，先放下
        if len(args) == 0:
            return ['403', '命令使用错误']
        else:
        file_list = []
        for i in args:
            tmp_file = '%s/%s' % (self.current_dir, i)
            if os.path.isfile(tmp_file):
                file_list.append(tmp_file)
        if len(file_list) == 0:
            return ['403', '%s 文件不存在' % ','.join(args)]
        else:
            for j in file_list:
                pass
        '''
        conn = self.request
        dest_file = args[0]
        abs_file_path = '%s/%s' % (self.current_dir, dest_file)
        print('要下载的文件为:%s' % (abs_file_path))
        if not os.path.isfile(abs_file_path):
            conn.sendall('407')
            # return '407'
        else:
            conn.sendall('406')
            client_file_size = int(conn.recv(1024).strip().split(':')[1])
            server_file_size = os.stat(abs_file_path).st_size
            print('%s:%s\n%s:%s' % ('client', client_file_size, 'server', server_file_size))
            conn.sendall('%s:%d' % (dest_file, server_file_size))
            if client_file_size == server_file_size:
                conn.sendall(self.calcFileMD5(abs_file_path))
                return self.checkConsistency(abs_file_path)
            elif client_file_size < server_file_size:
                print('进行断点传输文件:%s' % abs_file_path)
                self.sendFile(abs_file_path, client_file_size)
                conn.sendall(self.calcFileMD5(abs_file_path))
                return self.checkConsistency(abs_file_path)
            else:
                print('开始完全同步文件 %s' % abs_file_path)
                self.sendFile(abs_file_path, 0)
                conn.sendall(self.calcFileMD5(abs_file_path))
                return self.checkConsistency(abs_file_path)

    def sendFile(self, dest_file, begin):
        conn = self.request
        print('发送文件')
        with open(dest_file, 'rb') as f:
            f.seek(begin)
            for line in f:
                print(line)
                conn.sendall(line)

    def checkConsistency(self, destfile):
        conn = self.request
        # conn.sendall(self.calcFileMD5(destfile))
        # 获取client端对比文件md5的结果
        print('检测一致性')
        result = conn.recv(1024).strip()
        print(result)
        if result == '203':
            return ['203', '%s 下载成功' % destfile]
        else:
            print('文件不一致')
            choice = conn.recv(1024).strip()
            print(choice)
            while True:
                print('开始重传')
                # choice = conn.recv(1024).strip()
                if choice == 'y' or choice == 'y':
                    self.sendFile(destfile, 0)
                    conn.sendall(self.calcFileMD5(destfile))
                    return ['203', 'md5一致，重新同步完成']
                elif choice == 'N' or choice == 'n':
                    return ['403', '%s md5不一致，并取消同步']
                elif choice == '':
                    choice = conn.recv(1024).strip()
                    continue
                else:
                    return ['403', '无效的选项']

    def calcFileMD5(self, destfile):
        m = hashlib.md5()
        if os.path.isfile(destfile):
            with open(destfile, 'rb') as f:
                for line in f:
                    m.update(line)
            return m.hexdigest()
        else:
            return 'error'

    def determine_send_file(self, destFile):
        conn = self.request
        destFileSize = os.stat(destFile).st_size
        '''
            client不存在文件返回0
                  存在文件就返回client中文件的大小
        '''
        try:
            clientDestFileSize = int(conn.recv(1024).strip())
        except ValueError:
            return ['403', '获取客户端文件大小错误']
        if clientDestFileSize == 0:
            with open(destFile, 'rb') as dest:
                # 直接发送文件
                m = hashlib.md5()
                for line in dest:
                    conn.sendall(line)
                    m.update(line)
                else:
                    dest.close()
                    conn.sendall('%s md5:%s' % (destFile, m.hexdigest()))
                return ['203', '发送文件 %s 成功' % destFile]
        elif clientDestFileSize == destFileSize:
            with open(destFile, 'rb') as dest:
                m = hashlib.md5()
                for line in dest:
                    m.update(line)
                conn.sendall
        else:
            # 用 f.seek 调整要发送的指针，增量发送
            with open(destFile, 'rb') as dest:
                dest.seek(clientDestFileSize)
                m = hashlib.md5()
                for line in dest:
                    pass

    def action_cd(self, args):
        if len(args) == 0:
            self.current_dir = self.userinfo['home_dir']
            return ['203', '切换到家目录下']
        elif len(args) >= 2:
            return ['403', 'cd后面不能接一个以上参数']
        else:
            # cmd = 'cd %s' % args[0]
            # returnstring = self.action(cmd)
            current_path_list = self.current_dir.strip('/').split('/')
            arg_path_list = args[0].strip().split('/')
            backdir_count = arg_path_list.count('..')
            diffpath = len(current_path_list) - 4 - backdir_count
            if diffpath < 0:
                return ['403', '切换目录越界']
            else:
                for i in xrange(0, backdir_count):
                    current_path_list.pop(-1)
                    arg_path_list.pop(0)
                print(current_path_list)
                print(arg_path_list)
                new_path = '/' + '/'.join(current_path_list) + '/' + '/'.join(arg_path_list)
                print(new_path)
                if os.path.isdir(new_path):
                    self.current_dir = new_path
                    return ['203', '成功切换至目录 %s' % new_path]
                else:
                    return ['403', '切换目录失败，目录不存在']
            '''
            if os.path.isdir('%s/[%s]' % (self.current_dir, args[0])):
                self.current_dir = ('%s/%s' % (self.current_dir, args[0]))
                return ['203', '成功切换至目录 %s' % args[0]]
            else:
                return ['403', '%s 目录不存在' % args[0]]
            '''

    def pwd(self, args):
        return ['203', '当前目录为：%s' % self.current_dir]

    def action(self, cmd):
        resp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        returnstring = resp.communicate()
        if resp.returncode == 0:
            return ['203', returnstring[0]]
        else:
            return ['403', returnstring[1]]

    def action_ls(self, args):
        if len(args) == 0:
            cmd = 'ls -l %s' % self.current_dir
            '''
            print(cmd)
            resp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            returnstring = resp.communicate()
            # print(str(returnstring))
            # print(resp.returncode)
            if resp.returncode == 0:
                return ['203', returnstring[0]]
            else:
                return ['403', returnstring[1]]
            '''
        elif len(args) == 1:
            abs_file_path = self.analyzePath(args[0])
            # print(abs_file_path[0], abs_file_path[1])
            if abs_file_path[0] == '203':
                cmd = 'ls -l %s' % abs_file_path[1]
            else:
                return abs_file_path
        else:
            return ['405', '参数格式过多']
        print(cmd)
        resp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        returnstring = resp.communicate()
        # print(str(returnstring))
        # print(resp.returncode)
        if resp.returncode == 0:
            return ['203', returnstring[0]]
        else:
            return ['403', returnstring[1]]

    def mkdir(self, args):
        if len(args) == 0:
            return ['405', 'mkdir后面需要接参数']
        else:
            cmd = 'mkdir %s/%s' % (self.current_dir, args[0])
            return self.action(cmd)
        '''
        returnstring = resp.communicate()
        if resp.returncode == 0:
            return ['203', returnstring[0]]
        else:
            return ['403', returnstring[1]]
        '''

    def analyzePath(self, pathstring):
        reobj_root = re.compile('^/')
        # reobj_back = re.compile('^\.')
        if reobj_root.match(pathstring):
            if pathstring.startswith(self.userinfo['home_dir']) and os.path.exists(pathstring):
                return ['203', pathstring]
            else:
                return ['409', '%s 是非法路径']
        # elif reobj_back.match(pathstring):
        else:
            abs_path_list = self.current_dir.strip('/').split('/')
            path_list = pathstring.split('/')
            for i in path_list:
                if i == '..':
                    path_list.pop(0)
                    abs_path_list.pop(-1)
                elif i == '.':
                    path_list.pop(0)
                else:
                    continue
            abs_path = '/%s/%s' % ('/'.join(abs_path_list), '/'.join(path_list))
            if abs_path.startswith(self.userinfo['home_dir']):
                if os.path.exists(abs_path):
                    return ['203', abs_path]
                else:
                    return ['403', '%s 路径不存在' % abs_path]
            else:
                return ['409', '%s 是非法路径' % abs_path]
            # print('生成的路径为：%s' % abs_path)
        # else:

    def actionRm(self, args):
        conn = self.request
        result = self.analyzePath(args[0])
        if result[0] == '203':
            if os.path.isfile(result[1]):
                os.remove(result[1])
                conn.sendall('%s:%s' % (result[0], '删除文件 %s 成功' % result[1]))
                return [result[0], '删除文件 %s 成功' % result[1]]
            else:
                os.rmdir(result[1])
                conn.sendall('%s:%s' % (result[0], '删除目录 %s 成功' % result[1]))
                return [result[0], '删除目录 %s 成功' % result[1]]
        else:
            conn.sendall('%s:%s' % (result[0], result[1]))
            return result

    def actionMv(self, args):
        conn = self.request
        src_path = self.analyzePath(args[0])
        dest_path = self.analyzePath(args[1])
        print('mv %s %s' % (src_path[1], dest_path[1]))
        if src_path[0] == '403':
            conn.sendall('%s:%s不存在' % ('403', src_path[1]))
            return ['403', '%s不存在' % src_path[1]]
        # elif os.path.isfile(src_path[1]) or os.path.isdir(src_path[1]):
        elif dest_path[0] == '203':
            # if os.path.isfile(dest_path[1]) or os.path.isdir(dest_path[1]):
            if os.path.isfile(dest_path[1]) and os.path.isdir(src_path[1]):
                conn.sendall('403:%s是目录，%s是文件，不合理操作' % (src_path[1], dest_path[1]))
                return ['403', '%s是目录，%s是文件，不合理操作' % (src_path[1], dest_path[1])]
            elif os.path.isdir(dest_path[1]):
                return_code = os.system('mv %s %s' % (src_path[1], dest_path[1]))
                if return_code == 0:
                    conn.sendall('203:mv移动操作成功')
                    return ['203', 'mv移动操作成功']
                else:
                    conn.sendall('408:mv移动操作失败，未知错误')
                    return ['408', 'mv移动失败，未知错误']
            else:
                conn.sendall('%s:%s 已存在，是否覆盖(Y/N)' % ('406', dest_path))
                while True:
                    choice = conn.recv(1024).strip()
                    if choice == 'y' or choice == 'Y':
                        return_code = os.system('mv -f %s %s' % (src_path[1], dest_path[1]))
                        if return_code == 0:
                            conn.sendall('203:mv覆盖操作成功')
                            return ['203', 'mv覆盖操作成功']
                        else:
                            conn.sendall('408:mv覆盖操作失败，未知错误')
                            return ['408', 'mv操作失败，未知错误']
                    elif choice == 'N' or choice == 'n':
                        return ['403', '%s 已存在，并取消覆盖' % dest_path[1]]
                    else:
                        continue
        elif dest_path[0] == '403':
            dest_path[1] = dest_path[1].split(' ')[0]
            return_code = os.system('mv %s %s' % (src_path[1], dest_path[1]))
            if return_code == 0:
                conn.sendall('203:mv重命名操作成功')
                return ['203', 'mv重命名操作成功']
            else:
                conn.sendall('408:mv重命名操作失败，未知错误')
                return ['408', 'mv重命名操作失败，未知错误']
        else:
            conn.sendall('409:%s' % dest_path[1])
            return ['409', dest_path[1]]

    def manageUser(self, commandstring):
        conn = self.request
        manager_dict = {
            'useradd': self.useradd,
            'userdel': self.userdel,
            'usermod': self.usermod,
            'show': self.showUser,
        }
        if commandstring.startswith('usermod'):
            reobj = re.compile('{.*}')
            args = reobj.findall(commandstring)[0]
            user_name = commandstring.split(' ')[1]
            ret = manager_dict['usermod'](user_name, args)
        else:
            args = commandstring.strip().split(' ')
            ret = manager_dict[args[0]](args[1:])
        conn.sendall('%s:%s' % (ret[0], ret[1]))
        return ret

    def resetPasswd(self, args):
        print(str(args))
        conn = self.request
        db = self.load_db()
        db[args[0]]['password'] = self.md5(args[1])
        self.write_to_db(db)
        conn.sendall('203:%s 修改密码成功' % args[0])
        return ['203', '%s 修改密码成功' % args[0]]

    def useradd(self, args):
        conn = self.request
        if self.read_from_db(args[0].strip(',')) != '1':
            # conn.sendall('%s:%s已存在，无法添加' % ('403', args[0].strip(',')))
            return ['403', '%s 已存在，无法添加' % args[0].strip(',')]
        else:
            user_dict = self.load_db()
            if len(args[2].strip(',')) == 0:
                home_dir = '%s/%s' % (self.base_home_dir, args[0].strip(','))
            if len(args[3].strip(',')) == 0:
                disk_quota = '1GB'
            user_dict[args[0].strip(',')] = {
                'password': self.md5(args[1].strip(',')),
                'home_dir': home_dir,
                'disk_quota': disk_quota,
            }
            self.write_to_db(user_dict)
            # conn.sendall('%s:添加%s成功' % ('203', args[0].strip(',')))
            return ['203', '添加 %s 成功' % args[0].strip(',')]

    '''
    def userdel(self, args):
        conn = self.request
        ret = self.actionUserdel(args)
        conn.sendall('%s:%s' % (ret[0], ret[1]))
        return ret
    '''

    def showUser(self, args):
        if args[0] == 'all':
            user_dict = self.load_db()
            user_string = ''
            for name in user_dict:
                remain_size = self.autoChangeSize(self.changeToByte(user_dict[name]['disk_quota']) - self.getDirSize(user_dict[name]['home_dir']))
                user_string += '\n>>>>>>>>%s--%s\n%s--%s\n%s--%s\n%s--%s' % ('用户名', name, '磁盘配额', user_dict[name]['disk_quota'], '家目录', user_dict[name]['home_dir'], '剩余可用空间', remain_size)
            return ['203', user_string]
        else:
            if self.read_from_db(args[0]) == '1':
                return ['402', '%s 不存在' % args[0]]
            else:
                userinfo = self.read_from_db(args[0])
                # print()
                remain_size = self.autoChangeSize(self.changeToByte(userinfo['disk_quota']) - self.getDirSize(userinfo['home_dir']))
                # print('%s %s' % (type(remain_size), remain_size))
                user_string = '\n>>>>>>>>%s--%s\n%s--%s\n%s--%s\n%s--%s' % ('用户名', args[0], '磁盘配额', userinfo['disk_quota'], '家目录', userinfo['home_dir'], '剩余可用空间', remain_size)
                return ['203', user_string]

    def userdel(self, args):
        if len(args) == 2:
            if args[1] == '-r':
                '''
                if self.read_from_db(args[0]) == '1':
                    return ['403', '%s 不存在']
                else:
                    user_dict = self.load_db()
                    user_dict.pop('')
                '''
                user_dict = self.load_db()
                try:
                    user_dict.pop(args[0])
                    return ['203', '删除用户 %s 成功,并删除用户家目录' % args[0]]
                except KeyError:
                    return ['403', '用户 %s 不存在' % args[0]]
            else:
                return ['403', '不支持该选项 %s' % args[1]]
        else:
            user_dict = self.load_db()
            try:
                user_dict.pop(args[0])
                return ['203', '删除用户 %s 成功' % args[0]]
            except KeyError:
                return ['403', '用户 %s 不存在' % args[0]]

    def usermod(self, user_name, args):
        '''
        -q 修改磁盘配额
        -d 重命名家目录，加上 -n 表示直接新建一个家目录
        '''
        conn = self.request
        args_dict = eval(args)
        '''
        for k in args_dict:
            if k == '-q':
                # 修改磁盘配额
                pass
            elif '-d' in args_dict and '-n' in args_dict:
                # 修改家目录名称
                pass
            elif '-d' in args_dict and '-n' not in args_dict:
                pass
            else:
        '''
        right_string = ''
        if '-q' in args_dict:
            quota = args_dict.pop('-q').upper()
            # 修改磁盘配额
            user_dict = self.load_db()
            user_dict[user_name]['disk_quota'] = quota
            self.write_to_db(user_dict)
            # return ['203', '修改磁盘']
            right_string += '成功修改磁盘配额为 %s\n' % quota
        if '-d' in args_dict and '-n' in args_dict:
            home = '%s/%s' % (self.base_home_dir, args_dict.pop('-d'))
            args_dict.pop('-n')
            if os.path.isdir(home):
                return ['403', '%s 已存在，无法创建' % home]
            else:
                os.mkdir(home)
                user_dict = self.load_db()
                user_dict[user_name]['home_dir'] = home
                self.write_to_db(user_dict)
                right_string += '成功创建新的家目录 %s' % home
        if '-d' in args_dict and '-n' not in args_dict:
            home = '%s/%s' % (self.base_home_dir, args_dict.pop('-d'))
            if os.path.isdir(home):
                return ['403', '%s 已存在，无法重命名' % home]
            else:
                user_dict = self.load_db()
                os.rename(user_dict[user_name]['home_dir'], home)
                user_dict[user_name]['home_dir'] = home
                self.write_to_db(user_dict)
                right_string += '成功重命名家目录 %s' % home
        conn.sendall('203:%s' % right_string)
        return ['203', right_string]

    def handle(self):
        conn = self.request
        self.spe_action_list = {
            'put': self.action_put,
            'get': self.action_get,
            'rm': self.actionRm,
            'mv': self.actionMv,
            'passwd': self.resetPasswd,
            # 'useradd': self.useradd,
            # 'userdel': self.userdel,
            # 'usermod': self.usermod,
        }

        admin_manage_list = ['useradd', 'userdel', 'usermod', 'show']
        conn.sendall('welcome, please login')
        print "client:%s" % str(self.client_address)
        loginInfo = conn.recv(1024)
        print(loginInfo)
        # flag, username, password = loginfo.strip().split(',')
        ret = self.auth_or_register(loginInfo)
        if ret in status_code:
            conn.sendall('%s %s' % (ret, status_code[ret]))
        else:
            conn.sendall("不支持的操作")
            conn.close()

        if ret == '200' or ret == '201':
            try:
                while True:
                    rsock, wsock, esock = select.select([conn], [conn], [conn], 60)
                    if len(rsock) == 0:
                        continue
                    commandstring = rsock[0].recv(1024).strip()
                    cmd_list = commandstring.split(' ')
                    command = cmd_list[0]
                    args = cmd_list[1:]
                    if commandstring == '' or commandstring == '\n':
                        continue
                    # 这里添加对get，put命令的解析
                    elif command in self.spe_action_list:
                        # 这里执行get ，put操作
                        print('开始执行命令 %s' % command)
                        ret = self.spe_action_list[command](args)
                        print('%s %s\n%s' % (ret[0], status_code[ret[0]], ret[1]))
                    elif command in admin_manage_list:
                        print('开始执行命令 %s' % command)
                        ret = self.manageUser(commandstring)
                        print('%s %s\n%s' % (ret[0], status_code[ret[0]], ret[1]))
                    else:
                        ret = self.interact(commandstring)
                        print(commandstring)
                        print(str(ret))
                        if ret[0] in status_code:
                            print('开始发送执行结果')
                            wsock[0].sendall("%s %s\n%s" % (ret[0], status_code[ret[0]], ret[1]))
                            print "成功发送执行结果"
                            # wsock[0].sendall("%s" % ret[1])
            except KeyboardInterrupt:
                print "退出程序。。。"
                sys.exit(1)
        '''
        if ret == '1':
            conn.sendall('200')
            print "%s成功注册账号：%s" % (self.client_address, loginInfo)
        else:
            conn.sendall('400')
            print "%s注册失败账号：%s" % (self.client_address, loginInfo)
        
        while True:
            c = conn.recv(1024)
            print c
        '''


if __name__ == '__main__':
    server = SocketServer.ThreadingTCPServer(('127.0.0.1', 9999), MyServer)
    server.serve_forever()
