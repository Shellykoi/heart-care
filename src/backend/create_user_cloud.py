"""
在云端数据库创建用户'刘紫湲'
此脚本会直接连接到云端数据库（通过环境变量 DATABASE_URL）并创建用户
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "backend"))

from database import SessionLocal, DATABASE_URL
from models import User, UserRole
from auth import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_user_liuziyuan_cloud():
    """在云端数据库创建用户'刘紫湲'"""
    print("=" * 60)
    print("在云端数据库创建用户'刘紫湲'")
    print("=" * 60)
    
    # 检查是否是云端环境
    is_cloud = any(x in DATABASE_URL.lower() for x in ['render.com', 'neon.tech', 'railway.app', 'heroku.com'])
    if not is_cloud:
        print("⚠️  警告: 当前 DATABASE_URL 看起来不是云端数据库")
        print(f"   数据库URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
        confirm = input("\n是否继续? (y/n): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return False
    
    db = SessionLocal()
    try:
        username = "刘紫湲"
        password = "123456"  # 默认密码，建议首次登录后修改
        
        # 检查用户是否已存在
        existing_user = db.query(User).filter(
            (User.username == username) | (User.nickname == username)
        ).first()
        
        if existing_user:
            print(f"\n⚠️  用户'{username}'已存在")
            print(f"   用户ID: {existing_user.id}")
            print(f"   用户名: {existing_user.username}")
            print(f"   昵称: {existing_user.nickname}")
            print(f"   角色: {existing_user.role}")
            print(f"   是否激活: {existing_user.is_active}")
            
            # 询问是否更新密码
            update = input("\n是否更新密码? (y/n): ").strip().lower()
            if update == 'y':
                existing_user.password_hash = get_password_hash(password)
                existing_user.is_active = True
                db.commit()
                print(f"✅ 密码已更新: {password}")
            else:
                print("跳过更新")
            
            return True
        else:
            # 创建新用户
            print(f"\n创建新用户...")
            new_user = User(
                username=username,
                password_hash=get_password_hash(password),
                role=UserRole.USER,  # 默认为学生角色
                is_active=True,
                nickname=username
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f"✅ 用户已创建")
            print(f"   用户ID: {new_user.id}")
            print(f"   用户名: {new_user.username}")
            print(f"   昵称: {new_user.nickname}")
            print(f"   角色: {new_user.role}")
            print(f"\n登录信息:")
            print(f"   账号: {username}")
            print(f"   密码: {password}")
            print(f"   登录类型: 学生登录")
            
            return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ 创建用户失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("云端用户创建工具")
    print("=" * 60)
    print("\n此工具将:")
    print("1. 连接到云端数据库（通过 DATABASE_URL 环境变量）")
    print("2. 创建或更新用户'刘紫湲'")
    print("\n⚠️  注意:")
    print("- 确保已设置正确的 DATABASE_URL 环境变量")
    print("- 此操作会修改云端数据库")
    print("- 本地配置不会受到影响（使用环境变量时）")
    print("=" * 60)
    
    # 显示当前数据库URL（隐藏敏感信息）
    if "@" in DATABASE_URL:
        prefix, suffix = DATABASE_URL.split("@", 1)
        redacted_url = "***@" + suffix
    else:
        redacted_url = DATABASE_URL
    
    # 检查是否是本地数据库
    is_local = any(x in DATABASE_URL.lower() for x in ['localhost', '127.0.0.1', 'local'])
    
    print(f"\n当前数据库URL: {redacted_url}")
    if is_local:
        print("⚠️  警告: 检测到本地数据库URL")
        print("   如果要在云端创建用户，请先设置云端数据库URL:")
        print("   Windows: $env:DATABASE_URL='云端数据库URL'")
        print("   Linux/Mac: export DATABASE_URL='云端数据库URL'")
        print("\n   或者直接在 Render Dashboard 的 Shell 中运行此脚本")
    
    confirm = input("\n是否继续? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    success = create_user_liuziyuan_cloud()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 完成！")
        print("=" * 60)
        print("\n现在可以:")
        print("1. 在云端尝试登录用户'刘紫湲'")
        print("2. 使用 diagnose_cloud_db.py 验证用户是否存在")
    else:
        print("\n" + "=" * 60)
        print("❌ 失败")
        print("=" * 60)
        print("\n请检查:")
        print("1. DATABASE_URL 环境变量是否正确")
        print("2. 数据库连接是否正常")
        print("3. 数据库权限是否足够")

if __name__ == "__main__":
    main()

