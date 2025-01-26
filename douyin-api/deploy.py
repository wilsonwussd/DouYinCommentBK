#!/usr/bin/env python3
import os
import sys
import time
import json
import signal
import subprocess
import requests
from pathlib import Path

# 配置信息
COOKIE = 'UIFID=c4a29131752d59acb78af076c3dbdd52744118e38e80b4b96439ef1e20799db016a10bc1be553047662060005ba2b7e8181666eedd75165be6636c2e0a383d866a3f60be596ffe54d1cc560bd723dc644a103e2b05ec982f040cb5acf6643f2ab6f06b6cff0c7d29c671ee1c61d169695d71db85f14e532f5b2978b82ab25f3583e6af099f1eed3b0d4fcddacfb68047958efe8bb089a532904a8fb087450faa9a62e6230aa7d26e5b83a1a8ec75d6a5f519b357b0a4bf8caab64b47277f5e0b'
BASE_URL = 'http://localhost:8080'
TEST_VIDEO_ID = '7346152359719996709'

def print_step(msg):
    print(f"\n{'='*20} {msg} {'='*20}")

def kill_existing_server():
    print_step("终止现有服务器进程")
    try:
        # 查找运行的 Python 进程
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'python3' in line and 'run.py' in line:
                pid = int(line.split()[1])
                os.kill(pid, signal.SIGKILL)
                print(f"已终止进程 PID: {pid}")
                time.sleep(1)  # 等待进程完全终止
    except Exception as e:
        print(f"终止进程时出错: {e}")

def update_config():
    print_step("更新配置文件")
    config_path = Path("config/config.py")
    if config_path.exists():
        with open(config_path, 'r') as f:
            content = f.read()
        
        # 更新 cookie
        content = content.replace("DOUYIN_COOKIE = os.getenv('DOUYIN_COOKIE', '')",
                                f"DOUYIN_COOKIE = '{COOKIE}'")
        
        with open(config_path, 'w') as f:
            f.write(content)
        print("配置文件更新成功")

def start_server():
    print_step("启动服务器")
    try:
        # 使用 nohup 在后台运行服务器
        subprocess.Popen(['nohup', 'python3', 'run.py', '&'],
                        stdout=open('logs/server.log', 'a'),
                        stderr=open('logs/server.error.log', 'a'))
        print("服务器启动中...")
        time.sleep(5)  # 等待服务器完全启动
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)

def test_apis():
    print_step("测试 API 接口")
    token = None
    
    # 1. 测试登录
    try:
        print("\n1. 测试登录接口")
        response = requests.post(f"{BASE_URL}/api/users/login",
                               json={"username": "testuser", "password": "testpass"})
        result = response.json()
        if 'access_token' in result:
            token = result['access_token']
            print("✓ 登录成功")
        else:
            print("✗ 登录失败")
            return
    except Exception as e:
        print(f"✗ 登录测试失败: {e}")
        return

    headers = {'Authorization': f'Bearer {token}'}

    # 2. 测试环境变量
    try:
        print("\n2. 测试环境变量接口")
        response = requests.get(f"{BASE_URL}/api/test/env", headers=headers)
        if response.status_code == 200:
            print("✓ 环境变量测试成功")
        else:
            print("✗ 环境变量测试失败")
    except Exception as e:
        print(f"✗ 环境变量测试失败: {e}")

    # 3. 测试评论采集
    try:
        print("\n3. 测试评论采集接口")
        response = requests.post(f"{BASE_URL}/api/comments/collect",
                               headers=headers,
                               json={"video_id": TEST_VIDEO_ID, "max_comments": 10})
        if response.status_code == 200:
            print("✓ 评论采集成功")
        else:
            print("✗ 评论采集失败")
    except Exception as e:
        print(f"✗ 评论采集测试失败: {e}")

    # 4. 测试评论获取
    try:
        print("\n4. 测试评论获取接口")
        response = requests.get(f"{BASE_URL}/api/comments/{TEST_VIDEO_ID}?page=1&per_page=5",
                              headers=headers)
        if response.status_code == 200:
            print("✓ 评论获取成功")
        else:
            print("✗ 评论获取失败")
    except Exception as e:
        print(f"✗ 评论获取测试失败: {e}")

def main():
    # 确保在正确的目录
    if not Path("run.py").exists():
        print("错误：请在 douyin-api 目录下运行此脚本")
        sys.exit(1)

    # 确保日志目录存在
    Path("logs").mkdir(exist_ok=True)

    try:
        kill_existing_server()
        update_config()
        start_server()
        test_apis()
        print_step("部署完成")
        print("服务器正在运行中...")
        print(f"API 地址: {BASE_URL}")
    except KeyboardInterrupt:
        print("\n部署过程被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n部署过程出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 