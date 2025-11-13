# 修复 counselors 表缺少 intro 字段的问题

## 问题描述

在获取咨询师列表时遇到数据库错误：
```
(pymysql.err.OperationalError) (1054, "Unknown column 'counselors.intro' in 'field list'")
```

## 问题原因

数据库表 `counselors` 中缺少 `intro` 字段，但模型定义（`models.py`）中包含了这个字段。这通常发生在：
1. 数据库表是早期创建的，没有包含 `intro` 字段
2. 模型定义后来添加了 `intro` 字段，但数据库表没有同步更新

## 解决方案

创建并运行了数据库迁移脚本 `migrate_add_intro.py`，为 `counselors` 表添加 `intro` 字段。

### 迁移脚本内容

```python
"""
数据库迁移脚本：为 counselors 表添加 intro 字段
"""
from sqlalchemy import text, inspect
from database import engine, SessionLocal

def add_intro_column():
    """为 counselors 表添加 intro 字段"""
    db = SessionLocal()
    try:
        # 检查字段是否已存在
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('counselors')]
        
        if 'intro' in columns:
            print("[OK] intro 字段已存在，无需添加")
            return
        
        # 添加字段
        print("正在为 counselors 表添加 intro 字段...")
        db.execute(text("""
            ALTER TABLE counselors 
            ADD COLUMN intro TEXT NULL 
            COMMENT '详细介绍（富文本）'
            AFTER bio
        """))
        db.commit()
        print("[OK] intro 字段添加成功")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] 添加字段失败: {e}")
        raise
    finally:
        db.close()
```

### 执行步骤

运行迁移脚本：
```bash
cd src/backend
python migrate_add_intro.py
```

### 执行结果

迁移脚本成功执行，输出：
```
正在为 counselors 表添加 intro 字段...
[OK] intro 字段添加成功
```

## 字段说明

`intro` 字段定义：
- **类型**: TEXT（支持长文本）
- **允许为空**: 是（NULL）
- **位置**: 在 `bio` 字段之后
- **用途**: 存储咨询师的详细介绍（富文本格式）
- **注释**: 详细介绍（富文本）

## 验证

迁移完成后，可以验证：
1. 查询咨询师列表应该不再报错
2. 可以正常获取咨询师的 `intro` 字段值（可能为 NULL）
3. 可以正常更新咨询师的 `intro` 字段

## 相关文件

- **模型定义**: `src/backend/models.py` (第116行)
- **迁移脚本**: `src/backend/migrate_add_intro.py`
- **API 路由**: `src/backend/routers/admin.py` (第241行)
- **API 路由**: `src/backend/routers/counselors.py` (使用 `intro` 字段)

## 注意事项

1. 迁移脚本是幂等的，可以多次运行而不会出错
2. 如果字段已存在，脚本会跳过添加操作
3. 现有记录的 `intro` 字段值为 NULL，需要手动或通过 API 更新

## 后续操作

如果需要为现有咨询师记录设置 `intro` 字段，可以：
1. 通过管理员后台手动更新
2. 通过 API 更新咨询师资料
3. 创建数据迁移脚本批量更新

## 更新日期

2024-11-05








