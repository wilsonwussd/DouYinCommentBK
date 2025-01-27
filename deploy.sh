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

# 检查系统要求
print_message $YELLOW "检查系统要求..."

# 检查 Python 版本
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    print_message $RED "错误: 未安装 Python3"
    exit 1
fi

# 检查 Node.js
node --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    print_message $RED "错误: 未安装 Node.js"
    exit 1
fi

# 检查 SQLite3
sqlite3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    print_message $RED "错误: 未安装 SQLite3"
    exit 1
fi

print_message $GREEN "系统要求检查通过"

# 创建虚拟环境
print_message $YELLOW "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
print_message $YELLOW "安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 初始化数据库
print_message $YELLOW "初始化数据库..."
python3 -c "
from douyin-api.app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
"

# 设置权限
print_message $YELLOW "设置文件权限..."
chmod +x restart_server.sh
chmod +x test_api.sh

# 检查配置文件
print_message $YELLOW "检查配置文件..."
if [ ! -f "cookie.txt" ]; then
    print_message $RED "警告: cookie.txt 文件不存在"
    print_message $YELLOW "请创建 cookie.txt 文件并填入抖音 cookie"
fi

# 启动服务
print_message $YELLOW "启动服务..."
./restart_server.sh

print_message $GREEN "部署完成！"
print_message $YELLOW "请确保："
print_message $YELLOW "1. cookie.txt 文件已正确配置"
print_message $YELLOW "2. 检查 server.log 确认服务启动状态"
print_message $YELLOW "3. 运行 ./test_api.sh 测试服务功能" 