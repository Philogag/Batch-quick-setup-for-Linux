#!/bin/bash

get_os_type(){
  info=`cat /etc/os-release`
  for i in ${info[@]}
  do 
    case ${i%%=*} in
    NAME)
      os_type=`echo ${i#*=} | tr -d \"`
      ;;
    VERSION_ID)
      os_version=`echo ${i#*=} | tr -d \"`
      ;;
    esac
  done
  SYSTEM_INFO=$os_type:$os_version
}
get_os_type()

echo $SYSTEM_INFO

case $SYSTEM_INFO in 
# "Deepin:15.11" | "Deepin:20 Beta" | "Deepin:20" | "Ubuntu:20.04" | "Ubuntu:18.04")
#     ;;
  "CentOS Linux:7")
    case $1 in
    ################################################
    ################ Network Config ################
      "bootproto" | "ipaddr" | "netmask" | "gateway" | "dns1" | "dns2")
        ensfile=`ls /etc/sysconfig/network-scripts/ | grep "ifcfg-e" | head -n 1`
        sed -i "s/${1^^}.*/${1^^}=$2/g" $ensfile
        if [$? -ne 0]; then
          echo failed.
        else 
          echo success.
        fi
      ;;
    #################################################
    ################ Set user passwd ################
      "passwd")
        echo "$3\n$3" | passwd --stdin $2
        if [$? -ne 0]; then
          echo failed.
        else 
          echo success.
        fi
      ;;
    ################################################
    ################# Set Hostname #################
      "hostname")
        hostnamectl set-hostname $2
        if [$? -ne 0]; then
          echo failed.
        else 
          echo success.
        fi
      ;;
    ################################################
    ################ Do Final Step #################
    # enable network 
      "exit")
        systemctl restart network
        rm -rf ~/reset.sh
      ;;
    esac
    ;;
esac
