#!/bin/bash
APP=go-gin
GUARD=guard_server.py
dir=$(dirname $0)
cd $dir
dir=$(pwd)
#pid=`cat ../var/monitor.pid`

pid=`ps uxU $USER|grep ${GUARD}|grep ${APP} |grep -v 'grep'|awk '{print $2}'`
echo "stop monitor process ${pid}"
kill ${pid}

sleep 0.5

pid=`ps uxU $USER|grep ${APP}|grep -- "--port"|grep -v 'grep'|awk '{print $2}'`
echo "stop server process ${pid}"
kill ${pid}

