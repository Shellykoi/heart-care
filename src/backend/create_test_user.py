"""
创建测试用户账户
手机号：13343538563
密码：123456yzzx
"""

from database import SessionLocal
from models import User, UserRole
from auth import get_password_hash

def create_test_user():
    """创建测试用户"""
    db = SessionLocal()
    try:
        phone = "13343538563"
        password = "123456yzzx"
        
        # 检查是否已存在
        existing_user = db.query(User).filter(User.phone == phone).first()
        if existing_user:
            # 更新密码
            existing_user.password_hash = get_password_hash(password)
            db.commit()
            print(f"✓ 更新用户密码：{phone} (密码: {password})")
            return
        
        # 创建新用户
        new_user = User(
            username=f"user_{phone}",
            phone=phone,
            password_hash=get_password_hash(password),
            role=UserRole.USER,
            is_active=True,
            nickname="测试用户"
        )
        
        db.add(new_user)
        db.commit()
        
        print(f"✓ 创建测试用户：{phone} (密码: {password})")
        
    except Exception as e:
        db.rollback()
        print(f"错误：{str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("创建测试用户...")
    create_test_user()

