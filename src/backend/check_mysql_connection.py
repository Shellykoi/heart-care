"""
MySQL 连接检查脚本
用于诊断 MySQL 连接问题
"""

import sys
import pymysql

# 数据库配置（从 database.py 复制）
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "shellykoi",
    "password": "123456koiii",
    "database": "heart_care",
    "charset": "utf8mb4"
}

def check_mysql_connection():
    """检查 MySQL 连接"""
    print("=" * 50)
    print("MySQL 连接诊断工具")
    print("=" * 50)
    
    # 1. 检查 pymysql 是否安装
    print("\n1. 检查 pymysql 模块...")
    try:
        import pymysql
        print("   [OK] pymysql 已安装")
    except ImportError:
        print("   [ERROR] pymysql 未安装")
        print("   请运行: pip install pymysql")
        return False
    
    # 2. 尝试连接 MySQL
    print("\n2. 尝试连接 MySQL 服务器...")
    try:
        # 先尝试不指定数据库连接（检查服务是否运行）
        connection = pymysql.connect(
            host=DATABASE_CONFIG["host"],
            port=DATABASE_CONFIG["port"],
            user=DATABASE_CONFIG["user"],
            password=DATABASE_CONFIG["password"],
            charset=DATABASE_CONFIG["charset"],
            connect_timeout=5
        )
        print(f"   [OK] 成功连接到 MySQL 服务器 (localhost:{DATABASE_CONFIG['port']})")
        connection.close()
    except pymysql.err.OperationalError as e:
        error_code = e.args[0]
        if error_code == 2003:
            print(f"   [ERROR] 无法连接到 MySQL 服务器")
            print(f"   错误代码: {error_code}")
            print(f"   错误信息: {e}")
            print("\n   可能的原因:")
            print("   1. MySQL 服务未启动")
            print("   2. MySQL 未监听在 localhost:3306")
            print("   3. 防火墙阻止了连接")
            print("\n   解决方法:")
            print("   - Windows: 打开服务管理器，启动 MySQL 服务")
            print("   - 或使用命令行: net start mysql (需要管理员权限)")
            print("   - 或使用: sc start mysql57")
            print("   - 如果使用 phpStudy，请从 phpStudy 控制面板启动 MySQL")
            return False
        elif error_code == 1045:
            print(f"   [ERROR] 认证失败（用户名或密码错误）")
            print(f"   请检查 database.py 中的用户名和密码配置")
            return False
        else:
            print(f"   [ERROR] 连接失败: {e}")
            return False
    except Exception as e:
        print(f"   [ERROR] 未知错误: {e}")
        return False
    
    # 3. 检查数据库是否存在
    print("\n3. 检查数据库是否存在...")
    try:
        connection = pymysql.connect(
            host=DATABASE_CONFIG["host"],
            port=DATABASE_CONFIG["port"],
            user=DATABASE_CONFIG["user"],
            password=DATABASE_CONFIG["password"],
            charset=DATABASE_CONFIG["charset"],
            connect_timeout=5
        )
        cursor = connection.cursor()
        
        # 检查数据库是否存在
        cursor.execute("SHOW DATABASES LIKE %s", (DATABASE_CONFIG["database"],))
        result = cursor.fetchone()
        
        if result:
            print(f"   [OK] 数据库 '{DATABASE_CONFIG['database']}' 存在")
        else:
            print(f"   [WARNING] 数据库 '{DATABASE_CONFIG['database']}' 不存在")
            print(f"   请运行初始化脚本创建数据库")
        
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"   [ERROR] 检查数据库时出错: {e}")
        return False
    
    # 4. 尝试连接数据库
    print("\n4. 尝试连接数据库...")
    try:
        connection = pymysql.connect(**DATABASE_CONFIG, connect_timeout=5)
        print(f"   [OK] 成功连接到数据库 '{DATABASE_CONFIG['database']}'")
        
        # 测试查询
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"   [OK] MySQL 版本: {version}")
        
        cursor.close()
        connection.close()
        print("\n" + "=" * 50)
        print("[SUCCESS] 所有检查通过！MySQL 连接正常")
        print("=" * 50)
        return True
    except Exception as e:
        print(f"   [ERROR] 连接数据库失败: {e}")
        print("\n" + "=" * 50)
        print("[FAILED] 连接失败")
        print("=" * 50)
        return False

if __name__ == "__main__":
    success = check_mysql_connection()
    sys.exit(0 if success else 1)

