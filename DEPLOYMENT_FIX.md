# 部署问题修复指南

## 已修复的问题

### 1. GitHub Pages 404 错误

**问题**：访问 GitHub Pages 时显示 404 错误。

**解决方案**：
1. 确保 GitHub Actions 工作流已正确配置（`.github/workflows/deploy.yml` 已存在）
2. 在 GitHub 仓库设置中启用 GitHub Pages：
   - 进入仓库 → Settings → Pages
   - Source 选择 "GitHub Actions"
   - 保存设置
3. 推送代码到 `main` 分支触发自动部署：
   ```bash
   git add .
   git commit -m "fix: update deployment configuration"
   git push origin main
   ```
4. 等待 GitHub Actions 工作流完成（可在 Actions 标签页查看）
5. 部署完成后，访问：`https://shellykoi.github.io/heart-care/`

### 2. 登录请求超时问题

**问题**：从 GitHub Pages 访问时，登录请求超时。

**已修复**：
- ✅ 前端 API 配置已更新，自动检测生产环境并使用正确的后端 URL
- ✅ 后端 CORS 配置已包含 GitHub Pages 域名
- ✅ 请求超时时间已设置为 60 秒

**验证**：
- 本地开发：使用 `http://localhost:8000/api`
- 生产环境（GitHub Pages）：自动使用 `https://heart-care-m28z.onrender.com/api`

### 3. 用户不存在问题

**问题**：登录时提示 "account='刘紫湲' not found"

**说明**：这是数据问题，不是代码问题。用户"刘紫湲"在数据库中不存在。

**解决方案**：
1. 如果是新用户，需要先注册
2. 如果是已有用户，检查：
   - 用户名是否正确
   - 是否使用了正确的登录方式（用户名/手机号/邮箱/学号）
   - 数据库中是否存在该用户

## 部署检查清单

### 本地开发环境
- [x] 后端服务运行在 `http://localhost:8000`
- [x] 前端开发服务器运行在 `http://localhost:3000`
- [x] 数据库连接正常
- [x] 本地登录功能正常

### 生产环境（GitHub Pages）
- [x] GitHub Actions 工作流配置正确
- [x] 前端自动检测生产环境并使用正确的后端 URL
- [x] 后端 CORS 配置包含 GitHub Pages 域名
- [ ] GitHub Pages 已启用（需要在 GitHub 仓库设置中手动启用）
- [ ] 代码已推送到 `main` 分支
- [ ] GitHub Actions 工作流执行成功

## 部署步骤

### 首次部署

1. **启用 GitHub Pages**：
   - 进入 GitHub 仓库 → Settings → Pages
   - Source 选择 "GitHub Actions"
   - 保存设置

2. **推送代码**：
   ```bash
   git add .
   git commit -m "chore: prepare for GitHub Pages deployment"
   git push origin main
   ```

3. **等待部署完成**：
   - 进入仓库 → Actions 标签页
   - 查看 "Deploy Vite App to GitHub Pages" 工作流
   - 等待构建和部署完成（通常需要 2-5 分钟）

4. **验证部署**：
   - 访问 `https://shellykoi.github.io/heart-care/`
   - 测试登录功能
   - 检查所有功能是否正常

### 后续更新

每次更新代码后，只需推送到 `main` 分支，GitHub Actions 会自动重新部署：

```bash
git add .
git commit -m "feat: your changes"
git push origin main
```

## 环境变量配置

### 前端环境变量（可选）

如果需要自定义后端 URL，可以在项目根目录创建 `.env.production`：

```env
VITE_API_BASE_URL=https://heart-care-m28z.onrender.com/api
```

### 后端环境变量

后端需要配置 `DATABASE_URL` 环境变量（在 Render 或其他部署平台配置）。

## 常见问题

### Q: GitHub Pages 仍然显示 404
**A**: 
1. 检查 GitHub Pages 是否已启用（Settings → Pages）
2. 检查 GitHub Actions 工作流是否成功执行
3. 确认仓库名称是否为 `heart-care`（如果不同，需要修改 `vite.config.ts` 中的 `repositoryName`）

### Q: 登录时仍然超时
**A**:
1. 检查后端服务是否正常运行（访问 `https://heart-care-m28z.onrender.com/api/health`）
2. 检查浏览器控制台是否有 CORS 错误
3. 确认前端是否正确检测到生产环境

### Q: 用户登录失败
**A**:
1. 确认用户已在数据库中注册
2. 检查用户名/密码是否正确
3. 检查后端日志查看具体错误信息

## 技术支持

如果遇到其他问题，请检查：
1. GitHub Actions 工作流日志
2. 浏览器控制台错误信息
3. 后端服务日志
4. 网络连接状态

