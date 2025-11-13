"""
测试 API 端点
"""
import requests
import json

# 测试健康检查
print("测试健康检查端点...")
try:
    response = requests.get("http://localhost:8000/api/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "="*50 + "\n")

# 测试管理员获取咨询师列表（需要认证）
print("测试管理员获取咨询师列表端点...")
try:
    # 先尝试登录获取 token
    login_data = {
        "account": "admin",  # 假设有管理员账号
        "password": "admin123"
    }
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    print(f"登录状态码: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        print(f"Token: {token[:20]}...")
        
        # 使用 token 测试管理员端点
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8000/api/admin/counselors/list?limit=100", headers=headers)
        print(f"获取咨询师列表状态码: {response.status_code}")
        print(f"响应: {response.text[:200]}")
    else:
        print(f"登录失败: {login_response.text}")
        # 测试不带 token 的请求
        response = requests.get("http://localhost:8000/api/admin/counselors/list?limit=100")
        print(f"不带 token 的状态码: {response.status_code}")
        print(f"响应: {response.text[:200]}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()








