#!/bin/bash

for i in `egrep ',7[0-9]{3},' /data/.qqslogin.profile | awk -F, '{print $3}' | uniq`;do
    echo -n "$i:"
    grep `echo -n $i` /data/.qqslogin.profile | awk -F, '{print $2}' | tr '\n' ' '
    for j in `grep `echo -n $i` .qqslogin | awk -F, '{print $2}'`;done
        
        echo 
    done
    
done