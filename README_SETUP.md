# 南湖心理咨询管理平台 - 完整功能实现指南

## 项目概述

本项目已完成从演示版本到完整功能版本的改造，所有假数据已移除，全部功能已连接到真实MySQL数据库。

## 技术栈

### 前端
- React 18 + TypeScript
- Vite
- shadcn/ui 组件库
- Axios (API 调用)
- Sonner (消息提示)

### 后端
- FastAPI
- SQLAlchemy (ORM)
- MySQL 5.7+
- JWT 认证
- Bcrypt 密码加密

## 数据库配置

后端通过环境变量 `DATABASE_URL` 控制数据库连接地址，代码中不再硬编码任何凭证。

### 本地开发（MySQL）

1. 复制 `env/local.env.template` 为 `.env`（或在 IDE 中配置环境变量），并填写自己的 MySQL 信息：

   ```
   DATABASE_URL=mysql+pymysql://root:your_local_password@localhost:3306/your_database
   SQLALCHEMY_ECHO=true
   ```

2. 确保安装了 MySQL 驱动：

   ```bash
   pip install pymysql
   ```

3. 本地启动 FastAPI 时，`src/backend/database.py` 会读取 `.env` 中的配置并连接本地 MySQL。日志中会输出：

   ```
   Connecting to database: ***@localhost:3306/your_database
   ```

### Render 部署（Neon PostgreSQL）

1. 在 Render 控制台的 **Environment → Environment Variables** 中添加：

   | Key           | Value                                                                 |
   | ------------- | --------------------------------------------------------------------- |
   | `DATABASE_URL` | `postgresql://<user>:<password>@<host>.neon.tech/neondb?sslmode=require` |

   可以直接使用 Neon 仪表盘生成的连接串（移除尾部多余的 `&`）。

2. 部署到 Render 时，后端会自动读取该变量并连接 Neon PostgreSQL；日志中会输出：

   ```
   Connecting to database: ***@ep-xxxx.neon.tech/neondb
   ```

> 注意：本地 `.env` 中的配置不会上传到 Render，云端与本地数据库互不干扰。

## 环境要求

- **Python**: 3.8 或更高版本
- **Node.js**: 16 或更高版本
- **MySQL**: 5.7 或更高版本
- **npm**: 随 Node.js 安装

## 快速开始

### 步骤 1: 安装后端依赖

进入后端目录并安装 Python 依赖：

```bash
cd src/backend
pip install -r requirements.txt
```

**注意**: 如果使用虚拟环境（推荐）：
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate

# 然后安装依赖
pip install -r requirements.txt
```

依赖包括：
- FastAPI - Web 框架
- SQLAlchemy - ORM
- PyMySQL - MySQL 驱动
- uvicorn - ASGI 服务器
- python-jose - JWT 认证
- passlib - 密码加密
- pydantic - 数据验证

### 步骤 2: 配置数据库

确保 MySQL 服务已启动，并且数据库用户 `shellykoi` 存在且有权限。

数据库连接信息通过 `.env` 或部署平台环境变量控制，无需修改 `src/backend/database.py`。

### 步骤 3: 初始化数据库

首次运行需要初始化数据库：

```bash
cd src/backend
python init_db.py
```

这个脚本会：
- 自动创建数据库（如果不存在）
- 创建所有表结构
- **清空所有现有数据**（如果表已存在）

**警告**: 此操作会删除所有现有数据，请确保在测试环境运行！

### 步骤 4: 启动后端服务

在 `src/backend` 目录下运行：

```bash
cd src/backend
python main.py
```

或者使用 uvicorn 直接启动：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**成功启动后，你会看到类似输出：**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

后端服务将在 `http://localhost:8000` 启动。

### 步骤 5: 验证后端服务

打开浏览器访问：
- **API 根路径**: http://localhost:8000/
- **API 文档 (Swagger)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc

如果看到 API 文档页面，说明后端启动成功。

### 步骤 6: 安装前端依赖（首次运行）

在项目根目录运行：

```bash
npm install
```

### 步骤 7: 启动前端服务

在项目根目录运行：

```bash
npm run dev
```

**成功启动后，你会看到类似输出：**
```
VITE v6.3.5  ready in 454 ms
➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

前端服务将在 `http://localhost:3000` 启动。

