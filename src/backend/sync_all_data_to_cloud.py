"""
同步本地MySQL数据库的所有数据到云端PostgreSQL数据库
按照外键依赖顺序同步所有表
如果用户密码哈希为空或无效，默认设置为123456
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "backend"))

from dotenv import load_dotenv, dotenv_values
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import pymysql

# 加载环境变量
ENV_FILES = [
    PROJECT_ROOT / ".env.local",
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "env" / "local.env",
]

for env_file in ENV_FILES:
    if env_file.exists():
        load_dotenv(env_file, override=False)

# 导入密码哈希函数
from auth import get_password_hash

# 表同步顺序（按照外键依赖关系）
TABLE_SYNC_ORDER = [
    "users",                    # 1. 用户表（无依赖）
    "test_scales",              # 2. 测评量表（无依赖）
    "counselors",               # 3. 咨询师（依赖 users）
    "counselor_schedules",      # 4. 咨询师日程（依赖 counselors）
    "counselor_unavailable",    # 5. 咨询师不可预约时段（依赖 counselors）
    "contents",                 # 6. 内容（无依赖）
    "appointments",             # 7. 预约（依赖 users, counselors）
    "consultation_records",     # 8. 咨询记录（依赖 appointments, users, counselors）
    "counselor_ratings",        # 9. 咨询师评分（依赖 appointments, users, counselors）
    "test_reports",             # 10. 测评报告（依赖 users, test_scales）
    "community_posts",          # 11. 社区帖子（依赖 users）
    "comments",                 # 12. 评论（依赖 community_posts, users）
    "post_reports",             # 13. 帖子举报（依赖 community_posts, users）
    "user_favorites",           # 14. 用户收藏（依赖 users）
    "counselor_favorites",      # 15. 咨询师收藏（依赖 users, counselors）
    "content_likes",            # 16. 内容点赞（依赖 users）
    "private_messages",         # 17. 私信（依赖 users）
    "emergency_helps",          # 18. 紧急求助（依赖 users）
    "user_blocks",              # 19. 用户拉黑（依赖 users）
    "system_logs",              # 20. 系统日志（依赖 users）
]


def get_local_db_url() -> str:
    """获取本地MySQL数据库连接URL"""
    # 尝试从环境变量读取
    local_url = os.getenv("LOCAL_DATABASE_URL", "")
    if local_url:
        return local_url.strip('"').strip("'")
    
    # 从.env文件读取
    for env_file in ENV_FILES:
        if env_file.exists():
            values = dotenv_values(env_file)
            candidate = values.get("LOCAL_DATABASE_URL") or values.get("DATABASE_URL")
            if candidate and candidate.strip():
                url = candidate.strip().strip('"').strip("'")
                # 如果是MySQL连接，使用它
                if url.startswith(("mysql://", "mysql+pymysql://")):
                    return url
    
    # 默认本地MySQL连接
    return "mysql+pymysql://root:123456@localhost:3306/heart_care"


def get_cloud_db_url() -> str:
    """获取云端PostgreSQL数据库连接URL"""
    # 优先从系统环境变量读取
    cloud_url = os.getenv("CLOUD_DATABASE_URL", "")
    if cloud_url:
        return cloud_url.strip('"').strip("'")
    
    # 从.env文件读取
    for env_file in ENV_FILES:
        if env_file.exists():
            values = dotenv_values(env_file)
            candidate = values.get("CLOUD_DATABASE_URL")
            if candidate and candidate.strip():
                return candidate.strip().strip('"').strip("'")
    
    # 如果都没有，提示用户输入
    print("\n" + "="*60)
    print("⚠️  未找到 CLOUD_DATABASE_URL 环境变量")
    print("="*60)
    print("\n请输入云端PostgreSQL数据库连接URL")
    print("格式: postgresql://user:password@host:port/database?sslmode=require")
    print("或者: postgresql+psycopg2://user:password@host:port/database?sslmode=require")
    print("\n提示: 可以从Render控制台或Neon仪表盘获取连接字符串")
    print("="*60)
    
    cloud_url = input("\n云端数据库URL: ").strip()
    if not cloud_url:
        raise ValueError("未提供云端数据库连接URL")
    
    # 去除可能的引号
    cloud_url = cloud_url.strip('"').strip("'")
    
    # 保存到环境变量（仅本次会话）
    os.environ["CLOUD_DATABASE_URL"] = cloud_url
    
    return cloud_url


def convert_mysql_to_postgres_value(value: Any, column_type: str, column_name: str = None, cloud_engine=None, table_name: str = None) -> Any:
    """将MySQL值转换为PostgreSQL兼容的值"""
    if value is None:
        return None
    
    # 处理布尔值（MySQL使用TINYINT(1)，PostgreSQL使用BOOLEAN）
    if 'tinyint' in column_type.lower() or 'boolean' in column_type.lower():
        if isinstance(value, (int, bool)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ('1', 'true', 'yes', 'on')
    
    # 处理枚举值
    if isinstance(value, str):
        value_lower = value.lower().strip()
        value_upper = value.upper().strip()
        
        # 处理gender字段的枚举值
        if column_name == 'gender':
            pg_values = get_pg_enum_values(cloud_engine, 'gender') if cloud_engine else []
            # 检查PostgreSQL中的枚举值是否是大写的
            if pg_values and len(pg_values) > 0 and pg_values[0].isupper():
                # PostgreSQL使用大写，转换为大写
                if value_lower in ('male', 'm', '男', '1'):
                    return 'MALE'
                elif value_lower in ('female', 'f', '女', '2'):
                    return 'FEMALE'
                elif value_lower in ('other', 'o', '其他', '3', ''):
                    return 'OTHER'
                else:
                    return 'OTHER'
            else:
                # PostgreSQL使用小写，转换为小写
                if value_lower in ('male', 'm', '男', '1'):
                    return 'male'
                elif value_lower in ('female', 'f', '女', '2'):
                    return 'female'
                elif value_lower in ('other', 'o', '其他', '3', ''):
                    return 'other'
                else:
                    return 'other'
        
        # 处理role字段的枚举值
        if column_name == 'role':
            pg_values = get_pg_enum_values(cloud_engine, 'userrole') if cloud_engine else []
            # 检查PostgreSQL中的枚举值是否是大写的
            if pg_values and len(pg_values) > 0 and pg_values[0].isupper():
                # PostgreSQL使用大写，转换为大写
                mapping = {
                    'user': 'USER',
                    'counselor': 'COUNSELOR',
                    'volunteer': 'VOLUNTEER',
                    'admin': 'ADMIN',
                }
                return mapping.get(value_lower, 'USER')
            else:
                # PostgreSQL使用小写，转换为小写
                mapping = {
                    'user': 'user',
                    'counselor': 'counselor',
                    'volunteer': 'volunteer',
                    'admin': 'admin',
                }
                return mapping.get(value_lower, 'user')
        
        # 处理status字段的枚举值（需要根据表名判断是哪个枚举类型）
        if column_name == 'status':
            # 根据表名判断使用哪个枚举类型
            if table_name == 'appointments':
                enum_name = 'appointmentstatus'
            elif table_name == 'counselors':
                enum_name = 'counselorstatus'
            else:
                # 默认使用appointmentstatus
                enum_name = 'appointmentstatus'
            
            pg_values = get_pg_enum_values(cloud_engine, enum_name) if cloud_engine else []
            use_upper = pg_values and len(pg_values) > 0 and pg_values[0].isupper()
            
            if use_upper:
                mapping = {
                    'pending': 'PENDING',
                    'confirmed': 'CONFIRMED',
                    'completed': 'COMPLETED',
                    'cancelled': 'CANCELLED',
                    'rejected': 'REJECTED',
                    'active': 'ACTIVE',
                    'inactive': 'INACTIVE',
                }
                return mapping.get(value_lower, 'PENDING')
            else:
                mapping = {
                    'pending': 'pending',
                    'confirmed': 'confirmed',
                    'completed': 'completed',
                    'cancelled': 'cancelled',
                    'rejected': 'rejected',
                    'active': 'active',
                    'inactive': 'inactive',
                }
                return mapping.get(value_lower, 'pending')
    
    return value


# 全局变量存储PostgreSQL枚举类型的实际值
PG_ENUM_VALUES = {}

def get_pg_enum_values(cloud_engine, enum_name: str) -> List[str]:
    """获取PostgreSQL中枚举类型的实际值"""
    if enum_name in PG_ENUM_VALUES:
        return PG_ENUM_VALUES[enum_name]
    
    try:
        with cloud_engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = '{enum_name}'
                )
                ORDER BY enumsortorder
            """))
            values = [row[0] for row in result.fetchall()]
            PG_ENUM_VALUES[enum_name] = values
            return values
    except Exception:
        return []


