# 抖音评论采集 API 服务

一个基于 Flask + SQLite + JWT 的抖音视频评论采集服务，支持采集指定视频的一级评论。

## 最新更新

### 2024-01-27 更新
- 修复了异步调用问题，优化了评论采集逻辑
- 修复了 `sign_x_bogus` 签名生成问题
- 优化了视频ID提取逻辑，现支持多种格式的输入
- 改进了错误处理和日志记录
- 新增了服务器管理脚本

### Bug 修复
- 修复了 `common` 模块路径加载问题
- 修复了异步客户端未正确关闭的问题
- 修复了评论数据处理中的类型转换问题
- 修复了 URL 解析中的视频 ID 提取问题

## 功能特性

- 用户认证：基于 JWT 的用户认证系统
- 评论采集：支持采集指定视频的评论数据
- 数据存储：使用 SQLite 存储用户和评论数据
- 异步处理：使用 `httpx` 异步客户端提高性能
- 签名算法：集成抖音最新的签名算法

## API 接口文档

### 1. 健康检查
```http
GET /api/health
```
返回服务器和数据库状态

### 2. 用户注册
```http
POST /api/users/register
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

### 3. 用户登录
```http
POST /api/users/login
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```
返回 JWT token

### 4. 获取用户信息
```http
GET /api/users/me
Authorization: Bearer <your_token>
```

### 5. 评论采集
```http
POST /api/comments/collect
Authorization: Bearer <your_token>
Content-Type: application/json

{
    "video_id": "7431759837333130523",
    "max_comments": 10
}
```
支持以下格式的视频ID：
- 纯数字ID
- 完整视频URL
- 短链接

### 6. 获取评论
```http
GET /api/comments/<video_id>?page=1&per_page=10
Authorization: Bearer <your_token>
```

## 环境要求

- Python 3.8+
- Node.js (用于签名生成)
- SQLite 3

## 安装部署

1. 克隆仓库
```bash
git clone <repository_url>
cd douyin-api
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
# 创建 cookie.txt 文件并填入抖音 cookie
echo "your_douyin_cookie" > cookie.txt
```

4. 初始化数据库
```bash
python init_db.py
```

5. 启动服务
```bash
python run.py
```

## 管理脚本

### 重启服务器
```bash
#!/bin/bash
# restart_server.sh

echo "正在停止当前服务..."
pid=$(pgrep -f "python.*run.py")
if [ ! -z "$pid" ]; then
    kill $pid
    sleep 2
fi

echo "正在启动服务..."
cd /path/to/douyin-api
python3 run.py &
echo "服务已重启"
```

### 测试所有接口
```bash
#!/bin/bash
# test_apis.sh

# 设置基础 URL
BASE_URL="https://your-domain.com/api"
TOKEN=""

# 测试健康检查
echo "测试健康检查接口..."
curl $BASE_URL/health

# 注册新用户
echo "测试用户注册..."
curl -X POST -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"testpass"}' \
     $BASE_URL/users/register

# 用户登录
echo "测试用户登录..."
response=$(curl -X POST -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"testpass"}' \
     $BASE_URL/users/login)
TOKEN=$(echo $response | jq -r '.access_token')

# 获取用户信息
echo "测试获取用户信息..."
curl -H "Authorization: Bearer $TOKEN" $BASE_URL/users/me

# 采集评论
echo "测试评论采集..."
curl -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"video_id":"7431759837333130523","max_comments":10}' \
     $BASE_URL/comments/collect

# 获取评论
echo "测试获取评论..."
curl -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/comments/7431759837333130523?page=1&per_page=10"
```

## 使用说明

1. 确保服务器正常运行
```bash
curl http://localhost:8080/api/health
```

2. 注册新用户并获取 token
```bash
# 注册
curl -X POST -H "Content-Type: application/json" \
     -d '{"username":"your_username","password":"your_password"}' \
     http://localhost:8080/api/users/register

# 登录
curl -X POST -H "Content-Type: application/json" \
     -d '{"username":"your_username","password":"your_password"}' \
     http://localhost:8080/api/users/login
```

3. 使用 token 采集评论
```bash
curl -X POST -H "Authorization: Bearer your_token" \
     -H "Content-Type: application/json" \
     -d '{"video_id":"video_id_here","max_comments":10}' \
     http://localhost:8080/api/comments/collect
```

## 常见问题

1. **签名生成失败**
   - 检查 Node.js 是否正确安装
   - 确保 douyin.js 文件存在且有正确的权限

2. **Cookie 相关问题**
   - 确保 cookie.txt 文件存在且包含有效的 cookie
   - cookie 格式必须完整，不能缺少关键字段

3. **数据库错误**
   - 检查数据库文件权限
   - 确保 SQLite 正确安装

## 贡献指南

欢迎提交 Issue 和 Pull Request。在提交 PR 前，请确保：

1. 代码符合 PEP 8 规范
2. 添加了必要的测试
3. 更新了文档
4. 所有测试用例通过

## 许可证

MIT License 