"""
测试云端数据库连接和登录功能
用于验证修复是否成功
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "backend"))

from database import SessionLocal, DATABASE_URL, engine
from models import User
from auth import verify_password
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("测试1: 数据库连接")
    print("=" * 60)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_user_exists():
    """测试用户是否存在"""
    print("\n" + "=" * 60)
    print("测试2: 用户'刘紫湲'是否存在")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            (User.username == "刘紫湲") | (User.nickname == "刘紫湲")
        ).first()
        
        if user:
            print(f"✅ 用户存在")
            print(f"   用户ID: {user.id}")
            print(f"   用户名: {user.username}")
            print(f"   昵称: {user.nickname}")
            print(f"   是否激活: {user.is_active}")
            print(f"   是否有密码: {'是' if user.password_hash else '否'}")
            return user
        else:
            print("❌ 用户不存在")
            return None
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return None
    finally:
        db.close()

def test_password_verification(user):
    """测试密码验证"""
    print("\n" + "=" * 60)
    print("测试3: 密码验证")
    print("=" * 60)
    
    if not user:
        print("⚠️  跳过（用户不存在）")
        return False
    
    test_passwords = ["123456", "zhaxia", "password"]
    
    for pwd in test_passwords:
        try:
            is_valid = verify_password(pwd, user.password_hash)
            if is_valid:
                print(f"✅ 密码验证成功: {pwd}")
                return True
        except Exception as e:
            print(f"⚠️  密码验证失败 ({pwd}): {e}")
    
    print("❌ 所有测试密码都验证失败")
    return False

def test_login_simulation(user):
    """模拟登录流程"""
    print("\n" + "=" * 60)
    print("测试4: 模拟登录流程")
    print("=" * 60)
    
    if not user:
        print("⚠️  跳过（用户不存在）")
        return False
    
    # 模拟登录逻辑（与 auth.py 中的逻辑一致）
    try:
        # 1. 检查用户是否存在（已通过）
        print("✅ 步骤1: 用户查找成功")
        
        # 2. 检查密码
        if not user.password_hash:
            print("❌ 步骤2: 用户没有密码")
            return False
        print("✅ 步骤2: 用户有密码")
        
        # 3. 检查账户状态
        if not user.is_active:
            print("❌ 步骤3: 账户未激活")
            return False
        print("✅ 步骤3: 账户已激活")
        
        # 4. 密码验证（使用默认密码）
        test_password = "123456"
        try:
            is_valid = verify_password(test_password, user.password_hash)
            if is_valid:
                print(f"✅ 步骤4: 密码验证成功 (密码: {test_password})")
                print("\n✅ 登录流程测试通过！")
                return True
            else:
                print(f"⚠️  步骤4: 密码验证失败 (测试密码: {test_password})")
                print("   提示: 实际密码可能不同，请使用正确的密码")
                return False
        except Exception as e:
            print(f"❌ 步骤4: 密码验证异常: {e}")
            return False
        
    except Exception as e:
        print(f"❌ 登录流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("云端数据库连接和登录功能测试")
    print("=" * 60)
    
    # 显示当前数据库URL（隐藏敏感信息）
    if "@" in DATABASE_URL:
        prefix, suffix = DATABASE_URL.split("@", 1)
        redacted_url = "***@" + suffix
    else:
        redacted_url = DATABASE_URL
    
    print(f"\n当前数据库URL: {redacted_url}")
    
    # 运行测试
    results = []
    
    # 测试1: 数据库连接
    results.append(("数据库连接", test_database_connection()))
    
    if not results[0][1]:
        print("\n❌ 数据库连接失败，无法继续测试")
        return
    
    # 测试2: 用户是否存在
    user = test_user_exists()
    results.append(("用户存在", user is not None))
    
    # 测试3: 密码验证
    if user:
        results.append(("密码验证", test_password_verification(user)))
    else:
        results.append(("密码验证", False))
    
    # 测试4: 登录流程
    results.append(("登录流程", test_login_simulation(user)))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！云端登录应该可以正常工作")
    else:
        print("❌ 部分测试失败，请检查:")
        print("   1. 数据库连接是否正常")
        print("   2. 用户是否存在")
        print("   3. 密码是否正确")
        print("   4. 用户是否激活")
    print("=" * 60)

if __name__ == "__main__":
    main()

