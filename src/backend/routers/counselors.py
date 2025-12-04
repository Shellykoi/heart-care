"""
咨询师路由 - 咨询师管理和查询
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, time, timedelta
from jose import jwt as jwt_lib, JWTError

from database import get_db
from models import Counselor, User, CounselorStatus, CounselorSchedule, CounselorUnavailable, CounselorFavorite, Appointment, ConsultationRecord, AppointmentStatus
from schemas import (
    CounselorCreate, CounselorResponse, CounselorUpdate, ScheduleSet,
    CounselorProfileUpdate, ScheduleUpdate, UnavailablePeriodCreate, UnavailablePeriodUpdate,
    CounselorFavoriteResponse, ClientInfo
)
from auth import get_current_active_user, oauth2_scheme
from sqlalchemy import func, distinct, and_, or_
from collections import defaultdict
from sqlalchemy.orm import joinedload
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """可选获取当前用户（如果已登录）"""
    if not token:
        return None
    try:
        from auth import SECRET_KEY, ALGORITHM
        payload = jwt_lib.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        user_id: int = int(user_id_str)
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            return None
        return user
    except (JWTError, ValueError, Exception):
        return None


@router.post("/apply", response_model=CounselorResponse)
def apply_as_counselor(
    counselor_data: CounselorCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    申请成为咨询师
    - 需要提供资质证明
    - 等待管理员审核
    """
    # 检查是否已经申请过
    existing = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="您已经提交过申请")
    
    # 创建咨询师申请
    new_counselor = Counselor(
        user_id=current_user.id,
        real_name=counselor_data.real_name,
        gender=counselor_data.gender,
        specialty=counselor_data.specialty,
        experience_years=counselor_data.experience_years,
        certificate_url=counselor_data.certificate_url,
        bio=counselor_data.bio,
        status=CounselorStatus.PENDING
    )
    
    db.add(new_counselor)
    db.commit()
    db.refresh(new_counselor)
    
    # 确保 average_rating 和 review_count 不为 None
    if new_counselor.average_rating is None:
        new_counselor.average_rating = 0.0
    if new_counselor.review_count is None:
        new_counselor.review_count = 0
    if new_counselor.fee is None:
        new_counselor.fee = 0.0
    
    return new_counselor


