"""
数据库迁移脚本：为 users 表添加 avatar 字段
"""
from sqlalchemy import inspect, text

from database import engine, SessionLocal


def ensure_user_avatar_column() -> bool:
    """
    检查 users 表是否存在 avatar 字段，若不存在则添加。
    返回值表示是否执行了新增操作。
    """
    db = SessionLocal()
    try:
        inspector = inspect(engine)
        existing_columns = {col["name"] for col in inspector.get_columns("users")}

        if "avatar" in existing_columns:
            print("[OK] users.avatar 字段已存在")
            return False

        print("[INFO] 正在添加 users.avatar 字段...")
        db.execute(
            text(
                """
                ALTER TABLE users
                ADD COLUMN avatar VARCHAR(500) NULL
                COMMENT '头像URL（存储在对象存储或静态目录）'
                AFTER nickname
                """
            )
        )
        db.commit()
        print("[OK] users.avatar 字段添加成功")
        return True
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        print(f"[ERROR] 添加 users.avatar 字段失败: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    ensure_user_avatar_column()







