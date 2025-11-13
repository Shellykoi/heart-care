/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 🌿 柔和极简主义主题配色 - 米色 + 黑黄点缀
        theme: {
          // 背景与层次
          background: "#F9F7F4",     // 页面底色 - 浅米色/奶油白色
          card: "#FFFFFF",           // 内容卡片背景 - 纯白色
          sidebarFrom: "#F5F0EB",    // 侧边栏渐变起点
          sidebarTo: "#F0E9E3",     // 侧边栏渐变终点

          // 文本与中性色
          textPrimary: "#222222",   // 主标题文字 - 深黑/炭黑
          textSecondary: "#666666", // 次要说明文字 - 中灰
          textMuted: "#999999",     // 弱化提示文字

          // 高亮与强调
          highlight: "#FFD166",     // 选中图标/点缀色（明亮黄色）
          accent: "#F8A44C",        // 次强调（温暖橙）
          accentSoft: "#FFEDD5",    // 柔和橙背景（提示、标签等）

          // 对比色
          black: "#1E1E1E",
          white: "#FFFFFF",

          // 阴影与边界
          borderLight: "#E8E2DB",
        },
      },
      boxShadow: {
        soft: "0 0 12px rgba(0,0,0,0.08)", // 侧边栏和卡片使用的柔和阴影
        medium: "0 6px 20px rgba(0,0,0,0.08)",
      },
      borderRadius: {
        xl: "20px",
        fullSemi: "9999px", // 用于半圆形侧边栏
      },
      fontFamily: {
        sans: ['"Inter"', '"Noto Sans SC"', "Helvetica", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
}

