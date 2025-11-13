"""
数据库迁移脚本：检查并添加 counselors 表缺失的字段
"""
from sqlalchemy import text, inspect
from database import engine, SessionLocal

def check_and_add_missing_fields():
    """检查并添加缺失的字段"""
    db = SessionLocal()
    try:
        # 获取当前数据库中的字段
        inspector = inspect(engine)
        existing_columns = {col['name'] for col in inspector.get_columns('counselors')}
        
        # 模型定义中应该存在的字段（根据 models.py）
        required_fields = {
            'avatar': {
                'type': 'VARCHAR(500)',
                'nullable': True,
                'comment': '头像URL（存储在MinIO）',
                'after': 'max_daily_appointments'
            }
        }
        
        # 检查并添加缺失的字段
        added_fields = []
        for field_name, field_config in required_fields.items():
            if field_name not in existing_columns:
                print(f"正在添加缺失字段: {field_name}...")
                db.execute(text(f"""
                    ALTER TABLE counselors 
                    ADD COLUMN {field_name} {field_config['type']} 
                    {'NULL' if field_config['nullable'] else 'NOT NULL'}
                    COMMENT '{field_config['comment']}'
                    AFTER {field_config['after']}
                """))
                db.commit()
                print(f"[OK] {field_name} 字段添加成功")
                added_fields.append(field_name)
            else:
                print(f"[OK] {field_name} 字段已存在")
        
        if not added_fields:
            print("[OK] 所有字段都已存在，无需添加")
        else:
            print(f"[OK] 成功添加 {len(added_fields)} 个字段: {', '.join(added_fields)}")
        
        return added_fields
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] 添加字段失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    check_and_add_missing_fields()








