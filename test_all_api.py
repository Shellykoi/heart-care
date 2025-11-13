#!/usr/bin/env python3
"""
全面测试API功能
测试注册、登录、Token验证、用户面板、咨询师面板等所有功能
"""

import requests
import json
import sys
from typing import Dict, Optional

import time

BASE_URL = "http://localhost:8000/api"
# 使用时间戳确保唯一性
TIMESTAMP = int(time.time())
TEST_USERNAME = f"testuser_{TIMESTAMP}"
TEST_PASSWORD = "test123456"
TEST_PHONE = f"138{str(TIMESTAMP)[-8:]}"  # 使用时间戳后8位
TEST_EMAIL = f"test_{TIMESTAMP}@test.com"

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg: str):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.RESET}")

def print_error(msg: str):
    print(f"{Colors.RED}[ERROR] {msg}{Colors.RESET}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}[WARNING] {msg}{Colors.RESET}")

def print_info(msg: str):
    print(f"{Colors.BLUE}[INFO] {msg}{Colors.RESET}")

def test_health_check() -> bool:
    """测试健康检查"""
    print("\n" + "="*60)
    print("1. 测试健康检查")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/api/health", timeout=5)
        if response.status_code == 200:
            print_success(f"健康检查通过: {response.json()}")
            return True
        else:
            print_error(f"健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"健康检查异常: {str(e)}")
        return False

def test_options_request() -> bool:
    """测试OPTIONS预检请求"""
    print("\n" + "="*60)
    print("2. 测试OPTIONS预检请求")
    print("="*60)
    try:
        # 测试登录接口的OPTIONS请求
        response = requests.options(
            f"{BASE_URL}/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            },
            timeout=5
        )
        print_info(f"OPTIONS响应状态码: {response.status_code}")
        print_info(f"OPTIONS响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print_success("OPTIONS请求成功")
            return True
        else:
            print_error(f"OPTIONS请求失败: {response.status_code}")
            print_error(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print_error(f"OPTIONS请求异常: {str(e)}")
        return False

def test_register() -> Optional[Dict]:
    """测试用户注册"""
    print("\n" + "="*60)
    print("3. 测试用户注册")
    print("="*60)
    try:
        data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "phone": TEST_PHONE,
            "email": TEST_EMAIL
        }
        print_info(f"注册数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print_info(f"注册响应状态码: {response.status_code}")
        print_info(f"注册响应内容: {response.text}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print_success("注册成功")
            print_success(f"Token: {result.get('access_token', '')[:30]}...")
            return result
        else:
            print_error(f"注册失败: {response.status_code}")
            print_error(f"错误信息: {response.text}")
            return None
    except Exception as e:
        print_error(f"注册异常: {str(e)}")
        return None

def test_login() -> Optional[Dict]:
    """测试用户登录"""
    print("\n" + "="*60)
    print("4. 测试用户登录")
    print("="*60)
    try:
        data = {
            "account": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        print_info(f"登录数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print_info(f"登录响应状态码: {response.status_code}")
        print_info(f"登录响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print_success("登录成功")
            print_success(f"Token: {result.get('access_token', '')[:30]}...")
            return result
        else:
            print_error(f"登录失败: {response.status_code}")
            print_error(f"错误信息: {response.text}")
            return None
    except Exception as e:
        print_error(f"登录异常: {str(e)}")
        return None

def test_token_verification(token: str) -> bool:
    """测试Token验证"""
    print("\n" + "="*60)
    print("5. 测试Token验证")
    print("="*60)
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 测试获取当前用户信息
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=headers,
            timeout=5
        )
        
        print_info(f"Token验证响应状态码: {response.status_code}")
        print_info(f"Token验证响应内容: {response.text}")
        
        if response.status_code == 200:
            user_info = response.json()
            print_success("Token验证成功")
            print_success(f"用户信息: {json.dumps(user_info, indent=2, ensure_ascii=False)}")
            return True
        else:
            print_error(f"Token验证失败: {response.status_code}")
            print_error(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print_error(f"Token验证异常: {str(e)}")
        return False

def test_user_stats(token: str) -> bool:
    """测试用户统计API"""
    print("\n" + "="*60)
    print("6. 测试用户统计API")
    print("="*60)
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/users/stats",
            headers=headers,
            timeout=5
        )
        
        print_info(f"用户统计响应状态码: {response.status_code}")
        print_info(f"用户统计响应内容: {response.text}")
        
        if response.status_code == 200:
            stats = response.json()
            print_success("用户统计API调用成功")
            print_success(f"统计数据: {json.dumps(stats, indent=2, ensure_ascii=False)}")
            return True
        else:
            print_error(f"用户统计API调用失败: {response.status_code}")
            print_error(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print_error(f"用户统计API异常: {str(e)}")
        return False

def test_counselor_stats(token: str) -> bool:
    """测试咨询师统计API"""
    print("\n" + "="*60)
    print("7. 测试咨询师统计API")
    print("="*60)
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/counselors/stats/mine",
            headers=headers,
            timeout=5
        )
        
        print_info(f"咨询师统计响应状态码: {response.status_code}")
        print_info(f"咨询师统计响应内容: {response.text}")
        
        if response.status_code == 200:
            stats = response.json()
            print_success("咨询师统计API调用成功")
            print_success(f"统计数据: {json.dumps(stats, indent=2, ensure_ascii=False)}")
            return True
        elif response.status_code in [403, 404]:
            # 403或404都表示用户不是咨询师，这是正常的
            print_warning("用户不是咨询师，这是正常的")
            return True
        else:
            print_error(f"咨询师统计API调用失败: {response.status_code}")
            print_error(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print_error(f"咨询师统计API异常: {str(e)}")
        return False

def test_search_counselors() -> bool:
    """测试搜索咨询师"""
    print("\n" + "="*60)
    print("8. 测试搜索咨询师")
    print("="*60)
    try:
        response = requests.get(
            f"{BASE_URL}/counselors/search",
            params={"limit": 10},
            timeout=5
        )
        
        print_info(f"搜索咨询师响应状态码: {response.status_code}")
        print_info(f"搜索咨询师响应内容: {response.text[:500]}...")  # 只显示前500字符
        
        if response.status_code == 200:
            counselors = response.json()
            print_success(f"搜索咨询师成功，找到 {len(counselors)} 个咨询师")
            if len(counselors) > 0:
                counselor = counselors[0]
                print_success(f"第一个咨询师信息: {json.dumps(counselor, indent=2, ensure_ascii=False)}")
                # 检查关键字段
                required_fields = ['id', 'real_name', 'gender', 'specialty', 'fee']
                missing_fields = [f for f in required_fields if f not in counselor]
                if missing_fields:
                    print_error(f"缺少必需字段: {missing_fields}")
                    return False
                else:
                    print_success("所有必需字段都存在")
            return True
        else:
            print_error(f"搜索咨询师失败: {response.status_code}")
            print_error(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print_error(f"搜索咨询师异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("南湖心理咨询管理平台 - API全面测试")
    print("="*60)
    
    # 测试结果统计
    results = {
        "health_check": False,
        "options_request": False,
        "register": False,
        "login": False,
        "token_verification": False,
        "user_stats": False,
        "counselor_stats": False,
        "search_counselors": False
    }
    
    # 1. 健康检查
    results["health_check"] = test_health_check()
    if not results["health_check"]:
        print_error("\n后端服务未运行，请先启动后端服务！")
        print_info("启动命令: cd src/backend && python main.py")
        sys.exit(1)
    
    # 2. OPTIONS请求
    results["options_request"] = test_options_request()
    
    # 3. 注册
    register_result = test_register()
    if register_result:
        results["register"] = True
        token = register_result.get("access_token")
    else:
        # 如果注册失败，尝试登录（用户可能已存在）
        print_warning("注册失败，尝试登录...")
        login_result = test_login()
        if login_result:
            results["login"] = True
            token = login_result.get("access_token")
        else:
            print_error("注册和登录都失败，无法继续测试")
            sys.exit(1)
    
    # 4. 登录（如果注册成功，也测试登录）
    if register_result:
        login_result = test_login()
        if login_result:
            results["login"] = True
            token = login_result.get("access_token")
    
    # 5. Token验证
    if token:
        results["token_verification"] = test_token_verification(token)
        
        # 6. 用户统计
        if results["token_verification"]:
            results["user_stats"] = test_user_stats(token)
            results["counselor_stats"] = test_counselor_stats(token)
    
    # 7. 搜索咨询师（不需要token）
    results["search_counselors"] = test_search_counselors()
    
    # 打印测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name:20s}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print_success("\n所有测试通过！")
        sys.exit(0)
    else:
        print_error(f"\n有 {total - passed} 个测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()

