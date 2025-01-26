#!/bin/bash

# 输出带颜色的信息
print_step() {
    echo -e "\033[1;34m[Step] $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m[Error] $1\033[0m"
}

print_success() {
    echo -e "\033[1;32m[Success] $1\033[0m"
}

# 确保在正确的目录
cd "$(dirname "$0")" || exit 1

# 创建日志目录
mkdir -p logs

# 终止现有的服务进程
print_step "Stopping existing server..."
pkill -f "python3 run.py" || true
sleep 2

# 删除旧的数据库文件以确保表结构更新
print_step "Cleaning old database..."
rm -f comments.db

# 启动服务器
print_step "Starting server..."
nohup python3 run.py > logs/server.log 2>&1 &
sleep 5

# 等待服务器完全启动
print_step "Waiting for server to start..."
for i in {1..12}; do
    if curl -s http://localhost:8080/api/health > /dev/null; then
        break
    fi
    echo "Waiting... ($i/12)"
    sleep 5
    if [ $i -eq 12 ]; then
        print_error "Server failed to start in time"
        exit 1
    fi
done

# 测试用户注册
print_step "Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{"username":"testuser","password":"testpass"}' http://localhost:8080/api/users/register)
if [[ $REGISTER_RESPONSE == *"error"* ]] && [[ $REGISTER_RESPONSE != *"用户名已存在"* ]]; then
    print_error "Registration failed: $REGISTER_RESPONSE"
fi

# 测试用户登录
print_step "Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{"username":"testuser","password":"testpass"}' http://localhost:8080/api/users/login)
if [[ $LOGIN_RESPONSE != *"access_token"* ]]; then
    print_error "Login failed: $LOGIN_RESPONSE"
    exit 1
fi

# 提取 token
TOKEN=$(echo $LOGIN_RESPONSE | sed 's/.*"access_token":"\([^"]*\)".*/\1/')

# 测试健康检查接口
print_step "Testing health check..."
HEALTH_RESPONSE=$(curl -s http://localhost:8080/api/health)
if [[ $HEALTH_RESPONSE != *"healthy"* ]]; then
    print_error "Health check failed: $HEALTH_RESPONSE"
    exit 1
fi

# 测试评论采集
print_step "Testing comment collection..."
COLLECT_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"video_id":"7346152359719996709","max_comments":10}' http://localhost:8080/api/comments/collect)
if [[ $COLLECT_RESPONSE != *"成功采集"* ]]; then
    print_error "Comment collection failed: $COLLECT_RESPONSE"
    exit 1
fi

# 测试评论查询
print_step "Testing comment retrieval..."
COMMENTS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8080/api/comments/7346152359719996709?page=1&per_page=5")
if [[ $COMMENTS_RESPONSE != *"comments"* ]]; then
    print_error "Comment retrieval failed: $COMMENTS_RESPONSE"
    exit 1
fi

print_success "Deployment completed successfully!"
print_success "Server is running at http://localhost:8080"
print_success "API documentation is available in README.md" 