def check_and_fix_enum_types(cloud_engine):
    """检查并修复PostgreSQL中的枚举类型，并记录实际值"""
    global PG_ENUM_VALUES
    print("\n🔍 检查PostgreSQL枚举类型...")
    
    # 使用begin()来确保事务正确提交
    with cloud_engine.begin() as conn:
        # 检查所有枚举类型并记录实际值
        enum_types_to_check = {
            'gender': ['male', 'female', 'other'],
            'userrole': ['user', 'counselor', 'volunteer', 'admin'],
            'appointmentstatus': ['pending', 'confirmed', 'completed', 'cancelled', 'rejected'],
            'counselorstatus': ['pending', 'active', 'inactive', 'rejected'],
        }
        
        for enum_name, expected_values in enum_types_to_check.items():
            try:
                result = conn.execute(text(f"""
                    SELECT enumlabel 
                    FROM pg_enum 
                    WHERE enumtypid = (
                        SELECT oid FROM pg_type WHERE typname = '{enum_name}'
                    )
                    ORDER BY enumsortorder
                """))
                existing_values = [row[0] for row in result.fetchall()]
                PG_ENUM_VALUES[enum_name] = existing_values
                
                if not existing_values:
                    print(f"  ⚠️  未找到{enum_name}枚举类型，尝试创建...")
                    values_str = "', '".join(expected_values)
                    try:
                        conn.execute(text(f"CREATE TYPE {enum_name} AS ENUM ('{values_str}')"))
                        PG_ENUM_VALUES[enum_name] = expected_values
                        print(f"  ✅ 已创建{enum_name}枚举类型")
                    except Exception as e:
                        print(f"  ⚠️  创建{enum_name}枚举类型失败: {e}")
                else:
                    print(f"  ✅ {enum_name}枚举类型已存在，值: {existing_values}")
            except Exception as e:
                error_msg = str(e).lower()
                if 'does not exist' in error_msg or 'not found' in error_msg:
                    # 如果枚举类型不存在，尝试创建
                    values_str = "', '".join(expected_values)
                    try:
                        conn.execute(text(f"CREATE TYPE {enum_name} AS ENUM ('{values_str}')"))
                        PG_ENUM_VALUES[enum_name] = expected_values
                        print(f"  ✅ 已创建{enum_name}枚举类型")
                    except Exception as create_error:
                        print(f"  ⚠️  创建{enum_name}枚举类型失败: {create_error}")
                else:
                    print(f"  ⚠️  检查{enum_name}枚举类型时出错: {e}")


