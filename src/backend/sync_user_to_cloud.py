"""
将本地用户'刘紫湲'同步到云端数据库
注意：此脚本会读取本地数据库，然后将用户数据同步到云端数据库
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "backend"))

# 保存原始环境变量
original_database_url = os.environ.get("DATABASE_URL", "")

def get_local_database_url():
    """获取本地数据库URL"""
    from dotenv import load_dotenv
    
    # 加载本地环境变量
    local_env_files = [
        PROJECT_ROOT / ".env.local",
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "env" / "local.env",
    ]
    
    for env_file in local_env_files:
        if env_file.exists():
            load_dotenv(env_file, override=False)
            db_url = os.getenv("DATABASE_URL")
            if db_url:
                return db_url
    
    return None

def get_cloud_database_url():
    """获取云端数据库URL（从环境变量或用户输入）"""
    # 首先尝试从环境变量获取
    cloud_url = os.environ.get("CLOUD_DATABASE_URL")
    if cloud_url:
        # 去除可能的引号
        cloud_url = cloud_url.strip('"').strip("'")
        return cloud_url
    
    # 如果没有，提示用户输入
    print("\n" + "=" * 60)
    print("需要云端数据库URL")
    print("=" * 60)
    print("请提供云端数据库连接字符串（Render/Neon等）")
    print("格式示例:")
    print("  - PostgreSQL: postgresql://user:password@host:port/database")
    print("  - MySQL: mysql+pymysql://user:password@host:port/database")
    print("\n或者设置环境变量 CLOUD_DATABASE_URL")
    print("=" * 60)
    
    cloud_url = input("\n请输入云端数据库URL（或按Enter跳过）: ").strip()
    if not cloud_url:
        return None
    
    # 去除可能的引号（单引号或双引号）
    cloud_url = cloud_url.strip('"').strip("'")
    
    return cloud_url

def sync_user_to_cloud():
    """同步用户到云端"""
    print("\n" + "=" * 60)
    print("用户数据同步工具")
    print("=" * 60)
    
    # 1. 获取本地数据库URL
    local_url = get_local_database_url()
    if not local_url:
        print("❌ 无法获取本地数据库URL")
        print("请确保存在 .env.local 或 env/local.env 文件")
        return False
    
    print(f"\n✅ 本地数据库URL已获取")
    
    # 2. 获取云端数据库URL
    cloud_url = get_cloud_database_url()
    if not cloud_url:
        print("❌ 未提供云端数据库URL，跳过同步")
        return False
    
    print(f"\n✅ 云端数据库URL已获取")
    
    # 3. 连接本地数据库并读取用户数据
    print("\n" + "=" * 60)
    print("步骤1: 从本地数据库读取用户'刘紫湲'...")
    print("=" * 60)
    
    try:
        # 临时设置本地数据库URL
        os.environ["DATABASE_URL"] = local_url
        
        # 重新导入以使用新的数据库URL
        import importlib
        import database
        importlib.reload(database)
        
        from database import SessionLocal as LocalSession
        from models import User
        
        local_db = LocalSession()
        try:
            user = local_db.query(User).filter(
                (User.username == "刘紫湲") |
                (User.nickname == "刘紫湲")
            ).first()
            
            if not user:
                print("❌ 本地数据库中未找到用户'刘紫湲'")
                return False
            
            print(f"✅ 找到用户:")
            print(f"   ID: {user.id}")
            print(f"   用户名: {user.username}")
            print(f"   昵称: {user.nickname}")
            print(f"   手机号: {user.phone or '未设置'}")
            print(f"   邮箱: {user.email or '未设置'}")
            print(f"   角色: {user.role}")
            print(f"   是否激活: {user.is_active}")
            
            # 保存用户数据
            user_data = {
                "username": user.username,
                "nickname": user.nickname,
                "phone": user.phone,
                "email": user.email,
                "student_id": user.student_id,
                "password_hash": user.password_hash,
                "role": user.role,
                "is_active": user.is_active,
                "gender": user.gender,
                "age": user.age,
                "school": user.school,
            }
        finally:
            local_db.close()
    except Exception as e:
        print(f"❌ 读取本地用户数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始环境变量
        if original_database_url:
            os.environ["DATABASE_URL"] = original_database_url
        else:
            os.environ.pop("DATABASE_URL", None)
    
    # 4. 连接云端数据库并创建/更新用户
    print("\n" + "=" * 60)
    print("步骤2: 同步用户到云端数据库...")
    print("=" * 60)
    
    try:
        # 设置云端数据库URL
        os.environ["DATABASE_URL"] = cloud_url
        
        # 重新导入以使用云端数据库URL
        import importlib
        import database
        importlib.reload(database)
        
        from database import SessionLocal as CloudSession
        from models import User
        
        cloud_db = CloudSession()
        try:
            # 检查用户是否已存在
            existing_user = cloud_db.query(User).filter(
                (User.username == user_data["username"]) |
                (User.nickname == user_data["nickname"])
            ).first()
            
            if existing_user:
                print(f"⚠️  用户已存在，更新用户数据...")
                # 更新用户数据
                for key, value in user_data.items():
                    if key != "username":  # 不更新用户名
                        setattr(existing_user, key, value)
                cloud_db.commit()
                print(f"✅ 用户数据已更新")
            else:
                print(f"创建新用户...")
                # 创建新用户
                new_user = User(**user_data)
                cloud_db.add(new_user)
                cloud_db.commit()
                cloud_db.refresh(new_user)
                print(f"✅ 用户已创建，ID: {new_user.id}")
            
            # 验证
            verify_user = cloud_db.query(User).filter(
                (User.username == user_data["username"]) |
                (User.nickname == user_data["nickname"])
            ).first()
            
            if verify_user:
                print(f"\n✅ 同步成功！")
                print(f"   用户ID: {verify_user.id}")
                print(f"   用户名: {verify_user.username}")
                print(f"   昵称: {verify_user.nickname}")
                return True
            else:
                print(f"❌ 同步后验证失败")
                return False
        finally:
            cloud_db.close()
    except Exception as e:
        print(f"❌ 同步到云端失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始环境变量
        if original_database_url:
            os.environ["DATABASE_URL"] = original_database_url
        else:
            os.environ.pop("DATABASE_URL", None)

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("用户数据同步工具")
    print("=" * 60)
    print("\n此工具将:")
    print("1. 从本地数据库读取用户'刘紫湲'的数据")
    print("2. 将用户数据同步到云端数据库")
    print("\n⚠️  注意: 此操作会修改云端数据库")
    print("=" * 60)
    
    confirm = input("\n是否继续? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    success = sync_user_to_cloud()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 同步完成！")
        print("=" * 60)
        print("\n现在可以:")
        print("1. 使用 diagnose_cloud_db.py 验证云端用户是否存在")
        print("2. 尝试在云端登录")
    else:
        print("\n" + "=" * 60)
        print("❌ 同步失败")
        print("=" * 60)
        print("\n请检查:")
        print("1. 本地数据库连接是否正常")
        print("2. 云端数据库URL是否正确")
        print("3. 云端数据库是否可访问")

if __name__ == "__main__":
    main()

