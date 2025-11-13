# GitHub Pages 部署指南（Vite + React）

> 目标：让仓库推送到 `main` 分支时自动构建并发布到 GitHub Pages，生成对外可访问的登录入口。

## 1. 前置准备
- 确保代码已推送到 GitHub 仓库（默认分支假设为 `main`）。
- GitHub 仓库设置 → Pages → “Build and deployment” 选择 **GitHub Actions**。
- 仓库拥有者需要开启 Actions 运行权限（Settings → Actions → General → 选择 “Allow all actions and reusable workflows”）。

## 2. 本地配置修改
这些改动已经在仓库中完成，若未来新建项目可对照执行：

1. **Vite 基础路径**  
   `vite.config.ts` 根据环境自动切换 `base`：
   ```ts
   const repositoryName = 'heart-care';
   const isGitHubPages = process.env.GITHUB_PAGES === 'true' || process.env.DEPLOY_TARGET === 'github-pages';
   const base = isGitHubPages ? `/${repositoryName}/` : '/';
   ```
   - 本地开发依旧访问 `http://localhost:3000/`。
   - GitHub Actions 构建时注入 `GITHUB_PAGES=true`，输出资源会指向 `https://<user>.github.io/heart-care/`。
   - 若仓库名改变，请同步更新 `repositoryName`。

2. **GitHub Actions 工作流**  
   `.github/workflows/deploy.yml` 会在推送到 `main` 或手动触发时执行：
   - 安装依赖 → `npm ci`
   - 构建产物（自动设置 `GITHUB_PAGES=true`）→ `npm run build`
   - 将 `build/index.html` 复制为 `build/404.html`，解决 SPA 子路由刷新 404 问题
   - 上传产物并部署到 GitHub Pages

## 3. 首次部署步骤
# Workflow 监听分支
- 默认监听 `main` 和 `master`。如果仓库使用其它默认分支，请同步修改 `.github/workflows/deploy.yml`。

## 3. 首次部署步骤
1. 将代码推送到 GitHub：  
   ```bash
   git add .
   git commit -m "chore: prepare GitHub Pages deployment"
   git push origin <default-branch>
   ```
2. 进入仓库 → Actions → 找到 “Deploy Vite App to GitHub Pages” 工作流，等待执行完成。
3. 完成后在仓库设置 → Pages 可以查看最终 URL（通常是 `https://<你的用户名>.github.io/heart-care/`）。

## 4. 后续更新流程
1. 在本地进行日常开发、提交：  
   ```bash
   git add <files>
   git commit -m "feat: xxx"
   git push origin main
   ```
2. push 后 GitHub Actions 自动构建与部署，等待工作流成功即可上线。
3. 若要手动重新部署，可在 Actions 面板点击工作流 → “Run workflow”。

## 5. 常见问题
- **页面空白或资源 404**：确认 `repositoryName` 是否与 GitHub 仓库名完全一致；提交后触发新构建。
- **刷新子路由跳转到 404**：Actions 会自动复制 `index.html` 为 `404.html`，若手动部署，请确保也做此操作。
- **登录页直接显示**：App 默认在未登录时显示 `LoginPage`，无须额外路由调整。
- **自定义域名**：在 GitHub Pages 设置里绑定自定义域名后，记得更新 DNS，并按需在仓库根目录添加 `CNAME` 文件。
- **前端连不上后端**：从 GitHub Pages（HTTPS）访问 HTTP 接口会被浏览器拦截。复制 `docs/env.example` 为 `.env.production`，把 `VITE_API_BASE_URL` 改成你的公网后端地址（必须是 https://，并包含 `/api` 后缀），重新 `npm run build` 后再部署。开发环境可在 `.env.development` 保留 `http://localhost:8000/api`。

部署成功后，将生成的链接分享给用户即可。首次启动建议在隐身窗口测试登录流程，确认 API CORS/HTTPS 等配置都正常工作。

