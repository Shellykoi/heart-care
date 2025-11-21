"""
诊断云端数据库连接和用户数据
用于检查云端数据库是否正常连接，以及用户"刘紫湲"是否存在
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "backend"))

from database import SessionLocal, DATABASE_URL, engine
from models import User
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_connection():
    """检查数据库连接"""
    print("=" * 60)
    print("检查数据库连接...")
    print("=" * 60)
    
    # 隐藏敏感信息
    if "@" in DATABASE_URL:
        prefix, suffix = DATABASE_URL.split("@", 1)
        redacted_url = "***@" + suffix
    else:
        redacted_url = DATABASE_URL
    
    print(f"数据库URL: {redacted_url}")
    print(f"数据库类型: {'PostgreSQL' if 'postgresql' in DATABASE_URL.lower() else 'MySQL' if 'mysql' in DATABASE_URL.lower() else 'Unknown'}")
    
    try:
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_user_liuziyuan():
    """检查用户'刘紫湲'是否存在"""
    print("\n" + "=" * 60)
    print("检查用户'刘紫湲'...")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 查找用户（支持多种字段）
        user = db.query(User).filter(
            (User.username == "刘紫湲") |
            (User.nickname == "刘紫湲") |
            (User.phone == "刘紫湲") |
            (User.email == "刘紫湲") |
            (User.student_id == "刘紫湲")
        ).first()
        
        if user:
            print(f"✅ 找到用户'刘紫湲'")
            print(f"   用户ID: {user.id}")
            print(f"   用户名: {user.username}")
            print(f"   昵称: {user.nickname}")
            print(f"   手机号: {user.phone or '未设置'}")
            print(f"   邮箱: {user.email or '未设置'}")
            print(f"   学号: {user.student_id or '未设置'}")
            print(f"   角色: {user.role}")
            print(f"   是否激活: {user.is_active}")
            print(f"   是否有密码: {'是' if user.password_hash else '否'}")
            return user
        else:
            print("❌ 未找到用户'刘紫湲'")
            print("\n尝试查找所有包含'刘'或'紫'或'湲'的用户...")
            
            # 模糊搜索
            users = db.query(User).filter(
                (User.username.like("%刘%")) |
                (User.username.like("%紫%")) |
                (User.username.like("%湲%")) |
                (User.nickname.like("%刘%")) |
                (User.nickname.like("%紫%")) |
                (User.nickname.like("%湲%"))
            ).all()
            
            if users:
                print(f"找到 {len(users)} 个相似用户:")
                for u in users:
                    print(f"   - ID: {u.id}, 用户名: {u.username}, 昵称: {u.nickname}")
            else:
                print("   未找到相似用户")
            
            return None
    except Exception as e:
        print(f"❌ 查询用户失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def list_all_users():
    """列出所有用户（用于调试）"""
    print("\n" + "=" * 60)
    print("列出所有用户（前10个）...")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        users = db.query(User).limit(10).all()
        print(f"总用户数（前10个）: {len(users)}")
        for user in users:
            print(f"   - ID: {user.id}, 用户名: {user.username}, 昵称: {user.nickname}, 角色: {user.role}")
    except Exception as e:
        print(f"❌ 查询用户列表失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_table_structure():
    """检查users表结构"""
    print("\n" + "=" * 60)
    print("检查users表结构...")
    print("=" * 60)
    
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        if "users" not in inspector.get_table_names():
            print("❌ users表不存在")
            return
        
        columns = inspector.get_columns("users")
        print(f"✅ users表存在，包含 {len(columns)} 个字段:")
        for col in columns:
            print(f"   - {col['name']}: {col['type']}")
    except Exception as e:
        print(f"❌ 检查表结构失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("云端数据库诊断工具")
    print("=" * 60)
    print(f"\n当前环境: {'云端' if 'render.com' in DATABASE_URL or 'neon.tech' in DATABASE_URL or 'railway.app' in DATABASE_URL else '本地'}")
    print()
    
    # 1. 检查数据库连接
    if not check_database_connection():
        print("\n❌ 数据库连接失败，无法继续诊断")
        return
    
    # 2. 检查表结构
    check_table_structure()
    
    # 3. 检查用户'刘紫湲'
    user = check_user_liuziyuan()
    
    # 4. 列出所有用户
    list_all_users()
    
    # 5. 总结
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)
    if user:
        print("✅ 用户'刘紫湲'存在，可以正常登录")
    else:
        print("❌ 用户'刘紫湲'不存在，需要创建或同步")
        print("\n建议:")
        print("1. 如果这是云端数据库，需要将本地用户数据同步到云端")
        print("2. 或者使用 create_user_liuziyuan.py 脚本创建用户")
        print("3. 或者检查数据库连接配置是否正确")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()



