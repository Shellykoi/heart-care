import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Users, UserCheck, FileText, BarChart3, Shield, CheckCircle, XCircle, Plus, Trash2, Eye, Star } from 'lucide-react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { SidebarLayout } from './SidebarLayout';
import { adminApi, healthApi, appointmentApi } from '../services/api';
import { toast } from 'sonner';
import IconCompanionHealing from '../assets/images/icon_陪伴疗愈.png';
import IconForestHealing from '../assets/images/icon_森林疗愈.png';
import IconSunHealing from '../assets/images/icon_日光疗愈.png';
import IconArtHealing from '../assets/images/icon_艺术疗愈.png';
import IconMeditationHealing from '../assets/images/icon_冥想疗愈.png';

interface AdminDashboardProps {
  onLogout: () => void;
  userInfo?: any;
}

export function AdminDashboard({ onLogout, userInfo }: AdminDashboardProps) {
  const [activeTab, setActiveTab] = useState('home');
  const [counselors, setCounselors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statistics, setStatistics] = useState<any>(null);
  const [statisticsLoading, setStatisticsLoading] = useState(true);
  const [consultationRecords, setConsultationRecords] = useState<any[]>([]);
  const [recordsLoading, setRecordsLoading] = useState(true);
  const [users, setUsers] = useState<any[]>([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [pendingPosts, setPendingPosts] = useState<any[]>([]);
  const [postsLoading, setPostsLoading] = useState(false);
  const [newCounselorDialog, setNewCounselorDialog] = useState(false);
  const [newCounselorForm, setNewCounselorForm] = useState({
    real_name: '',
    gender: 'female',
    specialty: '',
    experience_years: 1,
    bio: '',
  });

  useEffect(() => {
    // 检查后端连接
    checkBackendConnection();
    
    if (activeTab === 'home') {
      loadStatistics();
    }
    if (activeTab === 'counselors') {
      loadCounselors();
    }
    if (activeTab === 'records') {
      loadConsultationRecords();
    }
    if (activeTab === 'users') {
      loadUsers();
    }
    if (activeTab === 'content') {
      loadPendingPosts();
    }
  }, [activeTab]);

  const checkBackendConnection = async () => {
    try {
      await healthApi.check();
    } catch (error: any) {
      console.error('后端服务连接失败:', error);
      const errorDetail = error?.detail || error?.message || '无法连接到后端服务，请检查后端是否运行在 http://localhost:8000';
      // 如果错误信息包含换行符，使用description字段显示
      if (errorDetail.includes('\n')) {
        const lines = errorDetail.split('\n');
        toast.error(lines[0], {
          description: lines.slice(1).join('\n'),
          duration: 8000,
        });
      } else {
        toast.error(errorDetail, {
          duration: 5000,
        });
      }
    }
  };

  const loadStatistics = async (retryCount = 0) => {
    try {
      setStatisticsLoading(true);
      
      // 先检查后端连接
      try {
        await healthApi.check();
      } catch (healthError: any) {
        // 传递详细的错误信息
        const errorDetail = healthError?.detail || healthError?.message || '无法连接到后端服务，请检查后端是否运行在 http://localhost:8000';
        const connectionError: any = new Error(errorDetail);
        connectionError.detail = errorDetail;
        connectionError.isNetworkError = true;
        throw connectionError;
      }
      
      const data = await adminApi.getStatistics();
      setStatistics(data);
    } catch (error: any) {
      console.error('加载统计数据失败:', error);
      // 处理各种错误情况
      let errorMessage = '加载统计数据失败';
      
      // 优先检查 detail 字段（这是后端返回的错误信息）
      if (error?.detail) {
        const detailStr = typeof error.detail === 'string' ? error.detail : '加载统计数据失败';
        errorMessage = detailStr;
      } 
      // 检查是否是网络错误
      else if (error?.isNetworkError || !error?.response || error?.message?.includes('无法连接到后端服务')) {
        if (error?.detail) {
          errorMessage = error.detail;
        } else if (error?.message) {
          errorMessage = error.message;
        } else {
          errorMessage = '网络连接失败，请检查后端服务是否运行在 http://localhost:8000';
        }
        
        // 如果是网络错误且未重试过，尝试重试一次
        if (retryCount < 1 && (error?.isNetworkError || !error?.response)) {
          console.log('尝试重试加载统计数据...');
          setTimeout(() => {
            loadStatistics(retryCount + 1);
          }, 2000);
          return;
        }
      }
      // 检查 HTTP 状态码
      else if (error?.response) {
        if (error.response.status === 401) {
          errorMessage = '认证失败，请重新登录';
        } else if (error.response.status === 403) {
          errorMessage = '权限不足，需要管理员权限';
        } else if (error.response.data?.detail) {
          errorMessage = error.response.data.detail;
        } else {
          errorMessage = `请求失败 (${error.response.status})`;
        }
      }
      // 其他情况
      else if (error?.message) {
        errorMessage = error.message;
      }
      
      // 如果错误信息包含换行符，使用description字段显示
      if (errorMessage.includes('\n')) {
        const lines = errorMessage.split('\n');
        toast.error(lines[0], {
          description: lines.slice(1).join('\n'),
          duration: 8000,
        });
      } else {
        toast.error(errorMessage, {
          duration: 5000,
        });
      }
    } finally {
      setStatisticsLoading(false);
    }
  };

  const loadCounselors = async (retryCount = 0) => {
    try {
      setLoading(true);
      
      // 先检查后端连接
      try {
        await healthApi.check();
      } catch (healthError: any) {
        // 传递详细的错误信息
        const errorDetail = healthError?.detail || healthError?.message || '无法连接到后端服务，请检查后端是否运行在 http://localhost:8000';
        const connectionError: any = new Error(errorDetail);
        connectionError.detail = errorDetail;
        connectionError.isNetworkError = true;
        throw connectionError;
      }
      
      const data = await adminApi.getAllCounselors({ limit: 100 });
      const counselorList = Array.isArray(data) ? data : [];
      setCounselors(counselorList);
      if (counselorList.length === 0) {
        toast.info('暂无咨询师数据');
      }
    } catch (error: any) {
      console.error('加载咨询师列表失败:', error);
      // 处理各种错误情况
      let errorMessage = '加载咨询师列表失败';
      
      // 优先检查 detail 字段（这是后端返回的错误信息）
      if (error?.detail) {
        errorMessage = typeof error.detail === 'string' ? error.detail : '加载咨询师列表失败';
      } 
      // 检查是否是网络错误
      else if (error?.isNetworkError || !error?.response || error?.message?.includes('无法连接到后端服务')) {
        if (error?.detail) {
          errorMessage = error.detail;
        } else if (error?.message) {
          errorMessage = error.message;
        } else {
          errorMessage = '网络连接失败，请检查后端服务是否运行在 http://localhost:8000';
        }
        
        // 如果是网络错误且未重试过，尝试重试一次
        if (retryCount < 1 && (error?.isNetworkError || !error?.response)) {
          console.log('尝试重试加载咨询师列表...');
          setTimeout(() => {
            loadCounselors(retryCount + 1);
          }, 2000);
          return;
        }
      }
      // 检查 HTTP 状态码
      else if (error?.response) {
        if (error.response.status === 401) {
          errorMessage = '认证失败，请重新登录';
        } else if (error.response.status === 403) {
          errorMessage = '权限不足，需要管理员权限';
        } else if (error.response.data?.detail) {
          errorMessage = error.response.data.detail;
        } else {
          errorMessage = `请求失败 (${error.response.status})`;
        }
      }
      // 其他情况
      else if (error?.message) {
        errorMessage = error.message;
      }
      
      // 如果错误信息包含换行符，使用description字段显示
      if (errorMessage.includes('\n')) {
        const lines = errorMessage.split('\n');
        toast.error(lines[0], {
          description: lines.slice(1).join('\n'),
          duration: 8000,
        });
      } else {
        toast.error(errorMessage, {
          duration: 5000,
        });
      }
      setCounselors([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCounselor = async () => {
    try {
      // 验证必填字段
      if (!newCounselorForm.real_name.trim()) {
        toast.error('请输入姓名');
        return;
      }
      if (!newCounselorForm.specialty.trim()) {
        toast.error('请输入擅长领域');
        return;
      }
      // 密码由后端统一设置为默认值（123456）
      const response = await adminApi.createCounselorAccount({
        ...newCounselorForm,
      });
      
      console.log('创建咨询师成功:', response);
      toast.success('咨询师账户创建成功');
      setNewCounselorDialog(false);
      setNewCounselorForm({
        real_name: '',
        gender: 'female',
        specialty: '',
        experience_years: 1,
        bio: '',
      });
      loadCounselors();
    } catch (error: any) {
      console.error('创建咨询师失败:', error);
      const errorMessage = error?.response?.data?.detail || error?.detail || error?.message || '创建失败，请检查输入信息';
      toast.error(errorMessage);
    }
  };

  const handleDeleteCounselor = async (counselorId: number) => {
    if (!confirm('确定要删除该咨询师吗？')) return;
    
    try {
      await adminApi.deleteCounselor(counselorId);
      toast.success('咨询师已删除');
      loadCounselors();
    } catch (error: any) {
      toast.error(error?.detail || '删除失败');
    }
  };

  const loadConsultationRecords = async () => {
    try {
      setRecordsLoading(true);
      const data = await appointmentApi.getAllConsultationRecords({ limit: 1000 });
      setConsultationRecords(Array.isArray(data) ? data : []);
    } catch (error: any) {
      console.error('加载咨询记录失败:', error);
      toast.error(error?.detail || error?.message || '加载咨询记录失败');
      setConsultationRecords([]);
    } finally {
      setRecordsLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      setUsersLoading(true);
      const response = await adminApi.getAllUsers({ limit: 1000 });
      const data = response.data || response;
      setUsers(data.users || []);
    } catch (error: any) {
      console.error('加载用户列表失败:', error);
      toast.error(error?.detail || error?.message || '加载用户列表失败');
      setUsers([]);
    } finally {
      setUsersLoading(false);
    }
  };

  const loadPendingPosts = async () => {
    try {
      setPostsLoading(true);
      const response = await adminApi.getPendingPosts();
      const data = response.data || response;
      setPendingPosts(data.pending_posts || []);
    } catch (error: any) {
      console.error('加载待审核帖子失败:', error);
      toast.error(error?.detail || error?.message || '加载待审核帖子失败');
      setPendingPosts([]);
    } finally {
      setPostsLoading(false);
    }
  };

  const handleDisableUser = async (userId: number) => {
    if (!confirm('确定要禁用该用户吗？')) return;
    
    try {
      await adminApi.disableUser(userId);
      toast.success('用户已禁用');
      loadUsers();
    } catch (error: any) {
      toast.error(error?.detail || error?.message || '禁用失败');
    }
  };

  const handleApprovePost = async (postId: number) => {
    try {
      await adminApi.approvePost(postId);
      toast.success('帖子已审核通过');
      loadPendingPosts();
    } catch (error: any) {
      toast.error(error?.detail || error?.message || '审核失败');
    }
  };

  const handleDeletePost = async (postId: number) => {
    if (!confirm('确定要删除该帖子吗？')) return;
    
    try {
      await adminApi.deletePost(postId);
      toast.success('帖子已删除');
      loadPendingPosts();
    } catch (error: any) {
      toast.error(error?.detail || error?.message || '删除失败');
    }
  };

  const sidebarItems = [
    { id: 'home', label: '数据概览', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'records', label: '咨询记录', icon: <FileText className="w-4 h-4" /> },
    { id: 'users', label: '用户管理', icon: <Users className="w-4 h-4" /> },
    { id: 'counselors', label: '咨询师管理', icon: <UserCheck className="w-4 h-4" /> },
    { id: 'content', label: '内容管理', icon: <FileText className="w-4 h-4" /> },
    { id: 'system', label: '系统设置', icon: <Shield className="w-4 h-4" /> },
  ];

  const [selectedRecord, setSelectedRecord] = useState<any>(null);
  const [showRecordDialog, setShowRecordDialog] = useState(false);

  const displayName = userInfo?.nickname || userInfo?.username || '管理员';

  const tabMeta: Record<string, { title: string; subtitle?: string; description?: string }> = {
    home: {
      title: '数据概览',
      subtitle: `Hi，${displayName}`,
      description: '掌握平台运行状态与关键指标'
    },
    records: {
      title: '咨询记录',
      subtitle: `Hi，${displayName}`,
      description: '审阅与管理平台内的咨询记录'
    },
    users: {
      title: '用户管理',
      subtitle: `Hi，${displayName}`,
      description: '维护用户信息，保障使用体验'
    },
    counselors: {
      title: '咨询师管理',
      subtitle: `Hi，${displayName}`,
      description: '审核入驻咨询师，支持专业发展'
    },
    content: {
      title: '内容管理',
      subtitle: `Hi，${displayName}`,
      description: '审核社区内容，引导健康交流'
    },
    system: {
      title: '系统设置',
      subtitle: `Hi，${displayName}`,
      description: '配置平台规则与运营参数'
    }
  };

  const currentTabMeta = tabMeta[activeTab] || {
    title: '管理中心',
    subtitle: `Hi，${displayName}`
  };

  return (
    <SidebarLayout
      userInfo={userInfo}
      onLogout={onLogout}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      items={sidebarItems}
      role="admin"
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
                      <p className="text-sm text-gray-500">注册用户</p>
                      {statisticsLoading ? (
                        <p className="text-2xl mt-1 text-gray-400">加载中...</p>
                      ) : (
                        <p className="text-2xl mt-1">{statistics?.total_users || 0}</p>
                      )}
                    </div>
                    <div className="bg-blue-100 p-3 rounded-lg">
                      <img
                        src={IconCompanionHealing}
                        alt="注册用户"
                        className="w-10 h-10 object-contain"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">在职咨询师</p>
                      {statisticsLoading ? (
                        <p className="text-2xl mt-1 text-gray-400">加载中...</p>
                      ) : (
                        <p className="text-2xl mt-1">{statistics?.total_counselors || 0}</p>
                      )}
                    </div>
                    <div className="bg-purple-100 p-3 rounded-lg">
                      <img
                        src={IconForestHealing}
                        alt="在职咨询师"
                        className="w-10 h-10 object-contain"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">总咨询次数</p>
                      {statisticsLoading ? (
                        <p className="text-2xl mt-1 text-gray-400">加载中...</p>
                      ) : (
                        <p className="text-2xl mt-1">{statistics?.total_appointments || 0}</p>
                      )}
                    </div>
                    <div className="bg-green-100 p-3 rounded-lg">
                      <img
                        src={IconSunHealing}
                        alt="总咨询次数"
                        className="w-10 h-10 object-contain"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">测评参与</p>
                      {statisticsLoading ? (
                        <p className="text-2xl mt-1 text-gray-400">加载中...</p>
                      ) : (
                        <p className="text-2xl mt-1">{statistics?.total_tests || 0}</p>
                      )}
                    </div>
                    <div className="bg-orange-100 p-3 rounded-lg">
                      <img
                        src={IconArtHealing}
                        alt="测评参与"
                        className="w-10 h-10 object-contain"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

        </div>
      )}

      {activeTab === 'records' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>咨询记录数据看板</CardTitle>
              <CardDescription>所有已完成的咨询记录，包含用户评分、咨询师小结等详细信息</CardDescription>
            </CardHeader>
            <CardContent>
              {recordsLoading ? (
                <div className="text-center py-8 text-gray-500">
                  <p>加载中...</p>
                </div>
              ) : consultationRecords.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>暂无咨询记录</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>用户姓名</TableHead>
                      <TableHead>咨询师姓名</TableHead>
                      <TableHead>咨询类型</TableHead>
                      <TableHead>咨询方式</TableHead>
                      <TableHead>咨询时间</TableHead>
                      <TableHead>用户评分</TableHead>
                      <TableHead>咨询师小结</TableHead>
                      <TableHead>用户评价</TableHead>
                      <TableHead>操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {consultationRecords.map((record: any) => (
                      <TableRow key={record.id}>
                        <TableCell className="font-medium">
                          {record.user_name || record.user_nickname || '未知用户'}
                        </TableCell>
                        <TableCell>{record.counselor_name || '未知咨询师'}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{record.consult_type || '咨询'}</Badge>
                        </TableCell>
                        <TableCell>{record.consult_method || '未知方式'}</TableCell>
                        <TableCell>
                          {record.appointment_date
                            ? new Date(record.appointment_date).toLocaleString('zh-CN')
                            : '时间未知'}
                        </TableCell>
                        <TableCell>
                          {record.rating ? (
                            <div className="flex items-center gap-1">
                              <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                              <span>{record.rating}</span>
                            </div>
                          ) : (
                            <span className="text-gray-400">未评分</span>
                          )}
                        </TableCell>
                        <TableCell>
                          {record.summary ? (
                            <div className="max-w-xs truncate" title={record.summary}>
                              {record.summary}
                            </div>
                          ) : (
                            <span className="text-gray-400">暂无小结</span>
                          )}
                        </TableCell>
                        <TableCell>
                          {record.review ? (
                            <div className="max-w-xs truncate" title={record.review}>
                              {record.review}
                            </div>
                          ) : (
                            <span className="text-gray-400">暂无评价</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => {
                              setSelectedRecord(record);
                              setShowRecordDialog(true);
                            }}
                          >
                            <Eye className="w-3 h-3 mr-1" />
                            查看详情
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
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
                        {selectedRecord.user_name || selectedRecord.user_nickname || '未知用户'}
                      </p>
                    </div>
                    <div>
                      <Label>咨询师姓名</Label>
                      <p className="mt-1 font-medium">
                        {selectedRecord.counselor_name || '未知咨询师'}
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

                  <div>
                    <Label>咨询时间</Label>
                    <p className="mt-1">
                      {selectedRecord.appointment_date
                        ? new Date(selectedRecord.appointment_date).toLocaleString('zh-CN')
                        : '时间未知'}
                    </p>
                  </div>

                  {selectedRecord.description && (
                    <div>
                      <Label>咨询诉求</Label>
                      <p className="mt-1 text-gray-600 bg-gray-50 p-3 rounded">
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
                            <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                            <span className="font-medium">{selectedRecord.rating} / 5</span>
                          </>
                        ) : (
                          <span className="text-gray-400">未评分</span>
                        )}
                      </div>
                    </div>
                    <div>
                      <Label>评价时间</Label>
                      <p className="mt-1 text-sm text-gray-500">
                        {selectedRecord.review ? '已评价' : '未评价'}
                      </p>
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
        </div>
      )}

      {activeTab === 'users' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>用户列表</CardTitle>
              <CardDescription>管理平台所有注册用户</CardDescription>
            </CardHeader>
            <CardContent>
              {usersLoading ? (
                <div className="text-center py-8 text-gray-500">
                  <p>加载中...</p>
                </div>
              ) : users.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>暂无用户</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>用户名</TableHead>
                      <TableHead>昵称</TableHead>
                      <TableHead>性别</TableHead>
                      <TableHead>年龄</TableHead>
                      <TableHead>学校</TableHead>
                      <TableHead>角色</TableHead>
                      <TableHead>状态</TableHead>
                      <TableHead>注册时间</TableHead>
                      <TableHead>操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {users.map((user: any) => (
                      <TableRow key={user.id}>
                        <TableCell className="font-medium">{user.username}</TableCell>
                        <TableCell>{user.nickname || '-'}</TableCell>
                        <TableCell>
                          {user.gender === 'male' ? '男' : user.gender === 'female' ? '女' : '其他'}
                        </TableCell>
                        <TableCell>{user.age || '-'}</TableCell>
                        <TableCell>{user.school || '-'}</TableCell>
                        <TableCell>
                          <Badge variant={user.role === 'admin' ? 'default' : 'outline'}>
                            {user.role === 'admin' ? '管理员' : user.role === 'counselor' ? '咨询师' : '用户'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={user.is_active ? 'default' : 'destructive'}>
                            {user.is_active ? '正常' : '已禁用'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {new Date(user.created_at).toLocaleDateString('zh-CN')}
                        </TableCell>
                        <TableCell>
                          {user.is_active && (
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleDisableUser(user.id)}
                            >
                              禁用
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'counselors' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>咨询师管理</CardTitle>
                  <CardDescription>管理平台咨询师</CardDescription>
                </div>
                <Dialog open={newCounselorDialog} onOpenChange={setNewCounselorDialog}>
                  <DialogTrigger asChild>
                    <Button className="gap-2">
                      <Plus className="w-4 h-4" />
                      新增咨询师
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>新增咨询师</DialogTitle>
                      <DialogDescription>为咨询师创建账户</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label>姓名</Label>
                        <Input
                          value={newCounselorForm.real_name}
                          onChange={(e) => setNewCounselorForm({ ...newCounselorForm, real_name: e.target.value })}
                          placeholder="输入咨询师姓名"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>性别</Label>
                        <Select
                          value={newCounselorForm.gender}
                          onValueChange={(value) => setNewCounselorForm({ ...newCounselorForm, gender: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="female">女</SelectItem>
                            <SelectItem value="male">男</SelectItem>
                            <SelectItem value="other">其他</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>擅长领域</Label>
                        <Input
                          value={newCounselorForm.specialty}
                          onChange={(e) => setNewCounselorForm({ ...newCounselorForm, specialty: e.target.value })}
                          placeholder="输入擅长领域"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>从业年限</Label>
                        <Input
                          type="number"
                          value={newCounselorForm.experience_years}
                          onChange={(e) => setNewCounselorForm({ ...newCounselorForm, experience_years: parseInt(e.target.value) || 1 })}
                          placeholder="输入从业年限"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>个人简介</Label>
                        <Input
                          value={newCounselorForm.bio}
                          onChange={(e) => setNewCounselorForm({ ...newCounselorForm, bio: e.target.value })}
                          placeholder="输入个人简介"
                        />
                      </div>
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-sm text-blue-600">
                      密码将自动生成：123456（首次登录后请尽快修改）
                        </p>
                      </div>
                      <Button className="w-full" onClick={handleCreateCounselor}>
                        创建账户
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>姓名</TableHead>
                    <TableHead>擅长领域</TableHead>
                    <TableHead>咨询次数</TableHead>
                    <TableHead>评分</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead>操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                        加载中...
                      </TableCell>
                    </TableRow>
                  ) : counselors.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                        暂无咨询师
                      </TableCell>
                    </TableRow>
                  ) : (
                    counselors.map((counselor: any) => {
                      // 解析specialty字段（可能是JSON字符串）
                      let specialtyDisplay = '';
                      try {
                        if (typeof counselor.specialty === 'string') {
                          if (counselor.specialty.startsWith('[')) {
                            const parsed = JSON.parse(counselor.specialty);
                            specialtyDisplay = Array.isArray(parsed) ? parsed.join(', ') : counselor.specialty;
                          } else {
                            specialtyDisplay = counselor.specialty;
                          }
                        } else {
                          specialtyDisplay = Array.isArray(counselor.specialty) 
                            ? counselor.specialty.join(', ') 
                            : String(counselor.specialty || '');
                        }
                      } catch {
                        specialtyDisplay = counselor.specialty || '';
                      }
                      
                      return (
                        <TableRow key={counselor.id}>
                          <TableCell>{counselor.real_name}</TableCell>
                          <TableCell>{specialtyDisplay}</TableCell>
                          <TableCell>{counselor.total_consultations || 0}</TableCell>
                          <TableCell>{counselor.average_rating?.toFixed(1) || '0.0'}</TableCell>
                          <TableCell>
                            <Badge variant={counselor.status === 'active' ? 'default' : 'outline'}>
                              {counselor.status === 'active' ? '在职' : '待审核'}
                            </Badge>
                          </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Eye className="w-3 h-3 mr-1" />
                              查看
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleDeleteCounselor(counselor.id)}
                            >
                              <Trash2 className="w-3 h-3 mr-1" />
                              删除
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'content' && (
        <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>内容审核</CardTitle>
                <CardDescription>管理平台社区帖子，包括被多人举报的帖子</CardDescription>
              </CardHeader>
              <CardContent>
                {postsLoading ? (
                  <div className="text-center py-8 text-gray-500">
                    <p>加载中...</p>
                  </div>
                ) : pendingPosts.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <p>暂无待审核的帖子</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {pendingPosts.map((post: any) => (
                      <div key={post.id} className="p-4 border rounded-lg space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-medium">帖子 #{post.id}</h4>
                              <Badge variant="outline">{post.category}</Badge>
                              {post.report_count > 0 && (
                                <Badge variant="destructive">
                                  被举报 {post.report_count} 次
                                </Badge>
                              )}
                            </div>
                            <p className="text-sm text-gray-500">
                              作者：{post.author?.nickname || post.author?.username || '未知'} · 
                              {new Date(post.created_at).toLocaleString('zh-CN')}
                            </p>
                          </div>
                          <Badge variant="outline">待审核</Badge>
                        </div>
                        <div className="bg-gray-50 p-3 rounded">
                          <p className="text-sm text-gray-700 whitespace-pre-wrap line-clamp-5">
                            {post.content}
                          </p>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                          <span>点赞 {post.like_count || 0}</span>
                          <span>评论 {post.comment_count || 0}</span>
                          {post.report_count > 0 && (
                            <span className="text-red-500">举报 {post.report_count}</span>
                          )}
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            variant="default"
                            onClick={() => handleApprovePost(post.id)}
                          >
                            <CheckCircle className="w-3 h-3 mr-1" />
                            通过
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => handleDeletePost(post.id)}
                          >
                            <XCircle className="w-3 h-3 mr-1" />
                            删除
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
        </div>
      )}

      {activeTab === 'system' && (
        <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>系统设置</CardTitle>
                <CardDescription>配置平台运营参数</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <h4>平台信息</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm">平台名称</label>
                      <Input defaultValue="南湖心理咨询平台" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm">客服热线</label>
                      <Input defaultValue="400-123-4567" />
                    </div>
                  </div>
                </div>
                <div className="space-y-2">
                  <h4>预约规则</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm">提前取消时限（小时）</label>
                      <Input type="number" defaultValue="24" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm">咨询费用范围</label>
                      <Input defaultValue="0-200元" />
                    </div>
                  </div>
                </div>
                <Button>保存设置</Button>
              </CardContent>
            </Card>
        </div>
      )}
        </>
      }
    />
  );
}
