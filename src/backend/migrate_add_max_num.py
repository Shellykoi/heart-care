"""
数据库迁移脚本：为 counselor_schedules 表添加 max_num 字段
"""
from sqlalchemy import text, inspect
from database import engine, SessionLocal

def add_max_num_column():
    """为 counselor_schedules 表添加 max_num 字段"""
    db = SessionLocal()
    try:
        # 检查字段是否已存在
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('counselor_schedules')]
        
        if 'max_num' in columns:
            print("[OK] max_num 字段已存在，无需添加")
            return
        
        # 添加字段
        print("正在为 counselor_schedules 表添加 max_num 字段...")
        db.execute(text("""
            ALTER TABLE counselor_schedules 
            ADD COLUMN max_num INT NOT NULL DEFAULT 1 
            COMMENT '该时段最大预约量（默认1人/时段）'
            AFTER end_time
        """))
        db.commit()
        print("[OK] max_num 字段添加成功")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] 添加字段失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_max_num_column()








