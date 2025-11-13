"""
数据库配置和连接管理
使用 SQLAlchemy ORM 连接远程 MySQL/PostgreSQL
"""

import os
from typing import Dict, Any

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接配置从环境变量读取，避免在代码库中硬编码凭据
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Configure it in your local .env and Render service settings."
    )


def _build_connect_args(url: str) -> Dict[str, Any]:
    """根据数据库类型构造 connect_args。"""
    if url.startswith(("mysql://", "mysql+pymysql://", "mysql+mysqldb://")):
        return {
            "connect_timeout": 10,
            "read_timeout": 30,
            "write_timeout": 30,
            "charset": "utf8mb4",
        }
    return {}


connect_args = _build_connect_args(DATABASE_URL)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    connect_args=connect_args,
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
