#!/bin/bash
# 功能：1、这个是用来根据上周的腾讯的开服计划生成下周的开服计划的，并且会生成每个区服对应的区服ID和区服名称
# 	   用法: tencent_name.sh 开服邮件文件 开服个数（天多少个就生成多少个）
#	2、根据邮件简单显示当周的开服计划
#	   用法：tencent_name.sh 开服计划邮件

#animallist=['子鼠', '丑牛', '寅虎', '卯兔', '辰龙', '巳蛇', '午马', '未羊', '申猴', '酉鸡', '戌狗', '亥猪']
animallist=(子鼠  丑牛  寅虎  卯兔  辰龙  巳蛇  午马  未羊  申猴  酉鸡  戌狗  亥猪)
#constellationlist=['金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座', '白羊座']
constellationlist=(金牛座  双子座  巨蟹座  狮子座  处女座  天秤座  天蝎座  射手座  摩羯座  水瓶座  双鱼座  白羊座)

# 根据本周开服生成开服计划
function test1(){
    sed -i '/星期/d' $1
    sed -i '/^\s*$/d' $1	
    echo -e "\033[32m更新列表:\033[0m"
    UpdateList $1 "星座服"
    UpdateList $1 "生肖服"
    UpdateList $1 "联盟服"
    UpdateList $1 "热血服"   
    echo -e "\033[32m完整开服计划:\033[0m"
    awk '{print "tencent",$4,$5}' $1
}


function UpdateList(){
    echo "tencent|"`awk -v name=$2 '{if($3==name)print $4}' $1 | head -1`-`awk -v name=$2 '{if($3==name)print $4}' $1 | tail -1`

}


#UpdateList $1 "星座服"

# 参数：开服邮件 开服个数
function RexueAndLianmeng(){
	#last_rexue_qufuname=`grep "热血服" $1 | tail -1 | awk '{print $5}'`
	last_rexue_id=`grep "热血服" $1 | tail -1 | awk '{print $4}'`
	echo -e "\033[32m热血服区服名称:\033[0m" 
	if [ `grep "热血服" $1 | tail -1 | awk '{print $1}'` == 7 ];then
		other_name_list $last_rexue_id $2 '热血服'
	else
		other_name_list $[$last_rexue_id-1] $2 '热血服'		
	fi	
	
	last_lianmeng_id=`grep "联盟服" $1 | tail -1 | awk '{print $4}'`
	echo -e "\033[32m联盟服区服名称:\033[0m"
	if [ `grep "联盟服" $1 | tail -1 | awk '{print $1}'` -ne 1 ];then
		other_name_list $last_lianmeng_id $2 '联盟服'
	else
		other_name_list $[$last_lianmeng_id-1] $2 '联盟服'		
	fi

}

# 参数：起始ID  开服个数 开服类型 
function other_name_list(){
	if [ $3 == '热血服' ];then
		for i in `seq $[$1+1] $[$2+$1]`;do
			echo "tencent $i ${3:0:2}$i服"
		done
	else
		for i in `seq $[$1+1] $[$2+$1]`;do
			if [ $i -gt 6000 ];then
				echo "tencent $i ${3:0:2}$[$i-6000]区"
			else
				echo "tencent $[$i+6000] ${3:0:2}$i区"
					
			fi
		done
	fi

}

# 参数：星座服/生肖服的名称 列表名称
function find_index() {
	#echo $1
	case $2 in
	'animallist')
		for i in `seq 0 11`;do
			#echo ${animallist[$i]}
			if [ $1 == ${animallist[$i]} ];then
				echo -n $i
				break
			else
				if [ $i -eq 11 ];then
					echo "找不到该成员"
					exit 1
				else
					continue
				fi
			fi
		done
		;;
	'constellationlist')
		for i in `seq 0 11`;do
			if [ $1 == ${constellationlist[$i]} ];then
				echo -n $i
				break
			else
				if [ $i -eq 11 ];then
					echo "找不到该成员"
					exit 1
				else
					continue
				fi
			fi
		done
		;;
	*)
		echo "参数错误"
		;;
	esac
}
#find_index '午马' animallist
#echo ''
#find_index '射手座' constellationlist
#echo ${animallist[2]}

