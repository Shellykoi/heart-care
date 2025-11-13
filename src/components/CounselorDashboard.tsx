import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Badge } from './ui/badge';
import { Calendar, Heart, Users, Clock, MessageSquare, BarChart3, Settings } from 'lucide-react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { counselorApi, appointmentApi, communityApi } from '../services/api';
import { SidebarLayout } from './SidebarLayout';
import { toast } from 'sonner';
import { CounselorSettingsContent } from './CounselorSettings';
import IconCompanionHealing from '../assets/images/icon_陪伴疗愈.png';
import IconSunHealing from '../assets/images/icon_日光疗愈.png';
import IconForestHealing from '../assets/images/icon_森林疗愈.png';
import IconArtHealing from '../assets/images/icon_艺术疗愈.png';
import IconMeditationHealing from '../assets/images/icon_冥想疗愈.png';
import IconTeaHealing from '../assets/images/icon_茶道疗愈.png';

const getErrorMessage = (error: any, fallback: string) => {
  if (!error) {
    return fallback;
  }

  const detail = error?.detail ?? error?.message ?? error?.msg;

  const stringify = (value: any) => {
    if (!value) {
      return '';
    }
    if (typeof value === 'string') {
      return value;
    }
    if (typeof value === 'object') {
      if (value.msg && typeof value.msg === 'string') {
        return value.msg;
      }
      try {
        return JSON.stringify(value);
      } catch {
        return '';
      }
    }
    return String(value);
  };

  if (Array.isArray(detail)) {
    const messages = detail
      .map(item => stringify(item))
      .filter(Boolean);
    if (messages.length > 0) {
      return messages.join('; ');
    }
  }

  const message = stringify(detail);
  return message || fallback;
};

interface CounselorDashboardProps {
  onLogout: () => void;
  userInfo?: any;
}

