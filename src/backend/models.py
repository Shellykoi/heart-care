"""
数据库模型定义
使用 SQLAlchemy ORM 定义所有表结构
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Float, Boolean, ForeignKey, Date, Time, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
import json


# 枚举类型定义
class UserRole(str, enum.Enum):
    """用户角色"""
    USER = "user"  # 普通用户
    COUNSELOR = "counselor"  # 心理咨询师
    VOLUNTEER = "volunteer"  # 志愿者
    ADMIN = "admin"  # 管理员


class Gender(str, enum.Enum):
    """性别"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class AppointmentStatus(str, enum.Enum):
    """预约状态"""
    PENDING = "pending"  # 待确认
    CONFIRMED = "confirmed"  # 已确认
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消
    REJECTED = "rejected"  # 已拒绝


class ConsultMethod(str, enum.Enum):
    """咨询方式"""
    VIDEO = "video"  # 线上视频
    OFFLINE = "offline"  # 线下面谈
    VOICE = "voice"  # 语音咨询
    TEXT = "text"  # 文字咨询


class CounselorStatus(str, enum.Enum):
    """咨询师状态"""
    PENDING = "pending"  # 待审核
    ACTIVE = "active"  # 在职
    INACTIVE = "inactive"  # 停职
    REJECTED = "rejected"  # 已拒绝


# 数据库表模型
class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    student_id = Column(String(50), unique=True, nullable=True)  # 学号
    password_hash = Column(String(255), nullable=False)
    
    # 基本信息
    nickname = Column(String(50), nullable=True)
    avatar = Column(String(500), nullable=True)  # 头像URL（存储在对象存储或静态目录）
    gender = Column(Enum(Gender), default=Gender.OTHER)
    age = Column(Integer, nullable=True)
    school = Column(String(100), nullable=True)  # 学校/单位
    
    # 角色和状态
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_anonymous = Column(Boolean, default=False)  # 隐身模式
    
    # 隐私设置
    show_test_results = Column(Boolean, default=False)  # 是否公开测评结果
    record_retention = Column(String(20), default="3months")  # 记录保留时长
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    counselors = relationship("Counselor", back_populates="user")
    appointments = relationship("Appointment", back_populates="user", foreign_keys="Appointment.user_id")
    consultation_records = relationship("ConsultationRecord", back_populates="user", foreign_keys="ConsultationRecord.user_id")
    test_reports = relationship("TestReport", back_populates="user")
    posts = relationship("CommunityPost", back_populates="author")
    favorites = relationship("UserFavorite", back_populates="user")
    counselor_favorites = relationship("CounselorFavorite", back_populates="user")
    content_likes = relationship("ContentLike", back_populates="user")
    sent_messages = relationship("PrivateMessage", foreign_keys="PrivateMessage.sender_id", back_populates="sender")
    received_messages = relationship("PrivateMessage", foreign_keys="PrivateMessage.receiver_id", back_populates="receiver")
    emergency_helps = relationship("EmergencyHelp", back_populates="user")


class Counselor(Base):
    """咨询师表"""
    __tablename__ = "counselors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # 基本信息
    real_name = Column(String(50), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    age = Column(Integer, nullable=True)  # 年龄
    specialty = Column(Text, nullable=False)  # 擅长领域（JSON数组格式，如 ["学业压力","情感困扰"]）
    experience_years = Column(Integer, nullable=False, default=0)  # 从业年限（work_years）
    
    # 资质信息
    qualification = Column(String(200), nullable=True)  # 资质证书（如 "国家二级心理咨询师"）
    certificate_url = Column(String(500), nullable=True)  # 证书照片（支持多张，JSON格式）
    bio = Column(Text, nullable=True)  # 个人简介
    intro = Column(Text, nullable=True)  # 详细介绍（富文本）
    
    # 服务设置
    consult_methods = Column(Text, nullable=True)  # 咨询方式（JSON数组格式，如 ["线下","视频","文字"]）
    consult_type = Column(Text, nullable=True)  # 支持的咨询类型（JSON数组，兼容旧字段）
    fee = Column(Float, default=0.0)  # 咨询费用（元/小时）
    consult_place = Column(String(255), nullable=True)  # 线下咨询地点
    max_daily_appointments = Column(Integer, default=3)  # 每日最大预约量
    
    # 展示信息
    avatar = Column(String(500), nullable=True)  # 头像URL（存储在MinIO）
    
    # 统计数据
    total_consultations = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    
    # 状态（0-待审核，1-已通过，2-已驳回，3-禁用）
    status = Column(Enum(CounselorStatus), default=CounselorStatus.PENDING)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="counselors")
    appointments = relationship("Appointment", back_populates="counselor")
    consultation_records = relationship("ConsultationRecord", back_populates="counselor", foreign_keys="ConsultationRecord.counselor_id")
    schedules = relationship("CounselorSchedule", back_populates="counselor")
    unavailable_periods = relationship("CounselorUnavailable", back_populates="counselor")
    favorites = relationship("CounselorFavorite", back_populates="counselor")


