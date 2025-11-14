"""
重置用户密码脚本
用于修复因bcrypt 72字节限制导致的密码哈希问题
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "backend"))

from dotenv import load_dotenv
from database import SessionLocal
from models import User
from auth import get_password_hash

def reset_user_password(username: str, new_password: str, use_cloud: bool = False):
    """
    重置用户密码
    
    Args:
        username: 用户名
        new_password: 新密码
        use_cloud: 是否使用云端数据库（从环境变量CLOUD_DATABASE_URL读取）
    """
    # 加载环境变量
    env_files = [
        PROJECT_ROOT / ".env.local",
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "env" / "local.env",
    ]
    
    for env_file in env_files:
        if env_file.exists():
            load_dotenv(env_file, override=False)
    
    # 如果使用云端数据库，从环境变量读取
    if use_cloud:
        cloud_url = os.environ.get("CLOUD_DATABASE_URL", "").strip('"').strip("'")
        if cloud_url:
            os.environ["DATABASE_URL"] = cloud_url
            print(f"✅ 使用云端数据库")
        else:
            print("❌ 未找到 CLOUD_DATABASE_URL 环境变量")
            return False
    else:
        print(f"✅ 使用本地数据库")
    
    db = SessionLocal()
    try:
        # 查找用户
        user = db.query(User).filter(
            (User.username == username) |
            (User.nickname == username)
        ).first()
        
        if not user:
            print(f"❌ 未找到用户: {username}")
            return False
        
        # 使用修复后的密码哈希函数重新生成密码哈希
        new_password_hash = get_password_hash(new_password)
        
        # 更新密码
        user.password_hash = new_password_hash
        db.commit()
        db.refresh(user)
        
        print(f"✅ 密码已重置")
        print(f"   用户ID: {user.id}")
        print(f"   用户名: {user.username}")
        print(f"   新密码: {new_password}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ 重置密码失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("重置用户密码工具")
    print("=" * 60)
    
    # 默认重置用户"刘紫湲"的密码为"123456"
    username = input("\n请输入用户名（默认: 刘紫湲）: ").strip() or "刘紫湲"
    new_password = input("请输入新密码（默认: 123456）: ").strip() or "123456"
    
    print("\n选择数据库:")
    print("1. 本地数据库")
    print("2. 云端数据库")
    choice = input("请选择 (1/2，默认: 1): ").strip() or "1"
    
    use_cloud = (choice == "2")
    
    print("\n" + "=" * 60)
    success = reset_user_password(username, new_password, use_cloud=use_cloud)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 密码重置完成！")
        print("=" * 60)
        print(f"\n现在可以使用以下信息登录:")
        print(f"   账号: {username}")
        print(f"   密码: {new_password}")
    else:
        print("\n" + "=" * 60)
        print("❌ 密码重置失败")
        print("=" * 60)

if __name__ == "__main__":
    main()

