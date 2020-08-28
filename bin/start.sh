#!/bin/bash
#ulimit -c unlimited
dir=$(dirname $0)
cd $dir
./stop.sh

APP=go-gin
BINARY_NAME=go-gin

go build -o ../build/${BINARY_NAME} -tags=jsoniter -v ../

mkdir -p ../storage/logs
mkdir -p ../var

monitor_log=../storage/logs/monitor.log

export mode=prod
python guard_server.py --exec_bin=../build/${APP} --log_file $monitor_log --port_begin=5300 --proc_count=4
