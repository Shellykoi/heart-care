"""
用户路由 - 用户信息管理
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User
from schemas import UserResponse, UserUpdate
from auth import get_current_active_user

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """获取用户个人资料"""
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新用户个人资料"""
    if user_data.nickname:
        current_user.nickname = user_data.nickname
    if user_data.gender:
        current_user.gender = user_data.gender
    if user_data.age:
        current_user.age = user_data.age
    if user_data.school:
        current_user.school = user_data.school
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.delete("/profile")
def delete_user_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除用户账户（软删除）"""
    current_user.is_active = False
    db.commit()
    
    return {"message": "账户已停用"}


@router.get("/appointments/history")
def get_appointment_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的预约历史"""
    appointments = current_user.appointments
    return {"appointments": appointments}


@router.get("/tests/history")
def get_test_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的测评历史"""
    test_reports = current_user.test_reports
    return {"test_reports": test_reports}


@router.get("/stats")
def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的统计数据"""
    from models import Appointment, AppointmentStatus, TestReport, UserFavorite
    
    # 待确认预约数（状态为待确认）
    pending_appointments = db.query(Appointment).filter(
        Appointment.user_id == current_user.id,
        Appointment.status == AppointmentStatus.PENDING
    ).count()
    
    # 已完成咨询数（状态为已完成，或状态为已确认且双方都已确认完成）
    from sqlalchemy import or_, and_
    completed_appointments = db.query(Appointment).filter(
        Appointment.user_id == current_user.id,
        or_(
            Appointment.status == AppointmentStatus.COMPLETED,
            and_(
                Appointment.status == AppointmentStatus.CONFIRMED,
                Appointment.user_confirmed_complete == True,
                Appointment.counselor_confirmed_complete == True
            )
        )
    ).count()
    
    # 测评报告数
    test_reports_count = db.query(TestReport).filter(
        TestReport.user_id == current_user.id
    ).count()
    
    # 收藏文章数
    favorites_count = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id
    ).count()
    
    return {
        "pending_appointments": pending_appointments,
        "completed_appointments": completed_appointments,
        "test_reports": test_reports_count,
        "favorites": favorites_count
    }


