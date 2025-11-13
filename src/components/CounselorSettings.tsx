import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Switch } from './ui/switch';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from './ui/dialog';
import { counselorApi } from '../services/api';
import { toast } from 'sonner';
import { User, Settings, Calendar, Upload, X, Plus, Edit, Trash2, Clock, AlertCircle } from 'lucide-react';
import { SidebarLayout } from './SidebarLayout';
interface CounselorSettingsContentProps {
  userInfo?: any;
  onProfileUpdate?: () => void;
}

export function CounselorSettingsContent({ userInfo, onProfileUpdate }: CounselorSettingsContentProps) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [counselorProfile, setCounselorProfile] = useState<any>(null);

  // 统一的错误信息提取函数
  const getErrorMessage = (error: any): string => {
    // 首先检查是否是网络错误（无响应），优先返回详细的诊断信息
    if (error?.isNetworkError || (!error?.response && error?.code)) {
      // 如果网络错误有 detail 字段，使用它（可能包含更详细的诊断信息）
      if (error?.detail && typeof error.detail === 'string') {
        return error.detail;
      }
      return '无法连接到后端服务，请检查：\n1. 后端服务是否已启动（在 src/backend 目录运行 python main.py）\n2. 后端是否运行在 http://localhost:8000\n3. 防火墙是否阻止了连接\n4. 查看浏览器控制台是否有CORS错误';
    }
    
    // 优先检查 detail 字段（这是后端返回的错误信息）
    if (error?.detail) {
      // 如果 detail 是数组（FastAPI 验证错误），提取第一个错误信息
      if (Array.isArray(error.detail) && error.detail.length > 0) {
        const firstError = error.detail[0];
        if (typeof firstError === 'object' && firstError?.msg) {
          return firstError.msg;
        }
        if (typeof firstError === 'string') {
          return firstError;
        }
      }
      // 如果是字符串，直接返回
      if (typeof error.detail === 'string') {
        return error.detail;
      }
      // 如果是对象，尝试转换为字符串（但避免 [object Object]）
      if (typeof error.detail === 'object') {
        try {
          const jsonStr = JSON.stringify(error.detail);
          if (jsonStr && jsonStr !== '{}' && jsonStr !== '[]') {
            return jsonStr;
          }
        } catch (e) {
          // 忽略转换错误
        }
      }
    }
    // 检查 response.data.detail
    if (error?.response?.data?.detail) {
      if (Array.isArray(error.response.data.detail) && error.response.data.detail.length > 0) {
        const firstError = error.response.data.detail[0];
        if (typeof firstError === 'object' && firstError?.msg) {
          return firstError.msg;
        }
        if (typeof firstError === 'string') {
          return firstError;
        }
      }
      if (typeof error.response.data.detail === 'string') {
        return error.response.data.detail;
      }
    }
    // 检查 message 字段
    if (error?.message) {
      const msgStr = typeof error.message === 'string' ? error.message : String(error.message);
      if (msgStr && msgStr !== '[object Object]') {
        return msgStr;
      }
    }
    // 检查 response.data.message
    if (error?.response?.data?.message) {
      const msgStr = typeof error.response.data.message === 'string' ? error.response.data.message : String(error.response.data.message);
      if (msgStr && msgStr !== '[object Object]') {
        return msgStr;
      }
    }
    return '操作失败，请重试';
  };
  
  // 显示错误信息（支持多行）
  const showError = (error: any, prefix: string = '操作失败') => {
    const errorMsg = getErrorMessage(error);
    if (errorMsg.includes('\n')) {
      const lines = errorMsg.split('\n');
      toast.error(prefix + ': ' + lines[0], {
        description: lines.slice(1).join('\n'),
        duration: 8000,
      });
    } else {
      toast.error(prefix + ': ' + errorMsg, {
        duration: 5000,
      });
    }
  };
  
  // 个人基本信息
  const [basicInfo, setBasicInfo] = useState({
    real_name: '',
    gender: 'female',
    age: '',
    experience_years: '',
    qualification: '',
    certificate_urls: [] as string[],
    avatar: '',
  });

  // 咨询服务设置
  const [serviceSettings, setServiceSettings] = useState({
    specialty: [] as string[],
    consult_methods: [] as string[],
    consult_type: [] as string[],
    fee: '',
    consult_place: '',
    max_daily_appointments: '',
    bio: '',
    intro: '',
  });

  // 可预约时间设置
  const [schedules, setSchedules] = useState<Array<{
    weekday: number;
    weekdayName: string;
    start_time: string;
    end_time: string;
    is_available: boolean;
  }>>([
    { weekday: 1, weekdayName: '周一', start_time: '08:00', end_time: '22:00', is_available: true },
    { weekday: 2, weekdayName: '周二', start_time: '08:00', end_time: '22:00', is_available: true },
    { weekday: 3, weekdayName: '周三', start_time: '08:00', end_time: '22:00', is_available: true },
    { weekday: 4, weekdayName: '周四', start_time: '08:00', end_time: '22:00', is_available: true },
    { weekday: 5, weekdayName: '周五', start_time: '08:00', end_time: '22:00', is_available: true },
    { weekday: 6, weekdayName: '周六', start_time: '08:00', end_time: '22:00', is_available: true },
    { weekday: 7, weekdayName: '周日', start_time: '08:00', end_time: '22:00', is_available: true },
  ]);

  // 不可预约时段
  const [unavailablePeriods, setUnavailablePeriods] = useState<Array<{
    id: number;
    start_date: string;
    end_date: string;
    start_time: string | null;
    end_time: string | null;
    reason: string;
    time_type: 'all' | 'custom';
    status: number;
    created_at: string;
  }>>([]);

  // 擅长领域预设选项
  const specialtyOptions = [
    '学业压力', '情感困扰', '人际关系', '职业发展', '焦虑抑郁',
    '家庭关系', '自我成长', '心理创伤', '成瘾问题', '睡眠障碍'
  ];

  // 咨询方式选项（直接使用中文值）
  const consultMethodOptions = [
    { value: '线上视频', label: '线上视频' },
    { value: '语音咨询', label: '语音咨询' },
    { value: '文字咨询', label: '文字咨询' },
    { value: '线下面谈', label: '线下面谈' },
  ];

  // 加载数据
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // 加载个人资料
      // API 拦截器已经返回了 data，直接使用
      console.log('[CounselorSettings] 开始加载咨询师资料...');
      const profile: any = await counselorApi.getProfile();
      console.log('[CounselorSettings] 加载的咨询师资料:', profile);
      console.log('[CounselorSettings] age 类型:', typeof profile.age, '值:', profile.age);
      console.log('[CounselorSettings] experience_years 类型:', typeof profile.experience_years, '值:', profile.experience_years);
      console.log('[CounselorSettings] real_name:', profile.real_name);
      console.log('[CounselorSettings] gender:', profile.gender);
      console.log('[CounselorSettings] specialty:', profile.specialty);
      console.log('[CounselorSettings] consult_methods:', profile.consult_methods);
      
      if (!profile) {
        console.error('[CounselorSettings] 获取到的资料为空');
        toast.error('获取咨询师资料失败：返回数据为空');
        return;
      }
      
      setCounselorProfile(profile);
      
      // 处理性别字段：将数据库中的 "FEMALE"/"MALE" 转换为小写 "female"/"male"
      let genderValue = 'female';
      if (profile.gender) {
        const genderStr = String(profile.gender).toLowerCase();
        if (['male', 'female', 'other'].includes(genderStr)) {
          genderValue = genderStr;
        } else if (genderStr === 'male' || genderStr.includes('male')) {
          genderValue = 'male';
        } else if (genderStr === 'female' || genderStr.includes('female')) {
          genderValue = 'female';
        } else {
          genderValue = 'other';
        }
      }
      
      // 处理个人基本信息，确保正确处理 None/null/undefined 值
      let ageValue = '';
      if (profile.age != null && profile.age !== '' && profile.age !== undefined) {
        try {
          // 确保 age 是数字，不是字符串
          const ageNum = typeof profile.age === 'number' ? profile.age : parseInt(String(profile.age));
          if (!isNaN(ageNum) && ageNum > 0) {
            ageValue = String(ageNum);
          }
        } catch (e) {
          console.warn('[CounselorSettings] 解析 age 失败:', e, '原始值:', profile.age);
        }
      }
      
      let experienceYearsValue = '';
      if (profile.experience_years != null && profile.experience_years !== '' && profile.experience_years !== undefined) {
        try {
          // 确保 experience_years 是数字，不是字符串
          const expYearsNum = typeof profile.experience_years === 'number' ? profile.experience_years : parseInt(String(profile.experience_years));
          if (!isNaN(expYearsNum) && expYearsNum >= 0) {
            experienceYearsValue = String(expYearsNum);
          }
        } catch (e) {
          console.warn('[CounselorSettings] 解析 experience_years 失败:', e, '原始值:', profile.experience_years);
        }
      }
      
      // 处理证书URL数组
      let certificateUrls: string[] = [];
      if (profile.certificate_url) {
        if (Array.isArray(profile.certificate_url)) {
          certificateUrls = profile.certificate_url.filter(url => url && String(url).trim());
        } else if (typeof profile.certificate_url === 'string') {
          try {
            // 尝试解析JSON字符串
            const parsed = JSON.parse(profile.certificate_url);
            if (Array.isArray(parsed)) {
              certificateUrls = parsed.filter(url => url && String(url).trim());
            } else {
              certificateUrls = [String(profile.certificate_url).trim()].filter(url => url);
            }
          } catch {
            // 不是JSON，直接使用字符串
            const urlStr = String(profile.certificate_url).trim();
            if (urlStr) {
              certificateUrls = [urlStr];
            }
          }
        }
      }
      
      const basicInfoData = {
        real_name: profile.real_name ? String(profile.real_name).trim() : '',
        gender: genderValue,
        age: ageValue,
        experience_years: experienceYearsValue,
        qualification: profile.qualification ? String(profile.qualification).trim() : '',
        certificate_urls: certificateUrls,
        avatar: profile.avatar ? String(profile.avatar).trim() : '',
      };
      
      console.log('[CounselorSettings] 设置 basicInfo:', basicInfoData);
      console.log('[CounselorSettings] 原始 profile.real_name:', profile.real_name, '类型:', typeof profile.real_name);
      console.log('[CounselorSettings] 原始 profile.qualification:', profile.qualification, '类型:', typeof profile.qualification);
      console.log('[CounselorSettings] 原始 profile.gender:', profile.gender, '转换后:', genderValue);
      console.log('[CounselorSettings] 原始 profile.age:', profile.age, '转换后:', ageValue);
      console.log('[CounselorSettings] 原始 profile.experience_years:', profile.experience_years, '转换后:', experienceYearsValue);
      
      setBasicInfo(basicInfoData);

      // 统一的JSON数组字段解析函数（与后端保持一致）
      const parseJsonArrayField = (value: any, defaultValue: string[] = []): string[] => {
        if (value === null || value === undefined) {
          return defaultValue;
        }
        
        if (Array.isArray(value)) {
          // 已经是数组，清理空格后返回
          return value.map(item => String(item).trim()).filter(item => item);
        }
        
        if (typeof value !== 'string') {
          return defaultValue;
        }
        
        const trimmed = value.trim();
        if (!trimmed) {
          return defaultValue;
        }
        
        // 尝试解析JSON数组
        try {
          if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
            const parsed = JSON.parse(trimmed);
            if (Array.isArray(parsed)) {
              return parsed.map(item => String(item).trim()).filter(item => item);
            }
          }
        } catch (e) {
          // JSON解析失败，继续尝试其他方式
        }
        
        // 尝试按逗号分割（支持中文逗号和英文逗号）
        let items: string[];
        if (trimmed.includes('，')) {
          items = trimmed.split('，');
        } else {
          items = trimmed.split(',');
        }
        
        // 清理空格和空项
        const result = items.map(item => item.trim()).filter(item => item);
        return result.length > 0 ? result : defaultValue;
      };

      // 处理咨询服务设置
      const specialty = parseJsonArrayField(profile.specialty, []);
      let consult_methods = parseJsonArrayField(profile.consult_methods, []);
      // 将旧数据（英文值）转换为新数据（中文值）
      const methodMap: Record<string, string> = {
        'video': '线上视频',
        'offline': '线下面谈',
        'voice': '语音咨询',
        'audio': '语音咨询',
        'text': '文字咨询',
      };
      consult_methods = consult_methods.map(method => methodMap[method] || method);
      const consult_type = parseJsonArrayField(profile.consult_type, []);

      console.log('解析后的数据:', {
        specialty,
        consult_methods,
        consult_type,
        original: {
          specialty: profile.specialty,
          consult_methods: profile.consult_methods,
          consult_type: profile.consult_type,
        }
      });

      setServiceSettings({
        specialty: specialty,
        consult_methods: consult_methods,
        consult_type: consult_type,
        fee: profile.fee ? String(profile.fee) : '0',
        consult_place: profile.consult_place || '',
        max_daily_appointments: profile.max_daily_appointments ? String(profile.max_daily_appointments) : '3',
        bio: profile.bio || '',
        intro: profile.intro || '',
      });

      // 加载时段设置
      // API 拦截器已经返回了 data，直接使用
      const schedulesRes: any = await counselorApi.getSchedules();
      const schedulesData = schedulesRes?.schedules || schedulesRes?.data?.schedules || [];
      
      const weekdayNames = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
      const updatedSchedules = [1, 2, 3, 4, 5, 6, 7].map(weekday => {
        const schedule = schedulesData.find((s: any) => s.weekday === weekday);
        if (schedule) {
          return {
            weekday,
            weekdayName: weekdayNames[weekday],
            start_time: schedule.start_time || '08:00',
            end_time: schedule.end_time || '22:00',
            is_available: schedule.is_available !== false,
          };
        }
        return {
          weekday,
          weekdayName: weekdayNames[weekday],
          start_time: '08:00',
          end_time: '22:00',
          is_available: true,
        };
      });
      setSchedules(updatedSchedules);

      // 加载不可预约时段（获取所有记录，不限制数量）
      // API 拦截器已经返回了 data，直接使用
      const unavailableRes: any = await counselorApi.getUnavailablePeriods(0, 1000);
      const periods = unavailableRes?.periods || unavailableRes?.data?.periods || [];
      setUnavailablePeriods(periods.map((p: any) => ({
        id: p.id,
        start_date: p.start_date,
        end_date: p.end_date,
        start_time: p.start_time,
        end_time: p.end_time,
        reason: p.reason || '',
        time_type: p.time_type || 'all',
        status: p.status !== undefined ? p.status : 1,
        created_at: p.created_at || '',
      })));

    } catch (error: any) {
      console.error('加载数据失败:', error);
      console.error('错误详情:', {
        message: error?.message,
        detail: error?.detail,
        response: error?.response,
        status: error?.status,
        code: error?.code,
      });
      
      // 提取错误信息
      let errorMsg = '加载数据失败';
      if (error?.detail) {
        if (Array.isArray(error.detail)) {
          const firstError = error.detail[0];
          if (typeof firstError === 'object' && firstError?.msg) {
            errorMsg = firstError.msg;
          } else if (typeof firstError === 'string') {
            errorMsg = firstError;
          }
        } else if (typeof error.detail === 'string') {
          errorMsg = error.detail;
        }
      } else if (error?.message) {
        errorMsg = error.message;
      }
      
      toast.error(errorMsg);
      showError(error, '加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 保存个人基本信息
  const handleSaveBasicInfo = async () => {
    try {
      // 前端校验
      if (!basicInfo.real_name.trim()) {
        toast.error('真实姓名不能为空');
        return;
      }
      // 验证从业年限
      if (basicInfo.experience_years && basicInfo.experience_years.trim()) {
        const expYears = parseInt(basicInfo.experience_years.trim());
        if (isNaN(expYears) || expYears < 0 || expYears > 50) {
          toast.error('从业年限必须是0-50之间的数字');
          return;
        }
      }

      setSaving(true);

      const updateData: any = {
        real_name: basicInfo.real_name,
        gender: basicInfo.gender,
        qualification: basicInfo.qualification || undefined,
        certificate_url: basicInfo.certificate_urls.length > 0 ? basicInfo.certificate_urls : undefined,
      };

      // 处理从业年限 - 只有有值且有效时才发送
      if (basicInfo.experience_years && basicInfo.experience_years.trim()) {
        const expYears = parseInt(basicInfo.experience_years.trim());
        if (!isNaN(expYears) && expYears >= 0 && expYears <= 50) {
          updateData.experience_years = expYears;
        } else {
          // 如果解析失败，不发送该字段（保持原值）
          console.warn('从业年限格式无效，将保持原值');
        }
      }
      // 如果字段为空，不发送该字段（保持原值）

      // 处理年龄 - 只有有值且有效时才发送
      if (basicInfo.age && basicInfo.age.trim()) {
        const ageNum = parseInt(basicInfo.age.trim());
        if (!isNaN(ageNum) && ageNum >= 22 && ageNum <= 65) {
          updateData.age = ageNum;
        } else {
          // 如果解析失败，不发送该字段（保持原值）
          console.warn('年龄格式无效，将保持原值');
        }
      }
      // 如果字段为空，不发送该字段（保持原值）

      if (basicInfo.avatar) {
        updateData.avatar = basicInfo.avatar;
      }

      // 检查是否需要审核（修改真实姓名或资质证书）
      const needReview = basicInfo.real_name !== (counselorProfile?.real_name || '') ||
        JSON.stringify(basicInfo.certificate_urls) !== JSON.stringify(counselorProfile?.certificate_url || []);
      
      if (needReview) {
        updateData.need_review = true;
      }

      await counselorApi.updateProfile(updateData);
      
      toast.success('保存成功！' + (needReview ? '修改已提交审核，审核通过前将展示原有信息。' : ''));
      await loadData();
      if (onProfileUpdate) onProfileUpdate();
      
    } catch (error: any) {
      console.error('保存失败:', error);
      showError(error, '保存失败');
    } finally {
      setSaving(false);
    }
  };

  // 保存咨询服务设置
  const handleSaveServiceSettings = async () => {
    try {
      // 前端校验
      const fee = parseFloat(serviceSettings.fee);
      if (isNaN(fee) || fee < 0) {
        toast.error('咨询费用需为数字且≥0');
        return;
      }

      if (serviceSettings.consult_methods.includes('线下面谈') && !serviceSettings.consult_place.trim()) {
        toast.error('选择线下面谈时，必须填写咨询地点');
        return;
      }

      if (serviceSettings.specialty.length === 0) {
        toast.error('请至少选择一个擅长领域');
        return;
      }

      setSaving(true);

      const maxDailyAppointments = parseInt(serviceSettings.max_daily_appointments);
      if (isNaN(maxDailyAppointments) || maxDailyAppointments < 1 || maxDailyAppointments > 10) {
        toast.error('每日最大预约量必须在1-10之间');
        return;
      }

      await counselorApi.updateProfile({
        specialty: serviceSettings.specialty,
        consult_methods: serviceSettings.consult_methods,
        consult_type: serviceSettings.consult_type.length > 0 ? serviceSettings.consult_type : undefined,
        fee: fee,
        consult_place: serviceSettings.consult_methods.includes('线下面谈') ? serviceSettings.consult_place : undefined,
        max_daily_appointments: maxDailyAppointments,
        bio: serviceSettings.bio || undefined,
        intro: serviceSettings.intro || undefined,
      });

      toast.success('保存成功！');
      await loadData();
      if (onProfileUpdate) onProfileUpdate();
      
    } catch (error: any) {
      console.error('保存失败:', error);
      showError(error, '保存失败');
    } finally {
      setSaving(false);
    }
  };

  // 保存时段设置
  const handleSaveSchedules = async () => {
    try {
      setSaving(true);

      // 获取每日最大预约量（从咨询服务设置中获取）
      const maxDailyAppointments = parseInt(serviceSettings.max_daily_appointments) || 3;
      if (isNaN(maxDailyAppointments) || maxDailyAppointments < 1 || maxDailyAppointments > 10) {
        toast.error('每日最大预约量必须在1-10之间，请先在咨询服务设置中配置');
        return;
      }

      const schedulesData = schedules
        .filter(s => s.is_available)
        .map(s => ({
          weekday: s.weekday,
          start_time: s.start_time,
          end_time: s.end_time,
          max_num: maxDailyAppointments,
          is_available: true,
        }));

      if (schedulesData.length === 0) {
        toast.error('请至少选择一个可预约的日期');
        return;
      }

      await counselorApi.setSchedules(schedulesData);
      
      toast.success('保存成功！');
      await loadData();
      if (onProfileUpdate) onProfileUpdate();
      
    } catch (error: any) {
      console.error('保存失败:', error);
      showError(error, '保存失败');
    } finally {
      setSaving(false);
    }
  };

  // 上传头像
  const handleUploadAvatar = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error('只能上传图片文件');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error('文件大小不能超过5MB');
      return;
    }

    try {
      const response: any = await counselorApi.uploadAvatar(file);
      // API 拦截器已经返回了 data，直接访问 response
      const avatarUrl = response?.avatar_url || response?.data?.avatar_url || (typeof response === 'string' ? response : '');
      setBasicInfo({ ...basicInfo, avatar: avatarUrl });
      toast.success('头像上传成功');
    } catch (error: any) {
      console.error('上传失败:', error);
      showError(error, '上传失败');
    }
  };

  // 添加擅长领域
  const handleAddSpecialty = (specialty: string) => {
    if (!serviceSettings.specialty.includes(specialty)) {
      setServiceSettings({
        ...serviceSettings,
        specialty: [...serviceSettings.specialty, specialty],
      });
    }
  };

  // 移除擅长领域
  const handleRemoveSpecialty = (specialty: string) => {
    setServiceSettings({
      ...serviceSettings,
      specialty: serviceSettings.specialty.filter(s => s !== specialty),
    });
  };

  // 切换咨询方式
  const handleToggleConsultMethod = (method: string) => {
    const methods = serviceSettings.consult_methods;
    if (methods.includes(method)) {
      setServiceSettings({
        ...serviceSettings,
        consult_methods: methods.filter(m => m !== method),
      });
    } else {
      setServiceSettings({
        ...serviceSettings,
        consult_methods: [...methods, method],
      });
    }
  };

  // 不可预约时段管理
  const [unavailableDialogOpen, setUnavailableDialogOpen] = useState(false);
  const [editingPeriod, setEditingPeriod] = useState<any>(null);
  const [periodForm, setPeriodForm] = useState({
    start_date: '',
    end_date: '',
    start_time: '',
    end_time: '',
    reason: '',
    time_type: 'all' as 'all' | 'custom',
  });

  const handleAddUnavailablePeriod = () => {
    setEditingPeriod(null);
    setPeriodForm({
      start_date: '',
      end_date: '',
      start_time: '',
      end_time: '',
      reason: '',
      time_type: 'all',
    });
    setUnavailableDialogOpen(true);
  };

  const handleEditUnavailablePeriod = (period: any) => {
    setEditingPeriod(period);
    setPeriodForm({
      start_date: period.start_date,
      end_date: period.end_date,
      start_time: period.start_time || '',
      end_time: period.end_time || '',
      reason: period.reason || '',
      time_type: period.time_type || 'all',
    });
    setUnavailableDialogOpen(true);
  };

  const handleSaveUnavailablePeriod = async () => {
    try {
      if (!periodForm.start_date || !periodForm.end_date) {
        toast.error('请填写开始和结束日期');
        return;
      }

      if (periodForm.time_type === 'custom' && (!periodForm.start_time || !periodForm.end_time)) {
        toast.error('自定义时段必须填写开始和结束时间');
        return;
      }

      // 构建请求数据，确保时间字段在 time_type 为 'all' 时不发送
      const requestData: any = {
        start_date: periodForm.start_date,
        end_date: periodForm.end_date,
        reason: periodForm.reason || undefined,
        time_type: periodForm.time_type,
      };

      if (periodForm.time_type === 'custom') {
        requestData.start_time = periodForm.start_time;
        requestData.end_time = periodForm.end_time;
      }

      if (editingPeriod) {
        await counselorApi.updateUnavailablePeriod(editingPeriod.id, requestData);
      } else {
        await counselorApi.addUnavailablePeriod(requestData);
      }

      toast.success(editingPeriod ? '更新成功' : '添加成功');
      setUnavailableDialogOpen(false);
      await loadData();
    } catch (error: any) {
      console.error('保存失败:', error);
      showError(error, '保存失败');
    }
  };

  const handleDeleteUnavailablePeriod = async (id: number) => {
    try {
      await counselorApi.deleteUnavailablePeriod(id);
      toast.success('删除成功');
      await loadData();
    } catch (error: any) {
      console.error('删除失败:', error);
      showError(error, '删除失败');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">个人设置</h1>
          <p className="text-gray-600 mt-2">管理您的个人信息和咨询设置</p>
        </div>

        <Tabs defaultValue="basic" className="space-y-6">
          <TabsList>
            <TabsTrigger value="basic" className="gap-2">
              <User className="w-4 h-4" />
              个人基本信息
            </TabsTrigger>
            <TabsTrigger value="service" className="gap-2">
              <Settings className="w-4 h-4" />
              咨询服务设置
            </TabsTrigger>
            <TabsTrigger value="schedule" className="gap-2">
              <Calendar className="w-4 h-4" />
              可预约时间设置
            </TabsTrigger>
          </TabsList>

          {/* 标签页1：个人基本信息 */}
          <TabsContent value="basic">
            <Card>
              <CardHeader>
                <CardTitle>个人基本信息</CardTitle>
                <CardDescription>管理您的基本信息和资质证明</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* 头像上传 */}
                <div className="flex items-center gap-6">
                  <Avatar className="w-24 h-24">
                    <AvatarImage src={basicInfo.avatar} />
                    <AvatarFallback>{basicInfo.real_name?.[0] || 'C'}</AvatarFallback>
                  </Avatar>
                  <div className="space-y-2">
                    <Label>个人头像</Label>
                    <div className="flex items-center gap-2">
                      <Input
                        type="file"
                        accept="image/*"
                        onChange={handleUploadAvatar}
                        className="hidden"
                        id="avatar-upload"
                      />
                      <Label htmlFor="avatar-upload" className="cursor-pointer">
                        <Button variant="outline" asChild>
                          <span>
                            <Upload className="w-4 h-4 mr-2" />
                            上传头像
                          </span>
                        </Button>
                      </Label>
                    </div>
                  </div>
                </div>

                {/* 基本信息表单 */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>真实姓名 <span className="text-red-500">*</span></Label>
                    <Input
                      value={basicInfo.real_name}
                      onChange={(e) => setBasicInfo({ ...basicInfo, real_name: e.target.value })}
                      placeholder="请输入真实姓名"
                    />
                    <p className="text-xs text-gray-500">修改后需管理员审核</p>
                  </div>

                  <div className="space-y-2">
                    <Label>性别 <span className="text-red-500">*</span></Label>
                    <Select
                      value={basicInfo.gender}
                      onValueChange={(value) => setBasicInfo({ ...basicInfo, gender: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">男</SelectItem>
                        <SelectItem value="female">女</SelectItem>
                        <SelectItem value="other">其他</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>年龄</Label>
                    <Input
                      type="number"
                      value={basicInfo.age}
                      onChange={(e) => setBasicInfo({ ...basicInfo, age: e.target.value })}
                      placeholder="22-65"
                      min={22}
                      max={65}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>从业年限 <span className="text-red-500">*</span></Label>
                    <Input
                      type="number"
                      value={basicInfo.experience_years}
                      onChange={(e) => setBasicInfo({ ...basicInfo, experience_years: e.target.value })}
                      placeholder="0-50"
                      min={0}
                      max={50}
                    />
                  </div>

                  <div className="space-y-2 col-span-2">
                    <Label>资质证书</Label>
                    <Input
                      value={basicInfo.qualification}
                      onChange={(e) => setBasicInfo({ ...basicInfo, qualification: e.target.value })}
                      placeholder="如：国家二级心理咨询师"
                    />
                    <p className="text-xs text-gray-500">修改后需管理员审核</p>
                  </div>

                  <div className="space-y-2 col-span-2">
                    <Label>证书照片</Label>
                    <div className="flex gap-2 flex-wrap">
                      {basicInfo.certificate_urls.map((url, index) => (
                        <div key={index} className="relative">
                          <img src={url} alt={`证书${index + 1}`} className="w-24 h-24 object-cover rounded" />
                          <Button
                            variant="destructive"
                            size="icon"
                            className="absolute -top-2 -right-2 w-6 h-6"
                            onClick={() => {
                              setBasicInfo({
                                ...basicInfo,
                                certificate_urls: basicInfo.certificate_urls.filter((_, i) => i !== index),
                              });
                            }}
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                      ))}
                      <Button
                        variant="outline"
                        size="icon"
                        className="w-24 h-24"
                        onClick={() => {
                          // TODO: 实现证书上传功能
                          toast.info('证书上传功能待实现');
                        }}
                      >
                        <Plus className="w-6 h-6" />
                      </Button>
                    </div>
                    <p className="text-xs text-gray-500">支持多图，最多3张</p>
                  </div>
                </div>

                <div className="flex justify-end gap-2">
                  <Button onClick={handleSaveBasicInfo} disabled={saving}>
                    {saving ? '保存中...' : '保存'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 标签页2：咨询服务设置 */}
          <TabsContent value="service">
            <Card>
              <CardHeader>
                <CardTitle>咨询服务设置</CardTitle>
                <CardDescription>配置您的咨询服务和收费标准</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* 擅长领域 */}
                <div className="space-y-2">
                  <Label>擅长领域 <span className="text-red-500">*</span></Label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {serviceSettings.specialty.map((s) => (
                      <Badge key={s} variant="secondary" className="px-3 py-1">
                        {s}
                        <X
                          className="w-3 h-3 ml-2 cursor-pointer"
                          onClick={() => handleRemoveSpecialty(s)}
                        />
                      </Badge>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {specialtyOptions
                      .filter(opt => !serviceSettings.specialty.includes(opt))
                      .map((opt) => (
                        <Button
                          key={opt}
                          variant="outline"
                          size="sm"
                          onClick={() => handleAddSpecialty(opt)}
                        >
                          <Plus className="w-3 h-3 mr-1" />
                          {opt}
                        </Button>
                      ))}
                  </div>
                  <Input
                    placeholder="或输入自定义领域后按回车添加"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        const value = (e.target as HTMLInputElement).value.trim();
                        if (value && !serviceSettings.specialty.includes(value)) {
                          handleAddSpecialty(value);
                          (e.target as HTMLInputElement).value = '';
                        }
                      }
                    }}
                  />
                </div>

                {/* 咨询方式 */}
                <div className="space-y-2">
                  <Label>咨询方式 <span className="text-red-500">*</span></Label>
                  <div className="grid grid-cols-2 gap-4">
                    {consultMethodOptions.map((method) => (
                      <div key={method.value} className="flex items-center space-x-2">
                        <Switch
                          checked={serviceSettings.consult_methods.includes(method.value)}
                          onCheckedChange={() => handleToggleConsultMethod(method.value)}
                        />
                        <Label>{method.label}</Label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 咨询类型 */}
                <div className="space-y-2">
                  <Label>咨询类型</Label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {serviceSettings.consult_type.map((type) => (
                      <Badge key={type} variant="secondary" className="px-3 py-1">
                        {type}
                        <X
                          className="w-3 h-3 ml-2 cursor-pointer"
                          onClick={() => {
                            setServiceSettings({
                              ...serviceSettings,
                              consult_type: serviceSettings.consult_type.filter(t => t !== type),
                            });
                          }}
                        />
                      </Badge>
                    ))}
                  </div>
                  <Input
                    placeholder="输入咨询类型后按回车添加（如：个体咨询、团体咨询等）"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        const value = (e.target as HTMLInputElement).value.trim();
                        if (value && !serviceSettings.consult_type.includes(value)) {
                          setServiceSettings({
                            ...serviceSettings,
                            consult_type: [...serviceSettings.consult_type, value],
                          });
                          (e.target as HTMLInputElement).value = '';
                        }
                      }
                    }}
                  />
                </div>

                {/* 每日最大预约量 */}
                <div className="space-y-2">
                  <Label>每日最大预约量</Label>
                  <Input
                    type="number"
                    value={serviceSettings.max_daily_appointments}
                    onChange={(e) => setServiceSettings({ ...serviceSettings, max_daily_appointments: e.target.value })}
                    placeholder="3"
                    min={1}
                    max={10}
                  />
                  <p className="text-xs text-gray-500">设置每日最多可接受的预约数量（1-10）</p>
                </div>

                {/* 咨询费用 */}
                <div className="space-y-2">
                  <Label>咨询费用（元/小时） <span className="text-red-500">*</span></Label>
                  <Input
                    type="number"
                    value={serviceSettings.fee}
                    onChange={(e) => setServiceSettings({ ...serviceSettings, fee: e.target.value })}
                    placeholder="0"
                    min={0}
                  />
                </div>

                {/* 线下咨询地点 */}
                {serviceSettings.consult_methods.includes('线下面谈') && (
                  <div className="space-y-2">
                    <Label>线下咨询地点 <span className="text-red-500">*</span></Label>
                    <Input
                      value={serviceSettings.consult_place}
                      onChange={(e) => setServiceSettings({ ...serviceSettings, consult_place: e.target.value })}
                      placeholder="请输入咨询地点"
                    />
                  </div>
                )}

                {/* 个人简介 */}
                <div className="space-y-2">
                  <Label>个人简介</Label>
                  <Textarea
                    value={serviceSettings.bio}
                    onChange={(e) => setServiceSettings({ ...serviceSettings, bio: e.target.value })}
                    placeholder="简要介绍您的专业背景和咨询理念"
                    rows={3}
                  />
                  <p className="text-xs text-gray-500">{serviceSettings.bio.length}/200</p>
                </div>

                {/* 详细介绍 */}
                <div className="space-y-2">
                  <Label>详细介绍</Label>
                  <Textarea
                    value={serviceSettings.intro}
                    onChange={(e) => setServiceSettings({ ...serviceSettings, intro: e.target.value })}
                    placeholder="详细介绍您的专业背景、咨询经验、擅长领域等（支持富文本）"
                    rows={6}
                  />
                  <p className="text-xs text-gray-500">{serviceSettings.intro.length}/500</p>
                </div>

                <div className="flex justify-end gap-2">
                  <Button onClick={handleSaveServiceSettings} disabled={saving}>
                    {saving ? '保存中...' : '保存'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 标签页3：可预约时间设置 */}
          <TabsContent value="schedule">
            <Card>
              <CardHeader>
                <CardTitle>可预约时间设置</CardTitle>
                <CardDescription>设置您的可预约时段和不可预约时间</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* 默认可预约时间 */}
                <div className="space-y-4">
                  <Label>默认可预约时间</Label>
                  <div className="space-y-3">
                    {schedules.map((schedule) => (
                      <div key={schedule.weekday} className="flex items-center gap-4">
                        <div className="w-20">{schedule.weekdayName}</div>
                        <Switch
                          checked={schedule.is_available}
                          onCheckedChange={(checked) => {
                            const updated = schedules.map(s =>
                              s.weekday === schedule.weekday
                                ? { ...s, is_available: checked }
                                : s
                            );
                            setSchedules(updated);
                          }}
                        />
                        {schedule.is_available && (
                          <>
                            <Input
                              type="time"
                              value={schedule.start_time}
                              onChange={(e) => {
                                const updated = schedules.map(s =>
                                  s.weekday === schedule.weekday
                                    ? { ...s, start_time: e.target.value }
                                    : s
                                );
                                setSchedules(updated);
                              }}
                              className="w-32"
                            />
                            <span>至</span>
                            <Input
                              type="time"
                              value={schedule.end_time}
                              onChange={(e) => {
                                const updated = schedules.map(s =>
                                  s.weekday === schedule.weekday
                                    ? { ...s, end_time: e.target.value }
                                    : s
                                );
                                setSchedules(updated);
                              }}
                              className="w-32"
                            />
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                  <div className="flex justify-end">
                    <Button onClick={handleSaveSchedules} disabled={saving}>
                      {saving ? '保存中...' : '保存时段设置'}
                    </Button>
                  </div>
                </div>

                {/* 不可预约时段 */}
                <div className="space-y-4 border-t pt-6">
                  <div className="flex items-center justify-between">
                    <Label>不可预约时段</Label>
                    <Button onClick={handleAddUnavailablePeriod} size="sm">
                      <Plus className="w-4 h-4 mr-2" />
                      添加不可预约时段
                    </Button>
                  </div>

                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>ID</TableHead>
                          <TableHead>开始日期</TableHead>
                          <TableHead>结束日期</TableHead>
                          <TableHead>时段</TableHead>
                          <TableHead>原因</TableHead>
                          <TableHead>状态</TableHead>
                          <TableHead>创建时间</TableHead>
                          <TableHead>操作</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {unavailablePeriods.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={8} className="text-center text-gray-500">
                              暂无不可预约时段
                            </TableCell>
                          </TableRow>
                        ) : (
                          unavailablePeriods.map((period) => {
                            // 格式化日期显示
                            const formatDate = (dateStr: string) => {
                              try {
                                const date = new Date(dateStr);
                                return date.toLocaleDateString('zh-CN', { 
                                  year: 'numeric', 
                                  month: '2-digit', 
                                  day: '2-digit' 
                                });
                              } catch {
                                return dateStr;
                              }
                            };

                            // 格式化创建时间显示
                            const formatDateTime = (dateTimeStr: string) => {
                              if (!dateTimeStr) return '-';
                              try {
                                const dt = new Date(dateTimeStr);
                                return dt.toLocaleString('zh-CN', {
                                  year: 'numeric',
                                  month: '2-digit',
                                  day: '2-digit',
                                  hour: '2-digit',
                                  minute: '2-digit',
                                  second: '2-digit'
                                });
                              } catch {
                                return dateTimeStr;
                              }
                            };

                            return (
                              <TableRow key={period.id}>
                                <TableCell className="font-mono text-sm">{period.id}</TableCell>
                                <TableCell>{formatDate(period.start_date)}</TableCell>
                                <TableCell>{formatDate(period.end_date)}</TableCell>
                                <TableCell>
                                  {period.time_type === 'all' ? (
                                    <Badge variant="secondary">全天</Badge>
                                  ) : (
                                    <span className="font-mono">
                                      {period.start_time || '-'} - {period.end_time || '-'}
                                    </span>
                                  )}
                                </TableCell>
                                <TableCell>
                                  <div className="max-w-[200px] truncate" title={period.reason || '-'}>
                                    {period.reason || '-'}
                                  </div>
                                </TableCell>
                                <TableCell>
                                  <Badge 
                                    variant={period.status === 1 ? "default" : "secondary"}
                                    className={period.status === 1 ? "bg-green-500" : ""}
                                  >
                                    {period.status === 1 ? '有效' : '已失效'}
                                  </Badge>
                                </TableCell>
                                <TableCell className="text-xs text-gray-500">
                                  {formatDateTime(period.created_at)}
                                </TableCell>
                                <TableCell>
                                  <div className="flex gap-2">
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => handleEditUnavailablePeriod(period)}
                                      title="编辑"
                                    >
                                      <Edit className="w-4 h-4" />
                                    </Button>
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => handleDeleteUnavailablePeriod(period.id)}
                                      title="删除"
                                    >
                                      <Trash2 className="w-4 h-4" />
                                    </Button>
                                  </div>
                                </TableCell>
                              </TableRow>
                            );
                          })
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* 不可预约时段弹窗 */}
      <Dialog open={unavailableDialogOpen} onOpenChange={setUnavailableDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingPeriod ? '编辑' : '添加'}不可预约时段</DialogTitle>
            <DialogDescription>设置临时不可预约的时间段</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>开始日期 <span className="text-red-500">*</span></Label>
                <Input
                  type="date"
                  value={periodForm.start_date}
                  onChange={(e) => setPeriodForm({ ...periodForm, start_date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>结束日期 <span className="text-red-500">*</span></Label>
                <Input
                  type="date"
                  value={periodForm.end_date}
                  onChange={(e) => setPeriodForm({ ...periodForm, end_date: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>时段类型</Label>
              <Select
                value={periodForm.time_type}
                onValueChange={(value: 'all' | 'custom') => setPeriodForm({ ...periodForm, time_type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全天</SelectItem>
                  <SelectItem value="custom">自定义时段</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {periodForm.time_type === 'custom' && (
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>开始时间 <span className="text-red-500">*</span></Label>
                  <Input
                    type="time"
                    value={periodForm.start_time}
                    onChange={(e) => setPeriodForm({ ...periodForm, start_time: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>结束时间 <span className="text-red-500">*</span></Label>
                  <Input
                    type="time"
                    value={periodForm.end_time}
                    onChange={(e) => setPeriodForm({ ...periodForm, end_time: e.target.value })}
                  />
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label>原因</Label>
              <Input
                value={periodForm.reason}
                onChange={(e) => setPeriodForm({ ...periodForm, reason: e.target.value })}
                placeholder="如：培训、个人事务等"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setUnavailableDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSaveUnavailablePeriod}>
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

// 导出完整页面版本（如果需要独立页面）
interface CounselorSettingsProps {
  onLogout: () => void;
  userInfo?: any;
}

export function CounselorSettings({ onLogout, userInfo }: CounselorSettingsProps) {
  const [activeTab, setActiveTab] = useState('settings');
  
  const sidebarItems = [
    { id: 'settings', label: '个人设置', icon: Settings },
  ];

  return (
    <SidebarLayout 
      userInfo={userInfo} 
      onLogout={onLogout}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      items={sidebarItems}
      role="counselor"
      children={<CounselorSettingsContent userInfo={userInfo} />}
    />
  );
}
