"""
数据库配置和连接管理
使用 SQLAlchemy ORM 连接 MySQL 5.7
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL 数据库连接配置
# 格式：mysql+pymysql://用户名:密码@主机:端口/数据库名
DATABASE_URL = "mysql+pymysql://shellykoi:123456koiii@localhost:3306/heart_care"

# 创建数据库引擎
# 注意：pymysql 的连接超时参数需要在 URL 中设置或使用 connect_args
engine = create_engine(
    DATABASE_URL,
    echo=True,  # 开发模式下打印 SQL 语句
    pool_pre_ping=True,  # 连接池预检查，确保连接有效
    pool_recycle=3600,  # 连接回收时间（秒）
    pool_size=5,  # 连接池大小（减少并发连接数）
    max_overflow=10,  # 最大溢出连接数
    pool_timeout=30,  # 从连接池获取连接的超时时间（秒）
    connect_args={
        "connect_timeout": 10,  # 连接超时（秒）
        "read_timeout": 30,  # 读取超时（秒）
        "write_timeout": 30,  # 写入超时（秒）
        "charset": "utf8mb4",  # 字符集
    }
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
