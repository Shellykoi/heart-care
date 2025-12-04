import React, { useState, useEffect, useMemo , useRef} from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Badge } from './ui/badge';
import { Calendar, Heart, BookOpen, Users, User, BarChart3, Star, CheckCircle } from 'lucide-react';
import { Calendar as CalendarComponent } from './ui/calendar';
import { AppointmentBooking } from './user/AppointmentBooking';
import { ConsultationCalendar } from './user/ConsultationCalendar';
import { PsychTest } from './user/PsychTest';
import { HealthContent } from './user/HealthContent';
import { Community } from './user/Community';
import { UserProfile } from './user/UserProfile';
import { userApi, appointmentApi } from '../services/api';
import { SidebarLayout } from './SidebarLayout';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { toast } from 'sonner';
import IconCompanionHealing from '../assets/images/icon_陪伴疗愈.png';
import IconMeditationHealing from '../assets/images/icon_冥想疗愈.png';
import IconForestHealing from '../assets/images/icon_森林疗愈.png';
import IconSunHealing from '../assets/images/icon_日光疗愈.png';
import IconTeaHealing from '../assets/images/icon_茶道疗愈.png';
import IconMusicHealing from '../assets/images/icon_音乐疗愈.png';
import IconHandmadeHealing from '../assets/images/icon_手作疗愈.png';
import IconArtHealing from '../assets/images/icon_艺术疗愈.png';
import IconWaterHealing from '../assets/images/icon_水域疗愈.png';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';


type AppointmentStatusType = 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'rejected';

const normalizeAppointmentStatus = (status: any): AppointmentStatusType => {
  if (!status) return 'pending';
  if (typeof status === 'string') {
    const normalized = status.toLowerCase().replace(/^appointmentstatus\./, '');
    return ['pending', 'confirmed', 'completed', 'cancelled', 'rejected'].includes(normalized)
      ? (normalized as AppointmentStatusType)
      : 'pending';
  }
  if (typeof status === 'object') {
    if ('value' in status) {
      return normalizeAppointmentStatus((status as { value: any }).value);
    }
    if ('name' in status) {
      return normalizeAppointmentStatus((status as { name: any }).name);
    }
  }
  return 'pending';
};

interface UserDashboardProps {
  onLogout: () => void;
  userInfo?: any;
}

