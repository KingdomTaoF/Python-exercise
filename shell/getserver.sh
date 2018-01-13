#!/bin/bash

getserver() {
    case $1 in
        "2")
            be=1
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
            ;;
    esac
    
    
    
    #for i in `egrep ',7[0-9]{3},' /data/.qqslogin.profile | awk -F, '{print $3}' | uniq`;do
    for i in `awk -F, -v be=$be '$2>be{print $3}' /data/.qqslogin.profile | awk -F, -v en=$en '$2<en{print $3}' | uniq`;do
        echo -n "$i:"
        grep `echo -n $i` /data/.qqslogin.profile | awk -F, '{print $2}' | tr "\n" " "
        echo 
        #for j in `grep `echo -n $i` .qqslogin | awk -F, '{print $2}'`;done
        #    echo 
        #done

    done
}

getserver 8