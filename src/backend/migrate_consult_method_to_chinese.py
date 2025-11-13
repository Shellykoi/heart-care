"""
数据库迁移脚本：将consult_method从英文枚举值转换为中文
将 'offline' -> '线下面谈', 'video' -> '线上视频', 'voice' -> '语音咨询', 'text' -> '文字咨询'
"""

from sqlalchemy import text
from database import engine, SessionLocal
from sqlalchemy.orm import Session

def migrate_consult_method_to_chinese():
    """将appointments和consultation_records表中的consult_method从英文转换为中文"""
    db = SessionLocal()
    try:
        print("开始迁移consult_method字段...")
        
        # 1. 先将字段类型从 ENUM 修改为 VARCHAR，避免中文值被截断
        print("正在修改数据库字段类型...")
        try:
            # 修改appointments表
            db.execute(text("""
                ALTER TABLE appointments 
                MODIFY COLUMN consult_method VARCHAR(50) NOT NULL
            """))
            print("  - appointments表字段类型已更新")
            
            # 修改consultation_records表
            db.execute(text("""
                ALTER TABLE consultation_records 
                MODIFY COLUMN consult_method VARCHAR(50) NOT NULL
            """))
            print("  - consultation_records表字段类型已更新")
            
            db.commit()
            print("[OK] 数据库字段类型修改完成")
        except Exception as e:
            print(f"[WARNING] 修改字段类型时出错（可能字段类型已经是VARCHAR）: {e}")
            db.rollback()
        
        # 映射关系
        method_mapping = {
            'offline': '线下面谈',
            'video': '线上视频',
            'voice': '语音咨询',
            'text': '文字咨询',
        }
        
        # 2. 更新appointments表
        print("正在更新appointments表...")
        for eng_value, chn_value in method_mapping.items():
            result = db.execute(text("""
                UPDATE appointments 
                SET consult_method = :chn_value 
                WHERE consult_method = :eng_value
            """), {"chn_value": chn_value, "eng_value": eng_value})
            count = result.rowcount
            if count > 0:
                print(f"  - 更新了 {count} 条记录: {eng_value} -> {chn_value}")
        
        # 3. 更新consultation_records表
        print("正在更新consultation_records表...")
        for eng_value, chn_value in method_mapping.items():
            result = db.execute(text("""
                UPDATE consultation_records 
                SET consult_method = :chn_value 
                WHERE consult_method = :eng_value
            """), {"chn_value": chn_value, "eng_value": eng_value})
            count = result.rowcount
            if count > 0:
                print(f"  - 更新了 {count} 条记录: {eng_value} -> {chn_value}")
        
        db.commit()
        print("[OK] consult_method字段迁移完成")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] 迁移失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_consult_method_to_chinese()







