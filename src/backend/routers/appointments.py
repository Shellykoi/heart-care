"""
预约路由 - 咨询预约管理
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Union

from database import get_db
from models import Appointment, User, Counselor, AppointmentStatus, ConsultationRecord
from schemas import AppointmentCreate, AppointmentResponse, AppointmentUpdate, ConsultationRecordResponse
from auth import get_current_active_user, require_role

router = APIRouter()


@router.post("/create", response_model=AppointmentResponse)
def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建咨询预约
    - 用户选择咨询师和时间段
    - 等待咨询师确认
    - 包含完整的校验逻辑
    """
    from datetime import datetime, timedelta
    from models import CounselorStatus
    import re
    
    # 检查咨询师是否存在且已激活
    counselor = db.query(Counselor).filter(
        Counselor.id == appointment_data.counselor_id,
        Counselor.status == CounselorStatus.ACTIVE
    ).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在或未激活")
    
    # 校验预约日期（不能预约过去的日期）
    appointment_datetime = appointment_data.appointment_date
    
    # 确保appointment_datetime是datetime对象
    if isinstance(appointment_datetime, str):
        # 处理ISO格式时间字符串
        try:
            appointment_datetime = datetime.fromisoformat(appointment_datetime.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="日期时间格式错误")
    
    # 如果有时区信息，转换为本地时间（UTC+8），然后去掉时区信息
    if appointment_datetime.tzinfo is not None:
        from datetime import timezone, timedelta
        tz_beijing = timezone(timedelta(hours=8))
        appointment_datetime = appointment_datetime.astimezone(tz_beijing).replace(tzinfo=None)
    
    # 确保appointment_datetime是naive datetime（没有时区信息）
    # 数据库字段是DateTime(timezone=True)，SQLAlchemy会自动处理时区转换
    
    now = datetime.now()
    if appointment_datetime < now:
        raise HTTPException(status_code=400, detail="不能预约过去的日期")
    
    # 处理结束时间（如果提供）
    end_datetime = None
    if appointment_data.end_time:
        end_datetime = appointment_data.end_time
        # 确保end_datetime是datetime对象
        if isinstance(end_datetime, str):
            try:
                end_datetime = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="结束时间格式错误")
        
        # 如果有时区信息，转换为本地时间
        if end_datetime.tzinfo is not None:
            from datetime import timezone, timedelta
            tz_beijing = timezone(timedelta(hours=8))
            end_datetime = end_datetime.astimezone(tz_beijing).replace(tzinfo=None)
        
        # 验证时间范围
        if end_datetime <= appointment_datetime:
            raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")
        
        # 验证时长（1-3小时）
        duration = end_datetime - appointment_datetime
        if duration < timedelta(hours=1) or duration > timedelta(hours=3):
            raise HTTPException(status_code=400, detail="预约时长必须在1-3小时之间")
    
    # 校验重复预约和时段冲突（支持自定义时间范围）
    # 由于数据库字段是DateTime(timezone=True)，我们需要使用时间范围查询
    time_tolerance = timedelta(minutes=1)
    
    # 如果提供了结束时间，检查整个时间范围是否冲突
    if end_datetime:
        # 检查咨询师在该时间范围内是否有其他预约
        existing_conflicts = db.query(Appointment).filter(
            Appointment.counselor_id == appointment_data.counselor_id,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]),
            # 检查时间范围是否重叠
            Appointment.appointment_date < end_datetime
        ).all()
        
        # 检查每个已有预约是否与当前预约时间范围重叠
        for existing in existing_conflicts:
            # 获取已有预约的结束时间（如果没有end_time，默认为开始时间+1小时）
            existing_start = existing.appointment_date
            if existing_start.tzinfo is not None:
                from datetime import timezone, timedelta
                tz_beijing = timezone(timedelta(hours=8))
                existing_start = existing_start.astimezone(tz_beijing).replace(tzinfo=None)
            
            # 从description中提取结束时间（如果存在）
            existing_end = existing_start + timedelta(hours=1)  # 默认1小时
            if existing.description and '|END_TIME:' in existing.description:
                try:
                    end_time_str = existing.description.split('|END_TIME:')[1].split('|')[0]
                    existing_end = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                    if existing_end.tzinfo is not None:
                        from datetime import timezone, timedelta
                        tz_beijing = timezone(timedelta(hours=8))
                        existing_end = existing_end.astimezone(tz_beijing).replace(tzinfo=None)
                except:
                    pass
            
            # 检查时间范围是否重叠
            if not (end_datetime <= existing_start or appointment_datetime >= existing_end):
                raise HTTPException(status_code=400, detail="该时间范围与已有预约冲突，请选择其他时段")
        
        # 检查用户在该时间范围内是否有其他预约
        user_conflicts = db.query(Appointment).filter(
            Appointment.user_id == current_user.id,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]),
            Appointment.appointment_date < end_datetime
        ).all()
        
        for existing in user_conflicts:
            existing_start = existing.appointment_date
            if existing_start.tzinfo is not None:
                from datetime import timezone, timedelta
                tz_beijing = timezone(timedelta(hours=8))
                existing_start = existing_start.astimezone(tz_beijing).replace(tzinfo=None)
            
            existing_end = existing_start + timedelta(hours=1)
            if existing.description and '|END_TIME:' in existing.description:
                try:
                    end_time_str = existing.description.split('|END_TIME:')[1].split('|')[0]
                    existing_end = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                    if existing_end.tzinfo is not None:
                        from datetime import timezone, timedelta
                        tz_beijing = timezone(timedelta(hours=8))
                        existing_end = existing_end.astimezone(tz_beijing).replace(tzinfo=None)
                except:
                    pass
            
            if not (end_datetime <= existing_start or appointment_datetime >= existing_end):
                raise HTTPException(status_code=400, detail="该时间范围您已有其他预约，请选择其他时段")
    else:
        # 没有提供结束时间，使用原来的逻辑（1小时）
        # 校验重复预约（同一用户不能预约同一咨询师的同一时段）
        existing_same_slot = db.query(Appointment).filter(
            Appointment.user_id == current_user.id,
            Appointment.counselor_id == appointment_data.counselor_id,
            Appointment.appointment_date >= appointment_datetime - time_tolerance,
            Appointment.appointment_date <= appointment_datetime + time_tolerance,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        ).first()
        
        if existing_same_slot:
            raise HTTPException(status_code=400, detail="您已预约该时段，请勿重复预约")
        
        # 校验时段冲突（同一用户不能在同一时间点预约多个咨询师）
        existing_conflict = db.query(Appointment).filter(
            Appointment.user_id == current_user.id,
            Appointment.appointment_date >= appointment_datetime - time_tolerance,
            Appointment.appointment_date <= appointment_datetime + time_tolerance,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        ).first()
        
        if existing_conflict:
            raise HTTPException(status_code=400, detail="该时段您已有其他预约，请选择其他时段")
    
    # ============ 详细预约前校验 ============
    # 1. 检查用户状态（是否合规、有无预约限制）
    # 检查用户是否被禁用（如果需要）
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="您的账号已被禁用，无法预约")
    
    # 2. 检查咨询师状态（是否可预约）
    if counselor.status != CounselorStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="咨询师当前不可预约")
    
    # 3. 检查咨询师的日程设置和不可预约时段
    # 确保appointment_datetime是本地时间（naive datetime）
    if appointment_datetime.tzinfo is not None:
        from datetime import timezone, timedelta
        tz_beijing = timezone(timedelta(hours=8))
        appointment_datetime = appointment_datetime.astimezone(tz_beijing).replace(tzinfo=None)
    
    target_date = appointment_datetime.date()
    weekday = target_date.isoweekday()
    time_str = appointment_datetime.strftime("%H:%M")
    slot_time = appointment_datetime.time()
    
    from models import CounselorSchedule, CounselorUnavailable
    from datetime import time as time_type
    from sqlalchemy import text
    
    # 安全地解析时间字段的辅助函数
    def _safe_parse_time(value):
        """安全地将时间值转换为 time 对象"""
        if value is None:
            return None
        if isinstance(value, time_type):
            return value
        if isinstance(value, str):
            # 尝试多种时间格式
            for fmt in ["%H:%M:%S", "%H:%M", "%H:%M:%S.%f"]:
                try:
                    return datetime.strptime(value, fmt).time()
                except ValueError:
                    continue
        return None
    
    # 获取咨询师在该工作日的时段设置（如果没有设置，使用默认8:00-22:00）
    # 使用原始 SQL 查询避免 MySQL TIME 类型转换错误
    try:
        result = db.execute(
            text("""
                SELECT start_time, end_time, max_num
                FROM counselor_schedules
                WHERE counselor_id = :counselor_id
                  AND weekday = :weekday
                  AND is_available = true
                LIMIT 1
            """),
            {"counselor_id": counselor.id, "weekday": weekday}
        )
        schedule_row = result.fetchone()
        
        if schedule_row:
            # 使用自定义时段设置
            start_time = _safe_parse_time(schedule_row[0])
            end_time = _safe_parse_time(schedule_row[1])
            max_num = schedule_row[2] if schedule_row[2] is not None else 1
            
            if start_time is None or end_time is None:
                # 如果解析失败，使用默认值
                start_time = time_type(8, 0)
                end_time = time_type(22, 0)
                max_num = 1
        else:
            # 使用默认时段：8:00-22:00
            start_time = time_type(8, 0)
            end_time = time_type(22, 0)
            max_num = 1
    except Exception as e:
        # 如果查询失败，使用默认值
        import logging
        logging.warning(f"查询咨询师日程设置失败: {e}，使用默认时段")
        start_time = time_type(8, 0)
        end_time = time_type(22, 0)
        max_num = 1
    
    # 检查时段是否在日程设置的时间范围内
    # 注意：这里需要允许时间等于结束时间（因为预约是整点预约，比如22:00应该允许）
    # 但实际预约时间应该小于结束时间（比如22:00的预约，实际是22:00-23:00，应该在8:00-22:00范围内）
    # 所以判断逻辑应该是：slot_time >= start_time and slot_time < end_time
    if slot_time < start_time or slot_time >= end_time:
        raise HTTPException(status_code=400, detail=f"该时段不在咨询师的可预约时间范围内（{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}）")
    
    # 检查该日期是否在不可预约时段内
    # 使用原始 SQL 查询避免 MySQL TIME 类型转换错误
    try:
        unavailable_result = db.execute(
            text("""
                SELECT start_time, end_time
                FROM counselor_unavailable
                WHERE counselor_id = :counselor_id
                  AND status = 1
                  AND start_date <= :target_date
                  AND end_date >= :target_date
            """),
            {"counselor_id": counselor.id, "target_date": target_date}
        )
        unavailable_rows = unavailable_result.fetchall()
        
        for row in unavailable_rows:
            if row[0] is None or row[1] is None:
                # 全天不可预约
                raise HTTPException(status_code=400, detail="该日期咨询师不可用（已设置为不可预约时段）")
            else:
                period_start = _safe_parse_time(row[0])
                period_end = _safe_parse_time(row[1])
                if period_start is None or period_end is None:
                    # 如果解析失败，跳过该记录
                    continue
                if period_start <= slot_time < period_end:
                    raise HTTPException(status_code=400, detail="该时段咨询师不可用（已设置为不可预约时段）")
    except HTTPException:
        # 重新抛出 HTTPException
        raise
    except Exception as e:
        # 如果查询失败，记录警告但继续处理（不阻止预约）
        import logging
        logging.warning(f"查询不可预约时段失败: {e}")
    
    # 4. 检查当前时段是否空闲（是否已被预约满）
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())
    
    slot_hour = slot_time.hour
    slot_min = slot_time.minute
    
    # 先获取该日期的所有预约，然后在Python中过滤
    same_slot_appointments = db.query(Appointment).filter(
        Appointment.counselor_id == counselor.id,
        Appointment.appointment_date >= start_of_day,
        Appointment.appointment_date < end_of_day,
        Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    ).all()
    
    # 在Python中过滤出相同时段的预约
    same_slot_count = sum(1 for apt in same_slot_appointments 
                         if apt.appointment_date.hour == slot_hour 
                         and apt.appointment_date.minute == slot_min)
    
    if same_slot_count >= max_num:
        raise HTTPException(status_code=400, detail="该时段已预约满，请选择其他时段")
    
    # 校验咨询诉求内容（检查是否包含违规内容）
    if appointment_data.description:
        # 简单的违规内容检测（可以扩展）
        forbidden_keywords = ['暴力', '违法', '犯罪', '自杀', '自残']
        description_lower = appointment_data.description.lower()
        for keyword in forbidden_keywords:
            if keyword in description_lower:
                raise HTTPException(status_code=400, detail="诉求内容不符合规范，请修改后提交")
    
    # ============ 创建预约记录 ============
    # 生成预约记录，同步更新三类关联数据：
    # 1. 锁定咨询师对应时段（标记为"已预约"，避免重复预约）
    # 2. 关联学生与该预约记录
    # 3. 记录预约初始状态（如"待确认"）
    
    # 如果提供了结束时间，将其存储在description中（格式：{原始description}|END_TIME:{end_time}）
    description_with_end_time = appointment_data.description or ''
    if end_datetime:
        if description_with_end_time:
            description_with_end_time = f"{description_with_end_time}|END_TIME:{end_datetime.isoformat()}"
        else:
            description_with_end_time = f"|END_TIME:{end_datetime.isoformat()}"
    
    new_appointment = Appointment(
        user_id=current_user.id,
        counselor_id=appointment_data.counselor_id,
        consult_type=appointment_data.consult_type,
        consult_method=appointment_data.consult_method,
        appointment_date=appointment_datetime,
        description=description_with_end_time,
        status=AppointmentStatus.PENDING  # 初始状态：待确认
    )
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    
    # 重新加载关联对象
    from sqlalchemy.orm import joinedload
    appointment = db.query(Appointment).options(
        joinedload(Appointment.user),
        joinedload(Appointment.counselor)
    ).filter(Appointment.id == new_appointment.id).first()
    
    # 构建响应数据，包含用户和咨询师信息
    appointment_dict = {
        "id": appointment.id,
        "user_id": appointment.user_id,
        "counselor_id": appointment.counselor_id,
        "consult_type": appointment.consult_type,
        "consult_method": appointment.consult_method,
        "appointment_date": appointment.appointment_date,
        "status": appointment.status,
        "description": appointment.description,
        "summary": appointment.summary,
        "rating": appointment.rating,
        "review": appointment.review,
        "user_confirmed_complete": appointment.user_confirmed_complete,
        "counselor_confirmed_complete": appointment.counselor_confirmed_complete,
        "created_at": appointment.created_at,
        "updated_at": appointment.updated_at,
        "user_name": appointment.user.nickname or appointment.user.username if appointment.user else None,
        "user_nickname": appointment.user.nickname if appointment.user else None,
        "counselor_name": appointment.counselor.real_name if appointment.counselor else None,
        "counselor": {
            "id": appointment.counselor.id,
            "real_name": appointment.counselor.real_name,
            "user_id": appointment.counselor.user_id,
        } if appointment.counselor else None,
    }
    
    return AppointmentResponse(**appointment_dict)


