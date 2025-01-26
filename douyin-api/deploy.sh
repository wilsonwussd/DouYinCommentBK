#!/bin/bash

echo "开始部署抖音评论采集 API 服务..."

# 检查 Python 版本
echo "检查 Python 版本..."
python3 --version || { echo "请先安装 Python 3"; exit 1; }

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv || { echo "创建虚拟环境失败"; exit 1; }

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate || { echo "激活虚拟环境失败"; exit 1; }

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt || { echo "安装依赖失败"; exit 1; }

# 检查 cookie 环境变量
if [ -z "$DOUYIN_COOKIE" ]; then
    if [ -f "../DouyinComments/cookie.txt" ]; then
        echo "从 DouyinComments/cookie.txt 读取 cookie..."
        export DOUYIN_COOKIE=$(cat ../DouyinComments/cookie.txt)
    else
        echo "请设置 DOUYIN_COOKIE 环境变量或确保 DouyinComments/cookie.txt 文件存在"
        exit 1
    fi
fi

# 检查 douyin.js 文件
if [ ! -f "app/douyin.js" ]; then
    if [ -f "../DouyinComments/douyin.js" ]; then
        echo "复制 douyin.js 文件..."
        cp ../DouyinComments/douyin.js app/
    else
        echo "请确保 douyin.js 文件存在"
        exit 1
    fi
fi

# 创建日志目录
echo "创建日志目录..."
mkdir -p logs

# 启动服务器
echo "启动服务器..."
export FLASK_DEBUG=1
export PYTHONPATH=$PWD
python run.py 