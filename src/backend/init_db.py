"""
数据库初始化脚本
清空所有测试数据，保留表结构
"""
from sqlalchemy import text
from database import engine, SessionLocal
from models import (
    User, Counselor, CounselorSchedule, Appointment, 
    TestReport, TestScale, Content, CommunityPost, 
    Comment, UserFavorite, ContentLike, PrivateMessage,
    EmergencyHelp, UserBlock, CounselorRating, SystemLog
)

def clear_all_data():
    """清空所有表的数据，保留表结构"""
    db = SessionLocal()
    try:
        # 按依赖关系顺序删除数据
        # 先删除有外键约束的表
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        db.execute(text("TRUNCATE TABLE counselor_ratings"))
        db.execute(text("TRUNCATE TABLE user_blocks"))
        db.execute(text("TRUNCATE TABLE emergency_helps"))
        db.execute(text("TRUNCATE TABLE private_messages"))
        db.execute(text("TRUNCATE TABLE content_likes"))
        db.execute(text("TRUNCATE TABLE user_favorites"))
        db.execute(text("TRUNCATE TABLE comments"))
        db.execute(text("TRUNCATE TABLE community_posts"))
        db.execute(text("TRUNCATE TABLE contents"))
        db.execute(text("TRUNCATE TABLE test_reports"))
        db.execute(text("TRUNCATE TABLE test_scales"))
        db.execute(text("TRUNCATE TABLE appointments"))
        db.execute(text("TRUNCATE TABLE counselor_schedules"))
        db.execute(text("TRUNCATE TABLE counselors"))
        db.execute(text("TRUNCATE TABLE system_logs"))
        db.execute(text("TRUNCATE TABLE users"))
        
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        
        db.commit()
        print("✅ 所有数据已清空，表结构已保留")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 清空数据失败: {e}")
        raise
    finally:
        db.close()


def init_default_data():
    """初始化默认数据（可选）"""
    from auth import get_password_hash
    from models import UserRole
    
    db = SessionLocal()
    try:
        # 创建默认管理员账户
        admin_user = db.query(User).filter(User.username == "一只炸虾").first()
        if not admin_user:
            admin_user = User(
                username="一只炸虾",
                password_hash=get_password_hash("zhaxia"),
                role=UserRole.ADMIN,
                is_active=True,
                nickname="系统管理员"
            )
            db.add(admin_user)
            print("✅ 管理员账户已创建：一只炸虾 / zhaxia")
        else:
            print("ℹ️  管理员账户已存在")
        
        db.commit()
        print("✅ 默认数据初始化完成")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化默认数据失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    print("=" * 50)
    print("数据库初始化脚本")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--init-defaults":
        # 清空数据并初始化默认数据
        clear_all_data()
        init_default_data()
    else:
        # 仅清空数据
        response = input("⚠️  警告：这将清空所有表的数据！\n是否继续？(yes/no): ")
        if response.lower() == 'yes':
            clear_all_data()
        else:
            print("❌ 操作已取消")
