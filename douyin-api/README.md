# 抖音评论采集 API 服务

这是一个基于 Flask + SQLite + JWT 的抖音评论采集 API 服务。该服务提供了用户认证、评论采集和查询等功能。

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