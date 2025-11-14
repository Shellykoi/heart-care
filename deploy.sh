#!/bin/bash

# 部署脚本：将 build 文件复制到根目录

echo "开始部署到 GitHub Pages..."

# 1. 构建项目
echo "正在构建项目..."
npm run build

# 2. 复制 build 目录内容到根目录
echo "正在复制 build 文件到根目录..."
cp -r build/* .

# 3. 确保 404.html 存在（用于 SPA 路由）
if [ ! -f "404.html" ]; then
  cp index.html 404.html
  echo "已创建 404.html"
fi

echo "部署文件准备完成！"
echo "请执行以下命令提交更改："
echo "  git add ."
echo "  git commit -m 'deploy: update GitHub Pages'"
echo "  git push"