// 来访者标签页组件
function ClientsTab() {
  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      setLoading(true);
      const data = await counselorApi.getMyClients({ limit: 1000 });
      setClients(Array.isArray(data) ? data : []);
    } catch (error: any) {
      console.error('加载来访者列表失败:', error);
      toast.error(getErrorMessage(error, '加载来访者列表失败'));
      setClients([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>来访者列表</CardTitle>
        <CardDescription>查看所有来访者信息（预约过或咨询过的用户）</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8 text-gray-500">
            <p>加载中...</p>
          </div>
        ) : clients.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>暂无来访者</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>姓名</TableHead>
                <TableHead>性别</TableHead>
                <TableHead>年龄</TableHead>
                <TableHead>学校</TableHead>
                <TableHead>首次预约</TableHead>
                <TableHead>最近预约</TableHead>
                <TableHead>总预约次数</TableHead>
                <TableHead>总咨询次数</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {clients.map((client: any) => (
                <TableRow key={client.user_id}>
                  <TableCell className="font-medium">
                    {client.nickname || client.username || '用户'}
                  </TableCell>
                  <TableCell>
                    {client.gender_display || (client.gender === 'male' ? '男' : client.gender === 'female' ? '女' : '未知')}
                  </TableCell>
                  <TableCell>{client.age || '未知'}</TableCell>
                  <TableCell>{client.school || '未知'}</TableCell>
                  <TableCell>
                    {client.first_appointment_date 
                      ? new Date(client.first_appointment_date).toLocaleDateString('zh-CN')
                      : '未知'}
                  </TableCell>
                  <TableCell>
                    {client.last_appointment_date 
                      ? new Date(client.last_appointment_date).toLocaleDateString('zh-CN')
                      : '未知'}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{client.total_appointments || 0}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="default">{client.total_consultations || 0}</Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

// 咨询记录标签页组件
function ConsultationRecordsTab() {
  const [consultationRecords, setConsultationRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState<any>(null);
  const [showRecordDialog, setShowRecordDialog] = useState(false);

  useEffect(() => {
    loadConsultationRecords();
  }, []);

  const loadConsultationRecords = async () => {
    try {
      setLoading(true);
      const data: any = await appointmentApi.getConsultationRecords({ limit: 1000 });
      const records = Array.isArray(data)
        ? data
        : Array.isArray((data as any)?.records)
          ? (data as any).records
          : Array.isArray((data as any)?.data)
            ? (data as any).data
            : [];
      setConsultationRecords(records);
    } catch (error: any) {
      console.error('加载咨询记录失败:', error);
      toast.error(getErrorMessage(error, '加载咨询记录失败'));
      setConsultationRecords([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>咨询记录看板</CardTitle>
          <CardDescription>已完成的咨询记录，包含用户评分、咨询师小结等详细信息</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-gray-500">
              <p>加载中...</p>
            </div>
          ) : consultationRecords.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>暂无完成的咨询记录</p>
            </div>
          ) : (
            <div className="space-y-4">
              {consultationRecords.map((record: any) => (
                <div key={record.id} className="p-4 border rounded-lg space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-lg">
                        {record.user_name || record.user_nickname || '用户'}
                      </p>
                      <p className="text-sm text-gray-500">
                        {record.appointment_date
                          ? new Date(record.appointment_date).toLocaleString('zh-CN')
                          : '时间未知'}
                      </p>
                      <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
                        <span>账号：{record.user_username || '未知账号'}</span>
                        {record.user_student_id && (
                          <span>学号：{record.user_student_id}</span>
                        )}
                        {record.user_phone && (
                          <span>电话：{record.user_phone}</span>
                        )}
                        {record.user_email && (
                          <span>邮箱：{record.user_email}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="default">已完成</Badge>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setSelectedRecord(record);
                          setShowRecordDialog(true);
                        }}
                      >
                        <img
                          src={IconMeditationHealing}
                          alt="查看详情"
                          className="w-3 h-3 mr-1 object-contain"
                        />
                        查看详情
                      </Button>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">咨询类型：</span>
                      <Badge variant="outline" className="ml-2">
                        {record.consult_type || '咨询'}
                      </Badge>
                    </div>
                    <div>
                      <span className="text-gray-500">咨询方式：</span>
                      <span className="ml-2">{record.consult_method || '未知方式'}</span>
                    </div>
                  </div>

                  {record.description && (
                    <div>
                      <p className="text-sm text-gray-500 mb-1">咨询诉求：</p>
                      <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded line-clamp-2">
                        {record.description}
                      </p>
                    </div>
                  )}

                  {record.summary && (
                    <div>
                      <p className="text-sm text-gray-500 mb-1">咨询师小结：</p>
                      <p className="text-sm text-gray-700 bg-blue-50 p-2 rounded line-clamp-2">
                        {record.summary}
                      </p>
                    </div>
                  )}

                  <div className="flex items-center gap-4">
                    {record.rating && (
                      <div className="flex items-center gap-1">
                        <span className="text-sm text-gray-500">用户评分：</span>
                        <img
                          src={IconSunHealing}
                          alt="用户评分"
                          className="w-4 h-4 object-contain"
                        />
                        <span className="font-medium">{record.rating}</span>
                      </div>
                    )}
                    {record.review && (
                      <div className="flex-1">
                        <p className="text-sm text-gray-500 mb-1">用户评价：</p>
                        <p className="text-sm text-gray-700 bg-green-50 p-2 rounded line-clamp-1">
                          {record.review}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 咨询记录详情对话框 */}
      <Dialog open={showRecordDialog} onOpenChange={setShowRecordDialog}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>咨询记录详情</DialogTitle>
            <DialogDescription>查看完整的咨询记录信息</DialogDescription>
          </DialogHeader>
          {selectedRecord && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>用户姓名</Label>
                  <p className="mt-1 font-medium">
                    {selectedRecord.user_name || selectedRecord.user_nickname || '用户'}
                  </p>
                  <div className="mt-2 space-y-1 text-sm text-gray-600">
                    <p>账号：{selectedRecord.user_username || '未知账号'}</p>
                    {selectedRecord.user_student_id && (
                      <p>学号：{selectedRecord.user_student_id}</p>
                    )}
                    {selectedRecord.user_phone && (
                      <p>电话：{selectedRecord.user_phone}</p>
                    )}
                    {selectedRecord.user_email && (
                      <p>邮箱：{selectedRecord.user_email}</p>
                    )}
                  </div>
                </div>
                <div>
                  <Label>咨询时间</Label>
                  <p className="mt-1">
                    {selectedRecord.appointment_date
                      ? new Date(selectedRecord.appointment_date).toLocaleString('zh-CN')
                      : '时间未知'}
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>咨询类型</Label>
                  <p className="mt-1">
                    <Badge variant="outline">{selectedRecord.consult_type || '咨询'}</Badge>
                  </p>
                </div>
                <div>
                  <Label>咨询方式</Label>
                  <p className="mt-1">{selectedRecord.consult_method || '未知方式'}</p>
                </div>
              </div>

              {selectedRecord.description && (
                <div>
                  <Label>咨询诉求</Label>
                  <p className="mt-1 text-gray-600 bg-gray-50 p-3 rounded whitespace-pre-wrap">
                    {selectedRecord.description}
                  </p>
                </div>
              )}

              {selectedRecord.summary && (
                <div>
                  <Label>咨询师小结</Label>
                  <p className="mt-1 text-gray-700 bg-blue-50 p-3 rounded whitespace-pre-wrap">
                    {selectedRecord.summary}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>用户评分</Label>
                  <div className="mt-1 flex items-center gap-2">
                    {selectedRecord.rating ? (
                      <>
                        <img
                          src={IconSunHealing}
                          alt="用户评分"
                          className="w-5 h-5 object-contain"
                        />
                        <span className="font-medium">{selectedRecord.rating} / 5</span>
                      </>
                    ) : (
                      <span className="text-gray-400">未评分</span>
                    )}
                  </div>
                </div>
              </div>

              {selectedRecord.review && (
                <div>
                  <Label>用户评价</Label>
                  <p className="mt-1 text-gray-700 bg-green-50 p-3 rounded whitespace-pre-wrap">
                    {selectedRecord.review}
                  </p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}

export function CounselorDashboard({ onLogout, userInfo }: CounselorDashboardProps) {
  const [activeTab, setActiveTab] = useState('home');
  const [stats, setStats] = useState({
    pending_appointments: 0,
    today_appointments: 0,
    total_consultations: 0,
    rating_percentage: 0
  });
  const [appointments, setAppointments] = useState<any[]>([]);
  const [selectedAppointment, setSelectedAppointment] = useState<any | null>(null);
  const [appointmentDialogOpen, setAppointmentDialogOpen] = useState(false);
  const [summaryDraft, setSummaryDraft] = useState('');
  const [isEditingSummary, setIsEditingSummary] = useState(false);
  const summaryTextareaRef = useRef<HTMLTextAreaElement | null>(null);
  const [schedules, setSchedules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [counselorProfile, setCounselorProfile] = useState<any>(null);
  const [profileForm, setProfileForm] = useState({
    real_name: '',
    gender: '',
    specialty: '',
    experience_years: '',
    fee: '',
  });
  const [scheduleForm, setScheduleForm] = useState<Array<{
    weekday: number;
    is_available: boolean;
    start_time: string;
    end_time: string;
  }>>([
    { weekday: 1, is_available: true, start_time: '08:00', end_time: '22:00' },
    { weekday: 2, is_available: true, start_time: '08:00', end_time: '22:00' },
    { weekday: 3, is_available: true, start_time: '08:00', end_time: '22:00' },
    { weekday: 4, is_available: true, start_time: '08:00', end_time: '22:00' },
    { weekday: 5, is_available: true, start_time: '08:00', end_time: '22:00' },
    { weekday: 6, is_available: true, start_time: '08:00', end_time: '22:00' },
    { weekday: 7, is_available: true, start_time: '08:00', end_time: '22:00' },
  ]);
  const [maxDailyAppointments, setMaxDailyAppointments] = useState(3);
  const [postForm, setPostForm] = useState({
    category: '经验分享',
    content: '',
  });

  useEffect(() => {
    loadStats();
    loadAppointments();
    loadSchedules();
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await counselorApi.getProfile();
      const data = response.data || response;
      setCounselorProfile(data);
      
      // 处理specialty字段（可能是数组）
      let specialtyStr = '';
      if (Array.isArray(data.specialty)) {
        specialtyStr = data.specialty.join(', ');
      } else if (typeof data.specialty === 'string') {
        try {
          const parsed = JSON.parse(data.specialty);
          specialtyStr = Array.isArray(parsed) ? parsed.join(', ') : data.specialty;
        } catch {
          specialtyStr = data.specialty;
        }
      }
      
      setProfileForm({
        real_name: data.real_name || '',
        gender: data.gender || '',
        specialty: specialtyStr,
        experience_years: String(data.experience_years || ''),
        fee: String(data.fee || 0),
      });
    } catch (error: any) {
      console.error('获取咨询师资料失败:', error);
      // 如果不是咨询师，清空表单
      setProfileForm({
        real_name: '',
        gender: '',
        specialty: '',
        experience_years: '',
        fee: '',
      });
    }
  };

  const loadStats = async () => {
    try {
      const data = await counselorApi.getStats();
      setStats(data);
    } catch (error) {
      console.error('获取统计数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAppointments = async () => {
    try {
      const data: any = await appointmentApi.getMyAppointments();
      const appointmentList = Array.isArray(data)
        ? data
        : Array.isArray((data as any)?.records)
          ? (data as any).records
          : Array.isArray((data as any)?.data)
            ? (data as any).data
            : [];

      setAppointments(appointmentList || []);

      if (selectedAppointment) {
        const refreshed = appointmentList.find((item: any) => item.id === selectedAppointment.id);
        if (refreshed) {
          setSelectedAppointment(refreshed);
          setSummaryDraft(refreshed.summary || '');
        } else {
          setAppointmentDialogOpen(false);
          setSelectedAppointment(null);
          setSummaryDraft('');
        }
      }
    } catch (error) {
      console.error('获取预约列表失败:', error);
      setAppointments([]);
    }
  };

  const loadSchedules = async () => {
    try {
      const response = await counselorApi.getSchedules();
      const data = response.data || response;
      const loadedSchedules = data.schedules || [];
      setSchedules(loadedSchedules);
      
      // 更新表单状态
      const weekdays = [1, 2, 3, 4, 5, 6, 7]; // 周一到周日
      const updatedForm = weekdays.map((weekday) => {
        const schedule = loadedSchedules.find((s: any) => s.weekday === weekday);
        if (schedule) {
          return {
            weekday,
            is_available: schedule.is_available ?? true,
            start_time: schedule.start_time || '08:00',
            end_time: schedule.end_time || '22:00',
          };
        }
        return {
          weekday,
          is_available: true,
          start_time: '08:00',
          end_time: '22:00',
        };
      });
      setScheduleForm(updatedForm);
    } catch (error) {
      console.error('获取时段设置失败:', error);
    }
  };

  const handleSaveSchedules = async () => {
    try {
      // 从表单状态读取时间值
      const scheduleData = scheduleForm
        .filter(item => item.is_available)
        .map(item => ({
          weekday: item.weekday,
          start_time: item.start_time,
          end_time: item.end_time,
          max_num: maxDailyAppointments,
          is_available: true
        }));
      
      if (scheduleData.length === 0) {
        toast.error('请至少选择一个可预约的日期');
        return;
      }
      
      await counselorApi.setSchedules(scheduleData);
      toast.success('时段设置已保存');
      loadSchedules();
    } catch (error: any) {
      console.error('保存时段设置失败:', error);
      toast.error(getErrorMessage(error, '保存失败，请重试'));
    }
  };

  const handleConfirmAppointment = async (appointmentId: number) => {
    try {
      const updated: any = await appointmentApi.update(appointmentId, { status: 'confirmed' });
      toast.success('预约已确认');
      if (updated && selectedAppointment?.id === appointmentId) {
        setSelectedAppointment(updated);
        setSummaryDraft(updated.summary || '');
      }
      await loadAppointments();
      await loadStats();
    } catch (error) {
      console.error('确认预约失败:', error);
      toast.error(getErrorMessage(error, '操作失败，请重试'));
    }
  };

  const handleSaveProfile = async () => {
    try {
      // 将specialty字符串转换为数组
      const specialtyArray = profileForm.specialty
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0);
      
      await counselorApi.updateProfile({
        real_name: profileForm.real_name || undefined,
        experience_years: profileForm.experience_years ? parseInt(profileForm.experience_years) : undefined,
        specialty: specialtyArray.length > 0 ? specialtyArray : undefined,
        fee: profileForm.fee ? parseFloat(profileForm.fee) : 0,
      });
      toast.success('保存成功');
      loadProfile();
    } catch (error: any) {
      console.error('保存资料失败:', error);
      toast.error(getErrorMessage(error, '保存失败，请重试'));
    }
  };

  const handleRejectAppointment = async (appointmentId: number) => {
    try {
      const updated: any = await appointmentApi.update(appointmentId, { status: 'rejected' });
      toast.success('预约已拒绝');
      if (updated && selectedAppointment?.id === appointmentId) {
        setSelectedAppointment(updated);
        setSummaryDraft(updated.summary || '');
      }
      await loadAppointments();
      await loadStats();
      if (selectedAppointment?.id === appointmentId) {
        closeAppointmentDialog();
      }
    } catch (error) {
      console.error('拒绝预约失败:', error);
      toast.error(getErrorMessage(error, '操作失败，请重试'));
    }
  };

  const handleSaveSummary = async (appointmentId: number, summary: string) => {
    try {
      const payload = summary.trim() ? summary.trim() : undefined;
      const updated: any = await appointmentApi.update(appointmentId, { summary: payload });
      toast.success('小结已保存');
      if (updated && selectedAppointment?.id === appointmentId) {
        setSelectedAppointment(updated);
        setSummaryDraft(updated.summary || '');
        setIsEditingSummary(false);
      }
      await loadAppointments();
      setIsEditingSummary(false);
    } catch (error) {
      console.error('保存小结失败:', error);
      toast.error('保存失败，请重试');
    }
  };

  const handleConfirmComplete = async (appointmentId: number) => {
    try {
      const updated: any = await appointmentApi.update(appointmentId, { counselor_confirmed_complete: true });
      toast.success('您已确认咨询结束，等待用户确认');
      if (updated && selectedAppointment?.id === appointmentId) {
        setSelectedAppointment(updated);
        setSummaryDraft(updated.summary || '');
      }
      await loadAppointments();
      await loadStats();
    } catch (error) {
      console.error('确认完成失败:', error);
      toast.error(getErrorMessage(error, '操作失败，请重试'));
    }
  };

  const handlePublishPost = async () => {
    if (!postForm.content.trim()) {
      toast.error('请输入帖子内容');
      return;
    }

    try {
      await communityApi.createPost({
        category: postForm.category,
        content: postForm.content,
      });
      toast.success('帖子发布成功');
      setPostForm({ category: '经验分享', content: '' });
    } catch (error: any) {
      console.error('发布帖子失败:', error);
      toast.error(getErrorMessage(error, '发布失败，请重试'));
    }
  };

  const openAppointmentDialog = (appointment: any) => {
    const latest = appointments.find((item: any) => item.id === appointment.id) || appointment;
    setSelectedAppointment(latest);
    setSummaryDraft(latest?.summary || '');
    setIsEditingSummary(!latest?.summary);
    setAppointmentDialogOpen(true);
  };

  const closeAppointmentDialog = () => {
    setAppointmentDialogOpen(false);
    setSelectedAppointment(null);
    setSummaryDraft('');
    setIsEditingSummary(false);
  };

  const sidebarItems = [
    { id: 'home', label: '工作台', icon: <Heart className="w-4 h-4" /> },
    { id: 'appointments', label: '预约管理', icon: <Calendar className="w-4 h-4" /> },
    { id: 'clients', label: '来访者', icon: <Users className="w-4 h-4" /> },
    { id: 'posts', label: '发布帖子', icon: <MessageSquare className="w-4 h-4" /> },
    { id: 'records', label: '咨询记录', icon: <Clock className="w-4 h-4" /> },
    { id: 'stats', label: '数据统计', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'settings', label: '个人设置', icon: <Settings className="w-4 h-4" /> },
  ];

  const displayName = counselorProfile?.real_name || userInfo?.nickname || userInfo?.username || '咨询师';

  const tabMeta: Record<string, { title: string; subtitle?: string; description?: string }> = {
    home: {
      title: '工作台',
      subtitle: `Hi，${displayName}`,
      description: '掌握今日动态，专注支持每一位来访者'
    },
    appointments: {
      title: '预约管理',
      subtitle: `Hi，${displayName}`,
      description: '查看并处理所有预约请求，保持沟通顺畅'
    },
    clients: {
      title: '来访者',
      subtitle: `Hi，${displayName}`,
      description: '维护来访者档案，持续跟进咨询进程'
    },
    posts: {
      title: '发布帖子',
      subtitle: `Hi，${displayName}`,
      description: '分享专业洞见，用内容传递关怀'
    },
    records: {
      title: '咨询记录',
      subtitle: `Hi，${displayName}`,
      description: '记录与回顾咨询要点，持续优化服务'
    },
    stats: {
      title: '数据统计',
      subtitle: `Hi，${displayName}`,
      description: '洞察咨询数据走势，辅助决策与成长'
    },
    settings: {
      title: '个人设置',
      subtitle: `Hi，${displayName}`,
      description: '完善个人资料与偏好，为服务加分'
    }
  };

  const currentTabMeta = tabMeta[activeTab] || {
    title: '咨询师中心',
    subtitle: `Hi，${displayName}`
  };

  return (
    <SidebarLayout
      userInfo={userInfo}
      onLogout={onLogout}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      items={sidebarItems}
      role="counselor"
      children={
        <>
          <div className="mb-8">
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
        <div className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">待确认预约</p>
                      <p className="text-2xl mt-1">{loading ? '...' : stats.pending_appointments}</p>
                    </div>

                      <img
                        src={IconCompanionHealing}
                        alt="待确认预约"
                        className="w-10 h-10 object-contain"
                      />

                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">今日咨询</p>
                      <p className="text-2xl mt-1">{loading ? '...' : stats.today_appointments}</p>
                    </div>

                      <img
                        src={IconSunHealing}
                        alt="今日咨询"
                        className="w-10 h-10 object-contain"
                      />

                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">总咨询次数</p>
                      <p className="text-2xl mt-1">{loading ? '...' : stats.total_consultations}</p>
                    </div>

                      <img
                        src={IconForestHealing}
                        alt="总咨询次数"
                        className="w-10 h-10 object-contain"
                      />

                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">好评率</p>
                      <p className="text-2xl mt-1">{loading ? '...' : `${stats.rating_percentage}%`}</p>
                    </div>

                      <img
                        src={IconArtHealing}
                        alt="好评率"
                        className="w-10 h-10 object-contain"
                      />

                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Pending Appointments */}
            <Card>
              <CardHeader>
                <CardTitle>待处理预约</CardTitle>
                <CardDescription>需要您确认的预约申请</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>来访者</TableHead>
                      <TableHead>咨询方向</TableHead>
                      <TableHead>咨询方式</TableHead>
                      <TableHead>预约时间</TableHead>
                      <TableHead>操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {appointments.filter((a: any) => a.status === 'pending').length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center py-8 text-gray-500">
                          暂无待确认预约
                        </TableCell>
                      </TableRow>
                    ) : (
                      appointments.filter((a: any) => a.status === 'pending').map((appointment: any) => (
                        <TableRow key={appointment.id}>
                          <TableCell>{appointment.user?.nickname || appointment.user?.username || '用户'}</TableCell>
                          <TableCell><Badge variant="outline">{appointment.consult_type || '咨询'}</Badge></TableCell>
                          <TableCell>{appointment.consult_method || '线上'}</TableCell>
                          <TableCell>{new Date(appointment.appointment_date).toLocaleString()}</TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <Button size="sm" variant="default" className="gap-1" onClick={() => handleConfirmAppointment(appointment.id)}>
                                <img
                                  src={IconForestHealing}
                                  alt="确认预约"
                                  className="w-4 h-4 object-contain"
                                />
                                确认
                              </Button>
                              <Button size="sm" variant="outline" className="gap-1" onClick={() => handleRejectAppointment(appointment.id)}>
                                <img
                                  src={IconTeaHealing}
                                  alt="拒绝预约"
                                  className="w-4 h-4 object-contain"
                                />
                                拒绝
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            {/* Today's Schedule */}
            <Card>
              <CardHeader>
                <CardTitle>今日日程</CardTitle>
                <CardDescription>今天的咨询安排</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {appointments.filter((a: any) => a.status === 'confirmed').length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <p>今日暂无已确认的咨询</p>
                  </div>
                ) : (
                  appointments.filter((a: any) => a.status === 'confirmed').map((appointment: any) => (
                    <div key={appointment.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition">
                      <div className="flex items-center gap-4">
                        <Avatar>
                          <AvatarFallback>{appointment.user?.nickname?.[0] || appointment.user?.username?.[0] || 'U'}</AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium">{appointment.user?.nickname || appointment.user?.username || '用户'}</p>
                          <p className="text-sm text-gray-500">{appointment.consult_type || '咨询'} · {appointment.consult_method || '线上'}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <p className="text-sm">{new Date(appointment.appointment_date).toLocaleString()}</p>
                        <Button size="sm" variant="outline" onClick={() => openAppointmentDialog(appointment)}>查看详情</Button>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
        </div>
      )}

      {activeTab === 'appointments' && (
        <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>所有预约</CardTitle>
                <CardDescription>管理您的咨询预约</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>来访者</TableHead>
                      <TableHead>咨询方向</TableHead>
                      <TableHead>咨询方式</TableHead>
                      <TableHead>预约时间</TableHead>
                      <TableHead>状态</TableHead>
                      <TableHead>操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {appointments.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                          暂无预约记录
                        </TableCell>
                      </TableRow>
                    ) : (
                      appointments.map((appointment: any) => {
                        const statusMap: Record<string, string> = {
                          'pending': '待确认',
                          'confirmed': '已确认',
                          'completed': '已完成',
                          'cancelled': '已取消',
                          'rejected': '已拒绝'
                        };
                        const statusText = statusMap[appointment.status] || appointment.status;
                        
                        return (
                          <TableRow key={appointment.id}>
                            <TableCell>{appointment.user?.nickname || appointment.user?.username || '用户'}</TableCell>
                            <TableCell><Badge variant="outline">{appointment.consult_type || '咨询'}</Badge></TableCell>
                            <TableCell>{appointment.consult_method || '线上'}</TableCell>
                            <TableCell>{new Date(appointment.appointment_date).toLocaleString()}</TableCell>
                            <TableCell>
                              <Badge variant={appointment.status === 'pending' ? 'outline' : 'default'}>
                                {statusText}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Button size="sm" variant="outline" onClick={() => openAppointmentDialog(appointment)}>
                                详情
                                    </Button>
                            </TableCell>
                          </TableRow>
                        );
                      })
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            {/* Schedule Settings */}
            <Card>
              <CardHeader>
                <CardTitle>日程设置</CardTitle>
                <CardDescription>设置您的可预约时段</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                    <Label>每周可预约时段</Label>
                    <div className="space-y-2">
                      {['周一', '周二', '周三', '周四', '周五', '周六', '周日'].map((day, index) => {
                        const weekday = index + 1;
                        const schedule = scheduleForm[index];
                        return (
                          <div key={day} className="flex items-center gap-2">
                            <input 
                              type="checkbox" 
                              checked={schedule?.is_available ?? true}
                              onChange={(e) => {
                                const updated = [...scheduleForm];
                                updated[index] = { ...updated[index], is_available: e.target.checked };
                                setScheduleForm(updated);
                              }}
                              className="rounded" 
                            />
                            <span className="text-sm w-12">{day}</span>
                            <Input 
                              type="time" 
                              value={schedule?.start_time || '08:00'}
                              onChange={(e) => {
                                const updated = [...scheduleForm];
                                updated[index] = { ...updated[index], start_time: e.target.value };
                                setScheduleForm(updated);
                              }}
                              className="w-24" 
                              disabled={!schedule?.is_available}
                            />
                            <span className="text-sm">-</span>
                            <Input 
                              type="time" 
                              value={schedule?.end_time || '22:00'}
                              onChange={(e) => {
                                const updated = [...scheduleForm];
                                updated[index] = { ...updated[index], end_time: e.target.value };
                                setScheduleForm(updated);
                              }}
                              className="w-24" 
                              disabled={!schedule?.is_available}
                            />
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>每天最大预约量</Label>
                    <Input 
                      type="number" 
                      value={maxDailyAppointments}
                      onChange={(e) => setMaxDailyAppointments(parseInt(e.target.value) || 3)}
                      min="1"
                      max="5"
                    />
                    <p className="text-xs text-gray-500">建议不超过5个</p>
                  </div>
                </div>
                <Button onClick={handleSaveSchedules}>保存设置</Button>
              </CardContent>
            </Card>
        </div>
      )}

      {activeTab === 'clients' && (
        <ClientsTab />
      )}

      {activeTab === 'posts' && (
        <Card>
          <CardHeader>
            <CardTitle>发布帖子</CardTitle>
            <CardDescription>发布心理健康相关的帖子</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>分类</Label>
              <Select 
                value={postForm.category}
                onValueChange={(value) => setPostForm({ ...postForm, category: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="经验分享">经验分享</SelectItem>
                  <SelectItem value="心理健康知识">心理健康知识</SelectItem>
                  <SelectItem value="咨询技巧">咨询技巧</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>帖子内容</Label>
              <Textarea 
                placeholder="输入帖子内容..." 
                rows={10}
                value={postForm.content}
                onChange={(e) => setPostForm({ ...postForm, content: e.target.value })}
              />
            </div>
            <Button onClick={handlePublishPost}>发布帖子</Button>
          </CardContent>
        </Card>
      )}

      {activeTab === 'records' && (
        <ConsultationRecordsTab />
      )}

      {activeTab === 'stats' && (
        <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>工作统计</CardTitle>
                <CardDescription>查看您的咨询数据和表现</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <p className="text-3xl text-blue-600">{stats.total_consultations || 0}</p>
                      <p className="text-sm text-gray-600 mt-1">总咨询次数</p>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <p className="text-3xl text-green-600">{stats.average_rating?.toFixed(1) || '0.0'}</p>
                      <p className="text-sm text-gray-600 mt-1">平均评分</p>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <p className="text-3xl text-purple-600">{stats.rating_percentage || 0}%</p>
                      <p className="text-sm text-gray-600 mt-1">好评率</p>
                    </div>
                  </div>
                  <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    <p className="text-gray-400">咨询量趋势图（使用Recharts实现）</p>
                  </div>
                </div>
              </CardContent>
            </Card>
        </div>
      )}

          {activeTab === 'settings' && (
            <CounselorSettingsContent 
              userInfo={userInfo}
              onProfileUpdate={loadProfile}
            />
          )}

          <Dialog
            open={appointmentDialogOpen}
            onOpenChange={(open) => {
              if (!open) {
                closeAppointmentDialog();
              }
            }}
          >
            <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>预约详情</DialogTitle>
                <DialogDescription>查看和管理预约信息</DialogDescription>
              </DialogHeader>

              {selectedAppointment ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>来访者</Label>
                      <p className="mt-1">
                        {selectedAppointment.user?.nickname ||
                          selectedAppointment.user?.username ||
                          selectedAppointment.user_name ||
                          selectedAppointment.user_nickname ||
                          '用户'}
                      </p>
                    </div>
                    <div>
                      <Label>预约时间</Label>
                      <p className="mt-1">
                        {selectedAppointment.appointment_date
                          ? new Date(selectedAppointment.appointment_date).toLocaleString()
                          : '未知'}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>咨询方向</Label>
                      <p className="mt-1">
                        <Badge variant="outline">
                          {selectedAppointment.consult_type || '咨询'}
                        </Badge>
                      </p>
                    </div>
                    <div>
                      <Label>咨询方式</Label>
                      <p className="mt-1">
                        {selectedAppointment.consult_method ||
                          selectedAppointment.consult_method_display ||
                          '线上'}
                      </p>
                    </div>
                  </div>

                  <div>
                    <Label>预约状态</Label>
                    <p className="mt-1">
                      <Badge variant={selectedAppointment.status === 'pending' ? 'outline' : 'default'}>
                        {selectedAppointment.status_display ||
                          (selectedAppointment.status === 'pending'
                            ? '待确认'
                            : selectedAppointment.status === 'confirmed'
                              ? '已确认'
                              : selectedAppointment.status === 'completed'
                                ? '已完成'
                                : selectedAppointment.status === 'rejected'
                                  ? '已拒绝'
                                  : selectedAppointment.status === 'cancelled'
                                    ? '已取消'
                                    : selectedAppointment.status)}
                      </Badge>
                    </p>
                  </div>

                  <div>
                    <Label>咨询诉求</Label>
                    <p className="mt-1 text-gray-600 whitespace-pre-wrap">
                      {selectedAppointment.description || '暂无描述'}
                    </p>
                  </div>

                  {selectedAppointment.status === 'pending' && (
                    <div className="flex gap-2">
                      <Button className="flex-1" onClick={() => handleConfirmAppointment(selectedAppointment.id)}>
                        <img
                          src={IconForestHealing}
                          alt="确认预约"
                          className="w-4 h-4 mr-1 object-contain"
                        />
                        确认预约
                      </Button>
                      <Button variant="destructive" className="flex-1" onClick={() => handleRejectAppointment(selectedAppointment.id)}>
                        <img
                          src={IconTeaHealing}
                          alt="拒绝预约"
                          className="w-4 h-4 mr-1 object-contain"
                        />
                        拒绝
                      </Button>
                    </div>
                  )}

                  {(selectedAppointment.status === 'confirmed' || selectedAppointment.status === 'completed') && (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label>咨询小结</Label>
                        <Textarea
                          ref={summaryTextareaRef}
                          placeholder="填写本次咨询的简要总结..."
                          rows={4}
                          value={summaryDraft}
                          onChange={(e) => setSummaryDraft(e.target.value)}
                          readOnly={!!selectedAppointment.summary && !isEditingSummary}
                          className={
                            !!selectedAppointment.summary && !isEditingSummary
                              ? 'bg-gray-50 text-gray-600 cursor-default'
                              : undefined
                          }
                        />
                        <div className="flex flex-col sm:flex-row gap-2">
                          {(!selectedAppointment.summary || isEditingSummary) ? (
                            <>
                              <Button
                                className="w-full sm:flex-1"
                                onClick={() => handleSaveSummary(selectedAppointment.id, summaryDraft)}
                              >
                                {selectedAppointment.summary ? '保存修改' : '保存小结'}
                              </Button>
                              {selectedAppointment.summary && (
                                <Button
                                  type="button"
                                  variant="outline"
                                  className="w-full sm:flex-1"
                                  onClick={() => {
                                    setSummaryDraft(selectedAppointment.summary || '');
                                    setIsEditingSummary(false);
                                  }}
                                >
                                  取消修改
                                </Button>
                              )}
                            </>
                          ) : (
                            <Button
                              type="button"
                              variant="outline"
                              className="w-full sm:w-auto"
                              onClick={() => {
                                setIsEditingSummary(true);
                                requestAnimationFrame(() => {
                                  summaryTextareaRef.current?.focus();
                                  const length = summaryDraft.length;
                                  summaryTextareaRef.current?.setSelectionRange(length, length);
                                });
                              }}
                            >
                              修改小结
                            </Button>
                          )}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-gray-600">用户确认：</span>
                          <Badge variant={selectedAppointment.user_confirmed_complete ? 'default' : 'outline'}>
                            {selectedAppointment.user_confirmed_complete ? '已确认' : '未确认'}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-gray-600">咨询师确认：</span>
                          <Badge variant={selectedAppointment.counselor_confirmed_complete ? 'default' : 'outline'}>
                            {selectedAppointment.counselor_confirmed_complete ? '已确认' : '未确认'}
                          </Badge>
                        </div>
                      </div>

                      {selectedAppointment.status === 'confirmed' && (() => {
                        const appointmentDate = selectedAppointment.appointment_date
                          ? new Date(selectedAppointment.appointment_date)
                          : null;
                        const consultationEndTime = appointmentDate
                          ? new Date(appointmentDate.getTime() + 60 * 60 * 1000)
                          : null;
                        const now = new Date();
                        const canConfirm = consultationEndTime ? now >= consultationEndTime : false;

                        return (
                          <>
                            {!canConfirm && (
                              <div className="p-2 bg-yellow-50 rounded text-sm text-yellow-700">
                                预约时间段尚未结束，请等待预约时间结束后再确认
                              </div>
                            )}
                            {canConfirm && !selectedAppointment.counselor_confirmed_complete && (
                              <Button
                                className="w-full"
                                variant="default"
                                onClick={() => handleConfirmComplete(selectedAppointment.id)}
                              >
                                确认咨询结束
                              </Button>
                            )}
                          </>
                        );
                      })()}

                      {selectedAppointment.user_confirmed_complete &&
                        selectedAppointment.counselor_confirmed_complete &&
                        selectedAppointment.status === 'completed' && (
                          <div className="p-2 bg-green-50 rounded text-sm text-green-700">
                            双方已确认，咨询已完成
                          </div>
                        )}
                    </div>
                  )}

                  {selectedAppointment.status === 'completed' && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-1">
                        <span className="text-sm text-gray-600">用户评分：</span>
                        {selectedAppointment.rating ? (
                          <>
                        <img
                          src={IconSunHealing}
                          alt="用户评分"
                          className="w-4 h-4 object-contain"
                        />
                            <span className="font-medium">{selectedAppointment.rating}</span>
                          </>
                        ) : (
                          <span className="text-sm text-gray-500">未评分</span>
                        )}
                      </div>
                      {selectedAppointment.review && (
                        <div>
                          <Label>用户评价</Label>
                          <p className="mt-1 text-gray-700 bg-green-50 p-3 rounded whitespace-pre-wrap">
                            {selectedAppointment.review}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div className="py-6 text-center text-gray-500">暂未选择预约</div>
              )}
            </DialogContent>
          </Dialog>
        </>
      }
    />
  );
}
