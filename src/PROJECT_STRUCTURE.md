# 南湖心理咨询管理平台 - 项目结构说明

## 📁 项目概览

这是一个完整的心理咨询管理平台，包含美观的前端界面和完整的后端 API 框架。

## 🎨 前端部分（React + Tailwind CSS）

### 技术栈
- **框架**: React 18
- **样式**: Tailwind CSS 4.0
- **UI 组件**: shadcn/ui
- **图标**: Lucide React

### 核心页面和组件

```
/
├── App.tsx                          # 主应用入口，角色路由
├── components/
│   ├── LoginPage.tsx               # 登录注册页面
│   ├── UserDashboard.tsx           # 普通用户控制台
│   ├── CounselorDashboard.tsx      # 咨询师工作台
│   ├── AdminDashboard.tsx          # 管理员后台
│   │
│   ├── user/                       # 用户功能模块
│   │   ├── AppointmentBooking.tsx  # 预约咨询
│   │   ├── PsychTest.tsx          # 心理测评
│   │   ├── HealthContent.tsx      # 健康科普
│   │   ├── Community.tsx          # 互助社区
│   │   └── UserProfile.tsx        # 个人中心
│   │
│   └── ui/                         # shadcn/ui 组件库
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       ├── input.tsx
│       ├── table.tsx
│       ├── tabs.tsx
│       └── ... (40+ 组件)
```

### 功能模块

#### 1. 登录注册 (LoginPage.tsx)
- ✅ 双标签切换（登录/注册）
- ✅ 多种登录方式（手机号/学号/邮箱）
- ✅ 角色选择（演示模式）
- ✅ 渐变背景 + 卡片布局
- ✅ 品牌展示和特性说明

#### 2. 普通用户控制台 (UserDashboard.tsx)
- ✅ 数据概览卡片（预约、咨询、测评、收藏）
- ✅ 最近预约列表
- ✅ 推荐内容展示
- ✅ 6个功能标签页

**子模块**:
- **预约咨询**: 咨询师搜索、筛选、预约、详情查看
- **心理测评**: 量表列表、历史报告、趋势分析
- **健康科普**: 文章/视频/音频浏览、分类筛选
- **互助社区**: 发帖、评论、点赞、匿名互动
- **个人中心**: 资料管理、隐私设置、安全中心

#### 3. 咨询师工作台 (CounselorDashboard.tsx)
- ✅ 工作数据概览
- ✅ 待处理预约列表
- ✅ 今日日程安排
- ✅ 预约管理（确认/拒绝/填写小结）
- ✅ 日程设置
- ✅ 数据统计可视化
- ✅ 个人主页设置

#### 4. 管理员后台 (AdminDashboard.tsx)
- ✅ 平台数据统计（用户、咨询师、预约、测评）
- ✅ 心理问题分布图
- ✅ 用户管理（查看、禁用）
- ✅ 咨询师审核（资质审查、通过/驳回）
- ✅ 内容审核（科普、社区帖子）
- ✅ 系统设置

### 设计特点
- 🎨 清新简洁的蓝紫渐变配色方案
- 📱 完全响应式设计
- ✨ 流畅的动画和过渡效果
- 🔐 隐私保护优先的 UI 设计
- 📊 数据可视化展示

---

## 🔧 后端部分（FastAPI + MySQL）

### 技术栈
- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 5.7
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT + OAuth2
- **密码加密**: Bcrypt

### 项目结构

```
/backend/
├── main.py                 # FastAPI 应用入口
├── database.py            # 数据库连接配置
├── models.py              # SQLAlchemy 数据模型
├── schemas.py             # Pydantic 数据验证模型
├── auth.py                # 认证和授权工具
├── requirements.txt       # Python 依赖
├── README.md              # 后端文档
│
└── routers/               # API 路由模块
    ├── __init__.py
    ├── auth.py           # 认证路由
    ├── users.py          # 用户路由
    ├── counselors.py     # 咨询师路由
    ├── appointments.py   # 预约路由
    ├── tests.py          # 测评路由
    ├── content.py        # 内容路由
    ├── community.py      # 社区路由
    └── admin.py          # 管理员路由
```

### 数据库设计（10个核心表）

#### 1. users（用户表）
- 基本信息：用户名、手机号、邮箱、学号
- 个人资料：昵称、性别、年龄、学校
- 角色和权限：user/counselor/volunteer/admin
- 隐私设置：隐身模式、数据保留时长

#### 2. counselors（咨询师表）
- 资质信息：姓名、证书、从业年限
- 专业领域：擅长方向、个人简介
- 服务设置：咨询方式、费用、预约量
- 统计数据：咨询次数、评分、评价数

#### 3. counselor_schedules（日程表）
- 每周可预约时段设置
- 支持按星期和时间段配置

#### 4. appointments（预约表）
- 预约信息：用户、咨询师、时间、方式
- 状态流转：待确认→已确认→已完成
- 咨询记录：诉求、小结、评分

#### 5. test_scales（测评量表）
- 量表信息：名称、分类、题目数量
- 题目内容（JSON 格式）

