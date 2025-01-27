#!/bin/bash

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 设置基础 URL (使用文档中的外部域名)
BASE_URL="https://slrgzucgttzq.sealoshzh.site/api"
TOKEN=""
COOKIE_FILE="cookie.txt"

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 检查cookie文件
print_message $YELLOW "\n检查cookie文件..."
if [ ! -f "$COOKIE_FILE" ]; then
    print_message $RED "错误: cookie.txt 文件不存在!"
    exit 1
fi

# 读取cookie
COOKIE=$(cat $COOKIE_FILE)
if [ -z "$COOKIE" ]; then
    print_message $RED "错误: cookie.txt 文件为空!"
    exit 1
fi
print_message $GREEN "成功读取cookie"

# 设置通用请求头
COMMON_HEADERS=(
    "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    "Cookie: $COOKIE"
    "Accept: application/json, text/plain, */*"
    "Accept-Language: zh-CN,zh;q=0.9"
    "Content-Type: application/json"
)

# 构建curl headers字符串
HEADERS=""
for header in "${COMMON_HEADERS[@]}"; do
    HEADERS="$HEADERS -H \"$header\""
done

# 测试健康检查
print_message $YELLOW "\n1. 测试健康检查接口..."
health_response=$(curl -s -k $BASE_URL/health)
if [[ $health_response == *"healthy"* ]]; then
    print_message $GREEN "健康检查成功: $health_response"
else
    print_message $RED "健康检查失败: $health_response"
    exit 1
fi

# 注册新用户
print_message $YELLOW "\n2. 测试用户注册..."
register_response=$(curl -s -k -X POST -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"testpass"}' \
     $BASE_URL/users/register)
if [[ $register_response == *"注册成功"* ]]; then
    print_message $GREEN "用户注册成功: $register_response"
else
    print_message $RED "用户注册失败: $register_response"
fi

# 用户登录
print_message $YELLOW "\n3. 测试用户登录..."
login_response=$(curl -s -k -X POST -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"testpass"}' \
     $BASE_URL/users/login)
if [[ $login_response == *"access_token"* ]]; then
    TOKEN=$(echo $login_response | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    print_message $GREEN "用户登录成功，获取到token"
else
    print_message $RED "用户登录失败: $login_response"
    exit 1
fi

# 获取用户信息
print_message $YELLOW "\n4. 测试获取用户信息..."
user_info_response=$(curl -s -k -H "Authorization: Bearer $TOKEN" $BASE_URL/users/me)
if [[ $user_info_response == *"username"* ]]; then
    print_message $GREEN "获取用户信息成功: $user_info_response"
else
    print_message $RED "获取用户信息失败: $user_info_response"
fi

# 测试不同格式的视频ID
VIDEO_URLS=(
    "7346152359719996709"                                    # 纯数字ID
    "https://www.douyin.com/video/7346152359719996709"      # 完整URL
    "https://v.douyin.com/123456"                           # 短链接
)

for video_url in "${VIDEO_URLS[@]}"; do
    # 提取视频ID
    if [[ $video_url == *"douyin.com"* ]]; then
        VIDEO_ID=$(echo $video_url | grep -o '[0-9]\{19\}')
    else
        VIDEO_ID=$video_url
    fi
    
    print_message $YELLOW "\n5. 测试视频 $VIDEO_ID 的评论采集..."
    
    # 测试评论采集（默认模式）
    print_message $YELLOW "5.1 测试默认评论采集..."
    collect_response=$(curl -s -k -X POST -H "Authorization: Bearer $TOKEN" \
         -H "Content-Type: application/json" \
         -d "{\"video_id\":\"$VIDEO_ID\",\"max_comments\":10}" \
         $BASE_URL/comments/collect)
    if [[ $collect_response == *"comments"* ]]; then
        print_message $GREEN "默认评论采集成功: $collect_response"
    else
        print_message $RED "默认评论采集失败: $collect_response"
    fi

    # 测试批量评论采集
    print_message $YELLOW "5.2 测试批量评论采集..."
    batch_response=$(curl -s -k -X POST -H "Authorization: Bearer $TOKEN" \
         -H "Content-Type: application/json" \
         -d "{\"video_id\":\"$VIDEO_ID\",\"max_comments\":100,\"page\":1,\"per_page\":30}" \
         $BASE_URL/comments/collect)
    if [[ $batch_response == *"comments"* ]]; then
        print_message $GREEN "批量评论采集成功: $batch_response"
    else
        print_message $RED "批量评论采集失败: $batch_response"
    fi

    # 等待评论采集完成
    print_message $YELLOW "等待10秒让评论采集完成..."
    sleep 10

    # 测试评论查询（第一页）
    print_message $YELLOW "5.3 测试评论查询（第一页）..."
    comments_response=$(curl -s -k -H "Authorization: Bearer $TOKEN" \
         "$BASE_URL/comments/$VIDEO_ID?page=1&per_page=5")
    if [[ $comments_response == *"comments"* ]]; then
        print_message $GREEN "评论查询成功: $comments_response"
    else
        print_message $RED "评论查询失败: $comments_response"
    fi

    # 测试评论查询（第二页）
    print_message $YELLOW "5.4 测试评论查询（第二页）..."
    comments_response2=$(curl -s -k -H "Authorization: Bearer $TOKEN" \
         "$BASE_URL/comments/$VIDEO_ID?page=2&per_page=5")
    if [[ $comments_response2 == *"comments"* ]]; then
        print_message $GREEN "评论查询成功: $comments_response2"
    else
        print_message $RED "评论查询失败: $comments_response2"
    fi
done

print_message $YELLOW "\n所有测试完成!" 