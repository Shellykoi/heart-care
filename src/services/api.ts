/**
 * API 服务层 - 统一管理所有 API 调用
 * 使用 axios 进行 HTTP 请求
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

type EnvRecord = Record<string, string | boolean | undefined>;

// API 基础配置
const metaEnv =
  typeof import.meta !== 'undefined'
    ? ((import.meta as unknown as { env?: EnvRecord }).env ?? undefined)
    : undefined;

const DEFAULT_DEV_API_BASE_URL = 'http://localhost:8000/api';
const DEFAULT_PROD_API_BASE_URL = 'https://heart-care-m28z.onrender.com/api';
const isDevMode =
  (typeof metaEnv?.DEV === 'boolean' && metaEnv.DEV) ||
  (typeof metaEnv?.MODE === 'string' && metaEnv.MODE === 'development');

const envApiBase =
  typeof metaEnv?.VITE_API_BASE_URL === 'string'
    ? metaEnv.VITE_API_BASE_URL.trim()
    : '';

let resolvedBaseUrl = envApiBase;
if (!resolvedBaseUrl) {
  resolvedBaseUrl = isDevMode ? DEFAULT_DEV_API_BASE_URL : DEFAULT_PROD_API_BASE_URL;
}
if (!resolvedBaseUrl && typeof window !== 'undefined') {
  resolvedBaseUrl = `${window.location.origin.replace(/\/+$/, '')}/api`;
}
if (!resolvedBaseUrl) {
  resolvedBaseUrl = DEFAULT_DEV_API_BASE_URL;
}

const API_BASE_URL = resolvedBaseUrl.replace(/\/+$/, '');
const API_ORIGIN = API_BASE_URL.endsWith('/api')
  ? API_BASE_URL.slice(0, -4)
  : API_BASE_URL;
const DEFAULT_API_ORIGIN = (isDevMode ? DEFAULT_DEV_API_BASE_URL : DEFAULT_PROD_API_BASE_URL).replace(
  /\/api$/,
  ''
);

// 创建 axios 实例
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 增加超时时间到60秒，避免请求超时
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加 Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error: AxiosError | any) => {
    // 处理网络错误（连接失败、超时等）
    if (!error.response) {
      // 更详细地识别网络错误类型
      let errorMessage = '网络连接失败';
      let errorDetail = '请检查后端服务是否运行';
      
      // 检查是否是自定义错误对象（来自healthApi.check）
      const customError = error as any;
      
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        errorMessage = '请求超时';
        errorDetail = '请求时间过长，可能是后端服务响应较慢，请稍后重试或检查后端服务状态';
      } else if (error.code === 'ERR_NETWORK' || error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
        errorMessage = '网络连接失败';
        // 提供更详细的诊断信息
        if (customError.detail && typeof customError.detail === 'string' && customError.detail.includes('\n')) {
          errorDetail = customError.detail;
        } else {
          errorDetail = `无法连接到后端服务，请检查：\n1. 后端服务是否已启动（在 src/backend 目录运行 python main.py）\n2. 后端是否运行在 ${API_ORIGIN || DEFAULT_API_ORIGIN}\n3. 防火墙是否阻止了连接\n4. 查看浏览器控制台是否有CORS错误`;
        }
      } else if (error.message) {
        errorMessage = error.message;
        errorDetail = error.message;
      }
      
      const networkError = {
        detail: errorDetail,
        message: errorMessage,
        code: error.code || 'NETWORK_ERROR',
        isNetworkError: true
      };
      return Promise.reject(networkError);
    }
    
    // 处理 HTTP 错误响应
    if (error.response.status === 401) {
      // Token 过期，清除本地存储并跳转到登录页
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      window.location.href = '/';
    }
    
    // 确保错误对象格式统一，便于前端处理
    const errorData = error.response.data || { detail: error.message || '请求失败' };
    // 如果error.response.data是对象，直接返回；否则包装成对象
    if (typeof errorData === 'object' && errorData !== null && !Array.isArray(errorData)) {
      return Promise.reject(errorData);
    }
    return Promise.reject({ detail: errorData || '请求失败' });
  }
);

// ============ 认证相关 ============
export const authApi = {
  // 用户注册
  register: (data: {
    username: string;
    password: string;
    phone?: string;
    email?: string;
    student_id?: string;
  }) => api.post('/auth/register', data),

  // 用户登录
  login: (data: { account: string; password: string }) =>
    api.post('/auth/login', data),

  // 用户登出
  logout: () => api.post('/auth/logout'),

  // 获取当前用户信息
  getCurrentUser: () => api.get('/auth/me'),
};

// ============ 用户相关 ============
export const userApi = {
  // 获取用户资料
  getProfile: () => api.get('/users/profile'),

  // 上传用户头像
  uploadAvatar: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/users/avatar/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // 更新用户资料
  updateProfile: (data: {
    nickname?: string;
    gender?: string;
    age?: number;
    school?: string;
  }) => api.put('/users/profile', data),

  // 删除账户
  deleteAccount: () => api.delete('/users/profile'),

  // 获取预约历史
  getAppointmentHistory: () => api.get('/users/appointments/history'),

  // 获取测评历史
  getTestHistory: () => api.get('/users/tests/history'),

  // 获取用户统计数据
  getStats: () => api.get('/users/stats'),

  // 获取咨询活动数据（时间和咨询时间统计）
  getConsultationActivity: () => api.get('/users/stats/consultation-activity'),
};

// ============ 咨询师相关 ============
export const counselorApi = {
  // 申请成为咨询师
  apply: (data: {
    real_name: string;
    gender: string;
    specialty: string;
    experience_years: number;
    certificate_url?: string;
    bio?: string;
  }) => api.post('/counselors/apply', data),

  // 搜索咨询师
  search: (params?: {
    specialty?: string;
    gender?: string;
    consult_method?: string;
    sort_by?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/counselors/search', { params }),

  // 获取咨询师详情
  getDetail: (counselorId: number) => api.get(`/counselors/${counselorId}`),

  // 获取咨询师完整资料
  getProfile: () => api.get('/counselors/profile'),

  // 更新咨询师完整资料（分步表单）
  updateProfile: (data: {
    real_name?: string;
    gender?: string;
    age?: number;
    experience_years?: number;
    avatar?: string;
    specialty?: string[];
    qualification?: string;
    certificate_url?: string[];
    consult_methods?: string[];
    consult_type?: string[];
    fee?: number;
    consult_place?: string;
    max_daily_appointments?: number;
    intro?: string;
    bio?: string;
    need_review?: boolean;
  }) => api.put('/counselors/profile', data),

  // 上传头像
  uploadAvatar: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/counselors/avatar/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // 获取咨询师统计数据
  getStats: () => api.get('/counselors/stats/mine'),

  // 获取咨询活动统计数据
  getConsultationActivity: () => api.get('/counselors/stats/consultation-activity'),

  // 批量设置咨询师时段
  setSchedules: (schedules: Array<{
    weekday: number;
    start_time: string;
    end_time: string;
    max_num?: number;
    is_available?: boolean;
  }>) => api.post('/counselors/schedules', { schedules }),

  // 更新单个星期的时段
  updateSchedule: (weekday: number, data: {
    start_time: string;
    end_time: string;
    max_num?: number;
  }) => api.put(`/counselors/schedules/${weekday}`, data),

  // 重置时段（删除自定义设置，使用默认8:00-22:00）
  resetSchedule: (weekday?: number) => api.post('/counselors/schedules/reset', { weekday }),

  // 获取咨询师时段
  getSchedules: () => api.get('/counselors/schedules'),

  // 获取来访者列表
  getMyClients: (params?: { skip?: number; limit?: number }) =>
    api.get('/counselors/my/clients', { params }),

  // 获取咨询师可用时段
  getAvailableSlots: (counselorId: number, date: string) =>
    api.get(`/counselors/${counselorId}/available-slots`, { params: { date } }),

  // 获取不可预约时段列表
  getUnavailablePeriods: (skip?: number, limit?: number) =>
    api.get('/counselors/unavailable', { params: { skip, limit } }),

  // 添加不可预约时段
  addUnavailablePeriod: (data: {
    start_date: string;
    end_date: string;
    time_type: 'all' | 'custom';
    start_time?: string;
    end_time?: string;
    reason?: string;
  }) => api.post('/counselors/unavailable', data),

  // 更新不可预约时段
  updateUnavailablePeriod: (periodId: number, data: {
    start_date?: string;
    end_date?: string;
    time_type?: 'all' | 'custom';
    start_time?: string;
    end_time?: string;
    reason?: string;
  }) => api.put(`/counselors/unavailable/${periodId}`, data),

  // 删除不可预约时段
  deleteUnavailablePeriod: (periodId: number) =>
    api.delete(`/counselors/unavailable/${periodId}`),
};

// ============ 预约相关 ============
export const appointmentApi = {
  // 创建预约
  create: (data: {
    counselor_id: number;
    consult_type: string;
    consult_method: string;
    appointment_date: string;
    description?: string;
    end_time?: string;  // 结束时间（可选，用于自定义时间范围）
  }) => api.post('/appointments/create', data),

  // 获取我的预约列表
  getMyAppointments: () => api.get('/appointments/my-appointments'),

  // 获取预约详情
  getDetail: (appointmentId: number) =>
    api.get(`/appointments/${appointmentId}`),

  // 更新预约
  update: (appointmentId: number, data: {
    status?: string;
    summary?: string;
    user_confirmed_complete?: boolean;
    counselor_confirmed_complete?: boolean;
    rating?: number;
    review?: string;
  }) => api.put(`/appointments/${appointmentId}`, data),

  // 取消预约
  cancel: (appointmentId: number) =>
    api.delete(`/appointments/${appointmentId}`),

  // 获取我的咨询师列表（历史预约过的）
  getMyCounselors: () => api.get('/appointments/my-counselors'),

  // 获取咨询记录列表
  getConsultationRecords: (params?: { skip?: number; limit?: number }) =>
    api.get('/appointments/consultation-records', { params }),

  // 获取所有咨询记录（仅管理员）
  getAllConsultationRecords: (params?: { skip?: number; limit?: number }) =>
    api.get('/appointments/consultation-records/all', { params }),
};

// ============ 心理测评相关 ============
export const testApi = {
  // 获取测评量表列表
  getScales: () => api.get('/tests/scales'),

  // 获取测评量表详情
  getScaleDetail: (scaleId: number) => api.get(`/tests/scales/${scaleId}`),

  // 提交测评结果
  submit: (data: {
    scale_id: number;
    score: number;
    level?: string;
    result_json?: string;
  }) => api.post('/tests/submit', data),

  // 获取我的测评报告列表
  getMyReports: () => api.get('/tests/reports/mine'),

  // 获取测评报告详情
  getReportDetail: (reportId: number) =>
    api.get(`/tests/reports/${reportId}`),
};

// ============ 健康科普相关 ============
export const contentApi = {
  // 获取内容列表
  getList: (params?: {
    content_type?: string;
    category?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/content/list', { params }),

  // 获取内容详情
  getDetail: (contentId: number) => api.get(`/content/${contentId}`),

  // 点赞内容
  like: (contentId: number) => api.post(`/content/${contentId}/like`),
};

// ============ 社区相关 ============
export const communityApi = {
  // 发布帖子
  createPost: (data: {
    category: string;
    content: string;
    tags?: string;
  }) => api.post('/community/posts', data),

  // 获取帖子列表
  getPosts: (params?: {
    category?: string;
    skip?: number;
    limit?: number;
  }) => api.get('/community/posts', { params }),

  // 获取帖子详情
  getPostDetail: (postId: number) => api.get(`/community/posts/${postId}`),

  // 点赞帖子
  likePost: (postId: number) => api.post(`/community/posts/${postId}/like`),

  // 发布评论
  createComment: (data: {
    post_id: number;
    content: string;
  }) => api.post('/community/comments', data),

  // 获取帖子评论列表
  getPostComments: (postId: number) =>
    api.get(`/community/posts/${postId}/comments`),

  // 举报帖子
  reportPost: (postId: number, reason?: string) =>
    api.post(`/community/posts/${postId}/report`, null, {
      params: { reason }
    }),
};

// ============ 健康检查 ============
export const healthApi = {
  // 检查后端服务健康状态
  check: async () => {
    try {
      // 先尝试检查根路径
      await axios.get('http://localhost:8000/', { 
        timeout: 5000,
        headers: {
          'Accept': 'application/json',
        }
      });
      // 再检查健康检查接口
      return await axios.get('http://localhost:8000/api/health', { 
        timeout: 5000,
        headers: {
          'Accept': 'application/json',
        }
      });
    } catch (error: any) {
      // 如果是连接错误，提供更详细的诊断信息
      if (!error.response && (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK' || error.message?.includes('Network Error'))) {
        const diagnosticError: any = new Error('无法连接到后端服务');
        diagnosticError.detail = '无法连接到后端服务，请检查：\n1. 后端服务是否已启动（运行 python main.py）\n2. 后端是否运行在 http://localhost:8000\n3. 防火墙是否阻止了连接\n4. 浏览器控制台是否有CORS错误';
        diagnosticError.code = error.code || 'CONNECTION_ERROR';
        diagnosticError.isNetworkError = true;
        diagnosticError.originalError = error;
        throw diagnosticError;
      }
      throw error;
    }
  },
  
  // 检查根路径
  checkRoot: async () => {
    try {
      return await axios.get('http://localhost:8000/', { 
        timeout: 5000,
        headers: {
          'Accept': 'application/json',
        }
      });
    } catch (error: any) {
      if (!error.response && (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK' || error.message?.includes('Network Error'))) {
        const diagnosticError: any = new Error('无法连接到后端服务');
        diagnosticError.detail = '无法连接到后端服务，请检查后端是否运行在 http://localhost:8000';
        diagnosticError.code = error.code || 'CONNECTION_ERROR';
        diagnosticError.isNetworkError = true;
        throw diagnosticError;
      }
      throw error;
    }
  },
};

// ============ 管理员相关 ============
export const adminApi = {
  // 获取平台统计数据
  getStatistics: () => api.get('/admin/statistics'),

  // 获取所有咨询师列表（管理员用，包含所有状态）
  getAllCounselors: (params?: { skip?: number; limit?: number }) =>
    api.get('/admin/counselors/list', { params }),

  // 获取待审核咨询师列表
  getPendingCounselors: () => api.get('/admin/counselors/pending'),

  // 审核通过咨询师
  approveCounselor: (counselorId: number) =>
    api.put(`/admin/counselors/${counselorId}/approve`),

  // 拒绝咨询师申请
  rejectCounselor: (counselorId: number) =>
    api.put(`/admin/counselors/${counselorId}/reject`),

  // 获取待审核帖子列表
  getPendingPosts: () => api.get('/admin/posts/pending'),

  // 审核通过帖子
  approvePost: (postId: number) =>
    api.put(`/admin/posts/${postId}/approve`),

  // 删除帖子
  deletePost: (postId: number) => api.delete(`/admin/posts/${postId}`),

  // 禁用用户
  disableUser: (userId: number) => api.put(`/admin/users/${userId}/disable`),

  // 获取所有用户列表
  getAllUsers: (params?: { skip?: number; limit?: number }) =>
    api.get('/admin/users/list', { params }),

  // 创建咨询师账户
  createCounselorAccount: (data: {
    real_name: string;
    gender: string;
    specialty: string;
    experience_years: number;
    bio?: string;
  }) => api.post('/admin/counselors/create', data),

  // 删除咨询师
  deleteCounselor: (counselorId: number) => api.delete(`/admin/counselors/${counselorId}`),
};

export default api;

