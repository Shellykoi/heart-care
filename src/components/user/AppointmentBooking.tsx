import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Avatar, AvatarFallback } from '../ui/avatar';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../ui/dialog';
import { 
  Search, Star, Video, MessageSquare, MapPin, Calendar, Filter, X, 
  Phone, FileText, Heart, Clock, UserCheck, TrendingUp
} from 'lucide-react';
import { counselorApi, appointmentApi } from '../../services/api';
import { toast } from 'sonner';
import { cn } from '../ui/utils';

// 时间选择器组件
interface TimePickerProps {
  value: string; // 格式: "HH:MM"
  onChange: (time: string) => void;
  availableSlots?: any[];
  minTime?: string; // 最小时间（用于结束时间选择）
  maxTime?: string; // 最大时间（用于结束时间选择）
}

const TimePicker: React.FC<TimePickerProps> = ({ 
  value, 
  onChange, 
  availableSlots = [],
  minTime,
  maxTime
}) => {
  const [hour, setHour] = useState(0);
  const [minute, setMinute] = useState(0);
  const hourScrollRef = useRef<HTMLDivElement>(null);
  const minuteScrollRef = useRef<HTMLDivElement>(null);

  // 初始化时间
  useEffect(() => {
    if (value) {
      const [h, m] = value.split(':').map(Number);
      setHour(h);
      setMinute(m);
    }
  }, [value]);

  // 生成小时选项（0-23）
  const hours = Array.from({ length: 24 }, (_, i) => i);
  
  // 生成分钟选项（0, 15, 30, 45 或 0-59）
  const minutes = Array.from({ length: 4 }, (_, i) => i * 15); // 每15分钟一个选项

  // 滚动到选中的值
  useEffect(() => {
    if (hourScrollRef.current) {
      const selectedElement = hourScrollRef.current.querySelector(`[data-hour="${hour}"]`);
      if (selectedElement) {
        selectedElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [hour]);

  useEffect(() => {
    if (minuteScrollRef.current) {
      const selectedElement = minuteScrollRef.current.querySelector(`[data-minute="${minute}"]`);
      if (selectedElement) {
        selectedElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [minute]);

  // 处理小时选择
  const handleHourChange = (h: number) => {
    setHour(h);
    const newTime = `${h.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
    onChange(newTime);
  };

  // 处理分钟选择
  const handleMinuteChange = (m: number) => {
    setMinute(m);
    const newTime = `${hour.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
    onChange(newTime);
  };

  // 过滤可用的小时和分钟
  const getAvailableHours = () => {
    if (availableSlots.length === 0) return hours;
    const availableHoursSet = new Set<number>();
    availableSlots.forEach((slot: any) => {
      if (slot?.time) {
        const [h] = slot.time.split(':').map(Number);
        availableHoursSet.add(h);
        // 也添加相邻的小时（因为可能有30分钟的时段）
        if (h > 0) availableHoursSet.add(h - 1);
        if (h < 23) availableHoursSet.add(h + 1);
      }
    });
    return hours.filter(h => availableHoursSet.has(h));
  };

  const getAvailableMinutes = () => {
    // 返回每15分钟一个选项
    return minutes;
  };

  const availableHours = getAvailableHours();
  const availableMinutes = getAvailableMinutes();

  return (
    <div className="relative flex items-center justify-center gap-6 py-6">
      {/* 选中指示器背景 */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[calc(100%-2rem)] h-14 bg-blue-50/80 border-y-2 border-blue-300 rounded-lg pointer-events-none" />
      
      {/* 小时选择器 */}
      <div className="relative z-10">
        <div className="text-xs text-gray-500 mb-3 text-center font-medium">时</div>
        <div 
          ref={hourScrollRef}
          className="w-20 h-56 overflow-y-auto snap-y snap-mandatory [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
          onScroll={(e) => {
            const scrollTop = e.currentTarget.scrollTop;
            const itemHeight = 56; // h-14 = 56px
            const selectedIndex = Math.round(scrollTop / itemHeight);
            const selectedHour = availableHours[selectedIndex];
            if (selectedHour !== undefined && selectedHour !== hour) {
              handleHourChange(selectedHour);
            }
          }}
        >
          {availableHours.map((h) => {
            const isSelected = h === hour;
            const timeStr = `${h.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
            const isDisabled = 
              (minTime && timeStr < minTime) ||
              (maxTime && timeStr > maxTime);
            
            return (
              <div
                key={h}
                data-hour={h}
                className={cn(
                  "h-14 flex items-center justify-center cursor-pointer transition-all snap-center rounded-md",
                  isSelected 
                    ? "text-blue-600 font-bold text-xl scale-110 bg-blue-50" 
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-50",
                  isDisabled && "opacity-30 cursor-not-allowed"
                )}
                onClick={() => !isDisabled && handleHourChange(h)}
              >
                {h.toString().padStart(2, '0')}
              </div>
            );
          })}
        </div>
      </div>

      {/* 分隔符 */}
      <div className="text-3xl font-bold text-gray-400 mt-12 z-10">:</div>

      {/* 分钟选择器 */}
      <div className="relative z-10">
        <div className="text-xs text-gray-500 mb-3 text-center font-medium">分</div>
        <div 
          ref={minuteScrollRef}
          className="w-20 h-56 overflow-y-auto snap-y snap-mandatory [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
          onScroll={(e) => {
            const scrollTop = e.currentTarget.scrollTop;
            const itemHeight = 56; // h-14 = 56px
            const selectedIndex = Math.round(scrollTop / itemHeight);
            const selectedMinute = availableMinutes[selectedIndex];
            if (selectedMinute !== undefined && selectedMinute !== minute) {
              handleMinuteChange(selectedMinute);
            }
          }}
        >
          {availableMinutes.map((m) => {
            const isSelected = m === minute;
            const timeStr = `${hour.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
            const isDisabled = 
              (minTime && timeStr < minTime) ||
              (maxTime && timeStr > maxTime);
            
            return (
              <div
                key={m}
                data-minute={m}
                className={cn(
                  "h-14 flex items-center justify-center cursor-pointer transition-all snap-center rounded-md",
                  isSelected 
                    ? "text-blue-600 font-bold text-xl scale-110 bg-blue-50" 
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-50",
                  isDisabled && "opacity-30 cursor-not-allowed"
                )}
                onClick={() => !isDisabled && handleMinuteChange(m)}
              >
                {m.toString().padStart(2, '0')}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// 咨询方向选项
const SPECIALTY_OPTIONS = [
  { value: '学业压力', label: '学业压力' },
  { value: '情感困扰', label: '情感困扰' },
  { value: '就业焦虑', label: '就业焦虑' },
  { value: '人际关系', label: '人际关系' },
  { value: '睡眠问题', label: '睡眠问题' },
  { value: '自我成长', label: '自我成长' },
];

// 咨询方式选项（直接使用中文值）
const CONSULT_METHOD_OPTIONS = [
  { value: '线下面谈', label: '线下面谈', icon: MapPin },
  { value: '线上视频', label: '线上视频', icon: Video },
  { value: '语音咨询', label: '语音咨询', icon: Phone },
  { value: '文字咨询', label: '文字咨询', icon: MessageSquare },
];

// 排序选项
const SORT_OPTIONS = [
  { value: 'hot', label: '按热度排序' },
  { value: 'rating', label: '按好评率排序' },
  { value: 'new', label: '按最新入驻排序' },
];

export function AppointmentBooking() {
  const [selectedCounselor, setSelectedCounselor] = useState<any>(null);
  const [counselors, setCounselors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [myCounselorIds, setMyCounselorIds] = useState<Set<number>>(new Set());
  const [availableSlots, setAvailableSlots] = useState<any[]>([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [showBookingDialog, setShowBookingDialog] = useState(false);
  const [showTimePickerDialog, setShowTimePickerDialog] = useState(false);
  const [timePickerType, setTimePickerType] = useState<'start' | 'end'>('start');
  
  // 筛选条件
  const [selectedSpecialties, setSelectedSpecialties] = useState<string[]>([]);
  const [selectedMethods, setSelectedMethods] = useState<string[]>([]);
  const [selectedGender, setSelectedGender] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('hot');
  
  // 预约表单
  const [appointmentForm, setAppointmentForm] = useState({
    consult_method: '线上视频',
    appointment_date: '',
    appointment_time: '',
    start_time: '',
    end_time: '',
    description: '',
  });

  useEffect(() => {
    loadCounselors();
    loadMyCounselors();
  }, []);

  useEffect(() => {
    loadCounselors();
  }, [selectedSpecialties, selectedMethods, selectedGender, sortBy]);

  const loadMyCounselors = async () => {
    try {
      const data = await appointmentApi.getMyCounselors();
      setMyCounselorIds(new Set(data.counselor_ids || []));
    } catch (error: any) {
      console.error('加载我的咨询师失败:', error);
      console.error('错误详情:', {
        message: error?.message,
        detail: error?.detail,
        response: error?.response,
        status: error?.status,
        code: error?.code,
      });
      
      // 如果是401错误，说明Token过期，不需要显示错误提示（api.ts会处理跳转）
      if (error?.response?.status !== 401) {
        const errorMessage = error?.detail || error?.message || '加载我的咨询师失败';
        toast.error(errorMessage, {
          duration: 5000,
        });
      }
    }
  };

  const loadCounselors = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };
      
      if (selectedSpecialties.length > 0) {
        params.specialty = selectedSpecialties.join(',');
      }
      
      if (selectedGender && selectedGender !== 'all') {
        params.gender = selectedGender;
      }
      
      if (selectedMethods.length > 0) {
        params.consult_method = selectedMethods.join(',');
      }
      
      if (sortBy) {
        params.sort_by = sortBy;
      }
      
      const data = await counselorApi.search(params);
      
      // 将"我的咨询师"放在前面
      const sortedData = (data || []).sort((a, b) => {
        const aIsMy = myCounselorIds.has(a.id);
        const bIsMy = myCounselorIds.has(b.id);
        if (aIsMy && !bIsMy) return -1;
        if (!aIsMy && bIsMy) return 1;
        return 0;
      });
      
      setCounselors(sortedData);
    } catch (error: any) {
      console.error('加载咨询师列表失败:', error);
      
      // 检查是否是网络连接错误
      if (error?.isNetworkError || (!error?.response && error?.code)) {
        const errorDetail = error?.detail || '无法连接到后端服务，请检查：\n1. 后端服务是否已启动（在 src/backend 目录运行 python main.py）\n2. 后端是否运行在 http://localhost:8000\n3. 防火墙是否阻止了连接\n4. 查看浏览器控制台是否有CORS错误';
        
        if (errorDetail.includes('\n')) {
          const lines = errorDetail.split('\n');
          toast.error(lines[0], {
            description: lines.slice(1).join('\n'),
            duration: 8000,
          });
        } else {
          toast.error(errorDetail, {
            duration: 8000,
          });
        }
      } else {
        // 其他错误
        const errorMsg = error?.detail || error?.message || '加载咨询师列表失败';
        toast.error(errorMsg, {
          duration: 5000,
        });
      }
      
      setCounselors([]);
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableSlots = async (counselorId: number, date: string) => {
    if (!date) return;
    
    try {
      setLoadingSlots(true);
      console.log(`[AppointmentBooking] 加载可用时段: counselorId=${counselorId}, date=${date}`);
      const data = await counselorApi.getAvailableSlots(counselorId, date);
      console.log(`[AppointmentBooking] 可用时段数据:`, data);
      const slots = data.available_slots || [];
      console.log(`[AppointmentBooking] 可用时段数量: ${slots.length}`);
      setAvailableSlots(slots);
      
      if (slots.length === 0) {
        // 检查是否是周末或不可用日期
        const dateObj = new Date(date);
        const weekday = dateObj.getDay(); // 0=周日, 1=周一, ..., 6=周六
        const weekdayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
        const dayName = weekdayNames[weekday];
        console.log(`[AppointmentBooking] 日期 ${date} 是 ${dayName}，可用时段为空`);
      }
    } catch (error: any) {
      console.error('加载可用时段失败:', error);
      console.error('错误详情:', {
        message: error?.message,
        detail: error?.detail,
        response: error?.response,
        status: error?.status,
        code: error?.code,
      });
      
      // 提取详细的错误信息
      let errorMsg = '加载可用时段失败';
      if (error?.detail) {
        if (typeof error.detail === 'string') {
          errorMsg = error.detail;
        } else if (Array.isArray(error.detail) && error.detail.length > 0) {
          const firstError = error.detail[0];
          errorMsg = typeof firstError === 'object' && firstError?.msg 
            ? firstError.msg 
            : String(firstError);
        }
      } else if (error?.message) {
        errorMsg = error.message;
      } else if (error?.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      }
      
      toast.error(errorMsg, {
        description: `日期: ${date}`,
        duration: 5000,
      });
      setAvailableSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleSpecialtyToggle = (specialty: string) => {
    setSelectedSpecialties(prev => 
      prev.includes(specialty)
        ? prev.filter(s => s !== specialty)
        : [...prev, specialty]
    );
  };

  const handleMethodToggle = (method: string) => {
    setSelectedMethods(prev => 
      prev.includes(method)
        ? prev.filter(m => m !== method)
        : [...prev, method]
    );
  };

  const handleDateChange = (date: string) => {
    setAppointmentForm(prev => ({ ...prev, appointment_date: date, appointment_time: '', start_time: '', end_time: '' }));
    if (selectedCounselor && date) {
      loadAvailableSlots(selectedCounselor.id, date);
    }
  };

  const handleOpenBooking = (counselor: any) => {
    setSelectedCounselor(counselor);
    setShowBookingDialog(true);
    setAppointmentForm({
      consult_method: '线上视频',
      appointment_date: '',
      appointment_time: '',
      start_time: '',
      end_time: '',
      description: '',
    });
    setAvailableSlots([]);
  };

  const handleOpenDetail = (counselor: any) => {
    setSelectedCounselor(counselor);
    setShowDetailDialog(true);
  };

  const formatFee = (fee: number) => {
    if (fee === 0) return '免费';
    return `${fee}元/小时`;
  };

  const formatGender = (gender: string) => {
    return gender === 'female' ? '女' : gender === 'male' ? '男' : '未知';
  };

  const getMethodIcon = (method: string) => {
    const option = CONSULT_METHOD_OPTIONS.find(opt => opt.value === method);
    return option?.icon || Video;
  };

  const parseConsultMethods = (methodsStr: string | null) => {
    if (!methodsStr) return [];
    try {
      return JSON.parse(methodsStr);
    } catch {
      return methodsStr.split(',');
    }
  };

  const getSpecialtyTags = (specialty: string) => {
    return specialty.split(',').filter(s => s.trim());
  };

  // 生成所有可用的时间点（每30分钟一个点）
  const generateAvailableTimePoints = (slots: any[]) => {
    const timePoints = new Set<string>();
    
    // 从可用时段中提取所有时间点
    slots.forEach(slot => {
      const [startHour, startMinute] = slot.time.split(':').map(Number);
      const startMinutes = startHour * 60 + startMinute;
      
      // 生成该时段内的所有30分钟间隔的时间点
      for (let offset = 0; offset < 60; offset += 30) {
        const totalMinutes = startMinutes + offset;
        const hour = Math.floor(totalMinutes / 60);
        const minute = totalMinutes % 60;
        if (hour < 24) {
          timePoints.add(`${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`);
        }
      }
    });
    
    return Array.from(timePoints).sort();
  };

  const handleTimeRangeSelect = (startTime: string, endTime: string) => {
    // 计算时长（小时）
    const [startHour, startMinute] = startTime.split(':').map(Number);
    const [endHour, endMinute] = endTime.split(':').map(Number);
    const startMinutes = startHour * 60 + startMinute;
    const endMinutes = endHour * 60 + endMinute;
    const durationHours = (endMinutes - startMinutes) / 60;
    
    // 检查时长是否在1-3小时之间
    if (durationHours < 1 || durationHours > 3) {
      toast.error('预约时长必须在1-3小时之间');
      return;
    }
    
    setAppointmentForm(prev => ({ 
      ...prev, 
      start_time: startTime, 
      end_time: endTime,
      appointment_time: `${startTime}-${endTime}`
    }));
  };

  const handleSubmitAppointment = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!appointmentForm.appointment_date) {
      toast.error('请选择预约日期');
      return;
    }
    
    if (!appointmentForm.start_time || !appointmentForm.end_time) {
      toast.error('请选择预约时间段（开始时间和结束时间）');
      return;
    }

    // 验证时长
    const [startHour, startMinute] = appointmentForm.start_time.split(':').map(Number);
    const [endHour, endMinute] = appointmentForm.end_time.split(':').map(Number);
    const startMinutes = startHour * 60 + startMinute;
    const endMinutes = endHour * 60 + endMinute;
    const durationHours = (endMinutes - startMinutes) / 60;
    
    if (durationHours < 1 || durationHours > 3) {
      toast.error('预约时长必须在1-3小时之间');
      return;
    }

    try {
      // 计算完整的预约时间（使用开始时间）
      const date = new Date(appointmentForm.appointment_date);
      date.setHours(startHour, startMinute, 0, 0);

      // 计算结束时间（如果提供了结束时间）
      let endDateTime: Date | undefined = undefined;
      if (appointmentForm.end_time) {
        const [endHour, endMinute] = appointmentForm.end_time.split(':').map(Number);
        endDateTime = new Date(appointmentForm.appointment_date);
        endDateTime.setHours(endHour, endMinute, 0, 0);
      }

      await appointmentApi.create({
        counselor_id: selectedCounselor.id,
        consult_type: '心理咨询',
        consult_method: appointmentForm.consult_method,
        appointment_date: date.toISOString(),
        description: appointmentForm.description || undefined,
        end_time: endDateTime ? endDateTime.toISOString() : undefined,
      });

      toast.success('预约提交成功，等待咨询师确认');
      setShowBookingDialog(false);
      setAppointmentForm({
        consult_method: '线上视频',
        appointment_date: '',
        appointment_time: '',
        start_time: '',
        end_time: '',
        description: '',
      });
      loadCounselors();
      loadMyCounselors();
    } catch (error: any) {
      console.error('提交预约失败:', error);
      
      // 显示详细的错误信息
      let errorMessage = '提交预约失败';
      if (error?.detail) {
        if (typeof error.detail === 'string') {
          errorMessage = error.detail;
        } else if (Array.isArray(error.detail)) {
          // 处理验证错误数组
          errorMessage = error.detail.map((e: any) => e.msg || e.message || JSON.stringify(e)).join('; ');
        } else {
          errorMessage = JSON.stringify(error.detail);
        }
      } else if (error?.message) {
        errorMessage = error.message;
      } else if (error?.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      toast.error(errorMessage, {
        duration: 5000,
      });
    }
  };

  const resultCount = counselors.length;

  return (
    <div className="space-y-6">
      {/* 顶部筛选区 - 标签化选择 */}
      <Card className="sticky top-0 z-10 shadow-md">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            筛选咨询师
            {(selectedSpecialties.length > 0 || selectedMethods.length > 0 || selectedGender !== 'all') && (
              <Badge className="ml-2 bg-blue-600 text-white">
                {selectedSpecialties.length + selectedMethods.length + (selectedGender !== 'all' ? 1 : 0)}
              </Badge>
            )}
          </CardTitle>
          <CardDescription>根据您的需求筛选合适的心理咨询师</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 咨询方向筛选 - 标签化 */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">咨询方向</Label>
            <div className="flex flex-wrap gap-2">
              {SPECIALTY_OPTIONS.map(option => {
                const isSelected = selectedSpecialties.includes(option.value);
                return (
                  <Badge
                    key={option.value}
                    variant={isSelected ? 'default' : 'outline'}
                    className={cn(
                      "cursor-pointer transition-all duration-200 hover:scale-105 active:scale-95",
                      isSelected 
                        ? "bg-blue-600 text-white hover:bg-blue-700" 
                        : "hover:bg-blue-50"
                    )}
                    onClick={() => handleSpecialtyToggle(option.value)}
                  >
                    {option.label}
                  </Badge>
                );
              })}
            </div>
          </div>

          {/* 咨询方式筛选 - 标签化 */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">咨询方式</Label>
            <div className="flex flex-wrap gap-2">
              {CONSULT_METHOD_OPTIONS.map(option => {
                const Icon = option.icon;
                const isSelected = selectedMethods.includes(option.value);
                return (
                  <Badge
                    key={option.value}
                    variant={isSelected ? 'default' : 'outline'}
                    className={cn(
                      "cursor-pointer transition-all duration-200 hover:scale-105 active:scale-95 flex items-center gap-1",
                      isSelected 
                        ? "bg-blue-600 text-white hover:bg-blue-700" 
                        : "hover:bg-blue-50"
                    )}
                    onClick={() => handleMethodToggle(option.value)}
                  >
                    <Icon className="w-3 h-3" />
                    {option.label}
                  </Badge>
                );
              })}
            </div>
          </div>

          {/* 性别筛选和排序 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-sm font-medium">咨询师性别</Label>
              <Select value={selectedGender} onValueChange={setSelectedGender}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">不限</SelectItem>
                  <SelectItem value="female">女</SelectItem>
                  <SelectItem value="male">男</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium">排序方式</Label>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {SORT_OPTIONS.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* 已选筛选条件标签 */}
          {(selectedSpecialties.length > 0 || selectedMethods.length > 0 || selectedGender !== 'all') && (
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t">
              <span className="text-sm text-gray-500">已选条件：</span>
              {selectedSpecialties.map(specialty => (
                <Badge key={specialty} variant="secondary" className="gap-1">
                  {SPECIALTY_OPTIONS.find(opt => opt.value === specialty)?.label}
                  <X 
                    className="w-3 h-3 cursor-pointer" 
                    onClick={() => handleSpecialtyToggle(specialty)}
                  />
                </Badge>
              ))}
              {selectedMethods.map(method => {
                const option = CONSULT_METHOD_OPTIONS.find(opt => opt.value === method);
                return (
                  <Badge key={method} variant="secondary" className="gap-1">
                    {option?.label}
                    <X 
                      className="w-3 h-3 cursor-pointer" 
                      onClick={() => handleMethodToggle(method)}
                    />
                  </Badge>
                );
              })}
              {selectedGender !== 'all' && (
                <Badge variant="secondary" className="gap-1">
                  {selectedGender === 'female' ? '女' : '男'}
                  <X 
                    className="w-3 h-3 cursor-pointer" 
                    onClick={() => setSelectedGender('all')}
                  />
                </Badge>
              )}
            </div>
          )}

          {/* 筛选结果数 - 悬浮气泡样式 */}
          <div className="flex items-center justify-between pt-2 border-t">
            <div className="text-sm text-gray-600">
              找到 <span className="font-semibold text-blue-600">{resultCount}</span> 位符合条件的咨询师
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 咨询师列表 */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-flex items-center gap-2">
            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-500">加载中...</p>
          </div>
        </div>
      ) : counselors.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500">暂无符合条件的咨询师</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {counselors.map((counselor) => {
            const isMyCounselor = myCounselorIds.has(counselor.id);
            const consultMethods = parseConsultMethods(counselor.consult_methods);
            const specialtyTags = getSpecialtyTags(counselor.specialty || '');
            
            return (
              <Card 
                key={counselor.id} 
                className="w-full max-w-[340px] mx-auto hover:shadow-xl transition-all duration-200 hover:-translate-y-2 relative"
              >
                {/* 我的咨询师标签 */}
                {isMyCounselor && (
                  <Badge className="absolute top-2 left-2 bg-red-500 text-white z-10">
                    我的咨询师
                  </Badge>
                )}
                
                {/* 收藏按钮 */}
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute top-2 right-2 z-10"
                  onClick={(e) => {
                    e.stopPropagation();
                    // TODO: 实现收藏功能
                    toast.info('收藏功能开发中');
                  }}
                >
                  <Heart className="w-4 h-4" />
                </Button>

                <CardContent className="pt-6">
                  {/* 顶部：咨询师头像、姓名、性别、从业年限 */}
                  <div className="flex items-start gap-4 mb-4">
                    <Avatar className="h-16 w-16 border-2 border-blue-500">
                      <AvatarFallback className="text-lg bg-blue-100 text-blue-600">
                        {counselor.real_name?.[0] || '?'}
                      </AvatarFallback>
                    </Avatar>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-lg font-semibold">{counselor.real_name || '未知'}</h3>
                        <Badge variant="outline" className="text-xs">
                          {formatGender(counselor.gender)}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-500 mb-2">
                        从业 {counselor.experience_years || 0} 年
                      </p>
                      {/* 咨询师评分模块 */}
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 fill-yellow-400 text-yellow-400 opacity-80" />
                        <span className="text-sm font-medium">
                          {counselor.average_rating?.toFixed(1) || '0.0'}
                        </span>
                        <span className="text-xs text-gray-500">
                          ({counselor.review_count || 0} 条评价)
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* 中部：擅长领域标签（多色小胶囊） */}
                  <div className="mb-3">
                    <Label className="text-xs text-gray-500 mb-2 block">擅长领域</Label>
                    <div className="flex flex-wrap gap-1">
                      {specialtyTags.slice(0, 3).map((tag, idx) => (
                        <Badge 
                          key={idx} 
                          className={cn(
                            "text-xs",
                            idx % 2 === 0 
                              ? "bg-blue-100 text-blue-700 hover:bg-blue-200" 
                              : "bg-purple-100 text-purple-700 hover:bg-purple-200"
                          )}
                        >
                          {tag}
                        </Badge>
                      ))}
                      {specialtyTags.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{specialtyTags.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* 咨询方式 */}
                  <div className="mb-3">
                    <Label className="text-xs text-gray-500 mb-1 block">咨询方式</Label>
                    <div className="flex flex-wrap gap-1">
                      {consultMethods.slice(0, 3).map((method: string, idx: number) => {
                        const Icon = getMethodIcon(method);
                        return (
                          <Badge key={idx} variant="outline" className="text-xs gap-1">
                            <Icon className="w-3 h-3" />
                            {CONSULT_METHOD_OPTIONS.find(opt => opt.value === method)?.label || method}
                          </Badge>
                        );
                      })}
                    </div>
                  </div>

                  {/* 底部：咨询方式图标和费用 */}
                  <div className="mb-4 pt-3 border-t">
                    <div className="flex items-center gap-2 mb-2">
                      {consultMethods.slice(0, 3).map((method: string, idx: number) => {
                        const Icon = getMethodIcon(method);
                        return (
                          <div key={idx} className="p-1.5 bg-gray-100 rounded">
                            <Icon className="w-3 h-3 text-gray-600" />
                          </div>
                        );
                      })}
                    </div>
                    <div className="flex items-center justify-between">
                      <Badge className="bg-green-100 text-green-700 hover:bg-green-100 text-sm font-semibold">
                        {formatFee(counselor.fee || 0)}
                      </Badge>
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <UserCheck className="w-3 h-3" />
                        <span>{counselor.total_consultations || 0}+ 用户</span>
                      </div>
                    </div>
                  </div>

                  {/* 操作按钮 - 全宽 */}
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      className="flex-1 transition-all duration-200 hover:scale-105 active:scale-95"
                      onClick={() => handleOpenDetail(counselor)}
                    >
                      查看详情
                    </Button>
                    <Button
                      className="flex-1 gap-2 bg-blue-600 hover:bg-blue-700 transition-all duration-200 hover:scale-105 active:scale-95"
                      onClick={() => handleOpenBooking(counselor)}
                    >
                      <Calendar className="w-4 h-4" />
                      立即预约
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* 咨询师详情对话框 */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>咨询师详情</DialogTitle>
            <DialogDescription>查看咨询师的详细信息和用户评价</DialogDescription>
          </DialogHeader>
          {selectedCounselor && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <Avatar className="h-20 w-20 border-2 border-primary/20">
                  <AvatarFallback className="text-2xl bg-primary/10 text-primary">
                    {selectedCounselor.real_name?.[0] || '?'}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="text-xl font-semibold mb-1">{selectedCounselor.real_name || '未知'}</h3>
                  <p className="text-gray-500 mb-2">
                    从业 {selectedCounselor.experience_years || 0} 年 · {formatGender(selectedCounselor.gender)}
                  </p>
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span className="font-medium">{selectedCounselor.average_rating?.toFixed(1) || '0.0'}</span>
                    <span className="text-gray-500">({selectedCounselor.review_count || 0} 条评价)</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="mb-2 font-medium">擅长领域</h4>
                <div className="flex flex-wrap gap-2">
                  {getSpecialtyTags(selectedCounselor.specialty || '').map((tag, idx) => (
                    <Badge key={idx} variant="secondary">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="mb-2 font-medium">咨询方式</h4>
                <div className="flex flex-wrap gap-2">
                  {parseConsultMethods(selectedCounselor.consult_methods).map((method: string, idx: number) => {
                    const Icon = getMethodIcon(method);
                    return (
                      <Badge key={idx} variant="outline" className="gap-1">
                        <Icon className="w-3 h-3" />
                        {CONSULT_METHOD_OPTIONS.find(opt => opt.value === method)?.label || method}
                      </Badge>
                    );
                  })}
                </div>
              </div>

              <div>
                <h4 className="mb-2 font-medium">咨询费用</h4>
                <p className="text-gray-600">{formatFee(selectedCounselor.fee || 0)}</p>
              </div>

              {selectedCounselor.bio && (
                <div>
                  <h4 className="mb-2 font-medium">个人简介</h4>
                  <p className="text-gray-600 whitespace-pre-wrap">{selectedCounselor.bio}</p>
                </div>
              )}

              <div className="flex gap-2 pt-4 border-t">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setShowDetailDialog(false);
                    handleOpenBooking(selectedCounselor);
                  }}
                >
                  立即预约
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* 预约对话框 */}
      <Dialog open={showBookingDialog} onOpenChange={setShowBookingDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>预约咨询</DialogTitle>
            <DialogDescription>
              预约 {selectedCounselor?.real_name || '未知'} 的心理咨询服务
            </DialogDescription>
          </DialogHeader>
          {selectedCounselor && (
            <form onSubmit={handleSubmitAppointment} className="space-y-4">
              {/* 咨询师信息 */}
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <Avatar className="h-12 w-12">
                  <AvatarFallback>
                    {selectedCounselor.real_name?.[0] || '?'}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium">{selectedCounselor.real_name}</p>
                  <p className="text-sm text-gray-500">{formatFee(selectedCounselor.fee || 0)}</p>
                </div>
              </div>

              {/* 咨询方式 */}
              <div className="space-y-2">
                <Label>咨询方式</Label>
                <Select 
                  value={appointmentForm.consult_method}
                  onValueChange={(value) => setAppointmentForm(prev => ({ ...prev, consult_method: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="选择咨询方式" />
                  </SelectTrigger>
                  <SelectContent>
                    {CONSULT_METHOD_OPTIONS.map(option => {
                      const Icon = option.icon;
                      return (
                        <SelectItem key={option.value} value={option.value}>
                          <div className="flex items-center gap-2">
                            <Icon className="w-4 h-4" />
                            {option.label}
                          </div>
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
              </div>

              {/* 预约日期 */}
              <div className="space-y-2">
                <Label>预约日期</Label>
                <Input 
                  type="date" 
                  min={new Date().toISOString().split('T')[0]}
                  max={new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}
                  value={appointmentForm.appointment_date}
                  onChange={(e) => handleDateChange(e.target.value)}
                  required
                />
              </div>

              {/* 时间段选择 */}
              {appointmentForm.appointment_date && (
                <div className="space-y-4">
                  {loadingSlots ? (
                    <div className="text-center py-4 text-gray-500">加载中...</div>
                  ) : availableSlots.length === 0 ? (
                    <div className="text-center py-4 text-gray-500">
                      该日期暂无可用时段，请选择其他日期
                    </div>
                  ) : (
                    <>
                      <div className="grid grid-cols-2 gap-4">
                        {/* 开始时间选择 */}
                        <div className="space-y-2">
                          <Label>开始时间</Label>
                          <Button
                            type="button"
                            variant="outline"
                            className="w-full h-12 text-base font-medium flex items-center justify-center gap-2"
                            onClick={() => {
                              setTimePickerType('start');
                              setShowTimePickerDialog(true);
                            }}
                          >
                            <Clock className="w-4 h-4" />
                            {appointmentForm.start_time || '选择开始时间'}
                          </Button>
                        </div>

                        {/* 结束时间选择 */}
                        <div className="space-y-2">
                          <Label>结束时间</Label>
                          <Button
                            type="button"
                            variant="outline"
                            className="w-full h-12 text-base font-medium flex items-center justify-center gap-2"
                            onClick={() => {
                              if (!appointmentForm.start_time) {
                                toast.error('请先选择开始时间');
                                return;
                              }
                              setTimePickerType('end');
                              setShowTimePickerDialog(true);
                            }}
                            disabled={!appointmentForm.start_time}
                          >
                            <Clock className="w-4 h-4" />
                            {appointmentForm.end_time || '选择结束时间'}
                          </Button>
                        </div>
                      </div>

                      {/* 显示已选择的时间段 */}
                      {appointmentForm.start_time && appointmentForm.end_time && (
                        <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg border border-blue-200">
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="font-medium">已选择时间段：</span>
                              <span>{appointmentForm.start_time} - {appointmentForm.end_time}</span>
                            </div>
                            {(() => {
                              const [startHour, startMinute] = appointmentForm.start_time.split(':').map(Number);
                              const [endHour, endMinute] = appointmentForm.end_time.split(':').map(Number);
                              const startMinutes = startHour * 60 + startMinute;
                              const endMinutes = endHour * 60 + endMinute;
                              const durationHours = (endMinutes - startMinutes) / 60;
                              return (
                                <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                                  {durationHours.toFixed(1)}小时
                                </Badge>
                              );
                            })()}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}

              {/* 咨询诉求 */}
              <div className="space-y-2">
                <Label>咨询诉求（可选）</Label>
                <Textarea
                  placeholder="简要描述您的困扰，帮助咨询师更好地准备..."
                  rows={4}
                  value={appointmentForm.description}
                  onChange={(e) => setAppointmentForm(prev => ({ ...prev, description: e.target.value }))}
                  maxLength={500}
                />
                <p className="text-xs text-gray-500">
                  {appointmentForm.description.length}/500
                </p>
              </div>

              <div className="flex gap-2 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowBookingDialog(false)}
                >
                  取消
                </Button>
                <Button 
                  type="submit" 
                  className="flex-1"
                  disabled={!appointmentForm.appointment_date || !appointmentForm.start_time || !appointmentForm.end_time}
                >
                  提交预约
                </Button>
              </div>
            </form>
          )}
        </DialogContent>
      </Dialog>

      {/* 时间选择器对话框 */}
      <Dialog open={showTimePickerDialog} onOpenChange={setShowTimePickerDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {timePickerType === 'start' ? '选择开始时间' : '选择结束时间'}
            </DialogTitle>
            <DialogDescription>
              {timePickerType === 'start' 
                ? '请选择预约的开始时间' 
                : '请选择预约的结束时间（时长需在1-3小时之间）'}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <TimePicker
              value={timePickerType === 'start' ? appointmentForm.start_time : appointmentForm.end_time}
              onChange={(time) => {
                if (timePickerType === 'start') {
                  setAppointmentForm(prev => ({ 
                    ...prev, 
                    start_time: time,
                    // 如果已选择的结束时间在开始时间之前，清空结束时间
                    end_time: prev.end_time && (() => {
                      const [endHour, endMinute] = prev.end_time.split(':').map(Number);
                      const [startHour, startMinute] = time.split(':').map(Number);
                      const endMinutes = endHour * 60 + endMinute;
                      const startMinutes = startHour * 60 + startMinute;
                      return endMinutes > startMinutes ? prev.end_time : '';
                    })()
                  }));
                } else {
                  // 验证结束时间
                  const [startHour, startMinute] = appointmentForm.start_time.split(':').map(Number);
                  const [endHour, endMinute] = time.split(':').map(Number);
                  const startMinutes = startHour * 60 + startMinute;
                  const endMinutes = endHour * 60 + endMinute;
                  const durationHours = (endMinutes - startMinutes) / 60;
                  
                  if (durationHours < 1 || durationHours > 3) {
                    toast.error('预约时长必须在1-3小时之间');
                    return;
                  }
                  
                  handleTimeRangeSelect(appointmentForm.start_time, time);
                }
                setShowTimePickerDialog(false);
              }}
              availableSlots={availableSlots}
              minTime={timePickerType === 'end' ? appointmentForm.start_time : undefined}
              maxTime={timePickerType === 'end' ? (() => {
                // 计算最大时间（开始时间+3小时）
                if (!appointmentForm.start_time) return undefined;
                const [startHour, startMinute] = appointmentForm.start_time.split(':').map(Number);
                const maxMinutes = startHour * 60 + startMinute + 180; // 3小时 = 180分钟
                const maxHour = Math.floor(maxMinutes / 60);
                const maxMin = maxMinutes % 60;
                return `${maxHour.toString().padStart(2, '0')}:${maxMin.toString().padStart(2, '0')}`;
              })() : undefined}
            />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
