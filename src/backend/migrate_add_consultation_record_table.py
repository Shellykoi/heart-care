"""
数据库迁移脚本：添加咨询记录表（consultation_records）
"""

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from database import Base
from models import ConsultationRecord
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 数据库连接配置
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/heartcare")

def create_consultation_record_table():
    """创建咨询记录表"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'consultation_records' in existing_tables:
            print("[INFO] consultation_records 表已存在，跳过创建")
            return
        
        print("[INFO] 开始创建 consultation_records 表...")
        
        # 创建表
        ConsultationRecord.__table__.create(engine, checkfirst=True)
        
        print("[OK] consultation_records 表创建成功")
        
        # 验证表结构
        columns = inspector.get_columns('consultation_records')
        print(f"[OK] 表 consultation_records 包含 {len(columns)} 个字段:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
    except Exception as e:
        print(f"[ERROR] 创建表失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("数据库迁移：添加咨询记录表")
    print("=" * 60)
    create_consultation_record_table()
    print("=" * 60)
    print("迁移完成！")
    print("=" * 60)







