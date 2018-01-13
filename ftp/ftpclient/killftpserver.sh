#!/bin/bash
#
pid=`ps aux | grep ftpserver.py | grep -v grep | awk '{print $2}'`
if [ -n $pid ];then
	kill -9 $pid && echo "$pid 停止成功"
else
	echo "后台没有ftpserver进程"
fi
