"""
本地数据库连接测试脚本。

在运行前，请确保已经在环境变量或 .env 中配置 DATABASE_URL，
并在需要的情况下安装 pymysql、psycopg2 等对应数据库驱动。
"""

from sqlalchemy import text

from database import engine


def main() -> None:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT VERSION();"))
        print(result.fetchone())


if __name__ == "__main__":
    main()

