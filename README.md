# 抖音评论采集后端服务

## 功能说明
- 用户认证：支持用户注册和登录，使用 JWT 进行身份验证
- 评论采集：支持采集指定抖音视频的一级评论和二级评论
- 评论管理：支持评论的分页查询和筛选
- 系统监控：提供健康检查接口，监控系统状态

## 项目架构
- 后端框架：Flask
- 数据库：SQLite
- 认证方式：JWT
- ORM：SQLAlchemy
- 服务器：Hypercorn

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

## 部署说明
1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行服务：
```bash
python run.py
```

3. 服务配置：
- 服务地址：`0.0.0.0:8080`
- 外部域名：`https://slrgzucgttzq.sealoshzh.site`

## API 接口说明

### 1. 用户相关接口

#### 1.1 用户注册
```http
POST /api/users/register
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}

响应示例：
{
    "message": "注册成功"
}
```

#### 1.2 用户登录
```http
POST /api/users/login
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}

响应示例：
{
    "access_token": "eyJhbGciOiJIUzI1..."
}
```

#### 1.3 获取用户信息
```http
GET /api/users/me
Authorization: Bearer <your_token>

响应示例：
{
    "username": "testuser",
    "created_at": "2025-01-26T15:31:57.137971",
    "last_login": "2025-01-26T15:31:57.137971",
    "status": "active"
}
```

### 2. 评论相关接口

#### 2.1 采集评论
```http
POST /api/comments/collect
Authorization: Bearer <your_token>
Content-Type: application/json

{
    "video_id": "7346152359719996709",
    "max_comments": 10
}

响应示例：
{
    "message": "成功采集 10 条评论",
    "video_id": "7346152359719996709"
}
```

#### 2.2 查询评论
```http
GET /api/comments/{video_id}?page=1&per_page=5
Authorization: Bearer <your_token>

响应示例：
{
    "comments": [
        {
            "comment_id": "7346152902128812852",
            "content": "评论内容",
            "created_at": "2024-01-26 12:00:00",
            "likes": 100,
            "reply_count": 10,
            "user_nickname": "用户昵称"
        }
    ],
    "total": 100,
    "page": 1,
    "per_page": 5,
    "total_pages": 20
}
```

### 3. 系统接口

#### 3.1 健康检查
```http
GET /api/health

响应示例：
{
    "status": "healthy",
    "database": "connected",
    "timestamp": "2025-01-26T15:40:43.596759"
}
```

## 注意事项
1. 所有需要认证的接口都需要在请求头中携带 `Authorization: Bearer <token>`
2. 评论采集接口支持限制最大采集数量
3. 评论查询接口支持分页，默认每页 10 条
4. 系统会自动记录用户最后登录时间

## 更新日志

### 2025-01-26
- 新增用户最后登录时间记录
- 优化数据库初始化逻辑
- 新增健康检查接口
- 完善错误处理和日志记录

### 2025-01-25
- 项目初始化
- 实现基础用户认证功能
- 实现评论采集和查询功能

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