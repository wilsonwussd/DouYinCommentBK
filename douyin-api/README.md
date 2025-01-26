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

## 功能特点

- 用户注册和登录（JWT 认证）
- 抖音视频评论采集
- 评论数据存储和查询
- 异步处理和并发控制
- 详细的日志记录

## 安装步骤

1. 克隆项目并进入项目目录：
```bash
git clone <repository_url>
cd douyin-api
```

2. 创建并激活虚拟环境：
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 设置环境变量：
```bash
export DOUYIN_COOKIE="your_douyin_cookie"  # 替换为你的抖音 cookie
export FLASK_DEBUG=1  # 开发环境设置
```

## 快速开始

1. 启动服务器：
```bash
python run.py
```

2. 服务器将在 http://localhost:5000 启动

## API 文档

### 1. 用户注册

- **URL**: `/api/register`
- **方法**: `POST`
- **请求体**:
```json
{
    "username": "your_username",
    "password": "your_password"
}
```
- **响应示例**:
```json
{
    "message": "注册成功"
}
```

### 2. 用户登录

- **URL**: `/api/login`
- **方法**: `POST`
- **请求体**:
```json
{
    "username": "your_username",
    "password": "your_password"
}
```
- **响应示例**:
```json
{
    "access_token": "your_jwt_token"
}
```

### 3. 采集评论

- **URL**: `/api/comments/collect`
- **方法**: `POST`
- **请求头**:
  - `Authorization: Bearer your_jwt_token`
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
            "id": 1,
            "video_id": "7346152359719996709",
            "comment_id": "7349050237821141810",
            "content": "评论内容",
            "likes": 4282,
            "user_nickname": "用户昵称",
            "user_id": "user123",
            "ip_location": "北京",
            "reply_count": 65,
            "created_at": "2024-03-22T05:08:22",
            "collected_at": "2025-01-26T12:33:14.866962"
        }
    ]
}
```

### 4. 查询评论

- **URL**: `/api/comments/<video_id>`
- **方法**: `GET`
- **请求头**:
  - `Authorization: Bearer your_jwt_token`
- **查询参数**:
  - `page`: 页码（默认 1）
  - `per_page`: 每页数量（默认 20）
- **响应示例**:
```json
{
    "total": 100,
    "pages": 5,
    "current_page": 1,
    "comments": [
        {
            "id": 1,
            "video_id": "7346152359719996709",
            "comment_id": "7349050237821141810",
            "content": "评论内容",
            "likes": 4282,
            "user_nickname": "用户昵称",
            "user_id": "user123",
            "ip_location": "北京",
            "reply_count": 65,
            "created_at": "2024-03-22T05:08:22",
            "collected_at": "2025-01-26T12:33:14.866962"
        }
    ]
}
```

### 5. 测试环境变量

- **URL**: `/api/test/env`
- **方法**: `GET`
- **请求头**:
  - `Authorization: Bearer your_jwt_token`
- **响应示例**:
```json
{
    "cookie_length": 2507,
    "cookie_preview": "cookie_preview_string",
    "env_vars": {
        "DOUYIN_COOKIE": "your_cookie",
        "FLASK_DEBUG": "1"
    }
}
```

## 依赖库

项目依赖以下主要库：

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-JWT-Extended==4.6.0
httpx==0.24.0
loguru==0.7.0
hypercorn==0.15.0
```

完整的依赖列表请参见 `requirements.txt`。

## 一键部署脚本

创建 `deploy.sh` 脚本：

```bash
#!/bin/bash

# 检查 Python 版本
python3 --version || { echo "请先安装 Python 3"; exit 1; }

# 创建虚拟环境
python3 -m venv venv || { echo "创建虚拟环境失败"; exit 1; }

# 激活虚拟环境
source venv/bin/activate || { echo "激活虚拟环境失败"; exit 1; }

# 安装依赖
pip install -r requirements.txt || { echo "安装依赖失败"; exit 1; }

# 检查 cookie 环境变量
if [ -z "$DOUYIN_COOKIE" ]; then
    echo "请设置 DOUYIN_COOKIE 环境变量"
    exit 1
fi

# 启动服务器
export FLASK_DEBUG=1
python run.py
```

使用方法：

1. 给脚本添加执行权限：
```bash
chmod +x deploy.sh
```

2. 运行脚本：
```bash
./deploy.sh
```

## 注意事项

1. 请确保设置了正确的抖音 cookie
2. 评论采集有频率限制，请合理设置采集参数
3. 建议在生产环境中关闭 debug 模式
4. 定期备份 SQLite 数据库文件

## 许可证

MIT License 