"""
数据库迁移脚本：为 appointments 表添加咨询结束确认字段
"""
from sqlalchemy import text, inspect
from database import engine, SessionLocal

def add_appointment_confirmation_fields():
    """为 appointments 表添加咨询结束确认字段"""
    db = SessionLocal()
    try:
        # 检查字段是否已存在
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('appointments')]
        
        fields_to_add = []
        
        if 'user_confirmed_complete' not in columns:
            fields_to_add.append(('user_confirmed_complete', '用户确认咨询结束'))
        else:
            print("[OK] user_confirmed_complete 字段已存在")
        
        if 'counselor_confirmed_complete' not in columns:
            fields_to_add.append(('counselor_confirmed_complete', '咨询师确认咨询结束'))
        else:
            print("[OK] counselor_confirmed_complete 字段已存在")
        
        if not fields_to_add:
            print("[OK] 所有字段已存在，无需添加")
            return
        
        # 添加字段
        for field_name, comment in fields_to_add:
            print(f"正在为 appointments 表添加 {field_name} 字段...")
            db.execute(text(f"""
                ALTER TABLE appointments 
                ADD COLUMN {field_name} BOOLEAN DEFAULT FALSE 
                COMMENT '{comment}'
            """))
            db.commit()
            print(f"[OK] {field_name} 字段添加成功")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] 添加字段失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_appointment_confirmation_fields()








