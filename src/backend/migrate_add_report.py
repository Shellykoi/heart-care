"""
数据库迁移脚本：添加举报功能
- 添加 report_count 字段到 community_posts 表
- 创建 post_reports 表
- 更新现有数据的 is_approved 字段（将 False 改为 True，因为现在默认直接发布）
"""

from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker
from database import Base, DATABASE_URL
from models import CommunityPost, PostReport
import sys

def migrate():
    """执行数据库迁移"""
    db_url = DATABASE_URL
    engine = create_engine(db_url)
    
    print("开始数据库迁移...")
    
    with engine.begin() as conn:
        # 检查 report_count 字段是否存在
        if 'sqlite' in db_url:
            # SQLite
            result = conn.execute(text("PRAGMA table_info(community_posts)"))
            columns = [row[1] for row in result]
            if 'report_count' not in columns:
                print("添加 report_count 字段...")
                conn.execute(text("ALTER TABLE community_posts ADD COLUMN report_count INTEGER DEFAULT 0"))
                print("✓ report_count 字段已添加")
            else:
                print("✓ report_count 字段已存在")
        else:
            # PostgreSQL/MySQL
            try:
                conn.execute(text("SELECT report_count FROM community_posts LIMIT 1"))
                print("✓ report_count 字段已存在")
            except Exception:
                print("添加 report_count 字段...")
                conn.execute(text("ALTER TABLE community_posts ADD COLUMN report_count INTEGER DEFAULT 0"))
                print("✓ report_count 字段已添加")
        
        # 更新现有帖子：将 is_approved=False 改为 True（因为现在默认直接发布）
        print("更新现有帖子的审核状态...")
        result = conn.execute(text("UPDATE community_posts SET is_approved = 1 WHERE is_approved = 0"))
        print(f"✓ 已更新 {result.rowcount} 条记录")
        
        # 检查 post_reports 表是否存在
        try:
            conn.execute(text("SELECT 1 FROM post_reports LIMIT 1"))
            print("✓ post_reports 表已存在")
        except Exception:
            print("创建 post_reports 表...")
            # 创建 post_reports 表
            if 'sqlite' in db_url:
                conn.execute(text("""
                    CREATE TABLE post_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        reason VARCHAR(200),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES community_posts(id),
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        UNIQUE(post_id, user_id)
                    )
                """))
            elif 'mysql' in db_url:
                # MySQL
                conn.execute(text("""
                    CREATE TABLE post_reports (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        post_id INT NOT NULL,
                        user_id INT NOT NULL,
                        reason VARCHAR(200),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES community_posts(id),
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        UNIQUE(post_id, user_id)
                    )
                """))
            else:
                # PostgreSQL
                conn.execute(text("""
                    CREATE TABLE post_reports (
                        id SERIAL PRIMARY KEY,
                        post_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        reason VARCHAR(200),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES community_posts(id),
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        UNIQUE(post_id, user_id)
                    )
                """))
            print("✓ post_reports 表已创建")
    
    print("\n数据库迁移完成！")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

