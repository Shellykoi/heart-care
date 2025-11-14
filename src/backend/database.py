"""
数据库配置和连接管理
使用 SQLAlchemy ORM 连接远程 MySQL/PostgreSQL
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv, dotenv_values
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger("heart_care.database")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILES = [
    PROJECT_ROOT / ".env.local",
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "env" / "local.env",
]

for env_file in ENV_FILES:
    if env_file.exists():
        load_dotenv(env_file, override=False)


def _ensure_database_url() -> str:
    """
    读取 DATABASE_URL。
    优先使用系统环境变量；若为空，则回退到本地 .env 文件。
    """
    env_value = os.getenv("DATABASE_URL")
    if env_value and env_value.strip():
        # 去除可能的引号（单引号或双引号）
        url = env_value.strip().strip('"').strip("'")
        return url

    for env_file in ENV_FILES:
        if not env_file.exists():
            continue

        values = dotenv_values(env_file)
        candidate = values.get("DATABASE_URL")
        if candidate and candidate.strip():
            # 去除可能的引号（单引号或双引号）
            url = candidate.strip().strip('"').strip("'")
            os.environ["DATABASE_URL"] = url
            logger.info("DATABASE_URL loaded from %s", env_file.name)
            return url

    return ""


# 数据库连接配置从环境变量读取，避免在代码库中硬编码凭据
DATABASE_URL = _ensure_database_url()
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Please configure it in your shell or a .env file before starting the backend service."
    )


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
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
}

if connect_args:
    engine_kwargs["connect_args"] = connect_args

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs,
)


def _ensure_users_table_columns() -> None:
    """
    启动时检查 users 表是否缺少关键字段，若缺失则自动补齐。
    目前主要用于处理旧版本数据库缺少 avatar 等字段导致的运行错误。
    """
    try:
        inspector = inspect(engine)
    except Exception as exc:  # pragma: no cover - 仅在启动日志中提示
        logger.warning("无法检查数据库 schema：%s", exc)
        return

    if "users" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("users")}

    migrations: list[tuple[str, str]] = []

    if "nickname" not in existing_columns:
        migrations.append(
            (
                "nickname",
                "ALTER TABLE users ADD COLUMN nickname VARCHAR(50) NULL",
            )
        )

    if "avatar" not in existing_columns:
        migrations.append(
            (
                "avatar",
                "ALTER TABLE users ADD COLUMN avatar VARCHAR(500) NULL",
            )
        )

    if "is_anonymous" not in existing_columns:
        migrations.append(
            (
                "is_anonymous",
                "ALTER TABLE users ADD COLUMN is_anonymous TINYINT(1) NOT NULL DEFAULT 0",
            )
        )

    if "show_test_results" not in existing_columns:
        migrations.append(
            (
                "show_test_results",
                "ALTER TABLE users ADD COLUMN show_test_results TINYINT(1) NOT NULL DEFAULT 0",
            )
        )

    if "record_retention" not in existing_columns:
        migrations.append(
            (
                "record_retention",
                "ALTER TABLE users ADD COLUMN record_retention VARCHAR(20) NULL DEFAULT '3months'",
            )
        )

    if not migrations:
        return

    with engine.begin() as connection:
        for column_name, statement in migrations:
            try:
                connection.execute(text(statement))
                logger.info("已补充缺失的字段 users.%s", column_name)
            except Exception as exc:  # pragma: no cover
                logger.error("补充字段 users.%s 失败：%s", column_name, exc)


_ensure_users_table_columns()

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
