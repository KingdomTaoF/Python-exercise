#!/bin/bash
#
# name:getInterface.sh
# description:
# usage:getInterface.sh options ARG
# author:king
# version:0.0.1
# date time:27/06/2016-00:40
#
# get the interface's IP
showIP() {
      if ifconfig | grep -o "^[^[:space:]]\{1,\}" | grep -o "$1$" &> /dev/null;then
              if [ "$1" == "lo" ];then
                      echo "this is lo interface ,IP is 127.0.0.1"
              else
                      echo "$1's IP `ifconfig $1 | grep -o "inet addr:[0-9\.]\{1,\}" | cut -d: -f2`"
              fi
      else
              echo "sorry, what is you type is not correct interface name"
      fi
}

# get an IP's interface
showInterface() {
      if ifconfig | grep -o "192.168.0.110" &> /dev/null;then
      else
              echo "sorry, the IP you type in doesn't belong to this host"
      fi
}

# show all the interface and its IP
showAll() {
      for I in `ifconfig | grep -o "^[^[:space:]]\{1,\}" | grep "[^lo]"`;do
              echo -n "$I:"
              showIP $I
      done
}

# usage of this script
usage() {
      echo "usage:`basename $0` [-i IP|-I interface|-a]"
}

# get the options
while getopts ":ai:I:" OPT;do
      case $OPT in
      a)
              showAll;;
      i)
              showIP $OPTARG;;
      I)
              showInterface $OPTARG;;
      *)
              usage;;
      esac
done