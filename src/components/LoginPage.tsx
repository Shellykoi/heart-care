import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Heart, Lock, Mail, Phone, User } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { authApi } from '../services/api';
import { toast } from 'sonner';

type UserRole = 'user' | 'counselor' | 'admin' | null;

const normalizeRoleValue = (role: any): string => {
  if (!role) return 'user';
  if (typeof role === 'string') {
    return role.toLowerCase().replace(/^userrole\./, '');
  }
  if (typeof role === 'object') {
    if (typeof role.value === 'string') {
      return role.value.toLowerCase().replace(/^userrole\./, '');
    }
    if (typeof role.name === 'string') {
      return role.name.toLowerCase().replace(/^userrole\./, '');
    }
  }
  return 'user';
};

interface LoginPageProps {
  onLogin: (role: UserRole, userInfo: any) => void;
}

export function LoginPage({ onLogin }: LoginPageProps) {
  const [loginType, setLoginType] = useState<'student' | 'counselor' | 'admin'>('student');
  const [loginAccount, setLoginAccount] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [registerData, setRegisterData] = useState({
    username: '',
    phone: '',
    email: '',
    student_id: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginAccount || !loginPassword) {
      toast.error('请输入账号和密码');
      return;
    }

    setIsLoading(true);
    try {
      const response: any = await authApi.login({
        account: loginAccount,
        password: loginPassword,
      });
      
      // 验证登录类型和用户角色是否匹配
      const normalizedRole = normalizeRoleValue(response?.user_info?.role);
      const validRole = ['user', 'counselor', 'admin'].includes(normalizedRole)
        ? (normalizedRole as Exclude<UserRole, null>)
        : 'user';
      const userRole = validRole;
      const expectedRole = loginType === 'student' ? 'user' : loginType === 'counselor' ? 'counselor' : 'admin';
      
      if (userRole !== expectedRole) {
        const roleNames: Record<string, string> = {
          'user': '学生',
          'counselor': '心理咨询师',
          'admin': '管理员',
          'volunteer': '志愿者'
        };
        const roleKey = normalizedRole in roleNames ? normalizedRole : userRole;
        toast.error(`登录类型不匹配，请选择${roleNames[roleKey]}登录`);
        setIsLoading(false);
        return;
      }
      
      // 保存 Token 和用户信息
      localStorage.setItem('access_token', response.access_token);
      const userInfo = {
        ...response.user_info,
        role: userRole
      };
      localStorage.setItem('user_info', JSON.stringify(userInfo));
      
      // 根据用户角色跳转
      onLogin(userRole, userInfo);
      toast.success('登录成功');
    } catch (error: any) {
      console.error('登录错误:', error);
      const errorMessage = error?.detail || error?.message || error?.toString() || '登录失败，请检查账号和密码';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!registerData.username || !registerData.password) {
      toast.error('请输入用户名和密码');
      return;
    }
    if (registerData.password.length < 6) {
      toast.error('密码长度至少6位');
      return;
    }

    setIsLoading(true);
    try {
      const response: any = await authApi.register({
        username: registerData.username,
        password: registerData.password,
        phone: registerData.phone || undefined,
        email: registerData.email || undefined,
        student_id: registerData.student_id || undefined,
      });
      
      // 保存 Token 和用户信息
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user_info', JSON.stringify(response.user_info));
      
      // 注册成功后自动登录
      onLogin('user', response.user_info);
      toast.success('注册成功');
    } catch (error: any) {
      console.error('注册错误:', error);
      const errorMessage = error?.detail || error?.message || error?.toString() || '注册失败，请检查输入信息';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid md:grid-cols-2 gap-8 items-center">
        {/* Left Side - Branding */}
        <div className="hidden md:flex flex-col justify-center space-y-6 p-8">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-4 rounded-2xl">
              <Heart className="w-12 h-12 text-white" />
            </div>
            <div>
              <h1 className="text-4xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                南湖心理咨询
              </h1>
              <p className="text-gray-600 mt-1">专业·安全·温暖</p>
            </div>
          </div>
          
          <div className="space-y-4 text-gray-600">
            <div className="flex items-start gap-3 p-4 bg-white/60 rounded-lg backdrop-blur-sm">
              <div className="bg-blue-100 p-2 rounded-lg">
                <Lock className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="text-gray-900 mb-1">隐私保护</h3>
                <p className="text-sm">所有个人数据加密存储，支持匿名咨询</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3 p-4 bg-white/60 rounded-lg backdrop-blur-sm">
              <div className="bg-purple-100 p-2 rounded-lg">
                <User className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h3 className="text-gray-900 mb-1">专业服务</h3>
                <p className="text-sm">持证心理咨询师，提供专业心理健康服务</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3 p-4 bg-white/60 rounded-lg backdrop-blur-sm">
              <div className="bg-green-100 p-2 rounded-lg">
                <Heart className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h3 className="text-gray-900 mb-1">全天候支持</h3>
                <p className="text-sm">7x24小时在线咨询，紧急热线随时待命</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <Card className="shadow-xl border-0">
          <CardHeader>
            <CardTitle>欢迎回来</CardTitle>
            <CardDescription>登录您的账户继续使用服务</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="login">登录</TabsTrigger>
                <TabsTrigger value="register">注册</TabsTrigger>
              </TabsList>
              
              <TabsContent value="login" className="space-y-4">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label>登录类型</Label>
                    <Select value={loginType} onValueChange={(value: 'student' | 'counselor' | 'admin') => setLoginType(value)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="student">学生登录</SelectItem>
                        <SelectItem value="counselor">心理咨询师登录</SelectItem>
                        <SelectItem value="admin">管理员登录</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="login-account">用户名</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="login-account"
                        type="text"
                        placeholder="请输入用户名"
                        className="pl-10"
                        value={loginAccount}
                        onChange={(e) => setLoginAccount(e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="login-password">密码</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="login-password"
                        type="password"
                        placeholder="请输入密码"
                        className="pl-10"
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <a href="#" className="text-blue-600 hover:underline">忘记密码？</a>
                    <a href="#" className="text-blue-600 hover:underline">短信验证码登录</a>
                  </div>

                  <Button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700" disabled={isLoading}>
                    {isLoading ? '登录中...' : '立即登录'}
                  </Button>
                </form>
              </TabsContent>
              
              <TabsContent value="register" className="space-y-4">
                <form onSubmit={handleRegister} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="reg-username">用户名</Label>
                    <Input
                      id="reg-username"
                      type="text"
                      placeholder="请输入用户名"
                      value={registerData.username}
                      onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="reg-phone">手机号（可选）</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="reg-phone"
                        type="tel"
                        placeholder="请输入手机号"
                        className="pl-10"
                        value={registerData.phone}
                        onChange={(e) => setRegisterData({ ...registerData, phone: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="reg-email">邮箱（可选）</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="reg-email"
                        type="email"
                        placeholder="请输入邮箱"
                        className="pl-10"
                        value={registerData.email}
                        onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="reg-student">学号（可选）</Label>
                    <Input
                      id="reg-student"
                      type="text"
                      placeholder="高校用户请输入学号"
                      value={registerData.student_id}
                      onChange={(e) => setRegisterData({ ...registerData, student_id: e.target.value })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="reg-password">密码</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="reg-password"
                        type="password"
                        placeholder="请设置密码（6-20位）"
                        className="pl-10"
                        value={registerData.password}
                        onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <Button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700" disabled={isLoading}>
                    {isLoading ? '注册中...' : '注册账号'}
                  </Button>

                  <p className="text-xs text-gray-500 text-center">
                    注册即表示同意《用户协议》和《隐私政策》
                  </p>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
