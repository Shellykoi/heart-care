# Dashboard Grid Layout Fix – Postmortem & Notes

## 背景
- 目标页面：`UserDashboard`。
- 症状：在桌面端布局中，左侧日历模块（期望占 3/5）与右侧数据看板（期望占 2/5）无法稳定保持 3:2 比例，偶尔退化成单列或列宽异常。
- 触发条件：Tailwind v4 预发行版的 JIT 生成类与我们使用的类名组合在部分构建/缓存场景下未正确输出，导致 `lg:grid-cols-5` + `lg:col-span-{n}` 组合失效。

## 根因
1. **Tailwind JIT 不稳定输出**  
   Tailwind v4 仍在快速迭代，同名的栅格类存在生成顺序与插入层级差异。当页面重新打包或缓存命中时，`grid-template-columns` 的最终实现偶尔缺失，从而让 `lg:grid-cols-5` 回退到单列默认值。
2. **外层容器存在 `max-width` 与 `overflow` 副作用**  
   之前的实现沿用默认 `.container` 限制以及内部组件自带的 `overflow-visible`，当列宽被压缩时，右侧组件撑开容器，进一步触发布局断裂。

## 解决方案
- **新增兜底类 `dashboard-grid-3-2`**  
  在 `src/index.css` 中为该类写死 1024px 以上使用 `grid-template-columns: 3fr 2fr`，并加上 `!important` 保障优先级。即使 Tailwind 未产出对应实用类，兜底规则也能强制生效。
- **补充列容器 `overflow-hidden`**  
  左右列都添加 `overflow-hidden`，避免内部模块意外撑破栅格，确保高度一致且不触发额外滚动。
- **保留现有 Tailwind 类作为“首选”**  
  继续保留 `lg:grid-cols-5` 与 `lg:col-span-{n}`，一旦 Tailwind 正常生成类名，仍然优先使用官方工具类；兜底类占位于 CSS Fallback 层，保证最终视觉正确。

## 实施要点
1. 修改 `src/components/UserDashboard.tsx`
   - 容器增加 `dashboard-grid-3-2`。
   - 左右两列添加 `overflow-hidden`。
2. 修改 `src/index.css`
   - 在文件末尾追加对 `dashboard-grid-3-2` 的媒体查询定义。

## 经验 & 建议
- **当 Tailwind JIT 不稳定时，加一层自定义 CSS 兜底**，尤其是关键布局。
- **配合 `overflow-hidden` 控制溢出**，防止内容撑坏栅格。
- **保留 Tailwind 工具类**，方便后续升级 Tailwind 后随时移除兜底。
- 后续升级 Tailwind 版本时，留意该类可否删除；若在新版本中问题消失，可在回归测试后移除兜底规则。

## 回归检查清单
- [ ] 桌面端（≥1024px）左右列均保持 3:2 比例。
- [ ] 右列滚动内容不会撑破栅格。
- [ ] 移动端单列布局未受影响。
- [ ] 深色模式下无视觉回归（使用系统 `dark` toggle 检查）。


