#!/bin/bash
# 功能：这个脚本时候用来生成总的开服计划的，用来汇报消息的时候用
#	并生成更新列表

if [ $# -ne 3 ];then
	echo "usage:./`basename $0` now/next 开服邮件 开服个数"
	exit 3
fi

tmpfile=/tmp/tmpfile

if [ $1 == "now" ];then
	sh /script/tencent_name.sh $2 > /tmp/tmpfile
elif [ $1 == 'next' ];then
	sh /script/tencent_name.sh $2 $3 > /tmp/tmpfile
else
	echo '错误的用法'
	exit 2	
fi

function nextWeek() {
	for i in `echo -e '星座服\n生肖服\n热血服\n联盟服'`;do
		echo -n "$i:`grep -A $1 "$i" $tmpfile | tail -$1 | head -1 | awk '{print $2}'`-"
		echo "`grep -A $1 "$i" $tmpfile | tail -1 | awk '{print $2}'`"

	done
}

function nextWeekList() {
	for i in `echo -e '星座服\n生肖服\n热血服\n联盟服'`;do
		echo -n "tencent|`grep -A $1 "$i" $tmpfile | tail -$1 | head -1 | awk '{print $2}'`-"
		echo "`grep -A $1 "$i" $tmpfile | tail -1 | awk '{print $2}'`"
	done
	
}

if [ $1 == now ];then
	# 本周开服计划
	echo -e "\033[32m开服计划:\033[0m" 
	for i in `grep -A 4 '更新列表' /script/tmpfile | tail -4 | awk -F'|' '{print $2}'`;do
		n=`echo $i | awk -F'-' '{print $1}'`
		if [ $n -lt 1000 ];then
			n=$[$n+6000]
		fi
		if [ $n -gt 7000 ];then
			echo 星座服：$i
		elif [ $n -gt 6000 ];then
			echo 联盟服：`echo $i | awk -F'-' '{print $1+6000"-"$2+6000}'`
			tmp=`echo $i | awk -F'-' '{print $1+6000"-"$2+6000}'`
		elif [ $n -gt 5000 ];then
			echo 生肖服：$i
		else
			echo 热血服：$i
		fi
	done
	echo -e "\033[32m更新列表:\033[0m" 
	for i in `grep -A 4 '更新列表' /script/tmpfile | tail -4`;do
		if [ `echo -n $i | wc -m` -lt 17 ];then
			echo tencent"|"`echo $i | awk -F'|' '{print $2}' | awk -F'-' '{print $1+6000"-"$2+6000}'`
		else
			echo $i
		fi

	done
else
	# 下周开服计划
	echo -e "\033[32m霸业腾讯:\033[0m" 
	nextWeek $3
	echo "以上区服已搭建，请知悉"
	echo ""

	# 打印到运维管理后台生成更新列表时需要的内容
	echo -e "\033[32m更新列表内容:\033[0m" 
	nextWeekList $3
fi



