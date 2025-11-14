# 云端登录问题修复指南

## 问题描述

- ✅ 本地数据库有用户"刘紫湲"，可以正常登录
- ❌ 云端服务器（Render）无法登录，提示用户不存在

## 原因分析

云端数据库和本地数据库是**两个独立的数据库**：
- 本地数据库：`mysql+pymysql://shellykoi:123456koiii@localhost:3306/heart_care`
- 云端数据库：Render 上的数据库（通过环境变量 `DATABASE_URL` 配置）

用户"刘紫湲"只存在于本地数据库，云端数据库中没有这个用户。

## 解决方案

### 方案1：在云端数据库创建用户（推荐）

使用提供的脚本在云端数据库创建用户：

```bash
# 1. 设置云端数据库URL（在 Render 或其他平台的环境变量中）
# 或者临时设置：
export DATABASE_URL="你的云端数据库URL"

# 2. 运行创建用户脚本
cd src/backend
python create_user_cloud.py
```

脚本会：
- 检查云端数据库连接
- 创建用户"刘紫湲"（如果不存在）
- 设置默认密码：`123456`

### 方案2：从本地同步用户数据

如果需要同步更多用户数据，可以使用同步脚本：

```bash
# 1. 设置云端数据库URL
export CLOUD_DATABASE_URL="你的云端数据库URL"

# 2. 运行同步脚本
cd src/backend
python sync_user_to_cloud.py
```

### 方案3：使用诊断工具检查

首先诊断云端数据库状态：

```bash
# 设置云端数据库URL
export DATABASE_URL="你的云端数据库URL"

# 运行诊断脚本
cd src/backend
python diagnose_cloud_db.py
```

## 在 Render 上操作

### 方法1：通过 Render Dashboard

1. 登录 Render Dashboard
2. 进入你的服务（Backend Service）
3. 打开 "Environment" 标签
4. 确认 `DATABASE_URL` 环境变量已设置
5. 打开 "Shell" 标签（或使用 SSH）
6. 运行创建用户脚本

### 方法2：通过本地脚本（推荐）

1. **临时设置云端数据库URL**：
   ```bash
   # Windows PowerShell
   $env:DATABASE_URL="你的云端数据库URL"
   
   # Linux/Mac
   export DATABASE_URL="你的云端数据库URL"
   ```

2. **运行创建用户脚本**：
   ```bash
   cd src/backend
   python create_user_cloud.py
   ```

3. **恢复本地配置**：
   ```bash
   # Windows PowerShell
   $env:DATABASE_URL=""
   
   # Linux/Mac
   unset DATABASE_URL
   ```

   或者直接重启终端，本地配置会从 `.env.local` 或 `env/local.env` 自动加载。

## 验证修复

### 1. 使用诊断脚本验证

```bash
# 设置云端数据库URL
export DATABASE_URL="你的云端数据库URL"

# 运行诊断
cd src/backend
python diagnose_cloud_db.py
```

应该看到：
```
✅ 找到用户'刘紫湲'
   用户ID: xxx
   用户名: 刘紫湲
   ...
```

### 2. 测试云端登录

1. 访问 GitHub Pages: https://shellykoi.github.io/heart-care/
2. 尝试登录：
   - 账号：`刘紫湲`
   - 密码：`123456`（或你设置的密码）
   - 登录类型：学生登录

### 3. 检查后端日志

在 Render Dashboard 中查看后端服务日志，确认：
- 登录请求正常接收
- 数据库查询成功
- 没有错误信息

## 本地配置保护

✅ **本地配置不会受到影响**，因为：

1. **环境变量优先级**：
   - 系统环境变量 > `.env.local` > `.env` > `env/local.env`
   - 本地开发时，`env/local.env` 会自动加载

2. **数据库配置逻辑**（`database.py`）：
   ```python
   # 优先使用系统环境变量
   env_value = os.getenv("DATABASE_URL")
   if env_value:
       return env_value  # 如果设置了环境变量，使用它
   
   # 否则从 .env 文件加载
   for env_file in ENV_FILES:
       if env_file.exists():
           load_dotenv(env_file)  # 加载本地配置
   ```

3. **使用脚本时**：
   - 临时设置 `DATABASE_URL` 环境变量只会影响当前终端会话
   - 关闭终端后，环境变量会恢复
   - 本地配置文件（`.env.local`、`env/local.env`）不会被修改

## 常见问题

### Q: 如何确认当前使用的是哪个数据库？

**A**: 运行诊断脚本：
```bash
python diagnose_cloud_db.py
```
脚本会显示当前连接的数据库URL（隐藏敏感信息）。

### Q: 创建用户后仍然无法登录？

**A**: 检查：
1. 用户是否已创建（运行诊断脚本）
2. 密码是否正确
3. 用户是否激活（`is_active=True`）
4. 后端服务是否重启（某些情况下需要重启）

### Q: 如何批量同步用户？

**A**: 可以修改 `sync_user_to_cloud.py` 脚本，添加批量同步逻辑。

### Q: 本地开发受影响怎么办？

**A**: 
1. 确保 `env/local.env` 文件存在且包含本地数据库URL
2. 不要设置系统环境变量 `DATABASE_URL`（除非临时使用）
3. 使用完云端脚本后，关闭终端或取消设置环境变量

## 脚本说明

### `diagnose_cloud_db.py`
- 诊断数据库连接
- 检查用户是否存在
- 列出所有用户
- 检查表结构

### `create_user_cloud.py`
- 直接在云端数据库创建用户
- 如果用户已存在，可以更新密码
- 简单直接，推荐使用

### `sync_user_to_cloud.py`
- 从本地数据库读取用户数据
- 同步到云端数据库
- 适合批量同步

## 后续维护

1. **定期检查**：使用诊断脚本定期检查云端数据库状态
2. **用户管理**：在 Render Dashboard 中管理用户数据
3. **备份数据**：定期备份云端数据库
4. **监控日志**：关注后端服务日志，及时发现连接问题

## 总结

✅ **本地配置安全**：本地开发环境不会受到影响
✅ **简单修复**：使用 `create_user_cloud.py` 脚本即可快速修复
✅ **验证工具**：使用 `diagnose_cloud_db.py` 验证修复结果

修复后，云端登录应该可以正常工作！