### 步骤 8: 验证前端服务

打开浏览器访问 http://localhost:3000，应该能看到登录页面。

## 完整启动流程总结

```bash
# 1. 安装后端依赖
cd src/backend
pip install -r requirements.txt

# 2. 初始化数据库（首次运行）
python init_db.py

# 3. 启动后端服务（保持终端运行）
cd src/backend
python main.py

3000..3010 | ForEach-Object { Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue } | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_ -Force }

   # 停止当前运行的后端服务
   # 然后重新启动
   cd src/backend
   python -m uvicorn main:app --reload

# 4. 打开新终端，安装前端依赖（首次运行）
cd <项目根目录>
npm install

# 5. 启动前端服务（保持终端运行）
npm run dev

# 6. 访问应用
# 前端: http://localhost:3000
# 后端 API: http://localhost:8000/docs
```

## 功能模块

### 1. 用户认证
- ✅ 用户注册（支持手机号/邮箱/学号）
- ✅ 用户登录（支持多种登录方式）
- ✅ JWT Token 认证
- ✅ 自动登录状态保持

### 2. 普通用户功能
- ✅ 个人中心（资料管理、隐私设置）
- ✅ 心理咨询预约（搜索、筛选、预约）
- ✅ 心理测评（量表列表、测评、历史报告）
- ✅ 健康科普（文章/视频/音频浏览）
- ✅ 互助社区（发帖、评论、点赞）
- ✅ 紧急求助

### 3. 咨询师功能
- ✅ 入驻申请
- ✅ 预约管理（确认/拒绝/填写小结）
- ✅ 日程设置
- ✅ 数据统计

### 4. 管理员功能
- ✅ 平台数据统计
- ✅ 用户管理
- ✅ 咨询师审核
- ✅ 内容审核（科普、社区帖子）

## API 文档

启动后端服务后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 数据库表结构

### 核心表
- `users` - 用户表
- `counselors` - 咨询师表
- `counselor_schedules` - 咨询师日程表
- `appointments` - 预约表
- `test_scales` - 测评量表表
- `test_reports` - 测评报告表
- `contents` - 健康科普内容表
- `community_posts` - 社区帖子表
- `comments` - 评论表

### 扩展表
- `user_favorites` - 用户收藏表
- `private_messages` - 私信表
- `emergency_helps` - 紧急求助表
- `user_blocks` - 用户拉黑表
- `content_likes` - 内容点赞表
- `counselor_ratings` - 咨询师评分表
- `system_logs` - 系统日志表

## 使用流程

### 首次使用

1. **初始化数据库**
   ```bash
   cd src/backend
   python init_db.py
   ```

2. **启动后端服务**
   ```bash
   cd src/backend
   python main.py
   ```

3. **启动前端服务**
   ```bash
   npm run dev
   ```

4. **注册第一个用户**
   - 访问 http://localhost:3000
   - 点击"注册"标签
   - 填写用户名、密码等信息
   - 提交注册

5. **开始使用**
   - 登录后可以体验所有功能
   - 从空白数据库开始，所有数据都是真实存储的

### 创建管理员账号

管理员账号需要通过数据库直接创建，或修改现有用户的角色：

```sql
UPDATE users SET role = 'admin' WHERE username = 'your_username';
```

### 创建咨询师账号

1. 普通用户登录后，在个人中心申请成为咨询师
2. 管理员在后台审核通过
3. 用户角色自动变为 `counselor`

## 注意事项

1. **数据库连接**
   - 确保 MySQL 服务已启动
   - 确保数据库用户 `shellykoi` 存在且有权限
   - 如果连接失败，检查 `database.py` 中的配置

2. **前端 API 配置**
   - API 基础 URL 在 `src/services/api.ts` 中配置
   - 默认: `http://localhost:8000/api`
   - 如果后端端口不同，需要修改

3. **Token 管理**
   - Token 存储在 `localStorage` 中
   - 过期时间：24小时
   - Token 过期后需要重新登录

4. **数据安全**
   - 生产环境请修改 `auth.py` 中的 `SECRET_KEY`
   - 生产环境请修改数据库密码
   - 建议启用 HTTPS

## 开发说明

### 前端 API 调用

所有 API 调用都通过 `src/services/api.ts` 中的服务函数：

