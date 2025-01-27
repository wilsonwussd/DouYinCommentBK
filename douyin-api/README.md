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

示例视频链接：
```
https://www.douyin.com/video/7431759837333130523
```

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
创建 cookie.txt 文件并填入抖音 cookie。示例 cookie：
```
UIFID=c4a29131752d59acb78af076c3dbdd52744118e38e80b4b96439ef1e20799db016a10bc1be553047662060005ba2b7e8181666eedd75165be6636c2e0a383d866a3f60be596ffe54d1cc560bd723dc644a103e2b05ec982f040cb5acf6643f2ab6f06b6cff0c7d29c671ee1c61d169695d71db85f14e532f5b2978b82ab25f3583e6af099f1eed3b0d4fcddacfb68047958efe8bb089a532904a8fb087450faa9a62e6230aa7d26e5b83a1a8ec75d6a5f519b357b0a4bf8caab64b47277f5e0b; is_staff_user=false; sessionid_ss=ca6d96f8757beb18b17c06d70afe2a34; passport_auth_status_ss=446fdab91bab565cb750c6e134711854%2C; ssid_ucp_sso_v1=1.0.0-KGYzMTc1ZGNkMjEzMGNmNWQzMjQ1ZDk3Yzg1MTlmNDUxMzZjYzZlMWEKIAjEjpC97c1NEN6rqbwGGO8xIAww6PW1twY4BkD0B0gGGgJobCIgMTJlOTEzNGRmZjA1YWIzMTY5N2UyYTdkY2Q1YTgwM2M; fpk1=U2FsdGVkX1/Gh2AKqzdqNLjwYXn3jmtxUXdIH/bt/HGVxKQk8+VfWsVJgoXWXTSOai23erXYtRWYI8stzmuYwQ==; sid_ucp_v1=1.0.0-KGJiMjUxNmZmY2UwMGMzN2M4OTAxMTYzYzVmNjcyYjVjNGQ3MzBmNTgKGgjEjpC97c1NEOurqbwGGO8xIAw4BkD0B0gEGgJscSIgY2E2ZDk2Zjg3NTdiZWIxOGIxN2MwNmQ3MGFmZTJhMzQ; toutiao_sso_user=12e9134dff05ab31697e2a7dcd5a803c; passport_mfa_token=Cjbod%2BRujGO%2FGRjY9WLxd%2BTXapF8x%2BHjTY29cLOg979L03daT9Gys%2BpoVUpo2Fwm%2FsQv6vFcGtwaSgo8CIRppvqijYvl3g6apIhUEBiKSgtkwFQaH9fObHAMtSk3yXVocjqlX%2FDQ0KITQNP6wAvrErNHxQjSLJiFEOiK5w0Y9rHRbCACIgEDTA0cBA%3D%3D; sid_ucp_sso_v1=1.0.0-KGYzMTc1ZGNkMjEzMGNmNWQzMjQ1ZDk3Yzg1MTlmNDUxMzZjYzZlMWEKIAjEjpC97c1NEN6rqbwGGO8xIAww6PW1twY4BkD0B0gGGgJobCIgMTJlOTEzNGRmZjA1YWIzMTY5N2UyYTdkY2Q1YTgwM2M; csrf_session_id=69fc499c32d91f746068480d4372a8e4; sso_uid_tt=739b0f1394f41be1b57f7cfbabb18d33; sid_guard=ca6d96f8757beb18b17c06d70afe2a34%7C1737119211%7C5183990%7CTue%2C+18-Mar-2025+13%3A06%3A41+GMT; sso_uid_tt_ss=739b0f1394f41be1b57f7cfbabb18d33; fpk2=f51bb482c660d0eeadd1f058058a2b35; passport_assist_user=CkAx4Zi774JqmSB5Yrn2oSJoaeVO-G0iNke515blWZK4TKbCrwaivtVgq4lBnC4-X1Er6He7xDU3_YF-HSwaBroKGkoKPMgQEmyQX-er0LqDP017motpPLXydEwQy-E3OMUk-ogBRL1FsGBcNHFh4tvYTR8eEfM6VbmoXcDXgd5zUhCHiucNGImv1lQgASIBA_nGEFo%3D; sessionid=ca6d96f8757beb18b17c06d70afe2a34; sid_tt=ca6d96f8757beb18b17c06d70afe2a34; ssid_ucp_v1=1.0.0-KGJiMjUxNmZmY2UwMGMzN2M4OTAxMTYzYzVmNjcyYjVjNGQ3MzBmNTgKGgjEjpC97c1NEOurqbwGGO8xIAw4BkD0B0gEGgJscSIgY2E2ZDk2Zjg3NTdiZWIxOGIxN2MwNmQ3MGFmZTJhMzQ; toutiao_sso_user_ss=12e9134dff05ab31697e2a7dcd5a803c; uid_tt=ce778635931ed96d84e789b43ce360a7; uid_tt_ss=ce778635931ed96d84e789b43ce360a7; UIFID_TEMP=c4a29131752d59acb78af076c3dbdd52744118e38e80b4b96439ef1e20799db016a10bc1be553047662060005ba2b7e8181666eedd75165be6636c2e0a383d862093e4bb1c136c529ba529f769665eebfee2a3f5babfff3dd71842db6e234be8
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