def get_table_columns(engine, table_name: str) -> List[Dict[str, Any]]:
    """获取表的所有列信息"""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return columns


def sync_table(
    local_engine,
    cloud_engine,
    table_name: str,
    default_password: str = "123456"
) -> tuple[int, int]:
    """
    同步单个表的数据
    
    Returns:
        (成功数量, 失败数量)
    """
    print(f"\n{'='*60}")
    print(f"同步表: {table_name}")
    print(f"{'='*60}")
    
    # 获取列信息
    local_columns = get_table_columns(local_engine, table_name)
    cloud_columns = get_table_columns(cloud_engine, table_name)
    
    # 构建列名列表（只包含两个数据库都有的列）
    local_column_names = {col['name'] for col in local_columns}
    cloud_column_names = {col['name'] for col in cloud_columns}
    common_columns = sorted(local_column_names & cloud_column_names)
    
    if not common_columns:
        print(f"⚠️  警告: 表 {table_name} 没有共同列，跳过")
        return 0, 0
    
    # 获取主键列
    local_inspector = inspect(local_engine)
    cloud_inspector = inspect(cloud_engine)
    local_pk = local_inspector.get_pk_constraint(table_name)
    cloud_pk = cloud_inspector.get_pk_constraint(table_name)
    pk_column = local_pk.get('constrained_columns', [None])[0] if local_pk else None
    
    # 从本地数据库读取数据
    with local_engine.connect() as local_conn:
        # 构建SELECT查询
        columns_str = ", ".join([f"`{col}`" for col in common_columns])
        query = f"SELECT {columns_str} FROM `{table_name}`"
        
        try:
            result = local_conn.execute(text(query))
            rows = result.fetchall()
            print(f"📊 本地数据库找到 {len(rows)} 条记录")
        except Exception as e:
            print(f"❌ 读取本地数据失败: {e}")
            return 0, 0
    
    if not rows:
        print(f"ℹ️  表 {table_name} 没有数据，跳过")
        return 0, 0
    
    # 同步到云端数据库
    # 使用autocommit模式，每条记录单独提交，避免一条失败影响其他记录
    success_count = 0
    fail_count = 0
    inserted_ids = []  # 记录成功插入的ID（用于调试）
    
    # 创建连接（不使用事务，每条记录单独提交）
    cloud_conn = cloud_engine.connect()
    
    try:
        for idx, row in enumerate(rows):
            # 使用savepoint来隔离每条记录的插入
            savepoint_name = f"sp_{table_name}_{idx}"
            savepoint = cloud_conn.begin_nested()
            
            try:
                # 构建行数据字典
                row_dict = {}
                row_id = None  # 记录当前行的ID
                
                for i, col_name in enumerate(common_columns):
                    value = row[i]
                    
                    # 记录主键ID
                    if col_name == pk_column:
                        row_id = value
                    
                    # 特殊处理users表的password_hash
                    if table_name == "users" and col_name == "password_hash":
                        # 如果密码哈希为空或无效，使用默认密码
                        if not value or len(value) < 10:
                            value = get_password_hash(default_password)
                            if row_id:
                                print(f"  🔑 用户ID {row_id}: 密码已重置为默认密码")
                    
                    # 转换数据类型
                    col_info = next((c for c in local_columns if c['name'] == col_name), None)
                    if col_info:
                        value = convert_mysql_to_postgres_value(value, str(col_info['type']), col_name, cloud_engine, table_name)
                    
                    row_dict[col_name] = value
                
                # 构建INSERT语句（使用ON CONFLICT处理重复）
                columns_str = ", ".join([f'"{col}"' for col in common_columns])
                values_str = ", ".join([f":{col}" for col in common_columns])
                
                if pk_column and pk_column in common_columns:
                    # 有主键，使用ON CONFLICT DO UPDATE
                    update_set = ", ".join([
                        f'"{col}" = EXCLUDED."{col}"'
                        for col in common_columns
                        if col != pk_column
                    ])
                    insert_sql = f"""
                        INSERT INTO "{table_name}" ({columns_str})
                        VALUES ({values_str})
                        ON CONFLICT ("{pk_column}") DO UPDATE SET {update_set}
                    """
                else:
                    # 无主键或主键不在列中，直接INSERT
                    insert_sql = f"""
                        INSERT INTO "{table_name}" ({columns_str})
                        VALUES ({values_str})
                        ON CONFLICT DO NOTHING
                    """
                
                result = cloud_conn.execute(text(insert_sql), row_dict)
                savepoint.commit()
                success_count += 1
                
                # 记录成功插入的ID（仅对users表）
                if table_name == "users" and row_id is not None:
                    inserted_ids.append(row_id)
                
            except IntegrityError as e:
                # 外键约束错误或其他完整性错误
                savepoint.rollback()
                fail_count += 1
                if fail_count <= 5:  # 只打印前5个错误
                    error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
                    # 截断过长的错误信息
                    if len(error_msg) > 200:
                        error_msg = error_msg[:200] + "..."
                    print(f"  ⚠️  跳过重复或冲突记录: {error_msg}")
            except Exception as e:
                savepoint.rollback()
                fail_count += 1
                if fail_count <= 5:  # 只打印前5个错误
                    error_msg = str(e)
                    # 截断过长的错误信息
                    if len(error_msg) > 300:
                        error_msg = error_msg[:300] + "..."
                    print(f"  ❌ 插入失败: {error_msg}")
    finally:
        cloud_conn.close()
    
    print(f"✅ 成功: {success_count} 条")
    if fail_count > 0:
        print(f"⚠️  失败/跳过: {fail_count} 条")
    
    # 对于users表，显示实际插入的ID列表
    if table_name == "users" and inserted_ids:
        print(f"  📋 已插入的用户ID: {sorted(inserted_ids)}")
    
    return success_count, fail_count


