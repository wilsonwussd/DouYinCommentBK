# 抖音评论采集后端服务

## 项目简介
基于 Flask + SQLite + JWT 的抖音视频评论采集服务,支持一级评论和二级评论的采集、存储和查询。

## 功能特性
- 用户认证与授权(基于 JWT)
- Cookie 管理(验证、更新)
- 评论采集(支持批量)
- 评论查询(支持分页)
- 健康检查
- 日志记录

## 快速开始

### 环境要求
- Python 3.8+
- SQLite 3
- 其他依赖见 requirements.txt

### 安装部署
1. 克隆代码
```bash
git clone https://github.com/wilsonwussd/DouYinCommentBK.git
cd DouYinCommentBK
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件,配置必要的环境变量
```

4. 启动服务
```bash
./restart_server.sh
```

## API 接口文档

### 1. 健康检查
- **接口**: `GET /api/health`
- **描述**: 检查服务健康状态
- **返回示例**:
```json
{
    "database": "connected",
    "status": "healthy",
    "timestamp": "2025-01-27T09:50:05.126866"
}
```

### 2. 用户注册
- **接口**: `POST /api/users/register`
- **描述**: 注册新用户
- **请求体**:
```json
{
    "username": "testuser",
    "password": "testpass"
}
```
- **返回示例**:
```json
{
    "message": "注册成功"
}
```

### 3. 用户登录
- **接口**: `POST /api/users/login`
- **描述**: 用户登录获取 token
- **请求体**:
```json
{
    "username": "testuser",
    "password": "testpass"
}
```
- **返回示例**:
```json
{
    "access_token": "eyJhbGciOiJIUzI1..."
}
```

### 4. 获取用户信息
- **接口**: `GET /api/users/me`
- **描述**: 获取当前用户信息
- **请求头**: 
  - `Authorization: Bearer <token>`
- **返回示例**:
```json
{
    "username": "testuser",
    "created_at": "2025-01-27T05:52:00.025302",
    "last_login": "2025-01-27T09:50:05.311559",
    "status": "active"
}
```

### 5. Cookie 验证
- **接口**: `GET /api/cookie/verify`
- **描述**: 验证当前 Cookie 是否有效
- **请求头**: 
  - `Authorization: Bearer <token>`
- **返回示例**:
```json
{
    "valid": true,
    "message": "Cookie 有效",
    "expires_in": "未知"
}
```

### 6. Cookie 更新
- **接口**: `POST /api/cookie/update`
- **描述**: 更新 Cookie
- **请求头**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **请求体**:
```json
{
    "cookie": "UIFID=xxx; sessionid_ss=xxx; ..."
}
```
- **返回示例**:
```json
{
    "success": true,
    "message": "Cookie 更新成功",
    "verification": {
        "valid": true,
        "expires_in": "未知"
    }
}
```

### 7. JSON 格式 Cookie 更新
- **接口**: `POST /api/cookie/update`
- **描述**: 使用 JSON 格式更新 Cookie
- **请求头**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **请求体**:
```json
{
    "cookies": [
        {
            "name": "sessionid_ss",
            "value": "xxx"
        },
        {
            "name": "passport_csrf_token",
            "value": "xxx"
        }
    ]
}
```
- **返回示例**:
```json
{
    "success": true,
    "message": "Cookie 更新成功",
    "verification": {
        "valid": true,
        "expires_in": "未知"
    }
}
```

### 8. 评论采集
- **接口**: `POST /api/comments/collect`
- **描述**: 采集视频评论
- **请求头**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **请求体**:
```json
{
    "video_id": "7346152359719996709",
    "max_comments": 100,
    "page": 1,
    "per_page": 30
}
```
- **支持的视频ID格式**:
  - 纯数字ID: `7346152359719996709`
  - 完整URL: `https://www.douyin.com/video/7346152359719996709`
  - 短链接: `https://v.douyin.com/123456`
- **返回示例**:
```json
{
    "video_id": "7346152359719996709",
    "comments": [
        {
            "comment_id": "7349050237821141810",
            "content": "评论内容",
            "created_at": "2024-03-22T05:08:22",
            "ip_location": "北京",
            "likes": 4283,
            "reply_count": 65,
            "user_id": "4029075265422887",
            "user_nickname": "用户昵称"
        }
    ],
    "total": 100
}
```

### 9. 评论查询
- **接口**: `GET /api/comments/{video_id}`
- **描述**: 查询已采集的评论
- **请求头**: 
  - `Authorization: Bearer <token>`
- **参数**:
  - `page`: 页码(默认1)
  - `per_page`: 每页数量(默认10)
- **返回示例**:
```json
{
    "comments": [...],
    "total": 9739,
    "current_page": 1,
    "pages": 1948
}
```

## 测试脚本使用
项目提供了完整的测试脚本 `test_api.sh`,可以测试所有 API 接口:

```bash
./test_api.sh
```

测试内容包括:
1. 健康检查
2. 用户注册
3. 用户登录
4. 用户信息获取
5. Cookie 验证
6. Cookie 更新
7. 评论采集
8. 评论查询

## 注意事项
1. Cookie 必须包含以下字段:
   - sessionid_ss
   - passport_csrf_token
   - passport_csrf_token_default
   - s_v_web_id
   - ttwid

2. 评论采集注意事项:
   - 建议单次采集不超过 100 条评论
   - 采集间隔建议大于 1 秒
   - 注意处理 Cookie 过期情况

## 更新日志

### 2024-01-27
- 新增 Cookie 验证接口
- 新增 Cookie 更新接口
- 新增 JSON 格式 Cookie 更新支持
- 优化异步调用逻辑
- 改进评论采集稳定性
- 增加详细的错误日志
- 完善 API 文档

### 2024-01-26
- 初始版本发布
- 基础功能实现

## 贡献指南
欢迎提交 Issue 和 Pull Request。

## 许可证
MIT License
