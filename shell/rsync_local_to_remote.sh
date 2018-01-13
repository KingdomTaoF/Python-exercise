#!/bin/bash
# 这个脚本用来同步自己写的脚本到云主机上
src="/script/WinAndLinux/"
dest="root@119.28.186.225:/script/"
rsync -avPn $src $dest
read -p "以上是要同步过去的文件，是否同步y/n：" choice
case $choice in
    Y|y)
        echo "开始同步"
        rsync -avPz --delete $src $dest
        ;;
    N|n)
        echo "退出"
        ;;
    *)
        echo "usage: `basename $0`"
        ;;
esac