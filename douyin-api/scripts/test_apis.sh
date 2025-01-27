#!/bin/bash

# 设置基础 URL
BASE_URL="https://slrgzucgttzq.sealoshzh.site/api"
TOKEN=""

# 测试健康检查
echo "测试健康检查接口..."
curl $BASE_URL/health
echo -e "\n"

# 注册新用户
echo "测试用户注册..."
curl -X POST -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"testpass"}' \
     $BASE_URL/users/register
echo -e "\n"

# 用户登录
echo "测试用户登录..."
response=$(curl -X POST -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"testpass"}' \
     $BASE_URL/users/login)
TOKEN=$(echo $response | jq -r '.access_token')
echo "获取到的 token: ${TOKEN:0:50}..."
echo -e "\n"

# 获取用户信息
echo "测试获取用户信息..."
curl -H "Authorization: Bearer $TOKEN" $BASE_URL/users/me
echo -e "\n"

# 测试环境变量
echo "测试环境变量..."
curl -H "Authorization: Bearer $TOKEN" $BASE_URL/test/env
echo -e "\n"

# 验证 cookie
echo "测试验证 cookie..."
curl -H "Authorization: Bearer $TOKEN" $BASE_URL/cookie/verify
echo -e "\n"

# 更新 cookie（这里使用示例 cookie，实际使用时需要替换为有效的 cookie）
echo "测试更新 cookie..."
curl -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"cookie":"your_new_cookie_here"}' \
     $BASE_URL/cookie/update
echo -e "\n"

# 采集评论
echo "测试评论采集..."
curl -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"video_id":"7431759837333130523","max_comments":10}' \
     $BASE_URL/comments/collect
echo -e "\n"

# 获取评论
echo "测试获取评论..."
curl -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/comments/7431759837333130523?page=1&per_page=10"
echo -e "\n"

echo "测试完成！" 