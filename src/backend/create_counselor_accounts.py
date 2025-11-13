"""
为现有心理咨询师创建账户密码
密码规则：统一为 123456（建议首次登录后立即修改）
"""

from database import SessionLocal
from models import Counselor, User, UserRole, Gender, CounselorStatus
from auth import get_password_hash

def create_counselor_accounts():
    """为所有没有账户的咨询师创建账户"""
    db = SessionLocal()
    try:
        # 获取所有活跃的咨询师
        counselors = db.query(Counselor).filter(
            Counselor.status == CounselorStatus.ACTIVE
        ).all()
        
        created_count = 0
        skipped_count = 0
        
        for counselor in counselors:
            # 检查是否已经有用户账户
            if counselor.user_id:
                user = db.query(User).filter(User.id == counselor.user_id).first()
                if user:
                    skipped_count += 1
                    print(f"跳过：{counselor.real_name} 已有账户 (用户名: {user.username})")
                    continue
            
            # 生成用户名（使用姓名）
            username = counselor.real_name
            
            # 检查用户名是否已存在
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                # 如果用户名已存在，添加后缀
                username = f"{counselor.real_name}_{counselor.id}"
            
            # 生成密码：统一为 123456
            password = "123456"
            
            # 创建用户账户
            new_user = User(
                username=username,
                password_hash=get_password_hash(password),
                role=UserRole.COUNSELOR,
                is_active=True,
                nickname=counselor.real_name,
                phone=None,
                email=None
            )
            
            db.add(new_user)
            db.flush()  # 获取 user.id
            
            # 更新咨询师的 user_id
            counselor.user_id = new_user.id
            
            db.commit()
            
            created_count += 1
            print(f"✓ 创建账户：{counselor.real_name} (用户名: {username}, 密码: {password})")
        
        print(f"\n完成！创建了 {created_count} 个账户，跳过了 {skipped_count} 个已有账户的咨询师")
        
    except Exception as e:
        db.rollback()
        print(f"错误：{str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("开始为心理咨询师创建账户...")
    create_counselor_accounts()