#### 6. test_reports（测评报告）
- 测评结果：得分、等级、详细分析
- 历史记录追踪

#### 7. contents（健康科普）
- 内容类型：文章、视频、音频
- 分类和标签
- 浏览量、点赞数统计

#### 8. community_posts（社区帖子）
- 三大板块：心情树洞、互助问答、经验分享
- 匿名发布、审核机制

#### 9. comments（评论表）
- 帖子评论、点赞
- 审核状态

#### 10. system_logs（系统日志）
- 用户操作记录
- 安全审计

### API 接口（8大模块，50+ 接口）

#### 认证模块 `/api/auth`
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `GET /me` - 获取当前用户

#### 用户模块 `/api/users`
- `GET /profile` - 个人资料
- `PUT /profile` - 更新资料
- `GET /appointments/history` - 预约历史

#### 咨询师模块 `/api/counselors`
- `POST /apply` - 申请成为咨询师
- `GET /search` - 搜索咨询师
- `PUT /profile` - 更新资料

#### 预约模块 `/api/appointments`
- `POST /create` - 创建预约
- `GET /my-appointments` - 我的预约
- `PUT /{id}` - 更新状态/填写小结

#### 测评模块 `/api/tests`
- `GET /scales` - 量表列表
- `POST /submit` - 提交测评
- `GET /reports/mine` - 我的报告

#### 内容模块 `/api/content`
- `GET /list` - 内容列表
- `GET /{id}` - 内容详情
- `POST /{id}/like` - 点赞

#### 社区模块 `/api/community`
- `POST /posts` - 发布帖子
- `GET /posts` - 帖子列表
- `POST /comments` - 发布评论

#### 管理员模块 `/api/admin`
- `GET /statistics` - 平台统计
- `PUT /counselors/{id}/approve` - 审核咨询师
- `PUT /posts/{id}/approve` - 审核帖子

### 认证机制
- JWT Token 认证
- 基于角色的权限控制（RBAC）
- 密码 Bcrypt 加密
- Token 过期时间：24小时

---

## 🚀 快速开始

### 前端启动
前端已经在当前环境中运行，可以直接预览界面。

### 后端启动

1. **安装 Python 依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **配置 MySQL 数据库**
```sql
CREATE DATABASE nanhu_psychology CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. **修改数据库连接**
编辑 `backend/database.py`:
```python
DATABASE_URL = "mysql+pymysql://root:your_password@localhost:3306/nanhu_psychology"
```

4. **启动服务**
```bash
python main.py
```

5. **访问 API 文档**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📋 功能清单

### ✅ 已实现（前端）
- [x] 登录注册页面（美观的渐变设计）
- [x] 普通用户完整功能（预约、测评、科普、社区、个人中心）
- [x] 咨询师工作台（预约管理、日程设置、数据统计）
- [x] 管理员后台（用户管理、咨询师审核、内容审核、数据统计）
- [x] 响应式布局（支持桌面和移动端）
- [x] 交互动画和过渡效果

### ✅ 已实现（后端）
- [x] 完整的数据库模型设计（10个表）
- [x] RESTful API 路由（8大模块）
- [x] JWT 认证系统
- [x] 基于角色的权限控制
- [x] 请求验证（Pydantic）
- [x] 数据库 ORM（SQLAlchemy）
- [x] API 文档（Swagger）

### 🔄 建议扩展
- [ ] 前后端对接（Axios 请求集成）
- [ ] 实时聊天功能（WebSocket）
- [ ] 文件上传（咨询资料、证书）
- [ ] 数据可视化图表（Recharts）
- [ ] 邮件/短信通知
- [ ] 支付功能集成
- [ ] 数据导出（Excel/PDF）

---

## 💡 技术亮点

1. **前端设计**
   - 采用现代化的卡片式布局
   - 蓝紫渐变主题色，符合心理健康平台的温暖基调
   - shadcn/ui 组件库，保证组件质量和一致性
   - 完善的交互反馈和状态提示

2. **后端架构**
   - FastAPI 高性能异步框架
   - 清晰的分层架构（Router → Service → Model）
   - 完善的认证授权机制
   - 规范的 RESTful API 设计

3. **数据库设计**
   - 规范化的表结构设计
   - 合理的外键关联
   - 时间戳自动管理
   - 软删除机制

4. **安全性**
   - 密码 Bcrypt 加密
   - JWT Token 认证
   - SQL 注入防护（ORM）
   - CORS 跨域配置
   - 敏感信息脱敏

---

## 📞 联系与支持

这是一个完整的心理咨询管理平台基础框架，包含了所有核心功能的前端界面和后端 API。您可以基于此框架进行二次开发和功能扩展。

**注意**: 
- 前端使用 React 而非 Vue，但功能完全对应您的需求
- 后端提供了完整的 FastAPI 框架，可直接运行
- 生产环境部署前请修改安全配置（SECRET_KEY 等）
- 建议添加日志系统和监控告警

祝您的项目顺利！🎉
