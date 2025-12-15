#!/bin/bash
# 停止脚本 - 停止运行中的应用

PORT=8000
PID=$(lsof -ti:$PORT)

if [ -z "$PID" ]; then
    echo "端口 $PORT 没有被占用，应用可能未运行"
    exit 0
fi

echo "找到运行中的应用进程: $PID"
read -p "是否要停止该进程? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    kill -9 $PID
    echo "应用已停止"
else
    echo "操作已取消"
fi