# 参数：起始index，开服个数，名字起始数字，区服ID，数组名
function name_list(){
	for i in `seq 1 $2`;do
		tmp=$[$1+$i]
		case $5 in
		'constellationlist')
			if [ $tmp -gt 11 ];then
				echo "tencent $[$4+$i] ${constellationlist[$[$tmp-12]]}$[$3+1]服"
			else
				echo "tencent $[$4+$i] ${constellationlist[$tmp]}$3服"
				#echo "tencent $[$4+$i] "
			fi
			;;
		'animallist')
			if [ $tmp -gt 11 ];then
				echo "tencent $[$4+$i] ${animallist[$[$tmp-12]]}$[$3+1]服"
			else
				echo "tencent $[$4+$i] ${animallist[$tmp]}$3服"
				#echo "tencent $[$4+$i] "
			fi
			;;			
		*)
			echo "错误的参数"
			;;
		esac
	done
}
#name_list 10 4 27 7315 constellationlist

# 根据上周邮件生成下周开服
function test2(){
	sed -i '/星期/d' $1
	sed -i '/^\s*$/d' $1
	
	last_xingzuo_qufuname=`grep "星座服" $1 | tail -1 | awk '{print $5}'`
	last_xingzuo_id=`grep "星座服" $1 | tail -1 | awk '{print $4}'`
	last_xingzuo_name=${last_xingzuo_qufuname:0:3}
	#echo $last_xingzuo_name
	last_xingzuo_index=`find_index $last_xingzuo_name constellationlist`
	last_xingzuo_namenum=${last_xingzuo_qufuname:3:2}
	#echo $last_xingzuo_index
	echo -e "\033[32m星座服区服名称:\033[0m"
	if [ `grep "星座服" $1 | tail -1 | awk '{print $1}'` == 7 ];then
		name_list $last_xingzuo_index $2 $last_xingzuo_namenum $last_xingzuo_id constellationlist
	else
		echo "tencent `grep "星座服" $1 | tail -1 | awk '{print $4,$5}'`"
		name_list $last_xingzuo_index $[$2-1] $last_xingzuo_namenum $last_xingzuo_id constellationlist
	fi
		
	last_shengxiao_qufuname=`grep "生肖服" $1 | tail -1 | awk '{print $5}'`
	last_shengxiao_id=`grep "生肖服" $1 | tail -1 | awk '{print $4}'`
	last_shengxiao_name=${last_shengxiao_qufuname:0:2}
	#echo $last_shengxiao_id
	last_shengxiao_index=`find_index $last_shengxiao_name animallist`
	if [ `echo -n $last_shengxiao_qufuname | wc -m` -gt 4 ];then 
		last_shengxiao_namenum=${last_shengxiao_qufuname:2:2}
	else
		last_shengxiao_namenum=${last_shengxiao_qufuname:2:1}
	fi
	echo -e "\033[32m生肖服区服名称:\033[0m"
	#name_list $last_shengxiao_index $2 $last_shengxiao_namenum $last_shengxiao_id animallist
	if [ `grep "生肖服" $1 | tail -1 | awk '{print $1}'` == 7 ];then
		name_list $last_shengxiao_index $2 $last_shengxiao_namenum $last_shengxiao_id animallist
	else
		echo "tencent `grep "生肖服" $1 | tail -1 | awk '{print $4,$5}'`"
		name_list $last_shengxiao_index $[$2-1] $last_shengxiao_namenum $last_shengxiao_id animallist	
	fi
}
#test2 'tencent.txt' 5

if [[ "$#" -eq 1  &&  -f $1 ]]; then
    	test1 $1
elif [ "$#" -eq 2 ];then
	test2 $1 $2
	RexueAndLianmeng $1 $2
else
    echo '用法：`basename $0` star_areaFile(上周or本周件列表文件) [开服个数]'
fi

#echo ${animallist[0]}
