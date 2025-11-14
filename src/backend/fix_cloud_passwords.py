"""
修复云端数据库中所有用户的密码哈希
将所有明文密码（如 '123456'）转换为正确的 bcrypt 哈希
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "backend"))

from dotenv import load_dotenv, dotenv_values
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from auth import get_password_hash, verify_password

# 加载环境变量
ENV_FILES = [
    PROJECT_ROOT / ".env.local",
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "env" / "local.env",
]

for env_file in ENV_FILES:
    if env_file.exists():
        load_dotenv(env_file, override=False)


def get_cloud_db_url() -> str:
    """获取云端PostgreSQL数据库连接URL"""
    # 优先从系统环境变量读取
    cloud_url = os.getenv("CLOUD_DATABASE_URL", "")
    if cloud_url:
        return cloud_url.strip('"').strip("'")
    
    # 从.env文件读取
    for env_file in ENV_FILES:
        if env_file.exists():
            values = dotenv_values(env_file)
            candidate = values.get("CLOUD_DATABASE_URL")
            if candidate and candidate.strip():
                return candidate.strip().strip("'").strip('"')
    
    # 如果都没有，提示用户输入
    print("\n" + "="*60)
    print("⚠️  未找到 CLOUD_DATABASE_URL 环境变量")
    print("="*60)
    print("\n请输入云端PostgreSQL数据库连接URL")
    print("格式: postgresql://user:password@host:port/database?sslmode=require")
    print("="*60)
    
    cloud_url = input("\n云端数据库URL: ").strip()
    if not cloud_url:
        raise ValueError("未提供云端数据库连接URL")
    
    cloud_url = cloud_url.strip('"').strip("'")
    os.environ["CLOUD_DATABASE_URL"] = cloud_url
    
    return cloud_url


def is_bcrypt_hash(password_hash: str) -> bool:
    """检查字符串是否是有效的 bcrypt 哈希"""
    if not password_hash:
        return False
    
    # bcrypt 哈希通常以 $2a$, $2b$, $2x$, $2y$ 开头，长度为 60 字符
    if len(password_hash) < 60:
        return False
    
    if password_hash.startswith(('$2a$', '$2b$', '$2x$', '$2y$')):
        return True
    
    return False


def fix_all_passwords(default_password: str = "123456"):
    """
    修复云端数据库中所有用户的密码哈希
    
    Args:
        default_password: 默认密码（如果检测到明文密码，使用此密码生成哈希）
    """
    cloud_url = get_cloud_db_url()
    print(f"\n✅ 连接到云端数据库...")
    
    cloud_engine = create_engine(cloud_url)
    SessionLocal = sessionmaker(bind=cloud_engine)
    
    db = SessionLocal()
    
    try:
        # 查询所有用户
        result = db.execute(text("""
            SELECT id, username, nickname, password_hash 
            FROM users 
            ORDER BY id
        """))
        
        users = result.fetchall()
        print(f"\n📊 找到 {len(users)} 个用户")
        
        fixed_count = 0
        skipped_count = 0
        
        print("\n" + "="*60)
        print("开始修复密码哈希...")
        print("="*60)
        
        for user_id, username, nickname, password_hash in users:
            display_name = nickname or username or f"用户{user_id}"
            
            # 检查是否是有效的 bcrypt 哈希
            if is_bcrypt_hash(password_hash):
                print(f"  ✓ 用户 {user_id} ({display_name}): 密码哈希已正确，跳过")
                skipped_count += 1
                continue
            
            # 不是有效的 bcrypt 哈希，需要修复
            print(f"  🔧 用户 {user_id} ({display_name}): 检测到无效密码哈希，正在修复...")
            
            # 生成新的密码哈希
            new_password_hash = get_password_hash(default_password)
            
            # 更新数据库
            db.execute(
                text("UPDATE users SET password_hash = :hash WHERE id = :user_id"),
                {"hash": new_password_hash, "user_id": user_id}
            )
            
            # 验证新哈希是否正确
            if verify_password(default_password, new_password_hash):
                print(f"    ✅ 密码已修复，新密码: {default_password}")
                fixed_count += 1
            else:
                print(f"    ❌ 密码哈希验证失败！")
        
        # 提交所有更改
        db.commit()
        
        print("\n" + "="*60)
        print("修复完成！")
        print("="*60)
        print(f"  修复用户数: {fixed_count}")
        print(f"  跳过用户数: {skipped_count}")
        print(f"  总用户数: {len(users)}")
        print(f"\n所有修复的用户默认密码为: {default_password}")
        print("="*60)
        
        return fixed_count, skipped_count
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0
    finally:
        db.close()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("修复云端数据库用户密码哈希工具")
    print("="*60)
    print("\n此工具将：")
    print("  1. 检查所有用户的密码哈希")
    print("  2. 将明文密码（如 '123456'）转换为 bcrypt 哈希")
    print("  3. 保持已正确哈希的密码不变")
    print("\n" + "="*60)
    
    default_password = input("\n请输入默认密码（用于修复明文密码，默认: 123456）: ").strip() or "123456"
    
    confirm = input(f"\n⚠️  确认要修复所有用户的密码哈希吗？(y/N): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    fixed, skipped = fix_all_passwords(default_password)
    
    if fixed > 0:
        print(f"\n✅ 成功修复 {fixed} 个用户的密码哈希！")
        print(f"现在可以使用默认密码 '{default_password}' 登录这些账户")
    else:
        print(f"\n✅ 所有用户的密码哈希都已正确，无需修复")


if __name__ == "__main__":
    main()

