#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查后端服务连接状态的脚本"""
import requests
import sys

def check_backend():
    """检查后端服务是否可用"""
    try:
        # 测试根路径
        print("正在检查后端服务...")
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            print("[OK] 后端服务运行正常")
            print(f"    响应: {response.json()}")
            
            # 测试健康检查接口
            health_response = requests.get('http://localhost:8000/api/health', timeout=5)
            if health_response.status_code == 200:
                print("[OK] 健康检查接口正常")
                print(f"    响应: {health_response.json()}")
                return True
            else:
                print(f"[ERROR] 健康检查接口返回状态码: {health_response.status_code}")
                return False
        else:
            print(f"[ERROR] 后端服务返回状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到后端服务")
        print("       请确保:")
        print("       1. 后端服务已启动 (在 src/backend 目录运行 python main.py)")
        print("       2. 后端运行在 http://localhost:8000")
        print("       3. 防火墙未阻止连接")
        return False
    except requests.exceptions.Timeout:
        print("[ERROR] 连接超时")
        print("       后端服务可能响应缓慢或未启动")
        return False
    except Exception as e:
        print(f"[ERROR] 检查失败: {type(e).__name__}: {e}")
        return False

if __name__ == '__main__':
    success = check_backend()
    sys.exit(0 if success else 1)