@router.get("/stats/consultation-activity")
def get_consultation_activity(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的咨询活动数据（时间和咨询时间统计）"""
    from models import Appointment, AppointmentStatus
    from sqlalchemy import or_, and_, func
    from datetime import datetime, timedelta, date
    from collections import defaultdict
    
    try:
        # 获取所有已完成的咨询
        completed_appointments = db.query(Appointment).filter(
            Appointment.user_id == current_user.id,
            or_(
                Appointment.status == AppointmentStatus.COMPLETED,
                and_(
                    Appointment.status == AppointmentStatus.CONFIRMED,
                    Appointment.user_confirmed_complete == True,
                    Appointment.counselor_confirmed_complete == True
                )
            )
        ).order_by(Appointment.appointment_date.desc()).all()
        
        # 按日期统计咨询次数（最近30天）
        today = date.today()
        date_stats = defaultdict(int)
        date_duration_stats = defaultdict(int)  # 每天的时长统计
        consultation_activities = []
        
        # 假设每次咨询时长为60分钟（如果没有实际时长数据）
        DEFAULT_DURATION_MINUTES = 60
        total_duration_minutes = 0
        
        for appointment in completed_appointments:
            try:
                # 处理日期对象
                if appointment.appointment_date is None:
                    continue
                    
                if isinstance(appointment.appointment_date, datetime):
                    # 如果有时区信息，转换为本地时间
                    if appointment.appointment_date.tzinfo is not None:
                        appointment_date = appointment.appointment_date.astimezone().date()
                        apt_datetime = appointment.appointment_date.astimezone().replace(tzinfo=None)
                    else:
                        appointment_date = appointment.appointment_date.date()
                        apt_datetime = appointment.appointment_date
                elif hasattr(appointment.appointment_date, 'date'):
                    appointment_date = appointment.appointment_date.date()
                    apt_datetime = appointment.appointment_date
                else:
                    appointment_date = appointment.appointment_date
                    apt_datetime = None
                
                # 确保 appointment_date 是 date 对象
                if not isinstance(appointment_date, date):
                    try:
                        if hasattr(appointment.appointment_date, 'date'):
                            appointment_date = appointment.appointment_date.date()
                        else:
                            appointment_date = date.fromisoformat(str(appointment.appointment_date).split()[0])
                    except:
                        continue
                
                # 确保 apt_datetime 是 datetime 对象
                if apt_datetime is None:
                    try:
                        if isinstance(appointment.appointment_date, datetime):
                            apt_datetime = appointment.appointment_date
                            if apt_datetime.tzinfo is not None:
                                apt_datetime = apt_datetime.astimezone().replace(tzinfo=None)
                        else:
                            apt_datetime = datetime.fromisoformat(str(appointment.appointment_date).replace('Z', '+00:00'))
                            if apt_datetime.tzinfo is not None:
                                apt_datetime = apt_datetime.astimezone().replace(tzinfo=None)
                    except:
                        apt_datetime = None
                
                days_ago = (today - appointment_date).days
                
                # 只统计最近30天的数据
                if days_ago <= 30:
                    date_str = appointment_date.isoformat()
                    date_stats[date_str] += 1
                    
                    # 计算咨询时长（优先从description中提取结束时间）
                    duration_minutes = DEFAULT_DURATION_MINUTES
                    end_datetime = None
                    
                    # 尝试从description中提取结束时间
                    if appointment.description and '|END_TIME:' in appointment.description:
                        try:
                            end_time_str = appointment.description.split('|END_TIME:')[1].split('|')[0]
                            end_datetime = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                            if end_datetime.tzinfo is not None:
                                end_datetime = end_datetime.astimezone().replace(tzinfo=None)
                            
                            # 计算实际时长
                            if apt_datetime and isinstance(end_datetime, datetime):
                                duration = end_datetime - apt_datetime
                                duration_minutes = max(60, min(180, int(duration.total_seconds() / 60)))
                        except:
                            # 如果提取失败，使用默认逻辑
                            pass
                    
                    # 如果没有从description中提取到结束时间，使用默认逻辑
                    if end_datetime is None and appointment.updated_at and apt_datetime:
                        try:
                            if isinstance(appointment.updated_at, datetime):
                                updated_at = appointment.updated_at
                                if updated_at.tzinfo is not None:
                                    updated_at = updated_at.astimezone().replace(tzinfo=None)
                            else:
                                updated_at = appointment.updated_at
                            
                            if isinstance(apt_datetime, datetime) and isinstance(updated_at, datetime):
                                duration = updated_at - apt_datetime
                                duration_minutes = max(60, min(180, int(duration.total_seconds() / 60)))
                        except:
                            duration_minutes = DEFAULT_DURATION_MINUTES
                    
                    # 累加每天的时长
                    date_duration_stats[date_str] += duration_minutes
                    total_duration_minutes += duration_minutes
                    
                    # 记录咨询活动
                    try:
                        datetime_str = appointment.appointment_date.isoformat() if hasattr(appointment.appointment_date, 'isoformat') else str(appointment.appointment_date)
                        consultation_activities.append({
                            "id": appointment.id,
                            "date": date_str,
                            "datetime": datetime_str,
                            "consult_type": appointment.consult_type or "心理咨询",
                            "consult_method": appointment.consult_method or "未知",
                            "counselor_name": appointment.counselor.name if appointment.counselor else "未知咨询师",
                            "duration_minutes": duration_minutes,
                            "rating": appointment.rating,
                            "status": "completed"
                        })
                    except:
                        continue
            except Exception as e:
                continue
        
        # 生成最近30天的日期列表（用于图表）
        date_list = []
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            date_str = d.isoformat()
            date_list.append({
                "date": date_str,
                "count": date_stats.get(date_str, 0),
                "total_duration": date_duration_stats.get(date_str, 0)  # 添加时长字段
            })
        
        # 按周统计
        week_stats = defaultdict(int)
        for appointment in completed_appointments:
            try:
                if appointment.appointment_date is None:
                    continue
                    
                # 处理日期对象
                if isinstance(appointment.appointment_date, datetime):
                    if appointment.appointment_date.tzinfo is not None:
                        appointment_date = appointment.appointment_date.astimezone().date()
                    else:
                        appointment_date = appointment.appointment_date.date()
                elif hasattr(appointment.appointment_date, 'date'):
                    appointment_date = appointment.appointment_date.date()
                else:
                    appointment_date = appointment.appointment_date
                
                # 确保 appointment_date 是 date 对象
                if not isinstance(appointment_date, date):
                    try:
                        if hasattr(appointment.appointment_date, 'date'):
                            appointment_date = appointment.appointment_date.date()
                        else:
                            appointment_date = date.fromisoformat(str(appointment.appointment_date).split()[0])
                    except:
                        continue
                
                days_ago = (today - appointment_date).days
                if days_ago <= 30:
                    # 计算是第几周（相对于今天）
                    week_num = days_ago // 7
                    week_stats[week_num] += 1
            except:
                continue
        
        # 按咨询类型统计
        type_stats = defaultdict(int)
        for appointment in completed_appointments:
            consult_type = appointment.consult_type or "心理咨询"
            type_stats[consult_type] += 1
        
        # 按小时统计（0-23小时）
        hour_stats = defaultdict(int)
        hour_duration_stats = defaultdict(int)  # 每个小时的总时长
        
        # 按时间段统计（上午、下午、晚上、深夜）
        time_period_stats = {
            "morning": 0,      # 6:00-12:00
            "afternoon": 0,    # 12:00-18:00
            "evening": 0,      # 18:00-22:00
            "night": 0         # 22:00-6:00
        }
        time_period_duration = {
            "morning": 0,
            "afternoon": 0,
            "evening": 0,
            "night": 0
        }
        
        # 咨询时长分布统计（1小时、1-2小时、2-3小时、3小时以上）
        duration_distribution = {
            "short": 0,      # 1小时
            "medium": 0,     # 1-2小时
            "long": 0,       # 2-3小时
            "very_long": 0   # > 3小时
        }
        
        for appointment in completed_appointments:
            try:
                if appointment.appointment_date is None:
                    continue
                    
                # 获取预约时间的datetime对象
                if isinstance(appointment.appointment_date, datetime):
                    apt_datetime = appointment.appointment_date
                    # 如果有时区信息，转换为本地时间并去掉时区
                    if apt_datetime.tzinfo is not None:
                        apt_datetime = apt_datetime.astimezone().replace(tzinfo=None)
                elif hasattr(appointment.appointment_date, 'replace'):
                    apt_datetime = appointment.appointment_date
                    if hasattr(apt_datetime, 'tzinfo') and apt_datetime.tzinfo is not None:
                        apt_datetime = apt_datetime.astimezone().replace(tzinfo=None)
                else:
                    try:
                        apt_datetime = datetime.fromisoformat(str(appointment.appointment_date).replace('Z', '+00:00'))
                        if apt_datetime.tzinfo is not None:
                            apt_datetime = apt_datetime.astimezone().replace(tzinfo=None)
                    except:
                        continue
                
                if not isinstance(apt_datetime, datetime):
                    continue
                
                # 获取小时
                hour = apt_datetime.hour
                hour_stats[hour] += 1
                
                # 计算咨询时长（优先从description中提取结束时间）
                duration_minutes = DEFAULT_DURATION_MINUTES
                end_datetime = None
                
                # 尝试从description中提取结束时间
                if appointment.description and '|END_TIME:' in appointment.description:
                    try:
                        end_time_str = appointment.description.split('|END_TIME:')[1].split('|')[0]
                        end_datetime = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                        if end_datetime.tzinfo is not None:
                            end_datetime = end_datetime.astimezone().replace(tzinfo=None)
                        
                        # 计算实际时长
                        if isinstance(apt_datetime, datetime) and isinstance(end_datetime, datetime):
                            duration = end_datetime - apt_datetime
                            duration_minutes = max(60, min(180, int(duration.total_seconds() / 60)))
                    except:
                        # 如果提取失败，使用默认逻辑
                        pass
                
                # 如果没有从description中提取到结束时间，使用默认逻辑
                if end_datetime is None and appointment.updated_at and appointment.appointment_date:
                    try:
                        if isinstance(appointment.updated_at, datetime):
                            updated_at = appointment.updated_at
                            if updated_at.tzinfo is not None:
                                updated_at = updated_at.astimezone().replace(tzinfo=None)
                        else:
                            updated_at = appointment.updated_at
                        
                        if isinstance(apt_datetime, datetime):
                            apt_date = apt_datetime
                        else:
                            apt_date = apt_datetime
                        
                        if isinstance(updated_at, datetime) and isinstance(apt_date, datetime):
                            duration = updated_at - apt_date
                            duration_minutes = max(60, min(180, int(duration.total_seconds() / 60)))
                    except:
                        duration_minutes = DEFAULT_DURATION_MINUTES
                
                hour_duration_stats[hour] += duration_minutes
                
                # 按时间段统计
                if 6 <= hour < 12:
                    time_period_stats["morning"] += 1
                    time_period_duration["morning"] += duration_minutes
                elif 12 <= hour < 18:
                    time_period_stats["afternoon"] += 1
                    time_period_duration["afternoon"] += duration_minutes
                elif 18 <= hour < 22:
                    time_period_stats["evening"] += 1
                    time_period_duration["evening"] += duration_minutes
                else:
                    time_period_stats["night"] += 1
                    time_period_duration["night"] += duration_minutes
                
                # 咨询时长分布（1小时、1-2小时、2-3小时、3小时以上）
                if duration_minutes < 60:
                    duration_distribution["short"] += 1
                elif duration_minutes < 120:
                    duration_distribution["medium"] += 1
                elif duration_minutes < 180:
                    duration_distribution["long"] += 1
                else:
                    duration_distribution["very_long"] += 1
            except Exception as e:
                continue
        
        # 生成24小时统计数据（用于图表）
        hour_list = []
        for hour in range(24):
            count = hour_stats.get(hour, 0)
            total_dur = hour_duration_stats.get(hour, 0)
            avg_dur = int(total_dur / count) if count > 0 else 0
            hour_list.append({
                "hour": hour,
                "count": count,
                "total_duration": total_dur,
                "average_duration": avg_dur
            })
        
        # 计算统计数据
        total_consultations = len(completed_appointments)
        average_duration_minutes = int(total_duration_minutes / total_consultations) if total_consultations > 0 else 0
        total_hours = total_duration_minutes / 60
        
        # 最近7天的咨询次数
        recent_7_days = sum(date_stats.get((today - timedelta(days=i)).isoformat(), 0) for i in range(7))
        
        # 最近30天的咨询次数
        recent_30_days = sum(date_stats.values())
        
        return {
            "total_consultations": total_consultations,
            "total_duration_minutes": total_duration_minutes,
            "total_duration_hours": round(total_hours, 1),
            "average_duration_minutes": average_duration_minutes,
            "recent_7_days": recent_7_days,
            "recent_30_days": recent_30_days,
            "daily_stats": date_list,  # 最近30天每日统计
            "week_stats": dict(week_stats),  # 按周统计
            "type_stats": dict(type_stats),  # 按类型统计
            "hour_stats": hour_list,  # 按小时统计（24小时）
            "time_period_stats": time_period_stats,  # 按时间段统计
            "time_period_duration": time_period_duration,  # 各时间段总时长
            "duration_distribution": duration_distribution,  # 咨询时长分布
            "activities": consultation_activities[:50]  # 最近50条活动记录
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取咨询活动数据失败: {str(e)}")