export function UserDashboard({ onLogout, userInfo }: UserDashboardProps) {
  const [activeTab, setActiveTab] = useState('home');
  const [stats, setStats] = useState({
    pending_appointments: 0,
    completed_appointments: 0,
    test_reports: 0,
    favorites: 0
  });
  const [recentAppointments, setRecentAppointments] = useState<any[]>([]);
  const [allAppointments, setAllAppointments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingAppointments, setLoadingAppointments] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState<any>(null);
  const [showAppointmentDialog, setShowAppointmentDialog] = useState(false);
  const [rating, setRating] = useState(0);
  const [review, setReview] = useState('');
  const [consultationActivity, setConsultationActivity] = useState<any>(null);
  const [loadingActivity, setLoadingActivity] = useState(false);
  const [viewMode, setViewMode] = useState<'day' | 'week' | 'month'>('month');
  // 选中的月份（用于月视图时同步日历和统计数据）
  const [selectedYear, setSelectedYear] = useState<number>(() => new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState<number>(() => new Date().getMonth());

  // 获取月份名称
  const getMonthName = (month: number) => {
    const monthNames = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'];
    return monthNames[month];
  };
  
  // 判断选中的月份是否是当前月
  const isSelectedCurrentMonth = useMemo(() => {
    const now = new Date();
    return selectedYear === now.getFullYear() && selectedMonth === now.getMonth();
  }, [selectedYear, selectedMonth]);
  
  const viewModeLabel = viewMode === 'day' 
    ? '今日' 
    : viewMode === 'week' 
      ? '本周' 
      : isSelectedCurrentMonth 
        ? '本月' 
        : `${selectedYear}年${getMonthName(selectedMonth)}`;
  const trendRangeLabel = viewMode === 'day' ? '近7天' : viewMode === 'week' ? '近4周' : '近6月';

  // 计算不同视图下的数据
  const viewData = useMemo(() => {
    if (!consultationActivity) return null;

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    // 日视图：今日数据
    if (viewMode === 'day') {
      const todayStr = today.toISOString().split('T')[0];
      const todayData = consultationActivity.daily_stats?.find((d: any) => d.date === todayStr) || { count: 0, total_duration: 0 };
      const todayHourStats = consultationActivity.hour_stats || [];
      
      // 计算今日总时长（分钟）
      const todayTotalDuration = todayHourStats.reduce((sum: number, h: any) => sum + (h.total_duration || 0), 0);
      const todayAvgDuration = todayData.count > 0 ? Math.round(todayTotalDuration / todayData.count) : 0;
      
      // 近7天趋势（用于迷你图）
      const recent7Days = consultationActivity.daily_stats?.slice(-7) || [];
      
      return {
        totalConsultations: todayData.count,
        totalDuration: todayTotalDuration, // 分钟
        avgDuration: todayAvgDuration, // 分钟
        trendData: recent7Days.map((d: any) => ({ date: d.date, count: d.count })),
        chartData: todayHourStats.map((h: any) => ({
          hour: `${h.hour}:00`,
          count: h.count,
          duration: h.total_duration || 0
        })),
        periodData: consultationActivity.time_period_stats || {},
        durationData: consultationActivity.duration_distribution || {}
      };
    }
    
    // 周视图：本周数据
    if (viewMode === 'week') {
      const weekStart = new Date(today);
      weekStart.setDate(today.getDate() - today.getDay() + 1); // 周一
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekStart.getDate() + 6); // 周日
      
      const weekStats = consultationActivity.daily_stats?.filter((d: any) => {
        const date = new Date(d.date);
        return date >= weekStart && date <= weekEnd;
      }) || [];
      
      const weekTotal = weekStats.reduce((sum: number, d: any) => sum + d.count, 0);
      const weekDuration = weekStats.reduce((sum: number, d: any) => sum + (d.total_duration || 0), 0);
      const weekAvgDuration = weekTotal > 0 ? Math.round(weekDuration / weekTotal) : 0;
      
      // 近4周趋势
      const recent4Weeks = Object.entries(consultationActivity.week_stats || {}).slice(0, 4).reverse();
      
      return {
        totalConsultations: weekTotal,
        totalDuration: Math.round(weekDuration / 60), // 小时
        avgDuration: weekAvgDuration, // 分钟
        trendData: recent4Weeks.map(([week, count]: [string, any]) => ({ week: `第${week}周`, count })),
        chartData: weekStats.map((d: any) => ({
          date: new Date(d.date).getDate() + '日',
          count: d.count,
          duration: d.total_duration || 0
        })),
        periodData: consultationActivity.time_period_stats || {},
        durationData: consultationActivity.duration_distribution || {}
      };
    }
    
    // 月视图：使用选中的月份数据
    if (viewMode === 'month') {
      const monthStart = new Date(selectedYear, selectedMonth, 1);
      const monthEnd = new Date(selectedYear, selectedMonth + 1, 0);
      
      const monthStats = consultationActivity.daily_stats?.filter((d: any) => {
        const date = new Date(d.date);
        return date >= monthStart && date <= monthEnd;
      }) || [];
      
      const monthTotal = monthStats.reduce((sum: number, d: any) => sum + d.count, 0);
      const monthDuration = monthStats.reduce((sum: number, d: any) => sum + (d.total_duration || 0), 0);
      const monthAvgDuration = monthTotal > 0 ? Math.round(monthDuration / monthTotal) : 0;
      
      // 近6月趋势（简化：使用最近30天数据）
      const recent30Days = consultationActivity.daily_stats?.slice(-30) || [];
      
      return {
        totalConsultations: monthTotal,
        totalDuration: Math.round(monthDuration / 60), // 小时
        avgDuration: monthAvgDuration, // 分钟
        trendData: recent30Days.map((d: any) => ({ date: d.date, count: d.count })),
        chartData: monthStats.map((d: any) => ({
          date: new Date(d.date).getDate() + '日',
          count: d.count,
          duration: d.total_duration || 0
        })),
        periodData: consultationActivity.time_period_stats || {},
        durationData: consultationActivity.duration_distribution || {}
      };
    }
    
    return null;
  }, [consultationActivity, viewMode, selectedYear, selectedMonth]);

  const trendSummaryText = useMemo(() => {
    if (!viewData || !Array.isArray(viewData.trendData) || viewData.trendData.length === 0) {
      return '暂无趋势数据';
    }
    const peak = viewData.trendData.reduce(
      (max: number, item: any) => Math.max(max, item?.count || 0),
      0
    );
    const latest = viewData.trendData[viewData.trendData.length - 1]?.count ?? 0;
    return `${trendRangeLabel}峰值 ${peak} 次，最近 ${latest} 次`;
  }, [trendRangeLabel, viewData]);

  const resolvedChartData = useMemo(() => {
    if (!viewData) return [];

    const normalizeEntry = (entry: any) => {
      const label =
        viewMode === 'day'
          ? entry.hour ?? entry.label ?? entry.date ?? ''
          : viewMode === 'week'
            ? entry.date ?? entry.label ?? entry.week ?? ''
            : entry.date ?? entry.label ?? '';

      return {
        label,
        count: Number(entry.count ?? 0),
        duration: Number(entry.duration ?? entry.total_duration ?? 0),
      };
    };

    const baseData = Array.isArray(viewData.chartData)
      ? viewData.chartData.filter((item: any) => item)
      : [];

    if (baseData.length > 0) {
      return baseData.map(normalizeEntry);
    }

    const fallbackSource = Array.isArray(consultationActivity?.daily_stats)
      ? consultationActivity.daily_stats
      : [];

    if (fallbackSource.length === 0) {
      return [];
    }

    const fallbackRange =
      viewMode === 'day' ? 7 : viewMode === 'week' ? 14 : 30;

    return fallbackSource
      .slice(-fallbackRange)
      .map((item: any) => ({
        label: item.date ? item.date.slice(5) : '',
        count: Number(item.count ?? 0),
        duration: Number(item.total_duration ?? 0),
      }));
  }, [consultationActivity, viewData, viewMode]);

  const hasChartData = resolvedChartData.length > 0;
  const chartTitle =
    viewMode === 'day'
      ? '今日咨询热度'
      : viewMode === 'week'
        ? '本周咨询趋势'
        : '近月咨询趋势';
  const chartSubtitle =
    viewMode === 'day'
      ? '按小时查看今日咨询活跃度'
      : viewMode === 'week'
        ? '每日咨询次数与时长'
        : '按日展示最近咨询趋势';

  const ChartTooltipContent = ({ active, payload }: any) => {
    if (!active || !payload || payload.length === 0) {
      return null;
    }

    const dataPoint = payload[0]?.payload;
    if (!dataPoint) return null;

    const durationDisplay =
      dataPoint.duration && dataPoint.duration > 0
        ? `总时长 ${Math.round(dataPoint.duration)} 分钟`
        : null;

    return (
      <div className="rounded-xl bg-white/95 backdrop-blur px-3 py-2 shadow-lg border border-[#E9E4DD]">
        <p className="text-xs text-[#A19C92]">{dataPoint.label || '未知'}</p>
        <p className="text-sm font-semibold text-[#1F1B18] mt-1">
          {dataPoint.count} 次咨询
        </p>
        {durationDisplay && (
          <p className="text-xs text-[#6B6B6B] mt-1">{durationDisplay}</p>
        )}
      </div>
    );
  };

  useEffect(() => {
    loadStats();
    loadAppointments();
    loadConsultationActivity();
  }, []);

  // 当切换到"我的预约"标签页时，重新加载数据
  useEffect(() => {
    if (activeTab === 'my-appointments') {
      loadAppointments();
    }
  }, [activeTab]);

  // 统一的错误处理函数
  const handleError = (error: any, defaultMessage: string) => {
    // 使用 JSON.stringify 序列化错误对象，方便调试
    try {
      const errorInfo = {
        message: error?.message,
        detail: error?.detail,
        code: error?.code,
        status: error?.status || error?.response?.status,
        isNetworkError: error?.isNetworkError,
        response: error?.response ? {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data
        } : undefined
      };
      console.error(`${defaultMessage} - 错误详情:`, JSON.stringify(errorInfo, null, 2));
    } catch (e) {
      console.error(`${defaultMessage} - 错误对象:`, error);
    }
    
    // 提取错误消息
    let errorMessage = defaultMessage;
    let errorDescription = '请检查网络连接或稍后重试';
    
    if (error?.isNetworkError || error?.code === 'NETWORK_ERROR' || error?.code === 'ECONNABORTED' || error?.code === 'ERR_NETWORK') {
      // 网络错误
      if (error?.detail) {
        errorMessage = typeof error.detail === 'string' ? error.detail : '网络连接失败';
        errorDescription = typeof error.detail === 'string' && error.detail.length > 50 
          ? error.detail 
          : '无法连接到后端服务，请检查后端服务是否已启动';
      } else if (error?.message) {
        errorMessage = error.message;
      }
    } else if (error?.detail) {
      // 后端返回的错误
      if (typeof error.detail === 'string') {
        errorMessage = error.detail;
      } else if (Array.isArray(error.detail) && error.detail.length > 0) {
        errorMessage = error.detail[0]?.msg || String(error.detail[0]);
      }
    } else if (error?.message) {
      errorMessage = error.message;
    } else if (error?.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    
    // 如果是401错误，说明Token过期，不需要显示错误提示（api.ts会处理跳转）
    if (error?.response?.status !== 401 && error?.status !== 401) {
      toast.error(errorMessage, {
        description: errorDescription,
        duration: 5000,
      });
    }
  };

  const loadStats = async () => {
    try {
      const data = await userApi.getStats();
      setStats(data);
    } catch (error: any) {
      handleError(error, '获取统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  const loadConsultationActivity = async () => {
    try {
      setLoadingActivity(true);
      const data = await userApi.getConsultationActivity();
      console.log('[UserDashboard] 咨询活动数据:', data);
      setConsultationActivity(data);
    } catch (error: any) {
      handleError(error, '获取咨询活动数据失败');
      // 即使出错也设置为null，避免显示旧数据
      setConsultationActivity(null);
    } finally {
      setLoadingActivity(false);
    }
  };

  const loadAppointments = async () => {
    try {
      setLoadingAppointments(true);
      console.log('[UserDashboard] 开始加载预约列表...');
      const data = await appointmentApi.getMyAppointments();
      console.log('[UserDashboard] 预约列表数据:', data);
      
      // 确保数据是数组，并规范化状态字段
      const appointments = (Array.isArray(data) ? data : []).map((appointment: any) => ({
        ...appointment,
        status: normalizeAppointmentStatus(appointment?.status),
      }));
      console.log('[UserDashboard] 处理后的预约数量:', appointments.length);
      
      // 过滤预约：显示"待确认"、"已确认"和"已完成"的预约
      // "已完成"包括：状态为completed，或者状态为confirmed且双方都已确认完成
      // "已确认"包括：状态为confirmed但双方还未都确认完成
      const filteredAppointments = appointments.filter((appointment: any) => {
        // 待确认
        if (appointment.status === 'pending') {
          return true;
        }
        // 已确认（状态为confirmed，无论是否双方都确认完成）
        if (appointment.status === 'confirmed') {
          return true;
        }
        // 已完成（状态为completed）
        if (appointment.status === 'completed') {
          return true;
        }
        // 其他状态（已取消、已拒绝等）不显示
        return false;
      });
      
      console.log('[UserDashboard] 过滤后的预约数量:', filteredAppointments.length);
      
      setRecentAppointments(filteredAppointments.slice(0, 5));
      setAllAppointments(filteredAppointments);
      
      if (appointments.length === 0) {
        console.warn('[UserDashboard] 预约列表为空');
      }
    } catch (error: any) {
      handleError(error, '获取预约列表失败');
      
      // 即使出错也设置为空数组，避免显示旧数据
      setRecentAppointments([]);
      setAllAppointments([]);
    } finally {
      setLoadingAppointments(false);
    }
  };

  const handleConfirmComplete = async (appointmentId: number) => {
    try {
      await appointmentApi.update(appointmentId, { user_confirmed_complete: true });
      toast.success('您已确认咨询结束，等待咨询师确认');
      loadAppointments();
      loadStats();
    } catch (error: any) {
      console.error('确认完成失败:', error);
      toast.error(error?.detail || error?.message || '操作失败，请重试');
    }
  };

  const handleSubmitRating = async (appointmentId: number) => {
    if (rating === 0) {
      toast.error('请选择评分');
      return;
    }
    try {
      await appointmentApi.update(appointmentId, { 
        rating, 
        review: review.trim() || undefined 
      });
      toast.success('评分提交成功');
      setShowAppointmentDialog(false);
      setRating(0);
      setReview('');
      loadAppointments();
      loadStats();
    } catch (error: any) {
      console.error('提交评分失败:', error);
      toast.error(error?.detail || error?.message || '提交失败，请重试');
    }
  };

  const openAppointmentDialog = (appointment: any) => {
    setSelectedAppointment({
      ...appointment,
      status: normalizeAppointmentStatus(appointment?.status),
    });
    setRating(appointment.rating || 0);
    setReview(appointment.review || '');
    setShowAppointmentDialog(true);
  };

  const sidebarItems = [
    { id: 'home', label: '首页', icon: <Heart className="w-4 h-4" />, group: '用户中心' },
    { id: 'appointment', label: '预约咨询', icon: <Calendar className="w-4 h-4" />, group: '咨询服务', highlight: true },
    { id: 'my-appointments', label: '我的预约', icon: <Calendar className="w-4 h-4" />, group: '咨询服务' },
    { id: 'test', label: '心理测评', icon: <BarChart3 className="w-4 h-4" />, group: '咨询服务' },
    { id: 'content', label: '健康科普', icon: <BookOpen className="w-4 h-4" />, group: '咨询服务' },
    { id: 'community', label: '互助社区', icon: <Users className="w-4 h-4" />, group: '咨询服务' },
    { id: 'profile', label: '个人中心', icon: <User className="w-4 h-4" />, group: '个人中心' },
  ];

  const displayName = userInfo?.nickname || userInfo?.username || '用户';

  /**
   * ========= 仪表盘视觉配置 =========
   * 以下数据用于统一控制首页四个核心概览卡片（待确认预约、已完成咨询、测评报告、收藏文章）的风格。
   * 如果后续需要调整颜色、阴影或圆角，只要修改这里的类名即可，不需要到 JSX 中逐个寻找。
   */
  const quickStatsCards = [
    {
      key: 'pending',
      title: '待确认预约',
      value: loading ? '...' : stats.pending_appointments,
      hint: '等待确认中',
      iconSrc: IconCompanionHealing,
      wrapperClass: 'bg-gradient-to-br from-[#FFF8ED] via-[#FFEED9] to-[#FFE1BC] text-[#4E3924]',
      iconWrapperClass: 'bg-white/70 text-[#B0752A]',
    },
    {
      key: 'completed',
      title: '已完成咨询',
      value: loading ? '...' : stats.completed_appointments,
      hint: '已完成咨询',
      iconSrc: IconMusicHealing,
      wrapperClass: 'bg-gradient-to-br from-[#F2FFF5] via-[#E4FBEA] to-[#C9F1D3] text-[#27412F]',
      iconWrapperClass: 'bg-white/70 text-[#2C8A4C]',
    },
    {
      key: 'reports',
      title: '测评报告',
      value: loading ? '...' : stats.test_reports,
      hint: '查看报告',
      iconSrc: IconArtHealing,
      wrapperClass: 'bg-gradient-to-br from-[#F6F6FF] via-[#ECECFE] to-[#D8D6FF] text-[#2F2D59]',
      iconWrapperClass: 'bg-white/70 text-[#4B49A3]',
    },
    {
      key: 'favorites',
      title: '收藏文章',
      value: loading ? '...' : stats.favorites,
      hint: '已收藏内容',
      iconSrc: IconTeaHealing,
      wrapperClass: 'bg-gradient-to-br from-[#FFF3F6] via-[#FFE3EB] to-[#FFC8D9] text-[#5B2635]',
      iconWrapperClass: 'bg-white/70 text-[#C74668]',
    },
  ];

  const recommendedIcons = [
    IconTeaHealing,
    IconMusicHealing,
    IconSunHealing,
    IconHandmadeHealing,
    IconForestHealing,
    IconWaterHealing,
  ];
  const tabMeta: { [key: string]: { title: string; subtitle?: string; description?: string } } = {
    home: {
      title: '首页',
      subtitle: `Hi，${displayName}`,
      description: '欢迎回到你的心理健康中心'
    },
    appointment: {
      title: '预约咨询',
      subtitle: `Hi，${displayName}`,
      description: '挑选合适的咨询师，开启新的对话'
    },
    'my-appointments': {
      title: '我的预约',
      subtitle: `Hi，${displayName}`,
      description: '查看并管理你的咨询安排'
    },
    test: {
      title: '心理测评',
      subtitle: `Hi，${displayName}`,
      description: '通过测评了解自己当前的心理状态'
    },
    content: {
      title: '健康科普',
      subtitle: `Hi，${displayName}`,
      description: '精选心理健康文章，陪你一起成长'
    },
    community: {
      title: '互助社区',
      subtitle: `Hi，${displayName}`,
      description: '和同路人分享、倾听与支持'
    },
    profile: {
      title: '个人中心',
      subtitle: `Hi，${displayName}`,
      description: '完善你的个人信息与偏好'
    }
  };

  const currentTabMeta = tabMeta[activeTab] || {
    title: '用户中心',
    subtitle: `Hi，${displayName}`
  };

  const FloatingEye = () => {
  const eyeRef = useRef<HTMLDivElement>(null);
  const pupilRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      const eye = eyeRef.current;
      const pupil = pupilRef.current;
      if (!eye || !pupil) return;

      const rect = eye.getBoundingClientRect();
      const angle = Math.atan2(
        event.clientY - (rect.top + rect.height / 2),
        event.clientX - (rect.left + rect.width / 2)
      );
      const distance = Math.min(rect.width * 0.2, 12);
      pupil.style.transform = `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px)`;
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="pointer-events-none fixed right-6 bottom-8 z-50">
      <div className="flex h-14 w-14 items-center justify-center rounded-full border border-[#E0DAD1] bg-gradient-to-br from-[#FFF8EF] to-[#F4E6D6] shadow-[0_12px_28px_rgba(32,26,20,0.18)]">
        <div
          ref={eyeRef}
          className="relative flex h-11 w-11 items-center justify-center rounded-full border border-[#D9C8B5] bg-gradient-to-br from-[#F6E4CE] to-[#E9CFB0]"
        >
          <span
            ref={pupilRef}
            className="h-4 w-4 rounded-full bg-[#2D1A12] ring-4 ring-[#F9E7D0] transition-transform duration-75 ease-out"
          />
          <span className="pointer-events-none absolute left-1/2 top-1/3 h-2 w-2 -translate-x-1/2 rounded-full bg-white/80" />
        </div>
      </div>
    </div>
  );
};


  return (
    <SidebarLayout
      userInfo={userInfo}
      onLogout={onLogout}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      items={sidebarItems}
      role="user"
      children={
        <>
        <FloatingEye />
          <div className="mb-10">
            <div className="flex flex-col gap-1 text-left">
              {currentTabMeta.subtitle && (
                <span className="text-sm text-[#8C8579]">
                  {currentTabMeta.subtitle}
                </span>
              )}
              <h1 className="text-3xl font-semibold text-[#1D1A18] tracking-tight">
                {currentTabMeta.title}
              </h1>
              {currentTabMeta.description && (
                <span className="text-sm text-[#A3998B]">
                  {currentTabMeta.description}
                </span>
              )}
            </div>
          </div>
          {activeTab === 'home' && (
            <div className="space-y-8 pb-8">
              {/* Quick Stats - 顶部概览区 - 更紧凑的布局 */}
              <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
                {quickStatsCards.map((card) => (
                  <Card
                    key={card.key}
                    className={`${card.wrapperClass} border-none rounded-[20px] shadow-[0_14px_32px_rgba(24,20,17,0.28)] transition-transform duration-200 hover:-translate-y-1 md:min-h-[180px]`}
                  >
                    <CardContent className="flex h-full flex-col justify-between gap-4 p-6 md:p-7">
                      <div className="flex items-center justify-between gap-4 pr-1">
                        <div className="space-y-1">
                          <p className="text-xs font-medium uppercase tracking-[0.12em] opacity-75">
                            {card.title}
                          </p>
                          <p className="text-3xl font-semibold leading-tight">
                            {card.value}
                          </p>
                        </div>
                        <div
                          className={`${card.iconWrapperClass} flex items-center justify-center rounded-2xl p-3.5 shadow-inner`}
                        >
                          <img
                            src={card.iconSrc}
                            alt={card.title}
                            className="h-10 w-10 object-contain md:h-12 md:w-12"
                          />
                        </div>
                      </div>
                      <p className="text-xs font-medium opacity-70">
                        {card.hint}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* 咨询统计 - 时间和咨询时间数据看板 - 采用设计稿风格 */}
              <Card className="bg-[var(--card-dark)] border border-[#2D2D31] rounded-[24px] shadow-[0_6px_20px_rgba(0,0,0,0.08)] overflow-hidden text-[var(--text-on-dark)]">
                <CardHeader className="px-8 pt-6 pb-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-base font-semibold text-[var(--text-on-dark)] flex items-center gap-2">
                        <img src={IconMeditationHealing} alt="咨询统计" className="w-6 h-6 object-contain" />
                        咨询统计
                      </CardTitle>
                      <CardDescription className="text-sm text-[#B1ADA6]">时间和咨询时间数据看板 - 记录我的活动</CardDescription>
                    </div>
                    {/* 视图切换按钮 */}
                    <div className="flex items-center gap-2 p-1 rounded-2xl bg-[#2D2D31]/80">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setViewMode('day')}
                        className={`rounded-2xl px-3 py-1 text-xs font-medium transition-colors ${viewMode === 'day' ? 'bg-[var(--highlight)] text-[var(--text-primary)] shadow-[var(--shadow-soft)]' : 'text-[#B1ADA6]'}`}
                      >
                        <img src={IconSunHealing} alt="日视图" className="w-4 h-4 mr-1 object-contain" />
                        日
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setViewMode('week')}
                        className={`rounded-2xl px-3 py-1 text-xs font-medium transition-colors ${viewMode === 'week' ? 'bg-[var(--highlight)] text-[var(--text-primary)] shadow-[var(--shadow-soft)]' : 'text-[#B1ADA6]'}`}
                      >
                        <img src={IconForestHealing} alt="周视图" className="w-4 h-4 mr-1 object-contain" />
                        周
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setViewMode('month')}
                        className={`rounded-2xl px-3 py-1 text-xs font-medium transition-colors ${viewMode === 'month' ? 'bg-[var(--highlight)] text-[var(--text-primary)] shadow-[var(--shadow-soft)]' : 'text-[#B1ADA6]'}`}
                      >
                        <img src={IconWaterHealing} alt="月视图" className="w-4 h-4 mr-1 object-contain" />
                        月
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="px-8 pt-0 pb-6">
                {loadingActivity ? (
                  <div className="h-64 flex items-center justify-center text-[#B1ADA6]">
                    <div className="text-center">
                      <img src={IconMeditationHealing} alt="加载中" className="w-12 h-12 mx-auto mb-2 animate-pulse opacity-80 object-contain" />
                      <p className="text-sm">加载中...</p>
                    </div>
                  </div>
                ) : consultationActivity && viewData ? (
                  <div className="grid grid-cols-1 gap-6 items-stretch lg:grid-cols-5 w-full max-w-none dashboard-grid-3-2">
                    {/* 左侧：日历模块，占 3/5 */}
                    <div className="min-w-0 w-full overflow-hidden lg:col-span-3">
                      <div className="h-full bg-white rounded-2xl shadow-sm p-4 w-full min-h-[220px]">
                        <ConsultationCalendar
                          appointments={allAppointments}
                          loading={loadingAppointments}
                          onMonthChange={(year, month) => {
                            setSelectedYear(year);
                            setSelectedMonth(month);
                          }}
                        />
                      </div>
                    </div>

                    {/* 右侧：图表 + 数据看板，占 2/5 */}
                    <div className="min-w-0 w-full overflow-hidden lg:col-span-2 flex flex-col gap-4">
                      <Card className="bg-white border border-[#F1EFEA] shadow-sm h-full w-full">
                        <CardContent className="p-6 flex h-full flex-col">
                          <div className="flex items-start justify-between">
                            <div>
                              <CardDescription className="text-sm text-[#6B6B6B]">{chartTitle}</CardDescription>
                              <p className="text-xs text-[#A19C92] mt-1">{chartSubtitle}</p>
                            </div>
                            <Badge variant="outline" className="rounded-lg border-[#E6E2DC] text-xs text-[#6B6B6B] bg-[#FFFAF3]">
                              {viewMode === 'day' ? '日视图' : viewMode === 'week' ? '周视图' : '月视图'}
                            </Badge>
                          </div>
                          <div className="mt-5 flex-1 min-h-[220px]">
                            {hasChartData ? (
                              <ResponsiveContainer width="100%" height={220}>
                                <AreaChart
                                  data={resolvedChartData}
                                  margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
                                >
                                  <defs>
                                    <linearGradient id="colorConsultations" x1="0" y1="0" x2="0" y2="1">
                                      <stop offset="5%" stopColor="#F97316" stopOpacity={0.35} />
                                      <stop offset="95%" stopColor="#F97316" stopOpacity={0.05} />
                                    </linearGradient>
                                  </defs>
                                  <CartesianGrid strokeDasharray="3 3" stroke="#F2EDE5" vertical={false} />
                                  <XAxis
                                    dataKey="label"
                                    tickLine={false}
                                    axisLine={false}
                                    tick={{ fill: '#A19C92', fontSize: 12 }}
                                  />
                                  <YAxis
                                    tickLine={false}
                                    axisLine={false}
                                    allowDecimals={false}
                                    width={36}
                                    tick={{ fill: '#A19C92', fontSize: 12 }}
                                  />
                                  <Tooltip cursor={{ stroke: '#F97316', strokeOpacity: 0.15 }} content={<ChartTooltipContent />} />
                                  <Area
                                    type="monotone"
                                    dataKey="count"
                                    stroke="#F97316"
                                    strokeWidth={2}
                                    fill="url(#colorConsultations)"
                                    activeDot={{ r: 5 }}
                                  />
                                </AreaChart>
                              </ResponsiveContainer>
                            ) : (
                              <div className="h-full min-h-[160px] flex flex-col items-center justify-center text-[#A19C92] text-sm">
                                <img src={IconHandmadeHealing} alt="暂无图表数据" className="w-10 h-10 mb-3 opacity-80 object-contain" />
                                暂无图表数据
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>

                      <div className="grid grid-cols-2 gap-4 md:gap-6">
                        {/* 总咨询次数 */}
                        <Card className="bg-white border border-[#F1EFEA] shadow-sm">
                          <CardContent className="flex h-full flex-col gap-5 p-5 md:p-6">
                            <div className="flex items-center justify-between">
                              <CardDescription className="text-sm font-medium text-[#4A463F]">总咨询次数</CardDescription>
                              <Badge variant="outline" className="rounded-full px-3 py-1 text-xs text-[#6B6B6B] border-[#E6E2DC] bg-[#FFFAF3]">
                                {viewMode === 'day' ? '日视图' : viewMode === 'week' ? '周视图' : '月视图'}
                              </Badge>
                            </div>
                            <div className="flex items-baseline justify-center gap-2 text-[#1F1B18]">
                              <span className="text-sm text-[#A19C92]">{viewModeLabel}</span>
                              <span className="text-4xl font-semibold leading-none">
                                {viewData.totalConsultations}
                              </span>
                              <span className="text-sm text-[#A19C92]">次咨询</span>
                            </div>
                          </CardContent>
                        </Card>

                        {/* 总咨询时长 */}
                        <Card className="bg-white border border-[#F1EFEA] shadow-sm">
                          <CardContent className="flex h-full flex-col gap-5 p-5 md:p-6">
                            <div className="flex items-center justify-between">
                              <CardDescription className="text-sm font-medium text-[#4A463F]">总咨询时长</CardDescription>
                              <Badge variant="outline" className="rounded-full px-3 py-1 text-xs text-[#6B6B6B] border-[#E6E2DC] bg-[#FFFAF3]">
                                {viewMode === 'day' ? '日视图' : viewMode === 'week' ? '周视图' : '月视图'}
                              </Badge>
                            </div>
                            <div className="flex items-baseline justify-center gap-2 text-[#1F1B18]">
                              <span className="text-sm text-[#A19C92]">{viewModeLabel}</span>
                              <span className="text-4xl font-semibold leading-none">
                                {viewData.totalDuration}
                              </span>
                              <span className="text-sm text-[#A19C92]">
                                {viewMode === 'day' ? '分钟' : '小时'}
                              </span>
                            </div>
                            <p className="text-xs text-center text-[#A19C92]">总时长</p>
                          </CardContent>
                        </Card>

                        {/* 平均时长 */}
                        <Card className="bg-white border border-[#F1EFEA] shadow-sm">
                          <CardContent className="flex h-full flex-col gap-5 p-5 md:p-6">
                            <div className="flex items-center justify-between">
                              <CardDescription className="text-sm font-medium text-[#4A463F]">平均时长</CardDescription>
                              <Badge variant="outline" className="rounded-full px-3 py-1 text-xs text-[#6B6B6B] border-[#E6E2DC] bg-[#FFFAF3]">
                                {viewMode === 'day' ? '日视图' : viewMode === 'week' ? '周视图' : '月视图'}
                              </Badge>
                            </div>
                            <div className="flex items-baseline justify-center gap-2 text-[#1F1B18]">
                              <span className="text-sm text-[#A19C92]">{viewModeLabel}</span>
                              <span className="text-4xl font-semibold leading-none">
                                {viewData.avgDuration}
                              </span>
                              <span className="text-sm text-[#A19C92]">分钟</span>
                            </div>
                            <p className="text-xs text-center text-[#A19C92]">单次平均</p>
                          </CardContent>
                        </Card>

                        {/* 趋势概览 */}
                        <Card className="bg-white border border-[#F1EFEA] shadow-sm">
                          <CardContent className="flex h-full flex-col gap-3 p-5 md:p-6">
                            <div className="flex items-center justify-between">
                              <CardDescription className="text-sm font-medium text-[#4A463F]">近期趋势</CardDescription>
                              <Badge variant="outline" className="rounded-full px-3 py-1 text-xs text-[#6B6B6B] border-[#E6E2DC] bg-[#FFFAF3]">
                                {trendRangeLabel}
                              </Badge>
                            </div>
                            <p className="mt-1 text-sm text-[#57534E] leading-relaxed text-center">
                              {trendSummaryText}
                            </p>
                            <div className="mt-2 flex items-center justify-center">
                              <img src={IconSunHealing} alt="趋势" className="h-8 w-8 object-contain" />
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-[#B1ADA6]">
                    <div className="text-center">
                      <img src={IconHandmadeHealing} alt="暂无数据" className="w-14 h-14 mx-auto mb-2 object-contain opacity-90" />
                      <p className="text-sm">暂无数据</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 我的预约 */}
            <Card className="bg-[var(--card-white)] border border-[var(--border)] rounded-[24px] shadow-[var(--shadow-soft)]">
              <CardHeader className="px-8 pt-8 pb-6">
                <CardTitle className="text-base font-semibold text-[var(--text-primary)] flex items-center gap-2">
                  <img src={IconCompanionHealing} alt="我的预约" className="w-6 h-6 object-contain" />
                  我的预约
                </CardTitle>
                <CardDescription className="text-sm text-[var(--text-secondary)]">最近的咨询预约记录</CardDescription>
              </CardHeader>
              <CardContent className="px-8 pb-8">
                {recentAppointments.length === 0 ? (
                  <div className="text-center py-8 text-[var(--text-secondary)]">
                    <p>暂无预约记录</p>
                    <p className="text-sm mt-2">前往"预约咨询"页面创建您的第一个预约</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto pb-4 -mx-2 px-2">
                    <div className="flex gap-4 min-w-max">
                      {recentAppointments.map((appointment: any) => {
                        let statusText = '待确认';
                        let statusColor = 'bg-blue-100 text-blue-700';
                        if (appointment.status === 'pending') {
                          statusText = '待确认';
                          statusColor = 'bg-blue-100 text-blue-700';
                        } else if (appointment.status === 'confirmed') {
                          if (appointment.user_confirmed_complete === true &&
                              appointment.counselor_confirmed_complete === true) {
                            statusText = '已完成';
                            statusColor = 'bg-green-100 text-green-700';
                          } else {
                            statusText = '已确认';
                            statusColor = 'bg-yellow-100 text-yellow-700';
                          }
                        } else if (appointment.status === 'completed') {
                          statusText = '已完成';
                          statusColor = 'bg-green-100 text-green-700';
                        } else {
                          statusText = appointment.status;
                        }

                        const appointmentDate = new Date(appointment.appointment_date);
                        const formattedDate = `${appointmentDate.getFullYear()}-${String(appointmentDate.getMonth() + 1).padStart(2, '0')}-${String(appointmentDate.getDate()).padStart(2, '0')} ${String(appointmentDate.getHours()).padStart(2, '0')}:${String(appointmentDate.getMinutes()).padStart(2, '0')}`;

                        return (
                          <Card
                            key={appointment.id}
                            className="w-80 flex-shrink-0 bg-[var(--card-white)] border border-[var(--border)] rounded-[24px] shadow-[var(--shadow-soft)] hover:shadow-[0_8px_24px_rgba(0,0,0,0.08)] transition-transform duration-300 hover:-translate-y-1 cursor-pointer"
                            onClick={() => openAppointmentDialog(appointment)}
                          >
                            <CardContent className="pt-8 px-8 pb-8">
                              <div className="flex items-start gap-4 mb-4">
                                <Avatar className="h-12 w-12 border-2 border-[#E9E4DD]">
                                  <AvatarFallback className="bg-[#FFEDD5] text-[var(--highlight)]">
                                    {appointment.counselor?.real_name?.[0] || 'C'}
                                  </AvatarFallback>
                                </Avatar>
                                <div className="flex-1">
                                  <p className="font-semibold text-base text-[var(--text-primary)] mb-1">{appointment.counselor?.real_name || '咨询师'}</p>
                                  <p className="text-sm text-[var(--text-secondary)]">{appointment.consult_type || '咨询'}</p>
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                                  <img src={IconForestHealing} alt="预约时间" className="w-5 h-5 object-contain" />
                                  <span>{formattedDate}</span>
                                </div>
                                <Badge className={statusColor}>{statusText}</Badge>
                              </div>
                            </CardContent>
                          </Card>
                        );
                      })}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 为你推荐 */}
            <Card className="bg-[var(--card-white)] border border-[var(--border)] rounded-[24px] shadow-[var(--shadow-soft)]">
              <CardHeader className="px-8 pt-6 pb-4">
                <CardTitle className="text-base font-semibold text-[var(--text-primary)] flex items-center gap-2">
                  <img src={IconArtHealing} alt="为你推荐" className="w-6 h-6 object-contain" />
                  为你推荐
                </CardTitle>
                <CardDescription className="text-sm text-[var(--text-secondary)]">基于你的关注内容推荐</CardDescription>
              </CardHeader>
              <CardContent className="px-8 pb-8">
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {[
                    { title: '如何应对考前焦虑', type: '文章', reads: '1.2k', tags: ['学业压力', '焦虑'] },
                    { title: '深呼吸放松技巧', type: '视频', reads: '856', tags: ['放松', '技巧'] },
                    { title: '改善睡眠质量的方法', type: '音频', reads: '2.3k', tags: ['睡眠', '健康'] },
                    { title: '情绪管理的五个步骤', type: '文章', reads: '3.1k', tags: ['情绪', '管理'] },
                    { title: '建立健康的人际关系', type: '视频', reads: '1.8k', tags: ['人际关系', '社交'] },
                    { title: '压力释放的有效途径', type: '文章', reads: '2.5k', tags: ['压力', '释放'] },
                  ].map((content, index) => {
                    const iconSrc = recommendedIcons[index % recommendedIcons.length];
                    return (
                      <div
                        key={index}
                        className="bg-[#FFEDD5] border border-[var(--border)] rounded-[16px] p-6 transition-transform duration-300 hover:-translate-y-1 hover:shadow-[0_8px_24px_rgba(0,0,0,0.08)]"
                      >
                        <div className="flex justify-between items-start">
                          <Badge className="bg-white/70 text-[var(--text-primary)] flex items-center gap-2">
                            <img src={iconSrc} alt={`${content.title} 图标`} className="w-6 h-6 object-contain" />
                            {content.type}
                          </Badge>
                          <span className="text-xs text-[var(--text-secondary)]">{content.reads} 阅读</span>
                        </div>
                        <h4 className="font-semibold text-[var(--text-primary)] mt-4 leading-snug">{content.title}</h4>
                        <div className="mt-4 flex gap-2 flex-wrap">
                          {content.tags.map((tag, tagIndex) => (
                            <Badge key={tagIndex} className="bg-white/60 text-[var(--text-primary)] flex items-center gap-1">
                              <img src={recommendedIcons[(index + tagIndex) % recommendedIcons.length]} alt={`${tag} 图标`} className="w-4 h-4 object-contain" />
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
        </div>
      )}

      {activeTab === 'appointment' && <AppointmentBooking />}
      {activeTab === 'my-appointments' && (
        <div className="space-y-6">
          <Card className="bg-[var(--card-white)] border border-[var(--border)] rounded-[24px] shadow-[var(--shadow-soft)]">
            <CardHeader className="px-8 pt-8 pb-6">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-base font-semibold text-[#222222] mb-1 flex items-center gap-2">
                    <img src={IconForestHealing} alt="我的预约" className="w-6 h-6 object-contain" />
                    我的预约
                  </CardTitle>
                  <CardDescription className="text-sm text-[#666666]">查看和管理您的所有预约</CardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => loadAppointments()}
                  disabled={loadingAppointments}
                  className="rounded-xl border-[#E8E2DB] hover:bg-gray-50"
                >
                  {loadingAppointments ? '加载中...' : '刷新'}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="px-8 pb-8">
              {loadingAppointments ? (
                <div className="text-center py-8 text-[#666666]">
                  <p>加载中...</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>咨询师</TableHead>
                      <TableHead>咨询类型</TableHead>
                      <TableHead>预约时间</TableHead>
                      <TableHead>状态</TableHead>
                      <TableHead>操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {allAppointments.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center py-8 text-[#666666]">
                          <div className="space-y-2">
                            <p>暂无预约记录</p>
                            <p className="text-sm">前往"预约咨询"页面创建您的第一个预约</p>
                          </div>
                        </TableCell>
                      </TableRow>
                    ) : (
                      allAppointments.map((appointment: any) => {
                      // 判断状态：如果状态为confirmed且双方都已确认完成，则显示为"已完成"
                      // 如果状态为confirmed但双方还未都确认完成，则显示为"已确认"
                      let statusText = '待确认';
                      if (appointment.status === 'pending') {
                        statusText = '待确认';
                      } else if (appointment.status === 'confirmed') {
                        // 已确认状态：检查是否双方都已确认完成
                        if (appointment.user_confirmed_complete === true && 
                            appointment.counselor_confirmed_complete === true) {
                          statusText = '已完成';
                        } else {
                          statusText = '已确认';
                        }
                      } else if (appointment.status === 'completed') {
                        statusText = '已完成';
                      } else {
                        statusText = appointment.status;
                      }
                      const appointmentDate = new Date(appointment.appointment_date);
                      const formattedDate = appointmentDate.toLocaleString('zh-CN');
                      
                      return (
                        <TableRow key={appointment.id}>
                          <TableCell className="font-medium">
                            {appointment.counselor?.real_name || '咨询师'}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{appointment.consult_type || '咨询'}</Badge>
                            {appointment.consult_method && (
                              <span className="ml-2 text-xs text-[#666666]">
                                {appointment.consult_method}
                              </span>
                            )}
                          </TableCell>
                          <TableCell>{formattedDate}</TableCell>
                          <TableCell>
                            <div className="flex flex-col gap-1">
                              <Badge variant={
                                statusText === '已完成' ? 'default' :
                                statusText === '待确认' ? 'outline' :
                                statusText === '已确认' ? 'secondary' :
                                'secondary'
                              }>
                                {statusText}
                              </Badge>
                              {statusText === '已完成' && (
                                <div className="flex items-center gap-1">
                                  {appointment.rating ? (
                                    <>
                                      <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                                      <span className="text-xs text-[#666666]">{appointment.rating}/5</span>
                                    </>
                                  ) : (
                                    <span className="text-xs text-[#666666]">待评价</span>
                                  )}
                                </div>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <Button variant="outline" size="sm" onClick={() => openAppointmentDialog(appointment)}>
                              查看详情
                            </Button>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
              )}
            </CardContent>
          </Card>
        </div>
      )}
      {activeTab === 'test' && <PsychTest />}
      {activeTab === 'content' && <HealthContent />}
      {activeTab === 'community' && <Community />}
      {activeTab === 'profile' && <UserProfile />}

      {/* 预约详情对话框 */}
      <Dialog open={showAppointmentDialog} onOpenChange={setShowAppointmentDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>预约详情</DialogTitle>
            <DialogDescription>查看和管理预约信息</DialogDescription>
          </DialogHeader>
          {selectedAppointment && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>咨询师</Label>
                  <p className="mt-1 font-medium">{selectedAppointment.counselor?.real_name || '咨询师'}</p>
                </div>
                <div>
                  <Label>咨询类型</Label>
                  <p className="mt-1">{selectedAppointment.consult_type || '咨询'}</p>
                </div>
              </div>
            <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>咨询方式</Label>
                <p className="mt-1">{selectedAppointment.consult_method || '未知方式'}</p>
                </div>
                <div>
                  <Label>预约时间</Label>
                <p className="mt-1">
                  {selectedAppointment.appointment_date
                    ? new Date(selectedAppointment.appointment_date).toLocaleString('zh-CN')
                    : '时间未知'}
                </p>
                </div>
              </div>
              <div>
                <Label>咨询诉求</Label>
                <p className="mt-1 text-[#666666] bg-gray-50 p-3 rounded whitespace-pre-wrap">
                  {selectedAppointment.description || '暂无描述'}
                </p>
              </div>
              {/* 状态信息 */}
              <div>
                <Label>预约状态</Label>
                <div className="mt-1">
                  <Badge variant={
                    selectedAppointment.status === 'completed' ? 'default' :
                    selectedAppointment.status === 'confirmed' ? 'default' :
                    selectedAppointment.status === 'pending' ? 'outline' :
                    'secondary'
                  }>
                    {selectedAppointment.status === 'pending' ? '待确认' :
                     selectedAppointment.status === 'confirmed' ? '已确认' :
                     selectedAppointment.status === 'completed' ? '已完成' :
                     selectedAppointment.status === 'cancelled' ? '已取消' :
                     selectedAppointment.status === 'rejected' ? '已拒绝' :
                     selectedAppointment.status}
                  </Badge>
                </div>
              </div>

              {/* 咨询小结 - 对于已完成的预约，始终显示 */}
              {selectedAppointment.status === 'completed' && (
                <div>
                  <Label>咨询小结</Label>
                  <p className="mt-1 text-[#666666] bg-gray-50 p-3 rounded whitespace-pre-wrap">
                    {selectedAppointment.summary || '咨询师尚未填写咨询小结'}
                  </p>
                </div>
              )}
              {selectedAppointment.status !== 'completed' && selectedAppointment.summary && (
                <div>
                  <Label>咨询小结</Label>
                  <p className="mt-1 text-[#666666] bg-gray-50 p-3 rounded whitespace-pre-wrap">
                    {selectedAppointment.summary}
                  </p>
                </div>
              )}

              {/* 时间信息 */}
              <div className="grid grid-cols-2 gap-4 border-t pt-4">
                <div>
                  <Label className="text-xs text-[#666666]">创建时间</Label>
                  <p className="mt-1 text-sm text-[#666666]">
                    {selectedAppointment.created_at 
                      ? new Date(selectedAppointment.created_at).toLocaleString('zh-CN')
                      : '未知'}
                  </p>
                </div>
                {selectedAppointment.updated_at && (
                  <div>
                    <Label className="text-xs text-[#666666]">更新时间</Label>
                    <p className="mt-1 text-sm text-[#666666]">
                      {new Date(selectedAppointment.updated_at).toLocaleString('zh-CN')}
                    </p>
                  </div>
                )}
              </div>
              
              {/* 已确认/已完成状态的预约，显示确认结束区域 */}
              {['confirmed', 'completed'].includes(selectedAppointment.status) && (() => {
                const appointmentDate = selectedAppointment.appointment_date
                  ? new Date(selectedAppointment.appointment_date)
                  : null;
                const consultationEndTime = appointmentDate
                  ? new Date(appointmentDate.getTime() + 60 * 60 * 1000)
                  : null;
                const now = new Date();
                const canConfirm = !consultationEndTime || now >= consultationEndTime;
                
                return (
                  <div className="space-y-2 border-t pt-4">
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-[#666666]">用户确认：</span>
                        <Badge variant={selectedAppointment.user_confirmed_complete ? "default" : "outline"}>
                          {selectedAppointment.user_confirmed_complete ? "已确认" : "未确认"}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[#666666]">咨询师确认：</span>
                        <Badge variant={selectedAppointment.counselor_confirmed_complete ? "default" : "outline"}>
                          {selectedAppointment.counselor_confirmed_complete ? "已确认" : "未确认"}
                        </Badge>
                      </div>
                    </div>
                    {!canConfirm && (
                      <div className="p-2 bg-yellow-50 rounded text-sm text-yellow-700">
                        预约时间段尚未结束，请等待预约时间结束后再确认
                      </div>
                    )}
                    {canConfirm && !selectedAppointment.user_confirmed_complete && (
                      <Button className="w-full" variant="default" onClick={() => handleConfirmComplete(selectedAppointment.id)}>
                        <CheckCircle className="w-4 h-4 mr-2" />
                        确认咨询结束
                      </Button>
                    )}
                    {selectedAppointment.user_confirmed_complete && selectedAppointment.counselor_confirmed_complete && selectedAppointment.status === 'completed' && (
                      <div className="p-2 bg-green-50 rounded text-sm text-green-700">
                        双方已确认，咨询已完成
                      </div>
                    )}
                  </div>
                );
              })()}
              
              {/* 已完成的预约，显示详细信息 */}
              {selectedAppointment.status === 'completed' && (
                <div className="space-y-4 border-t pt-4">
                  {/* 确认状态信息 */}
                  {/*<div className="bg-green-50 p-4 rounded-lg border border-green-200">
                    <Label className="text-green-800 font-semibold mb-2 block">咨询完成确认</Label>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-[#222222]">用户确认：</span>
                        <Badge variant={selectedAppointment.user_confirmed_complete ? "default" : "outline"}>
                          {selectedAppointment.user_confirmed_complete ? "✓ 已确认" : "未确认"}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-[#222222]">咨询师确认：</span>
                        <Badge variant={selectedAppointment.counselor_confirmed_complete ? "default" : "outline"}>
                          {selectedAppointment.counselor_confirmed_complete ? "✓ 已确认" : "未确认"}
                        </Badge>
                      </div>
                    </div>
                    {selectedAppointment.user_confirmed_complete && selectedAppointment.counselor_confirmed_complete && (
                      <div className="mt-2 text-sm text-green-700">
                        ✓ 双方已确认，咨询已完成
                      </div>
                    )}
                  </div>*/}

                  {/* 咨询师详细信息 */}
                  {selectedAppointment.counselor && (
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <Label className="font-semibold mb-2 block">咨询师信息</Label>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-[#666666]">姓名：</span>
                          <span className="ml-2 font-medium">{selectedAppointment.counselor.real_name || '未知'}</span>
                        </div>
                        {selectedAppointment.counselor.specialties && (
                          <div>
                            <span className="text-[#666666]">专业领域：</span>
                            <span className="ml-2">{Array.isArray(selectedAppointment.counselor.specialties) 
                              ? selectedAppointment.counselor.specialties.join('、')
                              : selectedAppointment.counselor.specialties}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* 评分和评价 */}
                  <div className="space-y-4">
                    <div>
                      <Label className="text-base font-semibold">评分与评价</Label>
                      {selectedAppointment.rating ? (
                        <div className="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-sm text-[#222222]">您的评分：</span>
                            <div className="flex items-center gap-1">
                              {[1, 2, 3, 4, 5].map((star) => (
                                <Star
                                  key={star}
                                  className={`w-5 h-5 ${
                                    star <= selectedAppointment.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                                  }`}
                                />
                              ))}
                            </div>
                            <span className="text-sm font-medium text-[#222222]">{selectedAppointment.rating}/5 星</span>
                          </div>
                          {selectedAppointment.review && (
                            <div className="mt-2">
                              <span className="text-sm text-[#222222]">您的评价：</span>
                              <p className="mt-1 text-sm text-gray-800 bg-white p-2 rounded whitespace-pre-wrap">
                                {selectedAppointment.review}
                              </p>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="mt-2">
                          <div className="mb-3">
                            <Label className="text-sm">评分</Label>
                            <div className="flex items-center gap-2 mt-2">
                              {[1, 2, 3, 4, 5].map((star) => (
                                <Star
                                  key={star}
                                  className={`w-6 h-6 cursor-pointer transition-colors ${
                                    star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                                  }`}
                                  onClick={() => setRating(star)}
                                />
                              ))}
                              <span className="ml-2 text-sm text-[#666666]">{rating}/5</span>
                            </div>
                          </div>
                          <div>
                            <Label className="text-sm">评价</Label>
                            <Textarea
                              placeholder="请输入您的评价（可选）..."
                              rows={4}
                              value={review}
                              onChange={(e) => setReview(e.target.value)}
                              className="mt-2"
                            />
                          </div>
                          <Button 
                            className="w-full mt-3" 
                            onClick={() => handleSubmitRating(selectedAppointment.id)}
                            disabled={rating === 0}
                          >
                            <Star className="w-4 h-4 mr-2" />
                            提交评分
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
        </>
      }
    />
  );
}

