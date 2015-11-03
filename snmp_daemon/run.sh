#!/bin/sh
while true
do
nohup python snmp_daemon.py >snmp.log 2>&1

restart_time=`date "+%Y-%m-%d %H:%M:%S"`
echo "Restart snmp daemon at $restart_time"
sleep 10s
done
