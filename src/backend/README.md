# 南湖心理咨询管理平台 - 后端 API

## 技术栈
- **框架**: FastAPI
- **数据库**: MySQL 5.7
- **ORM**: SQLAlchemy
- **认证**: JWT (JSON Web Token)

## 环境要求
- Python 3.8+
- MySQL 5.7+

## 安装步骤

### 1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置数据库
在 MySQL 中创建数据库：
```sql
CREATE DATABASE nanhu_psychology CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `database.py` 中的数据库连接信息：
```python
DATABASE_URL = "mysql+pymysql://用户名:密码@localhost:3306/nanhu_psychology"
```

### 4. 初始化数据库
首次运行时，SQLAlchemy 会自动创建所有表结构。

### 5. 启动服务
```bash
python main.py
```

或使用 uvicorn 直接启动：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档
启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 路由概览

### 认证模块 (`/api/auth`)
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `POST /logout` - 用户登出
- `GET /me` - 获取当前用户信息

### 用户模块 (`/api/users`)
- `GET /profile` - 获取个人资料
- `PUT /profile` - 更新个人资料
- `DELETE /profile` - 删除账户
- `GET /appointments/history` - 预约历史
- `GET /tests/history` - 测评历史

### 咨询师模块 (`/api/counselors`)
- `POST /apply` - 申请成为咨询师
- `GET /search` - 搜索咨询师
- `GET /{counselor_id}` - 咨询师详情
- `PUT /profile` - 更新咨询师资料
- `GET /stats/mine` - 咨询师统计数据

### 预约模块 (`/api/appointments`)
- `POST /create` - 创建预约
- `GET /my-appointments` - 我的预约列表
- `GET /{appointment_id}` - 预约详情
- `PUT /{appointment_id}` - 更新预约
- `DELETE /{appointment_id}` - 取消预约

### 心理测评模块 (`/api/tests`)
- `GET /scales` - 测评量表列表
- `GET /scales/{scale_id}` - 量表详情
- `POST /submit` - 提交测评
- `GET /reports/mine` - 我的测评报告
- `GET /reports/{report_id}` - 报告详情

### 健康科普模块 (`/api/content`)
- `GET /list` - 内容列表
- `GET /{content_id}` - 内容详情
- `POST /{content_id}/like` - 点赞内容

### 社区模块 (`/api/community`)
- `POST /posts` - 发布帖子
- `GET /posts` - 帖子列表
- `GET /posts/{post_id}` - 帖子详情
- `POST /posts/{post_id}/like` - 点赞帖子
- `POST /comments` - 发布评论
- `GET /posts/{post_id}/comments` - 获取评论

### 管理员模块 (`/api/admin`)
- `GET /statistics` - 平台统计数据
- `GET /counselors/pending` - 待审核咨询师
- `PUT /counselors/{counselor_id}/approve` - 审核通过
- `PUT /counselors/{counselor_id}/reject` - 拒绝申请
- `GET /posts/pending` - 待审核帖子
- `PUT /posts/{post_id}/approve` - 审核通过帖子
- `DELETE /posts/{post_id}` - 删除帖子
- `PUT /users/{user_id}/disable` - 禁用用户

## 数据库表结构

### 主要数据表
- `users` - 用户表
- `counselors` - 咨询师表
- `counselor_schedules` - 咨询师日程表
- `appointments` - 预约表
- `test_scales` - 测评量表
- `test_reports` - 测评报告表
- `contents` - 健康科普内容表
- `community_posts` - 社区帖子表
- `comments` - 评论表
- `system_logs` - 系统日志表

## 开发注意事项

1. **安全配置**
   - 修改 `auth.py` 中的 `SECRET_KEY`
   - 生产环境使用环境变量管理敏感信息

2. **数据库连接**
   - 确保 MySQL 服务正在运行
   - 检查数据库连接配置是否正确

3. **CORS 配置**
   - `main.py` 中已配置允许前端跨域访问
   - 根据实际部署调整允许的域名

4. **日志记录**
   - 建议添加日志中间件记录所有请求
   - 生产环境关闭 SQL echo

## 部署建议

### 生产环境配置
1. 使用 Gunicorn + Uvicorn 部署
2. 配置 Nginx 反向代理
3. 使用环境变量管理配置
4. 配置 HTTPS
5. 定期备份数据库

### Docker 部署（可选）
创建 `Dockerfile` 和 `docker-compose.yml` 实现容器化部署。

## 许可证
MIT License
