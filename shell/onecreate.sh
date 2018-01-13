#!/bin/bash
#
# 用法:onecreate.sh 开服邮件文件 开服个数

/bin/bash /script/tx_tencent_name.sh $1 $2 > /script/name.tmp
funum=$2

# 参数列表：区服类型 
getBeginAndEnd(){
	case $1 in
	"热血服"|"联盟服")
		begin=`grep -A $funum $1 /script/name.tmp | tail -$funum | awk '{print $2}' | head -1`
		end=`grep -A $funum $1 /script/name.tmp | tail -$funum | awk '{print $2}' | tail -1`
		if [ $1 == '联盟服' ];then
			echo "$1,$begin,$end"
		else
			echo "$1,$[$begin+1],$end"
		fi
		;;

	"生肖服"|"星座服")
		begin=`grep -A $funum $1 /script/name.tmp | tail -$funum | awk '{print $3}' | head -1`
		end=`grep -A $funum $1 /script/name.tmp | tail -$funum | awk '{print $3}' | tail -1`
		echo "$1,$begin,$end"
		;;
	*)
		echo "错误的参数"
		;;
	esac
}

#getBeginAndEnd "联盟服"
#getBeginAndEnd "热血服"
#getBeginAndEnd "星座服"
#getBeginAndEnd "生肖服"

#for i in `echo -e "热血服\n星座服\n生肖服"`;
#for i in `echo -e "联盟服"`;
echo "使用该脚本前，请先修改 /data/script"
for i in `echo -e "热血服\n星座服\n生肖服\n联盟服"`;
do
	#echo '1'
	#echo $i
	arg=`getBeginAndEnd $i`
	#echo $arg
	read -p "是否要创建 $arg(Y\n):" choice
	case $choice in
	Y|y)
		echo "正在创建开平入口"
		echo $arg
		#python /script/kaifusimple.py -f $arg
		;;
	N|n)
		echo "取消创建开平入口 $arg"
		continue
		;;
	*)
		echo "未知选项，退出"
		exit 3
		;;
	esac
	#getBeginAndEnd $i
done

#arg=`getBeginAndEnd "热血服"`
#be=$[`echo $arg | awk -F, '{print $2}'`+1]
#newarg=`echo $arg | awk -F, -v be=$be '{print $1","be","$3}'`
#echo $arg
#echo $newarg
