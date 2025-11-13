# 快速启动指南

## 一键启动（Windows PowerShell）

### 首次启动（需要安装依赖）

```powershell
# 1. 安装后端依赖
cd src/backend
pip install -r requirements.txt

# 2. 初始化数据库（首次运行）
python init_db.py

# 3. 启动后端服务（新终端窗口）
cd src/backend
python main.py

# 4. 启动前端服务（新终端窗口，在项目根目录）
npm run dev
```

### 日常启动（依赖已安装）

```powershell
# 终端1: 启动后端
cd src/backend
python main.py

# 终端2: 启动前端
npm run dev
```

## 验证启动成功

1. **后端**: 访问 http://localhost:8000/docs - 应看到 Swagger API 文档
2. **前端**: 访问 http://localhost:3000 - 应看到登录页面

## 常见问题

### 问题: ModuleNotFoundError

**解决**: 安装依赖
```powershell
cd src/backend
pip install -r requirements.txt
```

### 问题: 数据库连接失败

**解决**: 
1. 确保 MySQL 服务已启动
2. 检查 `src/backend/database.py` 中的数据库配置
3. 运行 `python src/backend/init_db.py` 初始化数据库

### 问题: 端口被占用

**解决**: 
- 后端端口 8000 被占用: 修改 `src/backend/main.py` 中的端口号
- 前端端口 3000 被占用: 修改 `vite.config.ts` 中的端口号

## 详细文档

更多信息请查看 [README_SETUP.md](README_SETUP.md)





