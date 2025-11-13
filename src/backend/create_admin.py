"""
创建管理员账户
管理员：一只炸虾
密码：zhaxia
"""

from database import SessionLocal
from models import User, UserRole
from auth import get_password_hash

def create_admin():
    """创建管理员账户"""
    db = SessionLocal()
    try:
        username = "一只炸虾"
        password = "zhaxia"
        
        # 检查是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            # 更新密码和角色
            existing_user.password_hash = get_password_hash(password)
            existing_user.role = UserRole.ADMIN
            existing_user.is_active = True
            db.commit()
            print(f"[OK] 更新管理员账户：{username} (密码: {password})")
            return
        
        # 创建新管理员
        admin_user = User(
            username=username,
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN,
            is_active=True,
            nickname="系统管理员"
        )
        
        db.add(admin_user)
        db.commit()
        
        print(f"[OK] 创建管理员账户：{username} (密码: {password})")
        print(f"\n管理员登录信息：")
        print(f"  登录类型：管理员登录")
        print(f"  账号：{username}")
        print(f"  密码：{password}")
        
    except Exception as e:
        db.rollback()
        print(f"错误：{str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("创建管理员账户...")
    create_admin()