@router.get("/my-appointments", response_model=List[AppointmentResponse])
def get_my_appointments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取我的预约列表（用户或咨询师）
    
    跨页面数据联动：
    - 所有关联页面（学生个人中心、咨询师工作台、管理员后台）均从同一核心数据库读取预约相关数据
    - 状态变更时实时同步至各页面，确保无论从哪个页面查看，预约记录、咨询师档期、咨询进度等信息完全一致
    - 学生预约列表、咨询师预约管理页、后台统计页均使用此接口获取数据，保证数据一致性
    """
    from models import Counselor
    from sqlalchemy.orm import joinedload
    
    # 检查是否是咨询师
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    
    if counselor:
        # 咨询师：获取自己的预约列表
        appointments = db.query(Appointment).options(
            joinedload(Appointment.user),
            joinedload(Appointment.counselor)
        ).filter(
            Appointment.counselor_id == counselor.id
        ).order_by(Appointment.created_at.desc()).all()
    else:
        # 用户：获取自己的预约列表
        appointments = db.query(Appointment).options(
            joinedload(Appointment.user),
            joinedload(Appointment.counselor)
        ).filter(
            Appointment.user_id == current_user.id
        ).order_by(Appointment.created_at.desc()).all()
    
    # 构建响应数据列表 - 优化性能
    result = []
    for appointment in appointments:
        # 安全地获取关联对象信息
        user = appointment.user
        counselor_obj = appointment.counselor
        
        appointment_dict = {
            "id": appointment.id,
            "user_id": appointment.user_id,
            "counselor_id": appointment.counselor_id,
            "consult_type": appointment.consult_type,
            "consult_method": appointment.consult_method,
            "appointment_date": appointment.appointment_date,
            "status": appointment.status,
            "description": appointment.description,
            "summary": appointment.summary,
            "rating": appointment.rating,
            "review": appointment.review,
            "user_confirmed_complete": appointment.user_confirmed_complete or False,
            "counselor_confirmed_complete": appointment.counselor_confirmed_complete or False,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at,
            "user_name": (user.nickname or user.username) if user else None,
            "user_nickname": user.nickname if user else None,
            "counselor_name": counselor_obj.real_name if counselor_obj else None,
            "counselor": {
                "id": counselor_obj.id,
                "real_name": counselor_obj.real_name,
                "user_id": counselor_obj.user_id,
            } if counselor_obj else None,
        }
        result.append(AppointmentResponse(**appointment_dict))
    
    return result


@router.get("/my-counselors")
def get_my_counselors(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取用户历史预约过的咨询师列表
    - 用于显示"我的咨询师"标签
    """
    from models import Counselor, CounselorStatus
    from sqlalchemy import distinct
    
    # 获取用户已预约过的咨询师ID列表（去重）
    counselor_ids = db.query(Appointment.counselor_id).filter(
        Appointment.user_id == current_user.id
    ).distinct().all()
    
    counselor_ids = [c[0] for c in counselor_ids]
    
    if not counselor_ids:
        return {"counselor_ids": []}
    
    # 获取咨询师信息（只返回已激活的）
    counselors = db.query(Counselor).filter(
        Counselor.id.in_(counselor_ids),
        Counselor.status == CounselorStatus.ACTIVE
    ).all()
    
    return {"counselor_ids": [c.id for c in counselors]}