class CounselorFavorite(Base):
    """咨询师收藏表"""
    __tablename__ = "counselor_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    counselor_id = Column(Integer, ForeignKey("counselors.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 唯一约束：一个用户只能收藏同一个咨询师一次
    __table_args__ = (UniqueConstraint('user_id', 'counselor_id', name='uq_user_counselor_favorite'),)
    
    # 关系
    user = relationship("User", back_populates="counselor_favorites")
    counselor = relationship("Counselor", back_populates="favorites")


class CounselorSchedule(Base):
    """咨询师日程表"""
    __tablename__ = "counselor_schedules"

    id = Column(Integer, primary_key=True, index=True)
    counselor_id = Column(Integer, ForeignKey("counselors.id"), nullable=False, index=True)
    
    weekday = Column(Integer, nullable=False, index=True)  # 星期几 (1-7，1=周一，7=周日)
    start_time = Column(Time, nullable=False)  # 开始时间（如 09:00:00）
    end_time = Column(Time, nullable=False)  # 结束时间（如 17:00:00）
    max_num = Column(Integer, nullable=False, default=1)  # 该时段最大预约量（默认1人/时段）
    is_available = Column(Boolean, default=True)  # 1-可用，0-停诊
    
    # 关系
    counselor = relationship("Counselor", back_populates="schedules")


class CounselorUnavailable(Base):
    """咨询师不可预约时段表"""
    __tablename__ = "counselor_unavailable"

    id = Column(Integer, primary_key=True, index=True)
    counselor_id = Column(Integer, ForeignKey("counselors.id"), nullable=False, index=True)
    
    start_date = Column(Date, nullable=False, index=True)  # 不可预约开始日期
    end_date = Column(Date, nullable=False, index=True)  # 不可预约结束日期
    start_time = Column(Time, default=None)  # 不可预约开始时间（默认全天，如 14:00:00）
    end_time = Column(Time, default=None)  # 不可预约结束时间（默认全天，如 18:00:00）
    reason = Column(String(200), nullable=True)  # 不可预约原因（如 "培训""个人事务"）
    status = Column(Integer, default=1)  # 1-有效，0-已失效（过期自动设置）
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    counselor = relationship("Counselor", back_populates="unavailable_periods")


class Appointment(Base):
    """预约表"""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    counselor_id = Column(Integer, ForeignKey("counselors.id"), index=True)
    
    # 预约信息
    consult_type = Column(String(100), nullable=True)  # 咨询类型
    consult_method = Column(String(50), nullable=False)  # 咨询方式（直接存储中文：线上视频、线下面谈、语音咨询、文字咨询）
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    
    # 咨询诉求
    description = Column(Text, nullable=True)
    
    # 状态
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    
    # 咨询小结
    summary = Column(Text, nullable=True)  # 咨询师填写的小结
    rating = Column(Integer, nullable=True)  # 用户评分 1-5
    review = Column(Text, nullable=True)  # 用户评价
    
    # 咨询结束确认（双方都需要确认）
    user_confirmed_complete = Column(Boolean, default=False)  # 用户确认咨询结束
    counselor_confirmed_complete = Column(Boolean, default=False)  # 咨询师确认咨询结束
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="appointments", foreign_keys=[user_id])
    counselor = relationship("Counselor", back_populates="appointments")
    counselor_rating = relationship("CounselorRating", back_populates="appointment", uselist=False)


class TestScale(Base):
    """心理测评量表"""
    __tablename__ = "test_scales"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 量表名称
    abbreviation = Column(String(20), nullable=True)  # 简称 (PSS, SDS, SAS)
    category = Column(String(50), nullable=False)  # 分类
    description = Column(Text, nullable=True)  # 描述
    duration = Column(String(20), nullable=True)  # 预计时长
    question_count = Column(Integer, nullable=False)  # 题目数量
    
    # 量表内容 (JSON格式存储题目)
    questions_json = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    reports = relationship("TestReport", back_populates="scale")


class TestReport(Base):
    """测评报告表"""
    __tablename__ = "test_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    scale_id = Column(Integer, ForeignKey("test_scales.id"))
    
    # 测评结果
    score = Column(Integer, nullable=False)
    level = Column(String(50), nullable=True)  # 结果等级
    result_json = Column(Text, nullable=True)  # 详细结果 (JSON)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="test_reports")
    scale = relationship("TestScale", back_populates="reports")


