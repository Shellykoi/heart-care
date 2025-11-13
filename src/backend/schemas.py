"""
Pydantic 模型定义
用于请求验证和响应序列化
"""

from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, List
from datetime import datetime
from models import UserRole, Gender, AppointmentStatus, CounselorStatus


# ============ 用户相关 ============
class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    """用户注册"""
    password: str = Field(..., min_length=6, max_length=20)
    student_id: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录"""
    account: str  # 可以是用户名/手机号/邮箱
    password: str


class UserUpdate(BaseModel):
    """用户信息更新"""
    nickname: Optional[str] = None
    gender: Optional[Gender] = None
    age: Optional[int] = None
    school: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    nickname: Optional[str]
    avatar: Optional[str] = None
    gender: Gender
    gender_display: Optional[str] = None  # 性别中文显示
    role: UserRole
    role_display: Optional[str] = None  # 角色中文显示
    is_active: bool
    created_at: datetime

    @model_validator(mode='after')
    def set_displays(self):
        """设置中文显示字段"""
        from utils import get_gender_display, get_user_role_display
        self.gender_display = get_gender_display(self.gender)
        self.role_display = get_user_role_display(self.role)
        return self

    class Config:
        from_attributes = True


# ============ 认证相关 ============
class Token(BaseModel):
    """JWT Token"""
    access_token: str
    token_type: str = "bearer"
    user_info: UserResponse


# ============ 咨询师相关 ============
class CounselorCreate(BaseModel):
    """咨询师申请"""
    real_name: str
    gender: Gender
    specialty: str
    experience_years: int
    certificate_url: Optional[str] = None
    bio: Optional[str] = None


class CounselorAccountCreate(BaseModel):
    """管理员创建咨询师账户"""
    real_name: str
    gender: str
    specialty: str
    experience_years: int
    bio: Optional[str] = None


class CounselorUpdate(BaseModel):
    """咨询师信息更新"""
    specialty: Optional[str] = None
    bio: Optional[str] = None
    fee: Optional[float] = None
    max_daily_appointments: Optional[int] = None


class CounselorProfileUpdate(BaseModel):
    """咨询师完整资料更新（分步表单）"""
    # 基本信息
    real_name: Optional[str] = None
    gender: Optional[Gender] = None
    age: Optional[int] = Field(None, ge=22, le=65)
    experience_years: Optional[int] = Field(None, ge=0, le=30)
    avatar: Optional[str] = None
    
    @model_validator(mode='before')
    @classmethod
    def convert_empty_strings(cls, data):
        """将空字符串转换为 None，以便正确验证"""
        if isinstance(data, dict):
            # 处理 age 字段
            if 'age' in data:
                if data['age'] == '' or data['age'] is None:
                    data['age'] = None
                elif isinstance(data['age'], str):
                    try:
                        data['age'] = int(data['age'].strip()) if data['age'].strip() else None
                    except (ValueError, AttributeError):
                        data['age'] = None
            
            # 处理 experience_years 字段
            if 'experience_years' in data:
                if data['experience_years'] == '' or data['experience_years'] is None:
                    data['experience_years'] = None
                elif isinstance(data['experience_years'], str):
                    try:
                        data['experience_years'] = int(data['experience_years'].strip()) if data['experience_years'].strip() else None
                    except (ValueError, AttributeError):
                        data['experience_years'] = None
        
        return data
    
    # 专业信息
    specialty: Optional[List[str]] = None  # 擅长领域数组
    qualification: Optional[str] = None
    certificate_url: Optional[List[str]] = None  # 证书照片URL数组（最多3张）
    consult_methods: Optional[List[str]] = None  # 咨询方式数组
    consult_type: Optional[List[str]] = None  # 咨询类型数组
    fee: Optional[float] = Field(None, ge=0, le=500)
    consult_place: Optional[str] = None
    max_daily_appointments: Optional[int] = Field(None, ge=1, le=10)  # 每日最大预约量
    
    # 个人简介
    intro: Optional[str] = Field(None, min_length=10, max_length=500)
    bio: Optional[str] = Field(None, min_length=10, max_length=200)
    
    # 审核状态控制（修改资质证书时需重新审核）
    need_review: Optional[bool] = False


class CounselorResponse(BaseModel):
    """咨询师响应"""
    id: int
    real_name: str
    gender: Gender
    gender_display: Optional[str] = None  # 性别中文显示
    specialty: str
    experience_years: int
    fee: float = 0.0
    average_rating: Optional[float] = 0.0
    review_count: Optional[int] = 0
    status: CounselorStatus
    status_display: Optional[str] = None  # 状态中文显示
    created_at: datetime
    # 可选字段（前端需要）
    bio: Optional[str] = None
    consult_methods: Optional[str] = None
    avatar: Optional[str] = None
    intro: Optional[str] = None
    qualification: Optional[str] = None
    consult_place: Optional[str] = None
    age: Optional[int] = None
    is_favorited: Optional[bool] = False  # 当前用户是否已收藏

    @model_validator(mode='before')
    @classmethod
    def set_defaults(cls, data):
        """确保 average_rating 和 review_count 不为 None"""
        # 如果是 SQLAlchemy 对象，转换为字典
        if not isinstance(data, dict) and hasattr(data, '__dict__'):
            data_dict = {}
            for key in ['id', 'real_name', 'gender', 'specialty', 'experience_years', 
                       'fee', 'average_rating', 'review_count', 'status', 'created_at',
                       'bio', 'consult_methods', 'avatar', 'intro', 'qualification', 
                       'consult_place', 'age', 'is_favorited']:
                if hasattr(data, key):
                    value = getattr(data, key, None)
                    # 处理 None 值
                    if key == 'average_rating' and value is None:
                        value = 0.0
                    elif key == 'review_count' and value is None:
                        value = 0
                    elif key == 'fee' and value is None:
                        value = 0.0
                    elif key == 'is_favorited' and value is None:
                        value = False
                    data_dict[key] = value
            data = data_dict
        elif isinstance(data, dict):
            # 处理字典
            if data.get('average_rating') is None:
                data['average_rating'] = 0.0
            if data.get('review_count') is None:
                data['review_count'] = 0
            if data.get('fee') is None:
                data['fee'] = 0.0
        return data

    @model_validator(mode='after')
    def set_displays(self):
        """设置中文显示字段"""
        from utils import get_gender_display, get_counselor_status_display
        self.gender_display = get_gender_display(self.gender)
        self.status_display = get_counselor_status_display(self.status)
        return self

    class Config:
        from_attributes = True


class ScheduleItem(BaseModel):
    """时段设置项"""
    weekday: int = Field(..., ge=1, le=7)
    start_time: str
    end_time: str
    max_num: Optional[int] = Field(1, ge=1, le=3)
    is_available: bool = True


class ScheduleSet(BaseModel):
    """设置咨询师时段"""
    schedules: List[ScheduleItem]


class ScheduleUpdate(BaseModel):
    """更新单个星期的时段"""
    weekday: int = Field(..., ge=1, le=7)
    start_time: str
    end_time: str
    max_num: Optional[int] = Field(1, ge=1, le=3)


class UnavailablePeriodCreate(BaseModel):
    """创建不可预约时段"""
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
    time_type: str = Field(default="all")  # "all" 全天, "custom" 自定义时段
    start_time: Optional[str] = None  # HH:MM
    end_time: Optional[str] = None  # HH:MM
    reason: Optional[str] = None


class CounselorFavoriteResponse(BaseModel):
    """咨询师收藏响应"""
    id: int
    counselor_id: int
    counselor: Optional[CounselorResponse] = None  # 咨询师信息
    created_at: datetime

    class Config:
        from_attributes = True


class ClientInfo(BaseModel):
    """来访者信息"""
    user_id: int
    username: str
    nickname: Optional[str] = None
    gender: Optional[Gender] = None
    gender_display: Optional[str] = None
    age: Optional[int] = None
    school: Optional[str] = None
    first_appointment_date: Optional[datetime] = None  # 首次预约时间
    last_appointment_date: Optional[datetime] = None  # 最近预约时间
    total_appointments: int = 0  # 总预约次数
    total_consultations: int = 0  # 总咨询次数（已完成）

    class Config:
        from_attributes = True


class UnavailablePeriodUpdate(BaseModel):
    """更新不可预约时段"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    time_type: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    reason: Optional[str] = None


