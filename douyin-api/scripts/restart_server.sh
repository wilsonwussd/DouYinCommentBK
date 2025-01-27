#!/bin/bash

echo "正在停止当前服务..."
pid=$(pgrep -f "python.*run.py")
if [ ! -z "$pid" ]; then
    kill $pid
    sleep 2
fi

echo "正在启动服务..."
cd /home/devbox/project/douyin-api
python3 run.py &
echo "服务已重启" 