class Content(Base):
    """健康科普内容表"""
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content_type = Column(String(20), nullable=False)  # article, video, audio
    category = Column(String(50), nullable=True)  # 分类
    
    # 内容
    content = Column(Text, nullable=True)  # 文章正文
    media_url = Column(String(500), nullable=True)  # 视频/音频链接
    cover_image = Column(String(500), nullable=True)  # 封面图
    
    # 元数据
    duration = Column(String(20), nullable=True)  # 时长
    author = Column(String(100), nullable=True)
    tags = Column(String(200), nullable=True)  # 标签 (逗号分隔)
    
    # 统计
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    # 审核状态
    is_published = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommunityPost(Base):
    """社区帖子表"""
    __tablename__ = "community_posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    
    # 帖子内容
    category = Column(String(50), nullable=False)  # 心情树洞/互助问答/经验分享
    content = Column(Text, nullable=False)
    tags = Column(String(200), nullable=True)  # 标签
    
    # 互动统计
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    report_count = Column(Integer, default=0)  # 举报次数
    
    # 审核状态
    is_approved = Column(Boolean, default=True)  # 默认直接发布，不需要审核
    is_deleted = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    """评论表"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    
    is_approved = Column(Boolean, default=True)  # 直接发布，不需要审核
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    post = relationship("CommunityPost", back_populates="comments")
    user = relationship("User")


class PostReport(Base):
    """帖子举报记录表"""
    __tablename__ = "post_reports"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 举报人
    reason = Column(String(200), nullable=True)  # 举报原因
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 唯一约束：同一用户不能重复举报同一帖子
    __table_args__ = (
        UniqueConstraint('post_id', 'user_id', name='uq_post_user_report'),
    )


class SystemLog(Base):
    """系统日志表"""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # 操作类型
    detail = Column(Text, nullable=True)  # 详细信息
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User")


class UserFavorite(Base):
    """用户收藏表"""
    __tablename__ = "user_favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_type = Column(String(20), nullable=False)  # content, post
    content_id = Column(Integer, nullable=False)  # 内容ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="favorites")


class PrivateMessage(Base):
    """私信表"""
    __tablename__ = "private_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    is_deleted_by_sender = Column(Boolean, default=False)
    is_deleted_by_receiver = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")


class EmergencyHelp(Base):
    """紧急求助表"""
    __tablename__ = "emergency_helps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    help_type = Column(String(50), nullable=False)  # 求助类型
    content = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, processing, resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="emergency_helps")


class UserBlock(Base):
    """用户拉黑表"""
    __tablename__ = "user_blocks"

    id = Column(Integer, primary_key=True, index=True)
    blocker_id = Column(Integer, ForeignKey("users.id"))  # 拉黑者
    blocked_id = Column(Integer, ForeignKey("users.id"))  # 被拉黑者
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    blocker = relationship("User", foreign_keys=[blocker_id])
    blocked = relationship("User", foreign_keys=[blocked_id])


class ContentLike(Base):
    """内容点赞表"""
    __tablename__ = "content_likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_type = Column(String(20), nullable=False)  # content, post, comment
    content_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="content_likes")


class CounselorRating(Base):
    """咨询师评分表"""
    __tablename__ = "counselor_ratings"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    counselor_id = Column(Integer, ForeignKey("counselors.id"), index=True)
    rating = Column(Integer, nullable=False)  # 1-5
    review = Column(Text, nullable=True)  # 评价内容（仅自己和管理员可见）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    appointment = relationship("Appointment", back_populates="counselor_rating")
    user = relationship("User")
    counselor = relationship("Counselor")


class ConsultationRecord(Base):
    """咨询记录表"""
    __tablename__ = "consultation_records"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    counselor_id = Column(Integer, ForeignKey("counselors.id"), index=True)
    
    # 咨询信息（从预约表复制）
    consult_type = Column(String(100), nullable=True)  # 咨询类型
    consult_method = Column(String(50), nullable=False)  # 咨询方式（直接存储中文：线上视频、线下面谈、语音咨询、文字咨询）
    appointment_date = Column(DateTime(timezone=True), nullable=False)  # 预约时间
    description = Column(Text, nullable=True)  # 咨询诉求
    
    # 咨询结果
    summary = Column(Text, nullable=True)  # 咨询师填写的小结
    rating = Column(Integer, nullable=True)  # 用户评分 1-5
    review = Column(Text, nullable=True)  # 用户评价
    
    # 确认信息
    user_confirmed_at = Column(DateTime(timezone=True), nullable=True)  # 用户确认时间
    counselor_confirmed_at = Column(DateTime(timezone=True), nullable=True)  # 咨询师确认时间
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    appointment = relationship("Appointment")
    user = relationship("User", back_populates="consultation_records", foreign_keys=[user_id])
    counselor = relationship("Counselor", back_populates="consultation_records", foreign_keys=[counselor_id])
