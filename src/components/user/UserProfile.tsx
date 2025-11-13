import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Avatar, AvatarFallback } from '../ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { User, Lock, Shield, Bell, Trash2, Download } from 'lucide-react';
import { userApi } from '../../services/api';
import { toast } from 'sonner';

export function UserProfile() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [formData, setFormData] = useState({
    nickname: '',
    gender: 'prefer-not',
    age: '',
    school: '',
  });

  // 加载用户资料
  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response: any = await userApi.getProfile();
      const data = response?.data || response;
      setUserProfile(data);
      
      // 将后端的gender值映射到前端的值
      // 后端: male, female, other -> 前端: male, female, prefer-not
      let genderValue = 'prefer-not';
      if (data.gender === 'male') {
        genderValue = 'male';
      } else if (data.gender === 'female') {
        genderValue = 'female';
      } else if (data.gender === 'other') {
        genderValue = 'prefer-not';
      }
      
      // 填充表单数据
      setFormData({
        nickname: data.nickname || '',
        gender: genderValue,
        age: data.age ? String(data.age) : '',
        school: data.school || '',
      });
    } catch (error: any) {
      console.error('加载用户资料失败:', error);
      toast.error(error?.detail || error?.message || '加载用户资料失败');
    } finally {
      setLoading(false);
    }
  };

  // 保存用户资料
  const handleSave = async () => {
    try {
      setSaving(true);
      
      // 准备更新数据
      const updateData: any = {};
      
      if (formData.nickname && formData.nickname.trim()) {
        updateData.nickname = formData.nickname.trim();
      }
      
      // 性别字段处理：prefer-not -> other，其他值保持不变
      if (formData.gender) {
        if (formData.gender === 'prefer-not') {
          updateData.gender = 'other';
        } else {
          updateData.gender = formData.gender;
        }
      }
      
      // age字段需要转换为整数
      if (formData.age && formData.age.trim()) {
        const ageNum = parseInt(formData.age.trim());
        if (isNaN(ageNum) || ageNum < 0 || ageNum > 150) {
          toast.error('年龄必须是0-150之间的数字');
          setSaving(false);
          return;
        }
        updateData.age = ageNum;
      }
      
      if (formData.school && formData.school.trim()) {
        updateData.school = formData.school.trim();
      }

      await userApi.updateProfile(updateData);
      toast.success('保存成功');
      
      // 重新加载数据
      await loadProfile();
    } catch (error: any) {
      console.error('保存用户资料失败:', error);
      toast.error(error?.detail || error?.message || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">加载中...</p>
      </div>
    );
  }

  // 获取头像显示字符
  const getAvatarInitial = () => {
    if (userProfile?.nickname) {
      return userProfile.nickname.charAt(0).toUpperCase();
    }
    if (userProfile?.username) {
      return userProfile.username.charAt(0).toUpperCase();
    }
    return 'U';
  };

  return (
    <div className="space-y-6">
      <Tabs defaultValue="basic" className="space-y-6">
        <TabsList>
          <TabsTrigger value="basic" className="gap-2">
            <User className="w-4 h-4" />
            基础信息
          </TabsTrigger>
          <TabsTrigger value="privacy" className="gap-2">
            <Shield className="w-4 h-4" />
            隐私设置
          </TabsTrigger>
          <TabsTrigger value="security" className="gap-2">
            <Lock className="w-4 h-4" />
            安全中心
          </TabsTrigger>
          <TabsTrigger value="notifications" className="gap-2">
            <Bell className="w-4 h-4" />
            通知设置
          </TabsTrigger>
        </TabsList>

        {/* Basic Info */}
        <TabsContent value="basic">
          <Card>
            <CardHeader>
              <CardTitle>个人信息</CardTitle>
              <CardDescription>管理您的基本信息</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center gap-6">
                <Avatar className="h-20 w-20">
                  <AvatarFallback className="text-2xl bg-gradient-to-br from-blue-500 to-purple-600 text-white">
                    {getAvatarInitial()}
                  </AvatarFallback>
                </Avatar>
                <Button variant="outline">更换头像</Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="nickname">昵称</Label>
                  <Input 
                    id="nickname" 
                    value={formData.nickname}
                    onChange={(e) => setFormData({ ...formData, nickname: e.target.value })}
                    placeholder="请输入昵称"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="gender">性别</Label>
                  <Select 
                    value={formData.gender}
                    onValueChange={(value) => setFormData({ ...formData, gender: value })}
                  >
                    <SelectTrigger id="gender">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">男</SelectItem>
                      <SelectItem value="female">女</SelectItem>
                      <SelectItem value="prefer-not">不透露</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="age">年龄</Label>
                  <Input 
                    id="age" 
                    type="number" 
                    value={formData.age}
                    onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                    placeholder="请输入年龄"
                    min="0"
                    max="150"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="school">学校/单位</Label>
                  <Input 
                    id="school" 
                    value={formData.school}
                    onChange={(e) => setFormData({ ...formData, school: e.target.value })}
                    placeholder="请输入学校或单位"
                  />
                </div>

                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="username">用户名</Label>
                  <Input 
                    id="username" 
                    value={userProfile?.username || ''} 
                    disabled 
                    className="bg-gray-50"
                  />
                  <p className="text-xs text-gray-500">用户名不可修改</p>
                </div>
              </div>

              <Button onClick={handleSave} disabled={saving}>
                {saving ? '保存中...' : '保存更改'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Privacy Settings */}
        <TabsContent value="privacy">
          <Card>
            <CardHeader>
              <CardTitle>隐私设置</CardTitle>
              <CardDescription>控制您的信息可见性和数据保留</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <h4 className="mb-1">公开测评结果</h4>
                    <p className="text-sm text-gray-500">允许咨询师查看您的测评报告</p>
                  </div>
                  <Switch />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <h4 className="mb-1">隐身浏览</h4>
                    <p className="text-sm text-gray-500">不在本地缓存浏览记录</p>
                  </div>
                  <Switch />
                </div>

                <div className="p-4 border rounded-lg space-y-3">
                  <h4>咨询记录保存时长</h4>
                  <Select defaultValue="3months">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1month">1个月</SelectItem>
                      <SelectItem value="3months">3个月</SelectItem>
                      <SelectItem value="forever">永久保留</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="p-4 border rounded-lg space-y-3">
                  <h4>数据管理</h4>
                  <div className="flex gap-2">
                    <Button variant="outline" className="gap-2">
                      <Download className="w-4 h-4" />
                      导出我的数据
                    </Button>
                    <Button variant="destructive" className="gap-2">
                      <Trash2 className="w-4 h-4" />
                      删除历史记录
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Settings */}
        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle>安全中心</CardTitle>
              <CardDescription>管理您的账户安全</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="p-4 border rounded-lg">
                  <h4 className="mb-3">修改密码</h4>
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <Label htmlFor="current-password">当前密码</Label>
                      <Input id="current-password" type="password" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="new-password">新密码</Label>
                      <Input id="new-password" type="password" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="confirm-password">确认新密码</Label>
                      <Input id="confirm-password" type="password" />
                    </div>
                    <Button>更新密码</Button>
                  </div>
                </div>

                <div className="p-4 border rounded-lg">
                  <h4 className="mb-3">绑定信息</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm">手机号</p>
                        <p className="text-sm text-gray-500">138****5678</p>
                      </div>
                      <Button variant="outline" size="sm">更换</Button>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm">邮箱</p>
                        <p className="text-sm text-gray-500">未绑定</p>
                      </div>
                      <Button variant="outline" size="sm">绑定</Button>
                    </div>
                  </div>
                </div>

                <div className="p-4 border rounded-lg">
                  <h4 className="mb-3">登录日志</h4>
                  <div className="space-y-2">
                    {[
                      { time: '2025-11-04 14:23', location: '湖北·武汉', device: 'Chrome浏览器' },
                      { time: '2025-11-03 09:15', location: '湖北·武汉', device: 'Chrome浏览器' },
                    ].map((log, index) => (
                      <div key={index} className="flex items-center justify-between text-sm p-2 bg-gray-50 rounded">
                        <div>
                          <p>{log.time}</p>
                          <p className="text-gray-500">{log.location} · {log.device}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notification Settings */}
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>通知设置</CardTitle>
              <CardDescription>管理您的消息通知偏好</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <h4 className="mb-1">预约提醒</h4>
                  <p className="text-sm text-gray-500">咨询前1小时发送提醒</p>
                </div>
                <Switch defaultChecked />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <h4 className="mb-1">心理科普推送</h4>
                  <p className="text-sm text-gray-500">接收个性化健康知识</p>
                </div>
                <Switch defaultChecked />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <h4 className="mb-1">社区互动通知</h4>
                  <p className="text-sm text-gray-500">有人回复或点赞您的帖子</p>
                </div>
                <Switch defaultChecked />
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <h4 className="mb-1">测评提醒</h4>
                  <p className="text-sm text-gray-500">定期测评健康提醒</p>
                </div>
                <Switch />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