```typescript
import { authApi, userApi, counselorApi } from '../services/api';

// 登录
const response = await authApi.login({ account: '...', password: '...' });

// 获取用户资料
const profile = await userApi.getProfile();
```

### 后端路由

所有后端路由都在 `src/backend/routers/` 目录下：

- `auth.py` - 认证相关
- `users.py` - 用户相关
- `counselors.py` - 咨询师相关
- `appointments.py` - 预约相关
- `tests.py` - 测评相关
- `content.py` - 内容相关
- `community.py` - 社区相关
- `admin.py` - 管理员相关

## 故障排除

### 问题 1: ModuleNotFoundError: No module named 'pymysql' 或 'fastapi'

**原因**: Python 依赖未安装

**解决方法**:
```bash
cd src/backend
pip install -r requirements.txt
```

如果使用虚拟环境，确保已激活：
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 问题 2: 数据库连接失败

**错误信息**: `OperationalError` 或 `Can't connect to MySQL server`

**解决方法**:
1. 检查 MySQL 服务是否启动
   ```bash
   # Windows (服务管理器)
   # 或使用命令行
   net start mysql
   ```
2. 检查数据库用户是否存在且有权限
   ```sql
   -- 登录 MySQL
   mysql -u root -p
   
   -- 创建用户（如果不存在）
   CREATE USER 'shellykoi'@'localhost' IDENTIFIED BY '123456koiii';
   GRANT ALL PRIVILEGES ON *.* TO 'shellykoi'@'localhost';
   FLUSH PRIVILEGES;
   ```
3. 检查密码是否正确（在 `database.py` 中）
4. 检查数据库是否已创建（运行 `init_db.py` 会自动创建）

### 问题 3: 前端无法连接后端

**错误信息**: `Network Error` 或 `CORS error`

**解决方法**:
1. 检查后端服务是否启动
   - 访问 http://localhost:8000/docs 确认后端运行
2. 检查 `src/services/api.ts` 中的 API 基础 URL
   ```typescript
   const API_BASE_URL = 'http://localhost:8000/api';
   ```
3. 检查后端 CORS 配置（在 `main.py` 中）
   - 确保包含 `http://localhost:3000`

### 问题 4: 端口被占用

**错误信息**: `Address already in use` 或 `Port 8000 is already in use`

**解决方法**:
```bash
# Windows: 查找占用端口的进程
netstat -ano | findstr :8000

# 杀死进程（替换 PID）
taskkill /PID <进程ID> /F

# 或修改 main.py 中的端口号
uvicorn.run("main:app", host="0.0.0.0", port=8001)
```

### 问题 5: Token 过期

Token 过期后会自动跳转到登录页，重新登录即可。

### 问题 6: 数据库表不存在

**错误信息**: `Table 'xxx' doesn't exist`

**解决方法**:
```bash
cd src/backend
python init_db.py
```

这会重新创建所有表结构。

### 问题 7: 依赖版本冲突

如果遇到依赖版本冲突警告，可以尝试：
```bash
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

## 常见启动错误速查表

| 错误信息 | 原因 | 解决方法 |
|---------|------|---------|
| `ModuleNotFoundError: No module named 'xxx'` | 依赖未安装 | `pip install -r requirements.txt` |
| `Can't connect to MySQL server` | MySQL 未启动 | 启动 MySQL 服务 |
| `Access denied for user` | 数据库用户权限问题 | 检查用户和密码配置 |
| `Address already in use` | 端口被占用 | 更换端口或结束占用进程 |
| `Table doesn't exist` | 数据库未初始化 | 运行 `python init_db.py` |
| `CORS error` | 跨域配置问题 | 检查 `main.py` 中的 CORS 设置 |

## 后续开发建议

1. **功能完善**
   - 短信验证码登录
   - 文件上传（证书、头像）
   - 实时聊天（WebSocket）
   - 支付功能集成

2. **性能优化**
   - 数据库索引优化
   - API 响应缓存
   - 前端代码分割

3. **安全加固**
   - 敏感信息加密
   - 请求频率限制
   - SQL 注入防护
   - XSS 防护

## 联系支持

如有问题，请查看：
- API 文档: http://localhost:8000/docs
- 后端 README: `src/backend/README.md`
- 数据库初始化说明: `src/backend/README_INIT.md`

