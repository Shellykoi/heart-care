# 数据同步脚本使用说明

## 功能说明

`sync_all_data_to_cloud.py` 脚本用于将本地MySQL数据库的所有数据同步到云端PostgreSQL数据库。

## 主要特性

1. **自动同步所有表**：按照外键依赖顺序同步20个表
2. **智能密码处理**：如果用户密码哈希为空或无效，自动设置为默认密码（123456）
3. **数据类型转换**：自动处理MySQL和PostgreSQL之间的数据类型差异
4. **冲突处理**：使用UPSERT（ON CONFLICT）处理重复数据
5. **详细日志**：显示同步进度和结果统计

## 使用方法

### 方法1：直接运行（推荐）

```bash
cd src/backend
python sync_all_data_to_cloud.py
```

### 方法2：使用批处理文件（Windows）

```bash
sync_data.bat
```

### 方法3：设置环境变量后运行

**Windows PowerShell:**
```powershell
$env:CLOUD_DATABASE_URL="postgresql://user:password@host:port/database?sslmode=require"
cd src\backend
python sync_all_data_to_cloud.py
```

**Linux/Mac:**
```bash
export CLOUD_DATABASE_URL="postgresql://user:password@host:port/database?sslmode=require"
cd src/backend
python sync_all_data_to_cloud.py
```

## 配置说明

### 本地数据库配置

脚本会自动从以下位置读取本地MySQL数据库连接：
1. 环境变量 `LOCAL_DATABASE_URL`
2. 环境变量 `DATABASE_URL`（如果是MySQL连接）
3. `.env.local`、`.env` 或 `env/local.env` 文件
4. 默认值：`mysql+pymysql://root:123456@localhost:3306/heart_care`

### 云端数据库配置

脚本会按以下顺序查找云端PostgreSQL数据库连接：
1. 环境变量 `CLOUD_DATABASE_URL`
2. `.env.local`、`.env` 或 `env/local.env` 文件中的 `CLOUD_DATABASE_URL`
3. 如果都没有，会提示用户输入

## 同步的表（按顺序）

1. users - 用户表
2. test_scales - 测评量表
3. counselors - 咨询师
4. counselor_schedules - 咨询师日程
5. counselor_unavailable - 咨询师不可预约时段
6. contents - 内容
7. appointments - 预约
8. consultation_records - 咨询记录
9. counselor_ratings - 咨询师评分
10. test_reports - 测评报告
11. community_posts - 社区帖子
12. comments - 评论
13. post_reports - 帖子举报
14. user_favorites - 用户收藏
15. counselor_favorites - 咨询师收藏
16. content_likes - 内容点赞
17. private_messages - 私信
18. emergency_helps - 紧急求助
19. user_blocks - 用户拉黑
20. system_logs - 系统日志

## 注意事项

1. **数据备份**：同步前建议备份云端数据库
2. **密码重置**：如果用户密码哈希为空或无效，会自动设置为 `123456`
3. **冲突处理**：如果云端已有相同主键的记录，会更新该记录
4. **外键约束**：脚本按照外键依赖顺序同步，确保数据完整性
5. **数据类型**：自动处理MySQL和PostgreSQL之间的数据类型差异（如布尔值、枚举值等）

## 运行示例

```
============================================================
数据同步工具: 本地MySQL -> 云端PostgreSQL
============================================================

📌 本地数据库: localhost:3306/heart_care
📌 云端数据库: ep-xxxx.neon.tech/neondb

🔌 正在连接数据库...
✅ 本地数据库连接成功
✅ 云端数据库连接成功

============================================================
⚠️  警告: 此操作将同步所有本地数据到云端数据库
   如果云端已有数据，将根据主键进行更新（UPSERT）
============================================================

是否继续？(yes/no，默认: yes): yes

🚀 开始同步数据...

============================================================
同步表: users
============================================================
📊 本地数据库找到 10 条记录
✅ 成功: 10 条

...

============================================================
📊 同步完成统计
============================================================
✅ 成功同步: 150 条记录
⚠️  失败/跳过: 0 条记录
⏱️  耗时: 5.23 秒
============================================================

🧪 测试同步结果...
✅ 云端users表: 10 条记录
✅ 找到用户 '刘紫湲': ID=1, username=刘紫湲, nickname=刘紫湲

📊 各表记录数统计:
  - users: 10 条
  - counselors: 5 条
  - appointments: 20 条
  ...

✅ 同步完成！
```

## 故障排除

### 问题1：连接失败

**错误**: `数据库连接失败`

**解决方案**:
1. 检查MySQL服务是否启动
2. 检查数据库连接字符串是否正确
3. 检查网络连接（云端数据库）

### 问题2：表不存在

**错误**: `表 xxx 不存在`

**解决方案**:
1. 确保云端数据库已初始化（运行 `init_db.py`）
2. 检查表名是否正确

### 问题3：外键约束错误

**错误**: `IntegrityError: foreign key constraint`

**解决方案**:
1. 确保按照正确的顺序同步（脚本已自动处理）
2. 检查外键引用的记录是否存在

### 问题4：密码验证失败

**问题**: 同步后无法登录

**解决方案**:
1. 使用默认密码 `123456` 尝试登录
2. 运行 `reset_user_password.py` 重置密码

## 相关脚本

- `reset_user_password.py` - 重置用户密码
- `init_db.py` - 初始化数据库表结构
- `sync_user_to_cloud.py` - 同步单个用户到云端