@router.get("/search", response_model=List[CounselorResponse])
def search_counselors(
    specialty: Optional[str] = None,
    gender: Optional[str] = None,
    consult_method: Optional[str] = None,
    sort_by: Optional[str] = None,  # 'hot', 'new', 'rating'
    skip: int = 0,
    limit: int = 20,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    搜索咨询师
    - 支持按擅长领域、性别、咨询方式筛选
    - 支持排序：按热度、最新入驻、好评率
    - 分页查询
    """
    import json
    
    query = db.query(Counselor).filter(Counselor.status == CounselorStatus.ACTIVE)
    
    # 如果用户已登录，获取用户收藏的咨询师ID列表
    favorited_counselor_ids = set()
    if current_user:
        favorites = db.query(CounselorFavorite.counselor_id).filter(
            CounselorFavorite.user_id == current_user.id
        ).all()
        favorited_counselor_ids = {f[0] for f in favorites}
    
    # 按擅长领域筛选（支持多个，用逗号分隔）
    if specialty:
        specialties = [s.strip() for s in specialty.split(',') if s.strip()]
        if specialties:
            from sqlalchemy import or_
            conditions = [Counselor.specialty.contains(s) for s in specialties]
            query = query.filter(or_(*conditions))
    
    # 按性别筛选
    if gender and gender != 'all':
        query = query.filter(Counselor.gender == gender)
    
    # 按咨询方式筛选
    if consult_method:
        methods = [m.strip() for m in consult_method.split(',') if m.strip()]
        if methods:
            # 由于 consult_methods 可能是 JSON 字符串或逗号分隔的字符串
            # 使用 LIKE 查询来匹配
            from sqlalchemy import or_
            conditions = []
            for method in methods:
                # 匹配 JSON 格式 ["video", "offline"] 或逗号分隔格式 "video,offline"
                conditions.append(
                    or_(
                        Counselor.consult_methods.like(f'%"{method}"%'),
                        Counselor.consult_methods.like(f'%{method}%')
                    )
                )
            if conditions:
                query = query.filter(or_(*conditions))
    
    # 排序
    if sort_by == 'hot':
        # 按热度排序（咨询量 + 好评率）
        query = query.order_by(
            (Counselor.total_consultations * 0.6 + Counselor.average_rating * 10 * 0.4).desc()
        )
    elif sort_by == 'new':
        # 按最新入驻排序
        query = query.order_by(Counselor.created_at.desc())
    elif sort_by == 'rating':
        # 按好评率排序
        query = query.order_by(Counselor.average_rating.desc(), Counselor.review_count.desc())
    else:
        # 默认按创建时间排序
        query = query.order_by(Counselor.created_at.desc())
    
    counselors = query.offset(skip).limit(limit).all()
    
    # 确保 average_rating 和 review_count 不为 None，并格式化 specialty 和 consult_methods
    for counselor in counselors:
        if counselor.average_rating is None:
            counselor.average_rating = 0.0
        if counselor.review_count is None:
            counselor.review_count = 0
        if counselor.fee is None:
            counselor.fee = 0.0
        
        # 解析 specialty 和 consult_methods 为字符串（用于显示）
        # CounselorResponse 期望 specialty 和 consult_methods 是字符串
        specialty_parsed = parse_json_array_field(counselor.specialty, default=[])
        consult_methods_parsed = parse_json_array_field(counselor.consult_methods, default=[])
        
        # 将数组转换为逗号分隔的字符串（用于显示）
        counselor.specialty = ', '.join(specialty_parsed) if specialty_parsed else ''
        counselor.consult_methods = ', '.join(consult_methods_parsed) if consult_methods_parsed else ''
        # 检查是否已收藏
        counselor.is_favorited = counselor.id in favorited_counselor_ids
    
    return counselors


def parse_json_array_field(value, default=None):
    """
    统一解析JSON数组字段的函数
    支持多种格式：
    1. JSON数组字符串：'["item1", "item2"]'
    2. 逗号分隔字符串：'item1, item2' 或 'item1，item2'（中文逗号）
    3. 单个字符串：'item1'
    4. None/空字符串：返回默认值或空数组
    """
    if value is None:
        return default if default is not None else []
    
    if isinstance(value, list):
        # 已经是数组，清理空格后返回
        return [str(item).strip() for item in value if item and str(item).strip()]
    
    if not isinstance(value, str):
        return default if default is not None else []
    
    value = value.strip()
    if not value:
        return default if default is not None else []
    
    # 尝试解析JSON数组
    try:
        if value.startswith('[') and value.endswith(']'):
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item and str(item).strip()]
    except (json.JSONDecodeError, ValueError):
        pass
    
    # 尝试按逗号分割（支持中文逗号和英文逗号）
    # 先尝试中文逗号
    if '，' in value:
        items = value.split('，')
    else:
        items = value.split(',')
    
    # 清理空格和空项
    result = [item.strip() for item in items if item.strip()]
    return result if result else (default if default is not None else [])


# ============ 具体路由（必须在参数路由之前）============

@router.get("/profile")
def get_counselor_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前咨询师的完整个人资料"""
    try:
        # 添加验证日志
        logger.info(f"[get_counselor_profile] 开始处理请求，用户ID: {current_user.id if current_user else None}")
        logger.info(f"[get_counselor_profile] 用户ID: {current_user.id}, 用户名: {current_user.username}")
        counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
        
        if not counselor:
            logger.warning(f"[get_counselor_profile] 用户 {current_user.id} 还不是咨询师")
            raise HTTPException(status_code=404, detail="您还不是咨询师")
        
        logger.info(f"[get_counselor_profile] 找到咨询师: ID={counselor.id}, 姓名={counselor.real_name}, 状态={counselor.status}")
        
        # 使用统一函数解析JSON字段
        specialty = parse_json_array_field(counselor.specialty, default=[])
        consult_methods = parse_json_array_field(counselor.consult_methods, default=[])
        consult_type = parse_json_array_field(counselor.consult_type, default=[])
        
        # certificate_url 特殊处理（可能是单个URL或数组）
        certificate_url = counselor.certificate_url
        if certificate_url:
            parsed = parse_json_array_field(certificate_url, default=[])
            certificate_url = parsed if parsed else []
        else:
            certificate_url = []
        
        # 调试日志：记录解析后的数据
        logger.info(f"[get_counselor_profile] 解析结果 - specialty: {specialty}, consult_methods: {consult_methods}, consult_type: {consult_type}")
        logger.info(f"[get_counselor_profile] 原始数据 - specialty: {counselor.specialty}, consult_methods: {counselor.consult_methods}, consult_type: {counselor.consult_type}")
        
        # 确保 age 和 experience_years 是整数或 None
        # 处理可能存在的字符串类型的值（如果数据库存储的是字符串）
        age_value = None
        if counselor.age is not None:
            try:
                if isinstance(counselor.age, str):
                    age_value = int(counselor.age.strip()) if counselor.age.strip() else None
                else:
                    age_value = int(counselor.age)
            except (ValueError, AttributeError) as e:
                logger.warning(f"[get_counselor_profile] 解析age失败: {e}, 原始值: {counselor.age}")
                age_value = None
        
        experience_years_value = 0
        if counselor.experience_years is not None:
            try:
                if isinstance(counselor.experience_years, str):
                    experience_years_value = int(counselor.experience_years.strip()) if counselor.experience_years.strip() else 0
                else:
                    experience_years_value = int(counselor.experience_years)
            except (ValueError, AttributeError) as e:
                logger.warning(f"[get_counselor_profile] 解析experience_years失败: {e}, 原始值: {counselor.experience_years}")
                experience_years_value = 0
        
        # 处理性别字段：确保返回小写值
        gender_value = "female"
        if counselor.gender:
            gender_str = str(counselor.gender).lower()
            if gender_str in ["male", "female", "other"]:
                gender_value = gender_str
            elif "male" in gender_str:
                gender_value = "male"
            elif "female" in gender_str:
                gender_value = "female"
            else:
                gender_value = "other"
        
        # 处理 datetime 和枚举类型的序列化
        status_value = counselor.status.value if hasattr(counselor.status, 'value') else str(counselor.status)
        created_at_value = counselor.created_at.isoformat() if counselor.created_at else None
        updated_at_value = counselor.updated_at.isoformat() if counselor.updated_at else None
        
        result = {
            "id": counselor.id,
            "user_id": counselor.user_id,
            "real_name": counselor.real_name or "",
            "gender": gender_value,
            "age": age_value,
            "specialty": specialty,
            "experience_years": experience_years_value,
            "qualification": counselor.qualification or "",
            "certificate_url": certificate_url,
            "consult_methods": consult_methods,
            "consult_type": consult_type,
            "fee": counselor.fee if counselor.fee is not None else 0.0,
            "consult_place": counselor.consult_place or "",
            "max_daily_appointments": counselor.max_daily_appointments if counselor.max_daily_appointments is not None else 3,
            "avatar": counselor.avatar or "",
            "bio": counselor.bio or "",
            "intro": counselor.intro or "",
            "status": status_value,
            "created_at": created_at_value,
            "updated_at": updated_at_value
        }
        
        logger.info(f"[get_counselor_profile] 返回数据详情:")
        logger.info(f"  - real_name: {result['real_name']} (类型: {type(result['real_name'])})")
        logger.info(f"  - gender: {result['gender']} (类型: {type(result['gender'])})")
        logger.info(f"  - age: {result['age']} (类型: {type(result['age'])})")
        logger.info(f"  - experience_years: {result['experience_years']} (类型: {type(result['experience_years'])})")
        logger.info(f"  - qualification: {result['qualification']} (类型: {type(result['qualification'])})")
        logger.info(f"  - specialty: {result['specialty']} (类型: {type(result['specialty'])})")
        logger.info(f"  - consult_methods: {result['consult_methods']} (类型: {type(result['consult_methods'])})")
        logger.info(f"  - consult_type: {result['consult_type']} (类型: {type(result['consult_type'])})")
        logger.info(f"  - certificate_url: {result['certificate_url']} (类型: {type(result['certificate_url'])})")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[get_counselor_profile] 获取咨询师资料失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取咨询师资料失败: {str(e)}")


@router.put("/profile")
def update_counselor_profile(
    counselor_data: CounselorProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新咨询师完整个人资料"""
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    
    if not counselor:
        raise HTTPException(status_code=404, detail="您还不是咨询师")
    
    # 检查是否需要重新审核（修改资质证书）
    need_review = counselor_data.need_review
    if counselor_data.certificate_url is not None:
        old_certificates = counselor.certificate_url or ""
        try:
            old_certs = json.loads(old_certificates) if old_certificates.startswith('[') else [old_certificates] if old_certificates else []
        except:
            old_certs = [old_certificates] if old_certificates else []
        
        new_certs = counselor_data.certificate_url or []
        if set(old_certs) != set(new_certs):
            need_review = True
    
    # 更新基本信息
    # 使用 model_dump(exclude_unset=True) 来只获取明确设置的字段
    update_dict = counselor_data.model_dump(exclude_unset=True)
    
    if 'real_name' in update_dict:
        counselor.real_name = update_dict['real_name']
    if 'gender' in update_dict:
        counselor.gender = update_dict['gender']
    if 'age' in update_dict:
        # 处理可能存在的字符串类型的值
        age_val = update_dict['age']
        if age_val is not None:
            try:
                if isinstance(age_val, str):
                    counselor.age = int(age_val.strip()) if age_val.strip() else None
                else:
                    counselor.age = int(age_val)
            except (ValueError, AttributeError):
                counselor.age = None
        else:
            counselor.age = None
    
    if 'experience_years' in update_dict:
        # 处理可能存在的字符串类型的值
        exp_val = update_dict['experience_years']
        if exp_val is not None:
            try:
                if isinstance(exp_val, str):
                    counselor.experience_years = int(exp_val.strip()) if exp_val.strip() else 0
                else:
                    counselor.experience_years = int(exp_val)
            except (ValueError, AttributeError):
                counselor.experience_years = 0
        else:
            counselor.experience_years = 0
    if 'avatar' in update_dict:
        counselor.avatar = update_dict['avatar']
    
    # 更新专业信息
    if 'specialty' in update_dict:
        # 确保 specialty 是数组，清理空格
        specialty_list = update_dict['specialty']
        if isinstance(specialty_list, list):
            # 清理空格和空项
            specialty_list = [str(item).strip() for item in specialty_list if item and str(item).strip()]
            counselor.specialty = json.dumps(specialty_list, ensure_ascii=False)
            logger.debug(f"[update_counselor_profile] 保存 specialty: {counselor.specialty}")
        elif isinstance(specialty_list, str):
            # 如果传入的是字符串，先解析再保存
            parsed = parse_json_array_field(specialty_list, default=[])
            counselor.specialty = json.dumps(parsed, ensure_ascii=False)
            logger.debug(f"[update_counselor_profile] 解析后保存 specialty: {counselor.specialty}")
    
    if 'qualification' in update_dict:
        counselor.qualification = update_dict['qualification']
    
    if 'certificate_url' in update_dict:
        cert_list = update_dict['certificate_url']
        if cert_list:
            if isinstance(cert_list, list):
                cert_list = [str(item).strip() for item in cert_list if item and str(item).strip()]
                counselor.certificate_url = json.dumps(cert_list, ensure_ascii=False) if cert_list else None
            else:
                counselor.certificate_url = json.dumps([str(cert_list).strip()], ensure_ascii=False)
        else:
            counselor.certificate_url = None
    
    if 'consult_methods' in update_dict:
        # 确保 consult_methods 是数组，清理空格
        methods_list = update_dict['consult_methods']
        if isinstance(methods_list, list):
            # 清理空格和空项
            methods_list = [str(item).strip() for item in methods_list if item and str(item).strip()]
            counselor.consult_methods = json.dumps(methods_list, ensure_ascii=False)
            logger.debug(f"[update_counselor_profile] 保存 consult_methods: {counselor.consult_methods}")
        elif isinstance(methods_list, str):
            # 如果传入的是字符串，先解析再保存
            parsed = parse_json_array_field(methods_list, default=[])
            counselor.consult_methods = json.dumps(parsed, ensure_ascii=False)
            logger.debug(f"[update_counselor_profile] 解析后保存 consult_methods: {counselor.consult_methods}")
    
    if 'consult_type' in update_dict:
        type_list = update_dict['consult_type']
        if type_list:
            if isinstance(type_list, list):
                type_list = [str(item).strip() for item in type_list if item and str(item).strip()]
                counselor.consult_type = json.dumps(type_list, ensure_ascii=False) if type_list else None
            elif isinstance(type_list, str):
                parsed = parse_json_array_field(type_list, default=[])
                counselor.consult_type = json.dumps(parsed, ensure_ascii=False) if parsed else None
        else:
            counselor.consult_type = None
    if 'fee' in update_dict:
        counselor.fee = update_dict['fee']
    if 'consult_place' in update_dict:
        counselor.consult_place = update_dict['consult_place']
    if 'max_daily_appointments' in update_dict:
        counselor.max_daily_appointments = update_dict['max_daily_appointments']
    
    # 更新个人简介
    if 'intro' in update_dict:
        counselor.intro = update_dict['intro']
    if 'bio' in update_dict:
        counselor.bio = update_dict['bio']
    
    # 如果需要重新审核，将状态改为待审核
    if need_review and counselor.status == CounselorStatus.ACTIVE:
        counselor.status = CounselorStatus.PENDING
    
    db.commit()
    db.refresh(counselor)
    
    return {"message": "资料更新成功", "need_review": need_review}


@router.post("/avatar/upload")
def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """上传咨询师头像"""
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="您还不是咨询师")
    
    # 检查文件类型
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只能上传图片文件")
    
    # 检查文件大小（5MB）
    file_content = file.file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过5MB")
    
    # 这里应该上传到MinIO或云存储，简化处理：返回URL
    # TODO: 实际上传到MinIO
    # 暂时返回一个模拟URL
    avatar_url = f"/uploads/avatars/{counselor.id}_{file.filename}"
    
    # 更新数据库
    counselor.avatar = avatar_url
    db.commit()
    
    return {"avatar_url": avatar_url, "message": "头像上传成功"}


@router.get("/stats/mine")
def get_counselor_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取咨询师的统计数据"""
    from models import Appointment, AppointmentStatus
    from datetime import datetime, date
    
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    
    if not counselor:
        raise HTTPException(status_code=404, detail="您还不是咨询师")
    
    # 待确认预约数
    pending_appointments = db.query(Appointment).filter(
        Appointment.counselor_id == counselor.id,
        Appointment.status == AppointmentStatus.PENDING
    ).count()
    
    # 今日咨询数
    today = date.today()
    today_appointments = db.query(Appointment).filter(
        Appointment.counselor_id == counselor.id,
        Appointment.appointment_date >= datetime.combine(today, datetime.min.time()),
        Appointment.appointment_date < datetime.combine(today, datetime.max.time()),
        Appointment.status == AppointmentStatus.CONFIRMED
    ).count()
    
    # 总咨询次数
    total_consultations = db.query(Appointment).filter(
        Appointment.counselor_id == counselor.id,
        Appointment.status == AppointmentStatus.COMPLETED
    ).count()
    
    # 好评率和平均评分（从CounselorRating表重新计算）
    from models import CounselorRating
    ratings = db.query(CounselorRating).filter(
        CounselorRating.counselor_id == counselor.id
    ).all()
    
    if ratings:
        good_ratings = sum(1 for r in ratings if r.rating >= 4)
        rating_percentage = int((good_ratings / len(ratings)) * 100)
        # 重新计算平均评分
        calculated_average_rating = round(sum(r.rating for r in ratings) / len(ratings), 1)
    else:
        rating_percentage = 0
        calculated_average_rating = None
    
    # 如果计算出的平均评分为None或0，但有评分数据，使用计算值
    # 如果还是没有，使用counselor.average_rating，如果还是None或0，则显示5.0（临时方案）
    if calculated_average_rating is not None and calculated_average_rating > 0:
        final_average_rating = calculated_average_rating
    elif counselor.average_rating is not None and counselor.average_rating > 0:
        final_average_rating = counselor.average_rating
    else:
        # 如果无法正确计算，显示5.0（临时方案）
        final_average_rating = 5.0
    
    return {
        "pending_appointments": pending_appointments,
        "today_appointments": today_appointments,
        "total_consultations": total_consultations or counselor.total_consultations,
        "rating_percentage": rating_percentage,
        "average_rating": final_average_rating,
        "review_count": counselor.review_count or len(ratings) if ratings else 0
    }


@router.get("/stats/consultation-activity")
def get_counselor_consultation_activity(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取咨询师的咨询活动数据（用于数据可视化）"""
    from models import CounselorRating

    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()

    if not counselor:
        raise HTTPException(status_code=404, detail="您还不是咨询师")

    try:
        completed_appointments = db.query(Appointment).filter(
            Appointment.counselor_id == counselor.id,
            or_(
                Appointment.status == AppointmentStatus.COMPLETED,
                and_(
                    Appointment.status == AppointmentStatus.CONFIRMED,
                    Appointment.user_confirmed_complete.is_(True),
                    Appointment.counselor_confirmed_complete.is_(True),
                ),
            )
        ).order_by(Appointment.appointment_date.desc()).all()

        today = date.today()
        date_stats = defaultdict(int)
        date_duration_stats = defaultdict(int)
        consultation_activities = []
        DEFAULT_DURATION_MINUTES = 60
        total_duration_minutes = 0

        for appointment in completed_appointments:
            if appointment.appointment_date is None:
                continue

            try:
                apt_datetime = appointment.appointment_date
                if isinstance(apt_datetime, datetime) and apt_datetime.tzinfo is not None:
                    apt_datetime = apt_datetime.astimezone().replace(tzinfo=None)
                elif not isinstance(apt_datetime, datetime):
                    apt_datetime = datetime.fromisoformat(str(apt_datetime).replace('Z', '+00:00'))
                    if apt_datetime.tzinfo is not None:
                        apt_datetime = apt_datetime.astimezone().replace(tzinfo=None)
            except Exception:
                apt_datetime = None

            if apt_datetime is None:
                continue

            appointment_date = apt_datetime.date()
            days_ago = (today - appointment_date).days

            if days_ago > 30:
                continue

            date_str = appointment_date.isoformat()
            date_stats[date_str] += 1

            duration_minutes = DEFAULT_DURATION_MINUTES
            end_datetime = None

            if appointment.description and "|END_TIME:" in appointment.description:
                try:
                    end_time_str = appointment.description.split("|END_TIME:")[1].split("|")[0]
                    end_datetime = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
                    if end_datetime.tzinfo is not None:
                        end_datetime = end_datetime.astimezone().replace(tzinfo=None)
                except Exception:
                    end_datetime = None

            if end_datetime is None and appointment.updated_at:
                try:
                    updated_at = appointment.updated_at
                    if isinstance(updated_at, datetime) and updated_at.tzinfo is not None:
                        updated_at = updated_at.astimezone().replace(tzinfo=None)
                    elif not isinstance(updated_at, datetime):
                        updated_at = datetime.fromisoformat(str(updated_at).replace('Z', '+00:00'))
                        if updated_at.tzinfo is not None:
                            updated_at = updated_at.astimezone().replace(tzinfo=None)

                    if isinstance(updated_at, datetime) and isinstance(apt_datetime, datetime):
                        duration = updated_at - apt_datetime
                        duration_minutes = max(60, min(180, int(duration.total_seconds() / 60)))
                except Exception:
                    duration_minutes = DEFAULT_DURATION_MINUTES

            if end_datetime and isinstance(end_datetime, datetime) and isinstance(apt_datetime, datetime):
                duration = end_datetime - apt_datetime
                duration_minutes = max(60, min(180, int(duration.total_seconds() / 60)))

            date_duration_stats[date_str] += duration_minutes
            total_duration_minutes += duration_minutes

            try:
                consultation_activities.append({
                    "id": appointment.id,
                    "date": date_str,
                    "datetime": appointment.appointment_date.isoformat()
                    if hasattr(appointment.appointment_date, "isoformat")
                    else str(appointment.appointment_date),
                    "consult_type": appointment.consult_type or "心理咨询",
                    "consult_method": appointment.consult_method or "未知",
                    "user_name": appointment.user.nickname if appointment.user else None,
                    "user_username": appointment.user.username if appointment.user else None,
                    "duration_minutes": duration_minutes,
                    "rating": appointment.rating,
                    "status": "completed",
                })
            except Exception:
                continue

        date_list = []
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            date_str = d.isoformat()
            date_list.append({
                "date": date_str,
                "count": date_stats.get(date_str, 0),
                "total_duration": date_duration_stats.get(date_str, 0),
            })

        week_stats = defaultdict(int)
        for appointment in completed_appointments:
            if appointment.appointment_date is None:
                continue
            try:
                apt_datetime = appointment.appointment_date
                if isinstance(apt_datetime, datetime) and apt_datetime.tzinfo is not None:
                    apt_datetime = apt_datetime.astimezone().replace(tzinfo=None)
                elif not isinstance(apt_datetime, datetime):
                    apt_datetime = datetime.fromisoformat(str(apt_datetime).replace('Z', '+00:00'))
                    if apt_datetime.tzinfo is not None:
                        apt_datetime = apt_datetime.astimezone().replace(tzinfo=None)
            except Exception:
                continue

            appointment_date = apt_datetime.date()
            days_ago = (today - appointment_date).days
            if days_ago <= 30:
                week_num = days_ago // 7
                week_stats[week_num] += 1

        type_stats = defaultdict(int)
        for appointment in completed_appointments:
            type_stats[appointment.consult_type or "心理咨询"] += 1

        hour_stats = defaultdict(int)
        hour_duration_stats = defaultdict(int)
        time_period_stats = {
            "morning": 0,
            "afternoon": 0,
            "evening": 0,
            "night": 0,
        }
        time_period_duration = {
            "morning": 0,
            "afternoon": 0,
            "evening": 0,
            "night": 0,
        }
        duration_distribution = {
            "short": 0,
            "medium": 0,
            "long": 0,
            "very_long": 0,
        }

        for appointment in completed_appointments:
            if appointment.appointment_date is None:
                continue

            try:
                apt_datetime = appointment.appointment_date
                if isinstance(apt_datetime, datetime) and apt_datetime.tzinfo is not None:
                    apt_datetime = apt_datetime.astimezone().replace(tzinfo=None)
                elif not isinstance(apt_datetime, datetime):
                    apt_datetime = datetime.fromisoformat(str(apt_datetime).replace('Z', '+00:00'))
                    if apt_datetime.tzinfo is not None:
                        apt_datetime = apt_datetime.astimezone().replace(tzinfo=None)
            except Exception:
                continue

            if not isinstance(apt_datetime, datetime):
                continue

            hour = apt_datetime.hour
            hour_stats[hour] += 1

            duration_minutes = DEFAULT_DURATION_MINUTES
            end_datetime = None

            if appointment.description and "|END_TIME:" in appointment.description:
                try:
                    end_time_str = appointment.description.split("|END_TIME:")[1].split("|")[0]
                    end_datetime = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
                    if end_datetime.tzinfo is not None:
                        end_datetime = end_datetime.astimezone().replace(tzinfo=None)
                except Exception:
                    end_datetime = None

            if end_datetime is None and appointment.updated_at:
                try:
                    updated_at = appointment.updated_at
                    if isinstance(updated_at, datetime) and updated_at.tzinfo is not None:
                        updated_at = updated_at.astimezone().replace(tzinfo=None)
                    elif not isinstance(updated_at, datetime):
                        updated_at = datetime.fromisoformat(str(updated_at).replace('Z', '+00:00'))
                        if updated_at.tzinfo is not None:
                            updated_at = updated_at.astimezone().replace(tzinfo=None)

                    if isinstance(updated_at, datetime):
                        duration = updated_at - apt_datetime
                        duration_minutes = max(60, min(180, int(duration.total_seconds() / 60)))
                except Exception:
                    duration_minutes = DEFAULT_DURATION_MINUTES

            if end_datetime and isinstance(end_datetime, datetime):
                duration = end_datetime - apt_datetime
                duration_minutes = max(60, min(180, int(duration.total_seconds() / 60)))

            hour_duration_stats[hour] += duration_minutes

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

            if duration_minutes < 60:
                duration_distribution["short"] += 1
            elif duration_minutes < 120:
                duration_distribution["medium"] += 1
            elif duration_minutes < 180:
                duration_distribution["long"] += 1
            else:
                duration_distribution["very_long"] += 1

        hour_list = []
        for hour in range(24):
            count = hour_stats.get(hour, 0)
            total_dur = hour_duration_stats.get(hour, 0)
            avg_dur = int(total_dur / count) if count > 0 else 0
            hour_list.append({
                "hour": hour,
                "count": count,
                "total_duration": total_dur,
                "average_duration": avg_dur,
            })

        total_consultations = len(completed_appointments)
        average_duration_minutes = int(total_duration_minutes / total_consultations) if total_consultations > 0 else 0
        total_hours = round(total_duration_minutes / 60, 1)
        recent_7_days = sum(date_stats.get((today - timedelta(days=i)).isoformat(), 0) for i in range(7))
        recent_30_days = sum(date_stats.values())

        ratings = db.query(CounselorRating).filter(CounselorRating.counselor_id == counselor.id).all()
        average_rating = round(sum(r.rating for r in ratings) / len(ratings), 1) if ratings else 0

        return {
            "total_consultations": total_consultations,
            "total_duration_minutes": total_duration_minutes,
            "total_duration_hours": total_hours,
            "average_duration_minutes": average_duration_minutes,
            "recent_7_days": recent_7_days,
            "recent_30_days": recent_30_days,
            "average_rating": average_rating,
            "daily_stats": date_list,
            "week_stats": dict(week_stats),
            "type_stats": dict(type_stats),
            "hour_stats": hour_list,
            "time_period_stats": time_period_stats,
            "time_period_duration": time_period_duration,
            "duration_distribution": duration_distribution,
            "activities": consultation_activities[:50],
        }
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取咨询活动数据失败: {exc}")


@router.post("/schedules")
def set_counselor_schedules(
    schedule_set: ScheduleSet,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    批量设置咨询师的可预约时段
    """
    from datetime import time
    
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    
    if not counselor:
        raise HTTPException(status_code=404, detail="您还不是咨询师")
    
    # 删除旧的时段设置
    db.query(CounselorSchedule).filter(
        CounselorSchedule.counselor_id == counselor.id
    ).delete()
    
    # 添加新的时段设置
    for schedule_item in schedule_set.schedules:
        start_time_obj = datetime.strptime(schedule_item.start_time, "%H:%M").time() if isinstance(schedule_item.start_time, str) else schedule_item.start_time
        end_time_obj = datetime.strptime(schedule_item.end_time, "%H:%M").time() if isinstance(schedule_item.end_time, str) else schedule_item.end_time
        
        schedule = CounselorSchedule(
            counselor_id=counselor.id,
            weekday=schedule_item.weekday,
            start_time=start_time_obj,
            end_time=end_time_obj,
            max_num=schedule_item.max_num or 1,
            is_available=schedule_item.is_available
        )
        db.add(schedule)
    
    db.commit()
    
    return {"message": "时段设置已更新"}


@router.put("/schedules/{weekday}")
def update_single_schedule(
    weekday: int,
    schedule_data: ScheduleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新单个星期的时段"""
    from datetime import time
    
    if weekday < 1 or weekday > 7:
        raise HTTPException(status_code=400, detail="星期必须在1-7之间")
    
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="您还不是咨询师")
    
    start_time_obj = datetime.strptime(schedule_data.start_time, "%H:%M").time() if isinstance(schedule_data.start_time, str) else schedule_data.start_time
    end_time_obj = datetime.strptime(schedule_data.end_time, "%H:%M").time() if isinstance(schedule_data.end_time, str) else schedule_data.end_time
    
    # 查找或创建该星期的时段
    schedule = db.query(CounselorSchedule).filter(
        CounselorSchedule.counselor_id == counselor.id,
        CounselorSchedule.weekday == weekday
    ).first()
    
    if schedule:
        schedule.start_time = start_time_obj
        schedule.end_time = end_time_obj
        schedule.max_num = schedule_data.max_num or 1
        schedule.is_available = True
    else:
        schedule = CounselorSchedule(
            counselor_id=counselor.id,
            weekday=weekday,
            start_time=start_time_obj,
            end_time=end_time_obj,
            max_num=schedule_data.max_num or 1,
            is_available=True
        )
        db.add(schedule)
    
    db.commit()
    return {"message": "时段设置已更新"}


@router.post("/schedules/reset")
def reset_schedule(
    weekday: Optional[int] = None,  # None表示重置全部
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """重置默认时段（删除该星期的自定义设置，使用默认8:00-22:00）"""
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="您还不是咨询师")
    
    if weekday is None:
        # 重置全部
        db.query(CounselorSchedule).filter(
            CounselorSchedule.counselor_id == counselor.id
        ).delete()
    else:
        if weekday < 1 or weekday > 7:
            raise HTTPException(status_code=400, detail="星期必须在1-7之间")
        db.query(CounselorSchedule).filter(
            CounselorSchedule.counselor_id == counselor.id,
            CounselorSchedule.weekday == weekday
        ).delete()
    
    db.commit()
    return {"message": "时段已重置为默认"}


def _safe_parse_time(value):
    """安全地将时间值转换为 time 对象"""
    if value is None:
        return None
    if isinstance(value, time):
        return value
    if isinstance(value, str):
        # 尝试多种时间格式
        for fmt in ["%H:%M:%S", "%H:%M", "%H:%M:%S.%f"]:
            try:
                return datetime.strptime(value, fmt).time()
            except ValueError:
                continue
        # 如果都失败，尝试解析带时区的格式
        try:
            return datetime.strptime(value.split('+')[0].split('-')[0], "%H:%M:%S").time()
        except:
            pass
    return None


@router.get("/schedules")
def get_counselor_schedules(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取咨询师的时段设置"""
    from sqlalchemy import text
    
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    
    if not counselor:
        raise HTTPException(status_code=404, detail="您还不是咨询师")
    
    # 直接使用原始 SQL 查询避免类型转换错误
    try:
        result = db.execute(
            text("""
                SELECT id, weekday, start_time, end_time, max_num, is_available
                FROM counselor_schedules
                WHERE counselor_id = :counselor_id
            """),
            {"counselor_id": counselor.id}
        )
        schedules_data = result.fetchall()
    except Exception as e:
        # 如果原始查询也失败，尝试使用 ORM（作为后备）
        logger.warning(f"原始查询失败，尝试使用 ORM: {e}")
        try:
            schedules = db.query(CounselorSchedule).filter(
                CounselorSchedule.counselor_id == counselor.id
            ).all()
            schedules_data = [
                (s.id, s.weekday, s.start_time, s.end_time, s.max_num, s.is_available)
                for s in schedules
            ]
        except Exception as e2:
            logger.error(f"ORM 查询也失败: {e2}")
            return {"schedules": []}
    
    result_schedules = []
    for row in schedules_data:
        try:
            start_time_obj = _safe_parse_time(row[2])
            end_time_obj = _safe_parse_time(row[3])
            
            start_time_str = start_time_obj.strftime("%H:%M") if start_time_obj else "00:00"
            end_time_str = end_time_obj.strftime("%H:%M") if end_time_obj else "00:00"
        except Exception as e:
            logger.error(f"处理时间字段时出错: {e}, start_time={row[2]}, end_time={row[3]}")
            # 尝试直接格式化为字符串
            if row[2]:
                start_time_str = str(row[2])[:5] if len(str(row[2])) >= 5 else str(row[2])
            else:
                start_time_str = "00:00"
            if row[3]:
                end_time_str = str(row[3])[:5] if len(str(row[3])) >= 5 else str(row[3])
            else:
                end_time_str = "00:00"
        
        result_schedules.append({
            "id": row[0],
            "weekday": row[1],
            "start_time": start_time_str,
            "end_time": end_time_str,
            "max_num": row[4] if row[4] is not None else 1,
            "is_available": bool(row[5]) if row[5] is not None else True
        })
    
    return {"schedules": result_schedules}


@router.get("/{counselor_id}/available-slots")
def get_available_slots(
    counselor_id: int,
    date: str = Query(..., description="日期，格式：YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    获取咨询师在指定日期的可用时段
    - 根据咨询师的日程设置生成可用时段（默认8:00-22:00）
    - 排除不可预约时段
    - 排除已被预约的时段（只排除PENDING和CONFIRMED状态，CANCELLED和REJECTED状态的预约会释放时段）
    - 排除过去的日期
    
    跨页面数据联动：
    - 所有关联页面（学生个人中心、咨询师工作台、管理员后台）均从同一核心数据库读取预约相关数据
    - 状态变更时实时同步至各页面，确保无论从哪个页面查看，预约记录、咨询师档期、咨询进度等信息完全一致
    """
    from models import Appointment, AppointmentStatus
    from datetime import datetime, date as date_type, timedelta, time
    
    # 检查咨询师是否存在且已激活
    counselor = db.query(Counselor).filter(
        Counselor.id == counselor_id,
        Counselor.status == CounselorStatus.ACTIVE
    ).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在或未激活")
    
    # 解析日期
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，应为 YYYY-MM-DD")
    
    # 排除过去的日期（仅显示今天及未来30天）
    today = date_type.today()
    max_date = today + timedelta(days=30)
    if target_date < today:
        raise HTTPException(status_code=400, detail="不能预约过去的日期")
    if target_date > max_date:
        raise HTTPException(status_code=400, detail="只能预约未来30天内的日期")
    
    # 获取星期几（1=周一，7=周日）
    weekday = target_date.isoweekday()
    
    # 获取咨询师在该工作日的时段设置（如果没有设置，使用默认8:00-22:00）
    from sqlalchemy import text
    
    schedule = None
    try:
        # 直接使用原始 SQL 查询避免类型转换错误
        result = db.execute(
            text("""
                SELECT id, weekday, start_time, end_time, max_num, is_available
                FROM counselor_schedules
                WHERE counselor_id = :counselor_id
                  AND weekday = :weekday
                  AND is_available = true
                LIMIT 1
            """),
            {"counselor_id": counselor_id, "weekday": weekday}
        )
        row = result.fetchone()
        if row:
            schedule = {
                'id': row[0],
                'weekday': row[1],
                'start_time': row[2],
                'end_time': row[3],
                'max_num': row[4],
                'is_available': bool(row[5])
            }
    except Exception as e:
        # 如果原始查询失败，尝试使用 ORM（作为后备）
        logger.warning(f"原始查询失败，尝试使用 ORM: {e}")
        try:
            schedule_obj = db.query(CounselorSchedule).filter(
                CounselorSchedule.counselor_id == counselor_id,
                CounselorSchedule.weekday == weekday,
                CounselorSchedule.is_available == True
            ).first()
            if schedule_obj:
                schedule = {
                    'id': schedule_obj.id,
                    'weekday': schedule_obj.weekday,
                    'start_time': schedule_obj.start_time,
                    'end_time': schedule_obj.end_time,
                    'max_num': schedule_obj.max_num,
                    'is_available': schedule_obj.is_available
                }
        except Exception as e2:
            logger.error(f"ORM 查询也失败: {e2}")
    
    if schedule:
        try:
            start_time = _safe_parse_time(schedule['start_time'])
            end_time = _safe_parse_time(schedule['end_time'])
            if start_time is None or end_time is None:
                raise ValueError("时间解析失败")
            max_num = schedule['max_num'] if schedule['max_num'] is not None else 1
        except Exception as e:
            logger.error(f"处理时间字段时出错: {e}, start_time={schedule.get('start_time')}, end_time={schedule.get('end_time')}")
            # 使用默认值
            start_time = time(8, 0)
            end_time = time(22, 0)
            max_num = 1
    else:
        # 默认时段：8:00-22:00
        start_time = time(8, 0)
        end_time = time(22, 0)
        max_num = 1
    
    # 获取该日期不可预约时段
    unavailable_periods = db.query(CounselorUnavailable).filter(
        CounselorUnavailable.counselor_id == counselor_id,
        CounselorUnavailable.status == 1,
        CounselorUnavailable.start_date <= target_date,
        CounselorUnavailable.end_date >= target_date
    ).all()
    
    # 获取该日期已预约的时段
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())
    
    existing_appointments = db.query(Appointment).filter(
        Appointment.counselor_id == counselor_id,
        Appointment.appointment_date >= start_of_day,
        Appointment.appointment_date < end_of_day,
        Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    ).all()
    
    # 转换为时间段集合（小时:分钟）
    booked_times = set()
    for apt in existing_appointments:
        booked_time = apt.appointment_date.strftime("%H:%M")
        booked_times.add(booked_time)
    
    # 生成可用时段（以1小时为单位）
    available_slots = []
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    
    current_minutes = start_minutes
    while current_minutes + 60 <= end_minutes:
        hour = current_minutes // 60
        minute = current_minutes % 60
        time_str = f"{hour:02d}:{minute:02d}"
        slot_time = time(hour, minute)
        
        # 检查是否在不可预约时段内
        is_unavailable = False
        for period in unavailable_periods:
            try:
                period_start_time = _safe_parse_time(period.start_time) if period.start_time else None
                period_end_time = _safe_parse_time(period.end_time) if period.end_time else None
                
                if period_start_time is None or period_end_time is None:
                    # 全天不可预约
                    is_unavailable = True
                    break
                else:
                    if period_start_time <= slot_time < period_end_time:
                        is_unavailable = True
                        break
            except Exception as e:
                logger.warning(f"处理不可预约时段时出错: {e}, period.start_time={period.start_time}, period.end_time={period.end_time}")
                # 如果解析失败，假设该时段不可预约（更安全的处理）
                if period.start_time is None or period.end_time is None:
                    is_unavailable = True
                    break
        
        if not is_unavailable and time_str not in booked_times:
            # 检查是否超过当日最大预约量
            slot_appointments = [apt for apt in existing_appointments 
                               if apt.appointment_date.hour == hour and apt.appointment_date.minute == minute]
            
            if len(slot_appointments) < max_num:
                available_slots.append({
                    "time": time_str,
                    "display": f"{hour:02d}:{minute:02d}-{(current_minutes + 60) // 60:02d}:{(current_minutes + 60) % 60:02d}"
                })
        
        current_minutes += 60
    
    return {"available_slots": available_slots}


# ============ 不可预约时段管理 ============

@router.get("/unavailable")
def get_unavailable_periods(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """获取咨询师的不可预约时段列表"""
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="您还不是咨询师")
    
    periods = db.query(CounselorUnavailable).filter(
        CounselorUnavailable.counselor_id == counselor.id
    ).order_by(CounselorUnavailable.start_date.desc()).offset(skip).limit(limit).all()
    
    return {
        "periods": [
            {
                "id": p.id,
                "start_date": p.start_date.isoformat() if isinstance(p.start_date, date) else str(p.start_date),
                "end_date": p.end_date.isoformat() if isinstance(p.end_date, date) else str(p.end_date),
                "start_time": p.start_time.strftime("%H:%M") if p.start_time else None,
                "end_time": p.end_time.strftime("%H:%M") if p.end_time else None,
                "time_type": "all" if p.start_time is None or p.end_time is None else "custom",
                "reason": p.reason,
                "status": p.status if p.status is not None else 1,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in periods
        ]
    }


@router.post("/unavailable")
def add_unavailable_period(
    period_data: UnavailablePeriodCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """添加不可预约时段"""
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="您还不是咨询师")
    
    # 解析日期
    try:
        start_date_obj = datetime.strptime(period_data.start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(period_data.end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，应为 YYYY-MM-DD")
    
    if end_date_obj < start_date_obj:
        raise HTTPException(status_code=400, detail="结束日期不能早于开始日期")
    
    # 解析时间
    start_time_obj = None
    end_time_obj = None
    if period_data.time_type == "custom":
        # 处理空字符串的情况
        start_time_str = period_data.start_time.strip() if period_data.start_time else None
        end_time_str = period_data.end_time.strip() if period_data.end_time else None
        
        if not start_time_str or not end_time_str:
            raise HTTPException(status_code=400, detail="自定义时段必须提供开始和结束时间")
        try:
            start_time_obj = datetime.strptime(start_time_str, "%H:%M").time()
            end_time_obj = datetime.strptime(end_time_str, "%H:%M").time()
        except ValueError:
            raise HTTPException(status_code=400, detail="时间格式错误，应为 HH:MM")
        
        if end_time_obj <= start_time_obj:
            raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")
    
    period = CounselorUnavailable(
        counselor_id=counselor.id,
        start_date=start_date_obj,
        end_date=end_date_obj,
        start_time=start_time_obj,
        end_time=end_time_obj,
        reason=period_data.reason,
        status=1
    )
    
    db.add(period)
    db.commit()
    db.refresh(period)
    
    return {"message": "不可预约时段已添加", "id": period.id}


@router.put("/unavailable/{period_id}")
def update_unavailable_period(
    period_id: int,
    period_data: UnavailablePeriodUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新不可预约时段"""
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="您还不是咨询师")
    
    period = db.query(CounselorUnavailable).filter(
        CounselorUnavailable.id == period_id,
        CounselorUnavailable.counselor_id == counselor.id
    ).first()
    
    if not period:
        raise HTTPException(status_code=404, detail="不可预约时段不存在")
    
    if period_data.start_date:
        try:
            period.start_date = datetime.strptime(period_data.start_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误")
    
    if period_data.end_date:
        try:
            period.end_date = datetime.strptime(period_data.end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误")
    
    if period_data.start_date and period_data.end_date and period.end_date < period.start_date:
        raise HTTPException(status_code=400, detail="结束日期不能早于开始日期")
    
    if period_data.time_type == "all":
        period.start_time = None
        period.end_time = None
    elif period_data.time_type == "custom":
        # 处理空字符串的情况
        start_time_str = period_data.start_time.strip() if period_data.start_time else None
        end_time_str = period_data.end_time.strip() if period_data.end_time else None
        
        if start_time_str and end_time_str:
            try:
                period.start_time = datetime.strptime(start_time_str, "%H:%M").time()
                period.end_time = datetime.strptime(end_time_str, "%H:%M").time()
            except ValueError:
                raise HTTPException(status_code=400, detail="时间格式错误")
            
            if period.end_time <= period.start_time:
                raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")
        else:
            raise HTTPException(status_code=400, detail="自定义时段必须提供开始和结束时间")
    
    if period_data.reason is not None:
        period.reason = period_data.reason
    
    db.commit()
    return {"message": "不可预约时段已更新"}


@router.delete("/unavailable/{period_id}")
def delete_unavailable_period(
    period_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除不可预约时段"""
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="您还不是咨询师")
    
    period = db.query(CounselorUnavailable).filter(
        CounselorUnavailable.id == period_id,
        CounselorUnavailable.counselor_id == counselor.id
    ).first()
    
    if not period:
        raise HTTPException(status_code=404, detail="不可预约时段不存在")
    
    db.delete(period)
    db.commit()
    
    return {"message": "不可预约时段已删除"}


# ============ 咨询师收藏相关 ============

@router.post("/{counselor_id}/favorite")
def favorite_counselor(
    counselor_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """收藏咨询师"""
    # 检查咨询师是否存在
    counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")
    
    # 检查是否已经收藏
    existing = db.query(CounselorFavorite).filter(
        CounselorFavorite.user_id == current_user.id,
        CounselorFavorite.counselor_id == counselor_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="您已经收藏过该咨询师")
    
    # 创建收藏记录
    favorite = CounselorFavorite(
        user_id=current_user.id,
        counselor_id=counselor_id
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    return {"message": "收藏成功", "favorite_id": favorite.id}


@router.delete("/{counselor_id}/favorite")
def unfavorite_counselor(
    counselor_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """取消收藏咨询师"""
    # 查找收藏记录
    favorite = db.query(CounselorFavorite).filter(
        CounselorFavorite.user_id == current_user.id,
        CounselorFavorite.counselor_id == counselor_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="您还没有收藏该咨询师")
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "取消收藏成功"}


@router.get("/my/favorites", response_model=List[CounselorFavoriteResponse])
def get_my_favorite_counselors(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取我收藏的咨询师列表"""
    favorites = db.query(CounselorFavorite).filter(
        CounselorFavorite.user_id == current_user.id
    ).options(
        joinedload(CounselorFavorite.counselor).joinedload(Counselor.user)
    ).order_by(
        CounselorFavorite.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    result = []
    for fav in favorites:
        counselor = fav.counselor
        if counselor and counselor.status == CounselorStatus.ACTIVE:
            # 解析 specialty 和 consult_methods
            specialty_parsed = parse_json_array_field(counselor.specialty, default=[])
            consult_methods_parsed = parse_json_array_field(counselor.consult_methods, default=[])
            
            counselor.specialty = ', '.join(specialty_parsed) if specialty_parsed else ''
            counselor.consult_methods = ', '.join(consult_methods_parsed) if consult_methods_parsed else ''
            counselor.is_favorited = True
            
            result.append({
                "id": fav.id,
                "counselor_id": counselor.id,
                "counselor": counselor,
                "created_at": fav.created_at
            })
    
    return result


# ============ 咨询师查看来访者 ============

@router.get("/my/clients", response_model=List[ClientInfo])
def get_my_clients(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """咨询师查看来访者列表（预约过或咨询过的用户）"""
    # 检查当前用户是否是咨询师
    counselor = db.query(Counselor).filter(Counselor.user_id == current_user.id).first()
    if not counselor:
        raise HTTPException(status_code=403, detail="您不是咨询师")
    
    # 获取所有预约过该咨询师的用户ID（去重）
    user_ids = db.query(distinct(Appointment.user_id)).filter(
        Appointment.counselor_id == counselor.id
    ).all()
    user_ids = [uid[0] for uid in user_ids]
    
    if not user_ids:
        return []
    
    # 获取用户信息及统计数据
    clients = []
    for user_id in user_ids[skip:skip+limit]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            continue
        
        # 获取首次预约时间
        first_appointment = db.query(Appointment).filter(
            Appointment.user_id == user_id,
            Appointment.counselor_id == counselor.id
        ).order_by(Appointment.appointment_date.asc()).first()
        
        # 获取最近预约时间
        last_appointment = db.query(Appointment).filter(
            Appointment.user_id == user_id,
            Appointment.counselor_id == counselor.id
        ).order_by(Appointment.appointment_date.desc()).first()
        
        # 统计总预约次数
        total_appointments = db.query(func.count(Appointment.id)).filter(
            Appointment.user_id == user_id,
            Appointment.counselor_id == counselor.id
        ).scalar() or 0
        
        # 统计总咨询次数（已完成的）
        total_consultations = db.query(func.count(ConsultationRecord.id)).filter(
            ConsultationRecord.user_id == user_id,
            ConsultationRecord.counselor_id == counselor.id
        ).scalar() or 0
        
        # 获取性别显示
        from utils import get_gender_display
        gender_display = get_gender_display(user.gender) if user.gender else None
        
        clients.append({
            "user_id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "gender": user.gender,
            "gender_display": gender_display,
            "age": user.age,
            "school": user.school,
            "first_appointment_date": first_appointment.appointment_date if first_appointment else None,
            "last_appointment_date": last_appointment.appointment_date if last_appointment else None,
            "total_appointments": total_appointments,
            "total_consultations": total_consultations
        })
    
    return clients


# ============ 参数路由（必须在所有具体路由之后）============

@router.get("/{counselor_id}", response_model=CounselorResponse)
def get_counselor_detail(
    counselor_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """获取咨询师详情"""
    counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
    
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")
    
    # 确保 average_rating 和 review_count 不为 None
    if counselor.average_rating is None:
        counselor.average_rating = 0.0
    if counselor.review_count is None:
        counselor.review_count = 0
    if counselor.fee is None:
        counselor.fee = 0.0
    
    # 解析 specialty 和 consult_methods 为字符串（用于显示）
    # CounselorResponse 期望 specialty 和 consult_methods 是字符串
    specialty_parsed = parse_json_array_field(counselor.specialty, default=[])
    consult_methods_parsed = parse_json_array_field(counselor.consult_methods, default=[])
    
    # 将数组转换为逗号分隔的字符串（用于显示）
    counselor.specialty = ', '.join(specialty_parsed) if specialty_parsed else ''
    counselor.consult_methods = ', '.join(consult_methods_parsed) if consult_methods_parsed else ''
    
    # 检查当前用户是否已收藏该咨询师
    counselor.is_favorited = False
    if current_user:
        favorite = db.query(CounselorFavorite).filter(
            CounselorFavorite.user_id == current_user.id,
            CounselorFavorite.counselor_id == counselor_id
        ).first()
        counselor.is_favorited = favorite is not None
    
    return counselor