def verify_users_before_sync_counselors(local_engine, cloud_engine):
    """在同步counselors表之前，验证云端users表中是否有足够的用户"""
    print("\n" + "="*60)
    print("🔍 验证用户数据（同步counselors前检查）")
    print("="*60)
    
    try:
        # 获取本地counselors表中需要的user_id
        with local_engine.connect() as local_conn:
            result = local_conn.execute(text("SELECT DISTINCT user_id FROM `counselors` WHERE user_id IS NOT NULL"))
            required_user_ids = {row[0] for row in result.fetchall()}
            print(f"📋 本地counselors表需要的user_id: {sorted(required_user_ids)}")
        
        # 获取云端users表中实际存在的id
        with cloud_engine.connect() as cloud_conn:
            result = cloud_conn.execute(text('SELECT id FROM "users"'))
            existing_user_ids = {row[0] for row in result.fetchall()}
            print(f"📋 云端users表实际存在的id: {sorted(existing_user_ids)}")
        
        # 检查缺失的user_id
        missing_ids = required_user_ids - existing_user_ids
        if missing_ids:
            print(f"\n⚠️  警告: 以下user_id在云端users表中不存在: {sorted(missing_ids)}")
            print("   这可能导致counselors表同步失败")
            return False
        else:
            print("\n✅ 所有需要的user_id在云端users表中都存在")
            return True
            
    except Exception as e:
        print(f"⚠️  验证过程出错: {e}")
        return True  # 验证失败时继续同步，让同步过程自己处理错误


