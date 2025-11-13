import { useState, useEffect } from 'react';
import { LoginPage } from './components/LoginPage';
import { UserDashboard } from './components/UserDashboard';
import { CounselorDashboard } from './components/CounselorDashboard';
import { AdminDashboard } from './components/AdminDashboard';
import { Toaster } from './components/ui/sonner';

type UserRole = 'user' | 'counselor' | 'admin' | null;

const normalizeRole = (role: any): UserRole => {
  if (!role) return 'user';
  if (typeof role === 'string') {
    const normalized = role.toLowerCase().replace(/^userrole\./, '');
    return (['user', 'counselor', 'admin'].includes(normalized) ? normalized : 'user') as UserRole;
  }
  if (typeof role === 'object') {
    if ('value' in role) {
      return normalizeRole(role.value);
    }
    if ('name' in role) {
      return normalizeRole(role.name);
    }
  }
  return 'user';
};

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userRole, setUserRole] = useState<UserRole>(null);
  const [userInfo, setUserInfo] = useState<any>(null);

  // 检查本地存储中的登录状态
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userInfoStr = localStorage.getItem('user_info');
    
    if (token && userInfoStr) {
      try {
        const user = JSON.parse(userInfoStr);
        const normalizedRole = normalizeRole(user.role);
        setUserInfo({ ...user, role: normalizedRole });
        setUserRole(normalizedRole);
        setIsLoggedIn(true);
      } catch (e) {
        // 清除无效的本地存储
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
      }
    }
  }, []);

  const handleLogin = (role: UserRole, userInfo: any) => {
    setIsLoggedIn(true);
    setUserRole(role);
    setUserInfo(userInfo);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    setIsLoggedIn(false);
    setUserRole(null);
    setUserInfo(null);
  };

  if (!isLoggedIn) {
    return (
      <>
        <LoginPage onLogin={handleLogin} />
        <Toaster />
      </>
    );
  }

  return (
    <>
      {userRole === 'user' && <UserDashboard onLogout={handleLogout} userInfo={userInfo} />}
      {userRole === 'counselor' && <CounselorDashboard onLogout={handleLogout} userInfo={userInfo} />}
      {userRole === 'admin' && <AdminDashboard onLogout={handleLogout} userInfo={userInfo} />}
      <Toaster />
    </>
  );
}