# ============ 预约相关 ============
class AppointmentCreate(BaseModel):
    """创建预约"""
    counselor_id: int
    consult_type: str
    consult_method: str  # 咨询方式（中文：线上视频、线下面谈、语音咨询、文字咨询）
    appointment_date: datetime
    description: Optional[str] = None
    end_time: Optional[datetime] = None  # 结束时间（可选，用于自定义时间范围）


class AppointmentUpdate(BaseModel):
    """更新预约"""
    status: Optional[AppointmentStatus] = None
    summary: Optional[str] = None
    user_confirmed_complete: Optional[bool] = None  # 用户确认咨询结束
    counselor_confirmed_complete: Optional[bool] = None  # 咨询师确认咨询结束
    rating: Optional[int] = None  # 用户评分 1-5
    review: Optional[str] = None  # 用户评价


class AppointmentResponse(BaseModel):
    """预约响应"""
    id: int
    user_id: int
    counselor_id: int
    consult_type: str
    consult_method: str  # 咨询方式（直接存储中文：线上视频、线下面谈、语音咨询、文字咨询）
    consult_method_display: Optional[str] = None  # 咨询方式中文显示（与consult_method相同，保持兼容）
    appointment_date: datetime
    status: AppointmentStatus
    status_display: Optional[str] = None  # 状态中文显示
    description: Optional[str] = None
    summary: Optional[str] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    user_confirmed_complete: bool = False
    counselor_confirmed_complete: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # 关联对象信息（用于前端显示）
    user_name: Optional[str] = None  # 用户姓名
    user_nickname: Optional[str] = None  # 用户昵称
    counselor_name: Optional[str] = None  # 咨询师姓名
    counselor: Optional[dict] = None  # 咨询师对象信息（用于前端显示）

    @model_validator(mode='after')
    def set_displays(self):
        """设置中文显示字段"""
        from utils import get_appointment_status_display
        # consult_method已经是中文，直接使用
        self.consult_method_display = self.consult_method
        self.status_display = get_appointment_status_display(self.status)
        return self

    class Config:
        from_attributes = True


