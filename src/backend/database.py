"""
数据库配置和连接管理
使用 SQLAlchemy ORM 连接远程 MySQL/PostgreSQL
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger("heart_care.database")


def _default_sqlite_url() -> str:
    """在缺少 DATABASE_URL 时提供本地 SQLite 作为开发环境回退。"""
    sqlite_path = Path(__file__).resolve().parent / "heartcare_dev.db"
    return f"sqlite:///{sqlite_path.as_posix()}"


# 数据库连接配置从环境变量读取，避免在代码库中硬编码凭据
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    fallback_sqlite_url = os.getenv("HEART_CARE_SQLITE_URL", _default_sqlite_url())
    logger.warning(
        "DATABASE_URL environment variable is not set. Falling back to local SQLite database: %s",
        fallback_sqlite_url,
    )
    DATABASE_URL = fallback_sqlite_url


def _build_connect_args(url: str | None) -> Dict[str, Any]:
    """根据数据库类型构造 connect_args。"""
    if not url:
        return {}

    if url.startswith(("mysql://", "mysql+pymysql://", "mysql+mysqldb://")):
        return {
            "connect_timeout": 10,
            "read_timeout": 30,
            "write_timeout": 30,
            "charset": "utf8mb4",
        }

    if url.startswith(("postgresql://", "postgresql+psycopg2://", "postgresql+asyncpg://")):
        # Neon 强制要求 SSL 连接
        return {"sslmode": "require"}

    if url.startswith("sqlite://"):
        return {"check_same_thread": False}

    return {}


connect_args = _build_connect_args(DATABASE_URL)


def _redacted_url(url: str) -> str:
    """用于日志输出，隐藏敏感信息。"""
    if "@" not in url:
        return url
    prefix, suffix = url.split("@", 1)
    return "***@" + suffix

# 输出调试信息
logger.info("Connecting to database: %s", _redacted_url(DATABASE_URL))

# 创建数据库引擎
engine_kwargs: Dict[str, Any] = {
    "echo": os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
    "connect_args": connect_args,
}

if DATABASE_URL.startswith("sqlite://"):
    # SQLite 不支持连接池参数
    engine_kwargs["connect_args"] = connect_args or {"check_same_thread": False}
else:
    engine_kwargs.update(
        {
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,
        }
    )

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖函数
    用于 FastAPI 的依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
