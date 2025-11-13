"""
测试后端API连接
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_connection():
    """测试后端连接"""
    print("=" * 50)
    print("测试后端API连接")
    print("=" * 50)
    
    # 测试1: 根路径
    print("\n1. 测试根路径...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        assert response.status_code == 200, "根路径应该返回200"
        print("   [OK] 根路径测试通过")
    except Exception as e:
        print(f"   [ERROR] 根路径测试失败: {e}")
        return False
    
    # 测试2: 健康检查
    print("\n2. 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        assert response.status_code == 200, "健康检查应该返回200"
        print("   [OK] 健康检查测试通过")
    except Exception as e:
        print(f"   [ERROR] 健康检查测试失败: {e}")
        return False
    
    # 测试3: CORS预检请求
    print("\n3. 测试CORS预检请求...")
    try:
        response = requests.options(
            f"{BASE_URL}/api/counselors/search",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,content-type"
            },
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        print(f"   CORS头: {dict(response.headers)}")
        assert response.status_code == 200, "CORS预检应该返回200"
        assert "Access-Control-Allow-Origin" in response.headers, "应该包含CORS头"
        print("   [OK] CORS预检测试通过")
    except Exception as e:
        print(f"   [ERROR] CORS预检测试失败: {e}")
        return False
    
    # 测试4: 咨询师搜索（无需认证）
    print("\n4. 测试咨询师搜索API...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/counselors/search",
            params={"limit": 10},
            headers={"Origin": "http://localhost:3000"},
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   返回咨询师数量: {len(data) if isinstance(data, list) else 'N/A'}")
            print("   [OK] 咨询师搜索测试通过")
        else:
            print(f"   响应: {response.text}")
            print("   [WARN] 咨询师搜索返回非200状态码")
    except Exception as e:
        print(f"   [ERROR] 咨询师搜索测试失败: {e}")
        return False
    
    # 测试5: 咨询师详情（无需认证）
    print("\n5. 测试咨询师详情API...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/counselors/1",
            headers={"Origin": "http://localhost:3000"},
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   咨询师姓名: {data.get('real_name', 'N/A')}")
            print("   [OK] 咨询师详情测试通过")
        elif response.status_code == 404:
            print("   [WARN] 咨询师不存在（这是正常的，如果没有数据）")
        else:
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"   [ERROR] 咨询师详情测试失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("所有测试完成！")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

