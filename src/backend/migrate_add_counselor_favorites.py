"""
数据库迁移脚本：添加咨询师收藏功能
- 创建 counselor_favorites 表
"""

from sqlalchemy import create_engine, text, UniqueConstraint
from database import DATABASE_URL
import sys

def migrate():
    """执行数据库迁移"""
    engine = create_engine(DATABASE_URL)
    
    print("开始数据库迁移...")
    
    with engine.begin() as conn:
        # 检查 counselor_favorites 表是否存在
        try:
            conn.execute(text("SELECT 1 FROM counselor_favorites LIMIT 1"))
            print("✓ counselor_favorites 表已存在")
        except Exception:
            print("创建 counselor_favorites 表...")
            # 创建 counselor_favorites 表
            if 'mysql' in DATABASE_URL:
                # MySQL
                conn.execute(text("""
                    CREATE TABLE counselor_favorites (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        counselor_id INT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (counselor_id) REFERENCES counselors(id),
                        UNIQUE KEY uq_user_counselor_favorite (user_id, counselor_id),
                        INDEX idx_user_id (user_id),
                        INDEX idx_counselor_id (counselor_id)
                    )
                """))
            elif 'postgresql' in DATABASE_URL:
                # PostgreSQL
                conn.execute(text("""
                    CREATE TABLE counselor_favorites (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        counselor_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (counselor_id) REFERENCES counselors(id),
                        UNIQUE(user_id, counselor_id)
                    )
                """))
            else:
                raise RuntimeError("Unsupported database type. Expected MySQL or PostgreSQL.")

            print("✓ counselor_favorites 表已创建")
    
    print("\n数据库迁移完成！")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)