@router.get("/consultation-records", response_model=List[ConsultationRecordResponse])
def get_consultation_records(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: Optional[Union[int, str]] = None,
    limit: Optional[Union[int, str]] = None
):
    """
    获取咨询记录列表
    - 管理员：可以查看所有咨询记录
    - 用户：只能查看自己的咨询记录
    - 咨询师：只能查看自己的咨询记录
    """
    from sqlalchemy.orm import joinedload
    
    def _coerce_pagination_value(value: Optional[Union[int, str]], default: int, minimum: int = 0, maximum: int = 1000) -> int:
        """将查询参数转换为合法的整数分页值，容错处理undefined、null等异常输入"""
        if value is None:
            coerced = default
        elif isinstance(value, int):
            coerced = value
        else:
            try:
                coerced = int(value)
            except (TypeError, ValueError):
                coerced = default
        if coerced < minimum:
            coerced = minimum
        if coerced > maximum:
            coerced = maximum
        return coerced
    
    skip_value = _coerce_pagination_value(skip, default=0, minimum=0)
    limit_value = _coerce_pagination_value(limit, default=100, minimum=1, maximum=1000)
    
    # 检查用户角色
    if current_user.role == "admin":
        # 管理员可以查看所有咨询记录
        records = db.query(ConsultationRecord).options(
            joinedload(ConsultationRecord.user),
            joinedload(ConsultationRecord.counselor)
        ).order_by(ConsultationRecord.created_at.desc()).offset(skip_value).limit(limit_value).all()
    elif current_user.role == "counselor":
        # 咨询师只能查看自己的咨询记录
        counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
        if not counselor:
            raise HTTPException(status_code=404, detail="咨询师信息不存在")
        records = db.query(ConsultationRecord).options(
            joinedload(ConsultationRecord.user),
            joinedload(ConsultationRecord.counselor)
        ).filter(
            ConsultationRecord.counselor_id == counselor.id
        ).order_by(ConsultationRecord.created_at.desc()).offset(skip_value).limit(limit_value).all()
    else:
        # 普通用户只能查看自己的咨询记录
        records = db.query(ConsultationRecord).options(
            joinedload(ConsultationRecord.user),
            joinedload(ConsultationRecord.counselor)
        ).filter(
            ConsultationRecord.user_id == current_user.id
        ).order_by(ConsultationRecord.created_at.desc()).offset(skip_value).limit(limit_value).all()
    
    # 构建响应数据
    result = []
    for record in records:
        record_dict = {
            "id": record.id,
            "appointment_id": record.appointment_id,
            "user_id": record.user_id,
            "counselor_id": record.counselor_id,
            "consult_type": record.consult_type,
            "consult_method": record.consult_method,
            "appointment_date": record.appointment_date,
            "description": record.description,
            "summary": record.summary,
            "rating": record.rating,
            "review": record.review,
            "user_confirmed_at": record.user_confirmed_at,
            "counselor_confirmed_at": record.counselor_confirmed_at,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "user_name": record.user.nickname or record.user.username if record.user else None,
            "user_nickname": record.user.nickname if record.user else None,
            "counselor_name": record.counselor.real_name if record.counselor else None,
            "user_username": record.user.username if record.user else None,
            "user_phone": record.user.phone if record.user else None,
            "user_email": record.user.email if record.user else None,
            "user_student_id": record.user.student_id if record.user else None,
        }
        result.append(ConsultationRecordResponse(**record_dict))
    
    return result


