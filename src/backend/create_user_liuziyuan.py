"""
创建用户账户：刘紫湲
用于解决登录问题
"""

from database import SessionLocal
from models import User, UserRole
from auth import get_password_hash

def create_user_liuziyuan():
    """创建或更新用户 刘紫湲"""
    db = SessionLocal()
    try:
        username = "刘紫湲"
        password = "123456"  # 默认密码，建议首次登录后修改
        
        # 检查用户是否已存在（通过用户名或昵称）
        existing_user = db.query(User).filter(
            (User.username == username) | (User.nickname == username)
        ).first()
        
        if existing_user:
            # 更新密码
            existing_user.password_hash = get_password_hash(password)
            existing_user.is_active = True
            db.commit()
            print(f"✓ 更新用户密码：{username} (密码: {password})")
            print(f"  用户ID: {existing_user.id}")
            print(f"  用户名: {existing_user.username}")
            print(f"  昵称: {existing_user.nickname}")
            print(f"  角色: {existing_user.role}")
            return existing_user
        else:
            # 创建新用户
            new_user = User(
                username=username,
                password_hash=get_password_hash(password),
                role=UserRole.USER,  # 默认为学生角色，如果是咨询师需要改为 COUNSELOR
                is_active=True,
                nickname=username
            )
            
            db.add(new_user)
            db.commit()
            
            print(f"✓ 创建用户：{username} (密码: {password})")
            print(f"  用户ID: {new_user.id}")
            print(f"  用户名: {new_user.username}")
            print(f"  角色: {new_user.role}")
            print(f"\n登录信息：")
            print(f"  账号：{username}")
            print(f"  密码：{password}")
            print(f"  登录类型：学生登录")
            
            return new_user
        
    except Exception as e:
        db.rollback()
        print(f"❌ 错误：{str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("创建/更新用户：刘紫湲")
    print("=" * 50)
    create_user_liuziyuan()
    print("=" * 50)



