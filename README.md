# 抖音评论采集后端服务

## 功能目标
- 提供用户登录和身份认证功能（基于 JWT）
- 支持采集指定抖音视频 ID 的一级评论和二级评论
- 通过 API 接口返回采集的评论内容
- 考虑并发问题，保证系统稳定性和高效性

## 项目架构
- **Flask**: 后端框架，处理 API 请求
- **SQLite**: 轻量级数据库，用于存储用户和评论数据
- **JWT**: 身份认证，保证 API 安全性
- **Hypercorn**: ASGI 服务器，支持异步操作

## 目录结构
```
douyin-api/
├── app/                # 核心代码模块
├── config/            # 配置文件
├── logs/              # 日志文件
├── tests/             # 单元测试
├── run.py             # 服务器启动文件
└── deploy.py          # 自动化部署脚本
```

## API 接口说明
外部域名：https://slrgzucgttzq.sealoshzh.site

### 用户认证
- `POST /api/users/register` - 用户注册
  - 请求体: `{"username": "testuser", "password": "testpass"}`
  
- `POST /api/users/login` - 用户登录
  - 请求体: `{"username": "testuser", "password": "testpass"}`
  - 返回: JWT token

### 评论操作
- `POST /api/comments/collect` - 采集评论
  - 请求体: `{"video_id": "视频ID", "max_comments": 10}`
  - 需要 JWT 认证
  
- `GET /api/comments/{video_id}` - 获取评论
  - 参数: `page=1&per_page=5`
  - 需要 JWT 认证

### 环境测试
- `GET /api/test/env` - 测试环境变量
  - 需要 JWT 认证

## 部署说明
1. 确保安装了 Python 3.8+ 和所需依赖
2. 运行自动化部署脚本：
```bash
python3 deploy.py
```

## 服务器配置
- 端口: 8080
- 绑定地址: 0.0.0.0
- 日志位置: logs/app.log

## 性能优化
- 使用异步请求处理
- 实现评论数据缓存
- 支持分页查询
- 并发请求限制

## 注意事项
- API 请求需要携带有效的 JWT token
- 评论采集有频率限制，请合理使用
- 建议使用外部域名访问API接口

## 项目简介

这是一个基于 Flask + SQLite + JWT 的 RESTful API 服务，用于采集指定抖音视频的评论数据。该服务提供用户认证、评论采集和查询等功能，支持分页查询和并发请求处理。

## 主要功能

- 用户注册和登录(JWT认证)
- 评论采集(支持指定视频ID和最大评论数)
- 评论查询(支持分页)
- 评论数据本地存储(SQLite)
- 并发请求处理
- 详细的错误处理和日志记录

## 安装说明

1. 克隆项目:
```bash
git clone https://github.com/wilsonwussd/DouYinCommenBK.git
cd DouYinCommenBK
```

2. 创建并激活虚拟环境:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖:
```bash
pip install -r requirements.txt
```

4. 配置环境变量:
```bash
export DOUYIN_COOKIE="your_cookie_here"  # 设置抖音cookie
export SECRET_KEY="your_secret_key"      # 设置应用密钥
export JWT_SECRET_KEY="your_jwt_key"     # 设置JWT密钥
```

5. 运行服务:
```bash
python run.py
```

## API 文档

### 1. 用户注册
- **URL**: `/api/users/register`
- **方法**: `POST`
- **请求体**:
```json
{
    "username": "testuser",
    "password": "testpass"
}
```
- **响应示例**:
```json
{
    "message": "注册成功"
}
```

### 2. 用户登录
- **URL**: `/api/users/login`
- **方法**: `POST`
- **请求体**:
```json
{
    "username": "testuser",
    "password": "testpass"
}
```
- **响应示例**:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. 采集评论
- **URL**: `/api/comments/collect`
- **方法**: `POST`
- **请求头**: 
```
Authorization: Bearer <access_token>
```
- **请求体**:
```json
{
    "video_id": "7346152359719996709",
    "max_comments": 10
}
```
- **响应示例**:
```json
{
    "message": "成功采集 10 条评论",
    "comments": [
        {
            "comment_id": "7349050237821141810",
            "content": "评论内容",
            "created_at": "2024-03-22T05:08:22",
            "ip_location": "北京",
            "likes": 4282,
            "reply_count": 65,
            "user_id": "user123",
            "user_nickname": "用户昵称"
        }
    ]
}
```

### 4. 查询评论
- **URL**: `/api/comments/<video_id>`
- **方法**: `GET`
- **请求头**: 
```
Authorization: Bearer <access_token>
```
- **查询参数**:
  - page: 页码(默认1)
  - per_page: 每页条数(默认10)
- **响应示例**:
```json
{
    "comments": [...],
    "current_page": 1,
    "pages": 4,
    "total": 16
}
```

## 使用示例

1. 注册新用户:
```bash
curl -X POST http://localhost:5000/api/users/register \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser", "password":"testpass"}'
```

2. 登录获取token:
```bash
curl -X POST http://localhost:5000/api/users/login \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser", "password":"testpass"}'
```

3. 采集评论:
```bash
curl -X POST http://localhost:5000/api/comments/collect \
     -H "Authorization: Bearer <your_token>" \
     -H "Content-Type: application/json" \
     -d '{"video_id":"7346152359719996709", "max_comments":10}'
```

4. 查询评论:
```bash
curl -X GET "http://localhost:5000/api/comments/7346152359719996709?page=1&per_page=5" \
     -H "Authorization: Bearer <your_token>"
```

## 依赖说明

- Flask==3.0.0
- Flask-JWT-Extended==4.6.0
- Flask-SQLAlchemy==3.1.1
- httpx==0.24.0
- loguru==0.7.0
- hypercorn==0.15.0

## 一键部署

项目提供了一键部署脚本 `deploy.sh`，使用方法:

```bash
chmod +x deploy.sh
./deploy.sh
```

脚本会自动完成环境配置、依赖安装和服务启动。

## 开源协议

MIT License 