@router.get("/consultation-records/all", response_model=List[ConsultationRecordResponse])
def get_all_consultation_records(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 1000
):
    """
    获取所有咨询记录（仅管理员）
    """
    from sqlalchemy.orm import joinedload
    
    records = db.query(ConsultationRecord).options(
        joinedload(ConsultationRecord.user),
        joinedload(ConsultationRecord.counselor)
    ).order_by(ConsultationRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    # 构建响应数据
    result = []
    for record in records:
        record_dict = {
            "id": record.id,
            "appointment_id": record.appointment_id,
            "user_id": record.user_id,
            "counselor_id": record.counselor_id,
            "consult_type": record.consult_type,
            "consult_method": record.consult_method,
            "appointment_date": record.appointment_date,
            "description": record.description,
            "summary": record.summary,
            "rating": record.rating,
            "review": record.review,
            "user_confirmed_at": record.user_confirmed_at,
            "counselor_confirmed_at": record.counselor_confirmed_at,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
            "user_name": record.user.nickname or record.user.username if record.user else None,
            "user_nickname": record.user.nickname if record.user else None,
            "counselor_name": record.counselor.real_name if record.counselor else None,
            "user_username": record.user.username if record.user else None,
            "user_phone": record.user.phone if record.user else None,
            "user_email": record.user.email if record.user else None,
            "user_student_id": record.user.student_id if record.user else None,
        }
        result.append(ConsultationRecordResponse(**record_dict))
    
    return result


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment_detail(
    appointment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取预约详情"""
    from sqlalchemy.orm import joinedload
    
    appointment = db.query(Appointment).options(
        joinedload(Appointment.user),
        joinedload(Appointment.counselor)
    ).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 检查权限
    if appointment.user_id != current_user.id:
        # 如果是咨询师，检查是否是自己的预约
        counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
        if not counselor or appointment.counselor_id != counselor.id:
            raise HTTPException(status_code=403, detail="无权查看此预约")
    
    # 构建响应数据，包含用户和咨询师信息
    appointment_dict = {
        "id": appointment.id,
        "user_id": appointment.user_id,
        "counselor_id": appointment.counselor_id,
        "consult_type": appointment.consult_type,
        "consult_method": appointment.consult_method,
        "appointment_date": appointment.appointment_date,
        "status": appointment.status,
        "description": appointment.description,
        "summary": appointment.summary,
        "rating": appointment.rating,
        "review": appointment.review,
        "user_confirmed_complete": appointment.user_confirmed_complete,
        "counselor_confirmed_complete": appointment.counselor_confirmed_complete,
        "created_at": appointment.created_at,
        "updated_at": appointment.updated_at,
        "user_name": appointment.user.nickname or appointment.user.username if appointment.user else None,
        "user_nickname": appointment.user.nickname if appointment.user else None,
        "counselor_name": appointment.counselor.real_name if appointment.counselor else None,
        "counselor": {
            "id": appointment.counselor.id,
            "real_name": appointment.counselor.real_name,
            "user_id": appointment.counselor.user_id,
        } if appointment.counselor else None,
    }
    
    return AppointmentResponse(**appointment_dict)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新预约状态
    - 用户可以取消预约
    - 咨询师可以确认/拒绝预约，填写小结
    - 状态流转同步：状态变更时同步更新相关数据
    """
    from models import Counselor
    from sqlalchemy.orm import joinedload
    
    appointment = db.query(Appointment).options(
        joinedload(Appointment.user),
        joinedload(Appointment.counselor)
    ).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 检查权限
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    is_counselor = counselor and appointment.counselor_id == counselor.id
    is_user = appointment.user_id == current_user.id
    
    if not (is_counselor or is_user):
        raise HTTPException(status_code=403, detail="无权修改此预约")
    
    old_status = appointment.status
    
    # 更新状态（带权限检查）
    if appointment_data.status:
        new_status = appointment_data.status
        
        # 权限检查：只有咨询师可以确认/拒绝预约
        if new_status in [AppointmentStatus.CONFIRMED, AppointmentStatus.REJECTED]:
            if not is_counselor:
                raise HTTPException(status_code=403, detail="只有咨询师可以确认或拒绝预约")
        
        # 权限检查：只有用户（学生）可以取消预约
        if new_status == AppointmentStatus.CANCELLED:
            if not is_user:
                raise HTTPException(status_code=403, detail="只有学生可以取消预约")
        
        # 权限检查：只有咨询师可以标记为已完成
        if new_status == AppointmentStatus.COMPLETED:
            if not is_counselor:
                raise HTTPException(status_code=403, detail="只有咨询师可以标记预约为已完成")
        
        appointment.status = new_status
    
    # 咨询师填写小结
    if appointment_data.summary is not None:
        if not is_counselor:
            raise HTTPException(status_code=403, detail="只有咨询师可以填写小结")
        appointment.summary = appointment_data.summary
    
    # 双方确认咨询结束
    # 检查预约时间是否已过（只有过了预约时间段才能确认结束）
    from datetime import datetime, timezone, timedelta
    tz_beijing = timezone(timedelta(hours=8))
    now_tz = datetime.now(tz_beijing)
    now = now_tz.replace(tzinfo=None)
    
    appointment_datetime_naive = appointment.appointment_date
    consultation_end_time = None
    if appointment_datetime_naive:
        if appointment_datetime_naive.tzinfo is not None:
            appointment_datetime_naive = appointment_datetime_naive.astimezone(tz_beijing).replace(tzinfo=None)
        consultation_end_time = appointment_datetime_naive + timedelta(hours=1)
    
    user_confirmed_now = False
    counselor_confirmed_now = False
    
    if appointment_data.user_confirmed_complete is not None:
        if not is_user:
            raise HTTPException(status_code=403, detail="只有用户（学生）可以确认咨询结束")
        if appointment_data.user_confirmed_complete:
            # 检查预约时间是否已过
            if consultation_end_time and now < consultation_end_time:
                raise HTTPException(status_code=400, detail="预约时间段尚未结束，无法确认结束")
            if appointment.status not in {AppointmentStatus.CONFIRMED, AppointmentStatus.COMPLETED}:
                raise HTTPException(status_code=400, detail="只有已确认的预约才能确认结束")
            if not appointment.user_confirmed_complete:
                user_confirmed_now = True
            appointment.user_confirmed_complete = True
    
    if appointment_data.counselor_confirmed_complete is not None:
        if not is_counselor:
            raise HTTPException(status_code=403, detail="只有咨询师可以确认咨询结束")
        if appointment_data.counselor_confirmed_complete:
            # 检查预约时间是否已过
            if consultation_end_time and now < consultation_end_time:
                raise HTTPException(status_code=400, detail="预约时间段尚未结束，无法确认结束")
            if appointment.status not in {AppointmentStatus.CONFIRMED, AppointmentStatus.COMPLETED}:
                raise HTTPException(status_code=400, detail="只有已确认的预约才能确认结束")
            if not appointment.counselor_confirmed_complete:
                counselor_confirmed_now = True
            appointment.counselor_confirmed_complete = True
    
    # 如果双方都确认了，自动标记为已完成并创建咨询记录
    if appointment.user_confirmed_complete and appointment.counselor_confirmed_complete:
        if appointment.status != AppointmentStatus.COMPLETED:
            appointment.status = AppointmentStatus.COMPLETED
            
            # 检查是否已存在咨询记录
            existing_record = db.query(ConsultationRecord).filter(
                ConsultationRecord.appointment_id == appointment_id
            ).first()
            
            if not existing_record:
                # 创建咨询记录
                # 确定确认时间：如果刚刚确认，使用当前时间；否则使用预约时间+1小时
                user_confirmed_time = now_tz if user_confirmed_now else (
                    appointment.appointment_date + timedelta(hours=1) if appointment.appointment_date else now_tz
                )
                counselor_confirmed_time = now_tz if counselor_confirmed_now else (
                    appointment.appointment_date + timedelta(hours=1) if appointment.appointment_date else now_tz
                )
                
                consultation_record = ConsultationRecord(
                    appointment_id=appointment_id,
                    user_id=appointment.user_id,
                    counselor_id=appointment.counselor_id,
                    consult_type=appointment.consult_type,
                    consult_method=appointment.consult_method,
                    appointment_date=appointment.appointment_date,
                    description=appointment.description,
                    summary=appointment.summary,
                    rating=appointment.rating,
                    review=appointment.review,
                    user_confirmed_at=user_confirmed_time,
                    counselor_confirmed_at=counselor_confirmed_time
                )
                db.add(consultation_record)
                
                # 更新咨询师的咨询次数统计
                counselor = db.query(Counselor).filter(Counselor.id == appointment.counselor_id).first()
                if counselor:
                    counselor.total_consultations = (counselor.total_consultations or 0) + 1
    
    # 用户评分和评价
    if appointment_data.rating is not None:
        if not is_user:
            raise HTTPException(status_code=403, detail="只有用户（学生）可以评分")
        if appointment.status != AppointmentStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="只有已完成的咨询才能评分")
        if appointment_data.rating < 1 or appointment_data.rating > 5:
            raise HTTPException(status_code=400, detail="评分必须在1-5之间")
        appointment.rating = appointment_data.rating
        
        # 更新咨询师评分统计
        from models import CounselorRating
        # 检查是否已有评分记录
        existing_rating = db.query(CounselorRating).filter(
            CounselorRating.appointment_id == appointment_id
        ).first()
        
        if existing_rating:
            # 更新现有评分
            existing_rating.rating = appointment_data.rating
            if appointment_data.review is not None:
                existing_rating.review = appointment_data.review
        else:
            # 创建新评分记录
            # 确保user_id和counselor_id是整数
            user_id = int(appointment.user_id) if appointment.user_id else None
            counselor_id = int(appointment.counselor_id) if appointment.counselor_id else None
            
            if not user_id or not counselor_id:
                raise HTTPException(status_code=400, detail="预约信息不完整，无法创建评分记录")
            
            new_rating = CounselorRating(
                appointment_id=appointment_id,
                user_id=user_id,
                counselor_id=counselor_id,
                rating=appointment_data.rating,
                review=appointment_data.review if appointment_data.review else None
            )
            db.add(new_rating)
        
        # 更新咨询师的平均评分和评价数
        counselor = db.query(Counselor).filter(Counselor.id == appointment.counselor_id).first()
        if counselor:
            # 重新计算平均评分
            all_ratings = db.query(CounselorRating).filter(
                CounselorRating.counselor_id == counselor.id
            ).all()
            if all_ratings:
                total_rating = sum(r.rating for r in all_ratings)
                counselor.review_count = len(all_ratings)
                counselor.average_rating = round(total_rating / len(all_ratings), 2)
            else:
                counselor.review_count = 0
                counselor.average_rating = 0.0
    
    if appointment_data.review is not None:
        if not is_user:
            raise HTTPException(status_code=403, detail="只有用户（学生）可以评价")
        appointment.review = appointment_data.review
    
    db.commit()
    
    # ============ 状态流转同步 ============
    # 状态变更时，同步更新相关数据，确保各页面显示的状态一致
    # 注意：取消预约后，时段会自动释放（因为查询可用时段时会排除CANCELLED状态的预约）
    
    db.refresh(appointment)
    
    # 重新加载关联对象
    appointment = db.query(Appointment).options(
        joinedload(Appointment.user),
        joinedload(Appointment.counselor)
    ).filter(Appointment.id == appointment_id).first()
    
    # 构建响应数据，包含用户和咨询师信息
    appointment_dict = {
        "id": appointment.id,
        "user_id": appointment.user_id,
        "counselor_id": appointment.counselor_id,
        "consult_type": appointment.consult_type,
        "consult_method": appointment.consult_method,
        "appointment_date": appointment.appointment_date,
        "status": appointment.status,
        "description": appointment.description,
        "summary": appointment.summary,
        "rating": appointment.rating,
        "review": appointment.review,
        "user_confirmed_complete": appointment.user_confirmed_complete,
        "counselor_confirmed_complete": appointment.counselor_confirmed_complete,
        "created_at": appointment.created_at,
        "updated_at": appointment.updated_at,
        "user_name": appointment.user.nickname or appointment.user.username if appointment.user else None,
        "user_nickname": appointment.user.nickname if appointment.user else None,
        "counselor_name": appointment.counselor.real_name if appointment.counselor else None,
        "counselor": {
            "id": appointment.counselor.id,
            "real_name": appointment.counselor.real_name,
            "user_id": appointment.counselor.user_id,
        } if appointment.counselor else None,
    }
    
    return AppointmentResponse(**appointment_dict)


@router.delete("/{appointment_id}")
def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    取消预约
    - 只有学生可以取消自己的预约
    - 取消后释放时段（标记为"可预约"），状态同步更新
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    if appointment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权取消此预约")
    
    # 只能取消待确认或已确认的预约
    if appointment.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
        raise HTTPException(status_code=400, detail="该预约状态不允许取消")
    
    # 更新状态为已取消
    appointment.status = AppointmentStatus.CANCELLED
    
    db.commit()
    
    # ============ 状态流转同步 ============
    # 取消预约后，时段会自动释放
    # 因为查询可用时段时会排除CANCELLED状态的预约
    # 这样其他用户就可以预约该时段了
    
    return {"message": "预约已取消，时段已释放"}
