#!/bin/bash

echo "开始部署抖音评论采集 API 服务..."

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python3"
    exit 1
fi

# 检查 Python 版本号
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$python_version < 3.8" | bc -l) )); then
    echo "错误: Python 版本必须 >= 3.8，当前版本: $python_version"
    exit 1
fi

# 创建并激活虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo "安装项目依赖..."
pip install -r requirements.txt

# 创建必要的目录
echo "创建日志目录..."
mkdir -p logs

# 检查环境变量
if [ -z "$DOUYIN_COOKIE" ]; then
    echo "警告: 未设置 DOUYIN_COOKIE 环境变量"
    echo "请设置 DOUYIN_COOKIE 环境变量后再运行服务"
    echo "示例: export DOUYIN_COOKIE='your_cookie_here'"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "生成随机 SECRET_KEY..."
    export SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "生成随机 JWT_SECRET_KEY..."
    export JWT_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
fi

# 启动服务
echo "启动 API 服务..."
PYTHONPATH=$(pwd) python3 run.py

echo "部署完成!" 