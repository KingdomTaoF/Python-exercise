#!/bin/bash

getserver() {
    case $1 in
        "2")
            be=204
            en=5000
            ;;
        "5")
            be=5001
            en=6000
            ;;
        "6")
            be=6001
            en=7000
            ;;
        "7")
            be=7001
            en=8000
            ;;
        "8")
            be=8001
            en=9000
            ;;
        *)
            echo "wrong index"
			exit 1
            ;;
    esac
    
    for i in `awk -F, -v be=$be '$2>be{print $2","$6}' /data/.qqslogin.profile | awk -F, -v en=$en '$1<en{print $2}' | sort | uniq`;do
        echo -n "$i:"	
        grep `echo -n $i` /data/.qqslogin.profile | awk -F, '{print $2}' | tr "\n" "," | sed -nr 's#(.*),$#\1#gp' 
		num=`awk -F, -v ip=$i '$6==ip{print $2}' /data/.qqslogin.profile | wc -l | awk '{print $1}'`
		echo -n ":$num:"
		machine_mem=`awk -F: -v ip=$i '{if($1==ip)print $2}' /data/tx_machinemem.ini`
		if [ $1 == "6" ];then
			remain_mem=$[${machine_mem}-$num*6]
		else
			remain_mem=$[${machine_mem}-$num*8]
		fi
		echo -n ${machine_mem}:${remain_mem}
        echo 

    done
}

#getserver "8" > /tmp/txserver.tmp
#getserver "8"

selectID() {
	getserver $1 | sort -r -t: -n -k5 | head -$[$2+3]
	echo "区服排序信息:"
	getserver $1 | sort -r -t: -n -k5 | awk -F: '{print $2}' | awk -F, '{print $NF}' | head -$2 | tr '\n' ',' | sed -nr 's#(.*),$#\1#gp'
	echo
}


case $1 in
	"rexue")
		selectID "2" $2	
		;;
	"lianmeng")
		selectID "6" $2
		;;
	"shengxiao")
		selectID "5" $2
		;;
	"xingzuo")
		selectID "7" $2
		;;
	"diqu")
		selectID "8" $2
		;;
	*)
		echo "usage:`basename $0` 开服类型 开服数量"
		;;
esac