def clear_cloud_database(cloud_engine):
    """清空云端数据库的所有数据（保留表结构）"""
    print("\n" + "="*60)
    print("🗑️  清空云端数据库数据...")
    print("="*60)
    
    # 按照依赖关系的逆序删除数据（先删除有外键的表）
    reverse_order = list(reversed(TABLE_SYNC_ORDER))
    
    with cloud_engine.begin() as conn:
        # PostgreSQL中，TRUNCATE CASCADE会自动处理外键约束
        try:
            for table_name in reverse_order:
                try:
                    # 检查表是否存在
                    inspector = inspect(cloud_engine)
                    if table_name not in inspector.get_table_names():
                        continue
                    
                    # 清空表数据（CASCADE会自动处理外键依赖）
                    conn.execute(text(f'TRUNCATE TABLE "{table_name}" CASCADE'))
                    print(f"  ✅ 已清空表: {table_name}")
                except Exception as e:
                    print(f"  ⚠️  清空表 {table_name} 失败: {e}")
                    # 继续清空其他表
                    continue
            
            print("\n✅ 云端数据库数据已清空")
        except Exception as e:
            print(f"\n❌ 清空数据失败: {e}")
            raise


def main():
    """主函数"""
    print("\n" + "="*60)
    print("数据同步工具: 本地MySQL -> 云端PostgreSQL")
    print("="*60)
    
    # 获取数据库连接
    try:
        local_url = get_local_db_url()
        cloud_url = get_cloud_db_url()
        
        print(f"\n📌 本地数据库: {local_url.split('@')[1] if '@' in local_url else local_url}")
        print(f"📌 云端数据库: {cloud_url.split('@')[1] if '@' in cloud_url else '***'}")
        
    except Exception as e:
        print(f"❌ 配置错误: {e}")
        return
    
    # 创建数据库引擎
    try:
        print("\n🔌 正在连接数据库...")
        local_engine = create_engine(
            local_url,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 10,
                "charset": "utf8mb4",
            } if "mysql" in local_url else {}
        )
        
        cloud_engine = create_engine(
            cloud_url,
            pool_pre_ping=True,
            connect_args={"sslmode": "require"} if "postgresql" in cloud_url else {}
        )
        
        # 测试连接
        with local_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 本地数据库连接成功")
        
        with cloud_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 云端数据库连接成功")
        
        # 检查并修复枚举类型
        check_and_fix_enum_types(cloud_engine)
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 询问是否清空云端数据
    print("\n" + "="*60)
    print("⚠️  同步选项")
    print("="*60)
    print("1. 清空云端数据后同步（推荐，确保完整同步所有数据）")
    print("2. 保留云端数据，仅更新/插入（可能因外键约束失败）")
    print("="*60)
    
    clear_option = input("\n请选择 (1/2，默认: 1): ").strip()
    should_clear = clear_option in ('', '1', 'yes', 'y')
    
    if should_clear:
        try:
            clear_cloud_database(cloud_engine)
        except Exception as e:
            print(f"\n❌ 清空数据失败: {e}")
            confirm = input("是否继续同步？(yes/no): ").strip().lower()
            if confirm not in ('yes', 'y'):
                print("❌ 已取消同步")
                return
    else:
        print("\n⚠️  将保留云端现有数据，仅进行更新/插入操作")
    
    # 确认同步
    print("\n" + "="*60)
    print("⚠️  警告: 此操作将同步所有本地数据到云端数据库")
    if not should_clear:
        print("   如果云端已有数据，将根据主键进行更新（UPSERT）")
    print("="*60)
    
    confirm = input("\n是否继续？(yes/no，默认: yes): ").strip().lower()
    if confirm and confirm not in ('yes', 'y', ''):
        print("❌ 已取消同步")
        return
    
    # 开始同步
    print("\n🚀 开始同步数据...")
    start_time = datetime.now()
    
    total_success = 0
    total_fail = 0
    
    for table_name in TABLE_SYNC_ORDER:
        try:
            # 检查表是否存在
            local_inspector = inspect(local_engine)
            cloud_inspector = inspect(cloud_engine)
            
            if table_name not in local_inspector.get_table_names():
                print(f"\n⚠️  本地数据库中没有表: {table_name}，跳过")
                continue
            
            if table_name not in cloud_inspector.get_table_names():
                print(f"\n⚠️  云端数据库中没有表: {table_name}，跳过")
                continue
            
            # 在同步counselors表之前，验证users表
            if table_name == "counselors":
                verify_users_before_sync_counselors(local_engine, cloud_engine)
            
            success, fail = sync_table(local_engine, cloud_engine, table_name)
            total_success += success
            total_fail += fail
            
        except Exception as e:
            print(f"\n❌ 同步表 {table_name} 时出错: {e}")
            import traceback
            traceback.print_exc()
            total_fail += 1
    
    # 同步完成
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("📊 同步完成统计")
    print("="*60)
    print(f"✅ 成功同步: {total_success} 条记录")
    print(f"⚠️  失败/跳过: {total_fail} 条记录")
    print(f"⏱️  耗时: {duration:.2f} 秒")
    print("="*60)
    
    # 测试同步结果
    print("\n🧪 测试同步结果...")
    try:
        with cloud_engine.connect() as conn:
            # 检查users表
            result = conn.execute(text('SELECT COUNT(*) FROM "users"'))
            user_count = result.scalar()
            print(f"✅ 云端users表: {user_count} 条记录")
            
            # 检查是否有"刘紫湲"用户
            result = conn.execute(
                text('SELECT id, username, nickname FROM "users" WHERE username = :username OR nickname = :nickname'),
                {"username": "刘紫湲", "nickname": "刘紫湲"}
            )
            user = result.fetchone()
            if user:
                print(f"✅ 找到用户 '刘紫湲': ID={user[0]}, username={user[1]}, nickname={user[2]}")
            else:
                print("⚠️  未找到用户 '刘紫湲'")
            
            # 统计各表记录数
            print("\n📊 各表记录数统计:")
            for table_name in TABLE_SYNC_ORDER:
                try:
                    result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
                    count = result.scalar()
                    if count > 0:
                        print(f"  - {table_name}: {count} 条")
                except:
                    pass
                    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ 同步完成！")


if __name__ == "__main__":
    main()

