# 抖音评论采集后端服务

基于 Flask + SQLite + JWT 的抖音视频评论采集服务，支持采集一级评论和二级评论。

## 功能特点

- 支持多种视频ID格式（纯数字ID、完整URL、短链接）
- JWT 身份认证，保证API安全
- 异步评论采集，提高性能
- 支持评论数据持久化存储
- 分页查询评论数据
- 完善的错误处理和日志记录

## 系统要求

- Python 3.8+
- SQLite 3
- Node.js (用于签名生成)

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/douyin-comment-collector.git
cd douyin-comment-collector
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

1. 创建 `cookie.txt` 文件，填入抖音 cookie：
```
# cookie.txt 示例内容
passport_csrf_token=xxx; passport_csrf_token_default=xxx; ...
```

2. 配置环境变量（可选）：
```bash
export DOUYIN_COOKIE="your_cookie_here"
export FLASK_SECRET_KEY="your_secret_key"
```

### 4. 启动服务

使用 `restart_server.sh` 脚本启动服务：
```bash
chmod +x restart_server.sh
./restart_server.sh
```

脚本功能说明：
1. 停止当前运行的服务（如果存在）
2. 检查 Python 环境和依赖
3. 启动新的服务实例
4. 记录服务日志到 server.log

### 5. 测试API

使用 `test_api.sh` 脚本测试所有接口：
```bash
chmod +x test_api.sh
./test_api.sh
```

脚本功能说明：
1. 检查 cookie 文件
2. 测试健康检查接口
3. 测试用户注册/登录
4. 测试评论采集和查询
5. 显示详细的测试结果

## API 文档

### 1. 健康检查

```http
GET /api/health
```

响应示例：
```json
{
    "status": "healthy",
    "database": "connected",
    "timestamp": "2025-01-27T08:11:46.471756"
}
```

### 2. 用户注册

```http
POST /api/users/register
Content-Type: application/json

{
    "username": "testuser",
    "password": "testpass"
}
```

响应示例：
```json
{
    "message": "注册成功"
}
```

### 3. 用户登录

```http
POST /api/users/login
Content-Type: application/json

{
    "username": "testuser",
    "password": "testpass"
}
```

响应示例：
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. 获取用户信息

```http
GET /api/users/me
Authorization: Bearer <access_token>
```

响应示例：
```json
{
    "username": "testuser",
    "created_at": "2025-01-27T05:52:00.025302",
    "last_login": "2025-01-27T08:11:46.656841",
    "status": "active"
}
```

### 5. 采集评论

```http
POST /api/comments/collect
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "video_id": "7346152359719996709",
    "max_comments": 100
}
```

支持的视频ID格式：
- 纯数字ID：`7346152359719996709`
- 完整URL：`https://www.douyin.com/video/7346152359719996709`
- 短链接：`https://v.douyin.com/123456`

响应示例：
```json
{
    "video_id": "7346152359719996709",
    "total": 100,
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
    ]
}
```

### 6. 查询评论

```http
GET /api/comments/<video_id>?page=1&per_page=20
Authorization: Bearer <access_token>
```

响应示例：
```json
{
    "total": 9739,
    "pages": 487,
    "current_page": 1,
    "comments": [
        {
            "comment_id": "7463765317694112548",
            "content": "评论内容",
            "created_at": "2025-01-25T08:21:31",
            "ip_location": "重庆",
            "likes": 19,
            "reply_count": 2,
            "user_id": "1062555095668956",
            "user_nickname": "用户昵称"
        }
    ]
}
```

## 最近更新

### v1.0.1 (2025-01-27)

1. **连接管理优化**：
   - 修复了客户端连接管理问题
   - 优化了异步请求处理
   - 改进了连接池配置

2. **评论采集改进**：
   - 支持多种视频ID格式
   - 优化批量采集性能
   - 添加重试机制

3. **错误处理增强**：
   - 完善异常捕获和处理
   - 优化错误提示信息
   - 增加详细日志记录

## 常见问题

### 1. 服务启动问题

1. **依赖安装失败**
   ```bash
   error: externally-managed-environment
   ```
   解决方案：
   - 创建并使用虚拟环境
   - 使用 `--break-system-packages` 参数（不推荐）

2. **端口被占用**
   ```bash
   Error: Address already in use
   ```
   解决方案：
   - 使用 `restart_server.sh` 正确停止旧服务
   - 手动结束占用端口的进程

### 2. 评论采集问题

1. **Cookie 无效**
   - 确保 cookie.txt 文件存在且内容有效
   - 定期更新 cookie 内容

2. **采集失败**
   - 检查网络连接
   - 验证视频ID格式
   - 查看 server.log 获取详细错误信息

## 部署建议

1. **系统配置**
   - 使用虚拟环境隔离依赖
   - 配置适当的系统资源限制
   - 启用日志轮转

2. **性能优化**
   - 适当调整并发连接数
   - 配置合理的采集间隔
   - 启用数据库索引

3. **安全建议**
   - 定期更换密钥
   - 限制 API 访问频率
   - 启用 HTTPS

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 作者

- 作者名字 - [GitHub](https://github.com/your-username)

## 致谢

- Flask 框架
- SQLite 数据库
- JWT 认证
- 所有贡献者 