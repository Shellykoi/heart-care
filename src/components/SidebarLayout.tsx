import React, { useState, useEffect } from 'react';
import { Avatar, AvatarFallback } from './ui/avatar';
import { ChevronLeft } from 'lucide-react';
import { cn } from './ui/utils';
import heartImage from '../assets/images/heart.png';

interface SidebarItem {
  id: string;
  label: string;
  icon: any;
  group?: string;
  highlight?: boolean;
}

interface SidebarLayoutProps {
  userInfo?: any;
  onLogout: () => void;
  activeTab: string;
  onTabChange: (tab: string) => void;
  items: SidebarItem[];
  children: any;
  role: 'user' | 'counselor' | 'admin';
}

export function SidebarLayout({ 
  userInfo, 
  onLogout, 
  activeTab, 
  onTabChange, 
  items, 
  children,
  role 
}: SidebarLayoutProps) {
  const [expanded, setExpanded] = useState(true); // 默认展开
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // 关键常量（统一管理）
  const GAP = 24;                       // 左/上/下与页面边缘的统一间距
  const LOGO_SIZE_EXPANDED = 110;       // 展开状态 Logo 尺寸
  const LOGO_SIZE_COLLAPSED = 60;       // 收起状态 Logo 尺寸
  const SIDEBAR_COLLAPSED_BASE = 70;    // 原始收起宽度
  const SIDEBAR_COLLAPSED = Math.max(
    SIDEBAR_COLLAPSED_BASE,
    LOGO_SIZE_COLLAPSED + 10 // 预留左右 padding
  );
  const SIDEBAR_EXPANDED = 180; // 展开宽度（适配更大 Logo）
  const TRANSITION = "transition-all duration-300 ease-in-out";
  const sidebarWidth = expanded ? SIDEBAR_EXPANDED : SIDEBAR_COLLAPSED;
  const mainMarginLeft = GAP + sidebarWidth + GAP;

  // 扁平化所有菜单项（忽略分组）
  const flatItems = items;

  return (
    <div className="relative min-h-screen bg-[var(--bg-page)] flex overflow-hidden">
      {/* ======= 白色胶囊侧边栏 ======= */}
      <aside
        className={cn(
          "fixed z-30 flex flex-col justify-between items-center",
          TRANSITION,
          "shadow-[var(--shadow-soft)]",
          isMobile && "fixed inset-0 z-50 rounded-none"
        )}
        style={{
          top: GAP,
          bottom: GAP,
          left: GAP,
          width: expanded ? SIDEBAR_EXPANDED : SIDEBAR_COLLAPSED,
          paddingTop: expanded ? 80 : 48,
          paddingBottom: 32,
          // 收起时胶囊半圆（高度 = width of internal icon area -> 使用 full 半径）
          borderRadius: expanded ? "60px" : "9999px",
          backgroundColor: "#FFFFFF", // **白色背景**
          border: "1px solid rgba(232,226,219,0.6)", // 轻边线，提升悬浮感
        }}
      >
        {/* 收起按钮（展开时显示） */}
        {!isMobile && (
          <button
            onClick={() => setExpanded((prev) => !prev)}
            className="absolute top-4 right-4 w-8 h-8 rounded-full bg-black/5 flex items-center justify-center hover:bg-black/10 transition-colors"
            aria-label={expanded ? "收起侧边栏" : "展开侧边栏"}
          >
            <ChevronLeft className={cn("w-4 h-4 text-[#222] transition-transform", !expanded && "rotate-180")} />
          </button>
        )}

        {/* 顶部 Logo */}
        <div className="flex flex-col items-center mt-24 gap-4">
          {expanded && (
            <>
              <div className="text-sm font-semibold text-[#222]">南湖心理咨询</div>
              <img
                src={heartImage}
                alt="南湖心理咨询"
                className="object-contain"
                style={{
                  width: LOGO_SIZE_EXPANDED,
                  height: LOGO_SIZE_EXPANDED,
                  maxWidth: 'none',
                  maxHeight: 'none'
                }}
              />
            </>
          )}
          {!expanded && (
            <img
              src={heartImage}
              alt="南湖心理咨询"
              className="object-contain"
              style={{
                width: LOGO_SIZE_COLLAPSED,
                height: LOGO_SIZE_COLLAPSED,
                maxWidth: 'none',
                maxHeight: 'none'
              }}
            />
          )}
        </div>

        {/* 菜单：按垂直均匀排列布局 */}
        <nav className="flex-1 flex flex-col justify-center items-stretch">
          {flatItems.map((item, idx) => {
            const isActive = activeTab === item.id;
            // 每项容器：展开时为整行按钮（padding 加宽），收起时居中。
            return (
              <button
                key={item.id}
                onClick={() => {
                  onTabChange(item.id);
                  if (isMobile) setExpanded(false);
                }}
                className={cn(
                  "flex items-center gap-3 mx-4 my-2 rounded-2xl",
                  TRANSITION,
                  expanded ? "px-3 py-2 justify-start" : "p-2 justify-center"
                )}
                style={{
                  // 选中时整块变黑（宽度占满内容区），未选中时透明
                  backgroundColor: isActive ? "#000000" : "transparent",
                }}
              >
                <div
                  className={cn(
                    "flex items-center justify-center w-10 h-10 rounded-full",
                    "transition-colors duration-200"
                  )}
                  style={{
                    color: isActive ? "#FFD166" : "#666666" // 图标颜色：选中黄、未选灰
                  }}
                >
                  {React.cloneElement(item.icon as any, { className: "w-5 h-5" })}
                </div>

                {/* 仅在展开时显示 label，间距 12px */}
                {expanded && (
                  <span className={cn("text-[14px] transition-colors duration-200",
                    isActive ? "text-white font-semibold" : "text-[#666]"
                  )} style={{ marginLeft: 12 }}>
                    {item.label}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* 底部用户信息 */}
        <div className="flex flex-col items-center mb-8">
          <Avatar className="h-10 w-10 border border-[#e8e2db]">
            <AvatarFallback className="bg-white text-[#222]">
              {userInfo?.nickname?.[0] || userInfo?.username?.[0] || 'U'}
            </AvatarFallback>
          </Avatar>
          {expanded && (
            <>
              <div className="mt-2 text-sm font-medium text-[#222]">{userInfo?.nickname || userInfo?.username || '用户'}</div>
              <div className="text-xs text-[#999]">ID: {userInfo?.id || '—'}</div>
            </>
          )}
        </div>
      </aside>

      {/* ======= 主体内容 ======= */}
      <main
        className={cn(
          "flex-1 min-h-screen bg-[var(--bg-page)] text-[var(--text-primary)] transition-all duration-300 ease-in-out overflow-auto"
        )}
        style={{
          marginLeft: isMobile ? "0px" : `${mainMarginLeft}px`,
          paddingTop: `${GAP}px`,
          paddingBottom: `${GAP}px`,
          paddingLeft: `${GAP * 2}px`,
          paddingRight: `${GAP * 2}px`,
        }}
      >
        {children}
      </main>
    </div>
  );
}