# ============ 测评相关 ============
class TestScaleResponse(BaseModel):
    """测评量表响应"""
    id: int
    name: str
    abbreviation: Optional[str]
    category: str
    description: Optional[str]
    duration: Optional[str]
    question_count: int

    class Config:
        from_attributes = True


class TestReportCreate(BaseModel):
    """提交测评"""
    scale_id: int
    score: int
    level: Optional[str] = None
    result_json: Optional[str] = None


class TestReportResponse(BaseModel):
    """测评报告响应"""
    id: int
    user_id: int
    scale_id: int
    score: int
    level: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 内容相关 ============
class ContentCreate(BaseModel):
    """创建内容"""
    title: str
    content_type: str  # article, video, audio
    category: Optional[str] = None
    content: Optional[str] = None
    media_url: Optional[str] = None
    cover_image: Optional[str] = None
    duration: Optional[str] = None
    tags: Optional[str] = None


class ContentResponse(BaseModel):
    """内容响应"""
    id: int
    title: str
    content_type: str
    category: Optional[str]
    cover_image: Optional[str]
    duration: Optional[str]
    view_count: int
    like_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 社区相关 ============
class PostCreate(BaseModel):
    """创建帖子"""
    category: str  # 心情树洞/互助问答/经验分享
    content: str
    tags: Optional[str] = None


class PostResponse(BaseModel):
    """帖子响应"""
    id: int
    author_id: int
    author_name: Optional[str] = None  # 作者显示名称（匿名或真实）
    author_nickname: Optional[str] = None  # 作者昵称
    author_role: Optional[str] = None  # 作者角色
    category: str
    content: str
    tags: Optional[str]
    like_count: int
    comment_count: int
    is_liked: Optional[bool] = False  # 当前用户是否已点赞
    created_at: datetime

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    """创建评论"""
    post_id: int
    content: str


class CommentResponse(BaseModel):
    """评论响应"""
    id: int
    post_id: int
    user_id: int
    user_name: Optional[str] = None  # 用户显示名称（匿名或真实）
    user_nickname: Optional[str] = None  # 用户昵称
    content: str
    like_count: int
    is_liked: Optional[bool] = False  # 当前用户是否已点赞
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 咨询记录相关 ============
class ConsultationRecordResponse(BaseModel):
    """咨询记录响应"""
    id: int
    appointment_id: int
    user_id: int
    counselor_id: int
    consult_type: Optional[str] = None
    consult_method: Optional[str] = None
    appointment_date: Optional[datetime] = None
    description: Optional[str] = None
    summary: Optional[str] = None  # 咨询师填写的小结
    rating: Optional[int] = None  # 用户评分 1-5
    review: Optional[str] = None  # 用户评价
    user_confirmed_at: Optional[datetime] = None
    counselor_confirmed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # 关联对象信息
    user_name: Optional[str] = None  # 用户姓名
    user_nickname: Optional[str] = None  # 用户昵称
    counselor_name: Optional[str] = None  # 咨询师姓名
    user_username: Optional[str] = None  # 用户账号
    user_phone: Optional[str] = None  # 用户手机号
    user_email: Optional[str] = None  # 用户邮箱
    user_student_id: Optional[str] = None  # 用户学号
    
    class Config:
        from_attributes = True


# ============ 统计数据 ============
class Statistics(BaseModel):
    """平台统计数据"""
    total_users: int
    total_counselors: int
    total_appointments: int
    total_tests: int
    active_users_month: int
    appointments_month: int
