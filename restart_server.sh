#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 停止当前运行的服务
print_message $YELLOW "正在停止当前服务..."
pid=$(pgrep -f "python.*run.py")
if [ ! -z "$pid" ]; then
    kill $pid
    sleep 2
    print_message $GREEN "成功停止服务 PID: $pid"
else
    print_message $YELLOW "没有找到运行中的服务"
fi

# 进入项目目录
cd /home/devbox/project/douyin-api

# 检查环境
print_message $YELLOW "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    print_message $RED "错误: Python3 未安装"
    exit 1
fi

# 检查依赖
print_message $YELLOW "检查项目依赖..."
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt
    print_message $GREEN "依赖安装完成"
else
    print_message $RED "警告: requirements.txt 不存在"
fi

# 启动服务
print_message $YELLOW "正在启动服务..."
nohup python3 run.py > server.log 2>&1 &

# 等待服务启动
sleep 5

# 检查服务是否成功启动
new_pid=$(pgrep -f "python.*run.py")
if [ ! -z "$new_pid" ]; then
    print_message $GREEN "服务已成功启动，PID: $new_pid"
    print_message $YELLOW "服务日志保存在 server.log"
else
    print_message $RED "服务启动失败，请检查 server.log"
    tail -n 10 server.log
    exit 1
fi 