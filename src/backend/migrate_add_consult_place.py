"""
数据库迁移脚本：为 counselors 表添加 consult_place 字段
"""
from sqlalchemy import text, inspect
from database import engine, SessionLocal

def add_consult_place_column():
    """为 counselors 表添加 consult_place 字段"""
    db = SessionLocal()
    try:
        # 检查字段是否已存在
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('counselors')]
        
        if 'consult_place' in columns:
            print("[OK] consult_place 字段已存在，无需添加")
            return
        
        # 添加字段
        print("正在为 counselors 表添加 consult_place 字段...")
        db.execute(text("""
            ALTER TABLE counselors 
            ADD COLUMN consult_place VARCHAR(255) NULL 
            COMMENT '线下咨询地点'
            AFTER fee
        """))
        db.commit()
        print("[OK] consult_place 字段添加成功")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] 添加字段失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_consult_place_column()








