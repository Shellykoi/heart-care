"""
管理员路由 - 后台管理功能
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, Counselor, Appointment, TestReport, CommunityPost, CounselorStatus
from schemas import Statistics, CounselorResponse
from auth import get_current_active_user, require_role
from typing import List

router = APIRouter()


@router.get("/statistics", response_model=Statistics)
def get_platform_statistics(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """获取平台统计数据"""
    total_users = db.query(func.count(User.id)).scalar()
    total_counselors = db.query(func.count(Counselor.id)).filter(
        Counselor.status == CounselorStatus.ACTIVE
    ).scalar()
    total_appointments = db.query(func.count(Appointment.id)).scalar()
    total_tests = db.query(func.count(TestReport.id)).scalar()
    
    # 本月活跃用户和预约数（简化版）
    active_users_month = total_users
    appointments_month = total_appointments
    
    return {
        "total_users": total_users,
        "total_counselors": total_counselors,
        "total_appointments": total_appointments,
        "total_tests": total_tests,
        "active_users_month": active_users_month,
        "appointments_month": appointments_month
    }


@router.get("/counselors/pending")
def get_pending_counselors(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """获取待审核的咨询师申请"""
    pending = db.query(Counselor).filter(
        Counselor.status == CounselorStatus.PENDING
    ).all()
    
    return {"pending_counselors": pending}


@router.put("/counselors/{counselor_id}/approve")
def approve_counselor(
    counselor_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """审核通过咨询师申请"""
    counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
    
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")
    
    counselor.status = CounselorStatus.ACTIVE
    
    # 更新用户角色
    user = db.query(User).filter(User.id == counselor.user_id).first()
    if user:
        user.role = "counselor"
    
    db.commit()
    
    return {"message": "审核通过"}


@router.put("/counselors/{counselor_id}/reject")
def reject_counselor(
    counselor_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """拒绝咨询师申请"""
    counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
    
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")
    
    counselor.status = CounselorStatus.REJECTED
    db.commit()
    
    return {"message": "申请已拒绝"}


@router.get("/posts/pending")
def get_pending_posts(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """获取待审核的社区帖子（包括被举报的帖子）"""
    from models import PostReport
    from sqlalchemy.orm import joinedload
    
    # 获取所有待审核的帖子（包括被多人举报的）
    pending = db.query(CommunityPost).options(
        joinedload(CommunityPost.author)
    ).filter(
        CommunityPost.is_approved == False,
        CommunityPost.is_deleted == False
    ).order_by(CommunityPost.created_at.desc()).all()
    
    # 为每个帖子添加举报信息
    result = []
    for post in pending:
        # 统计举报次数
        report_count = db.query(func.count(PostReport.id)).filter(
            PostReport.post_id == post.id
        ).scalar() or 0
        
        post_dict = {
            "id": post.id,
            "author_id": post.author_id,
            "author": {
                "id": post.author.id if post.author else None,
                "username": post.author.username if post.author else None,
                "nickname": post.author.nickname if post.author else None,
            } if post.author else None,
            "category": post.category,
            "content": post.content,
            "tags": post.tags,
            "like_count": post.like_count or 0,
            "comment_count": post.comment_count or 0,
            "report_count": report_count,
            "is_approved": post.is_approved,
            "is_deleted": post.is_deleted,
            "created_at": post.created_at,
        }
        result.append(post_dict)
    
    return {"pending_posts": result}


@router.put("/posts/{post_id}/approve")
def approve_post(
    post_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """审核通过社区帖子"""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    post.is_approved = True
    db.commit()
    
    return {"message": "审核通过"}


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """删除违规帖子"""
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    post.is_deleted = True
    db.commit()
    
    return {"message": "帖子已删除"}


@router.put("/users/{user_id}/disable")
def disable_user(
    user_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """禁用用户账号"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.is_active = False
    db.commit()
    
    return {"message": "用户已禁用"}


@router.get("/users/list")
def get_all_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """获取所有用户列表（管理员用）"""
    from schemas import UserResponse
    
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "phone": user.phone,
            "email": user.email,
            "student_id": user.student_id,
            "gender": user.gender.value if user.gender else None,
            "age": user.age,
            "school": user.school,
            "role": user.role.value if user.role else "user",
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
        result.append(user_dict)
    
    return {"users": result, "total": db.query(func.count(User.id)).scalar() or 0}


@router.post("/counselors/create")
def create_counselor_account(
    counselor_data: dict,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """管理员为咨询师创建账户"""
    from auth import get_password_hash
    from models import Counselor, UserRole, Gender, CounselorStatus
    
    try:
        # 验证必填字段
        real_name = counselor_data.get("real_name", "").strip()
        if not real_name:
            raise HTTPException(status_code=400, detail="姓名不能为空")
        
        username = real_name  # 简化：直接使用姓名作为用户名
        
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="该用户名已存在")
        
        # 创建用户账户
        password = counselor_data.get("password", "").strip()
        if not password:
            raise HTTPException(status_code=400, detail="密码不能为空")
        
        new_user = User(
            username=username,
            password_hash=get_password_hash(password),
            role=UserRole.COUNSELOR,
            is_active=True,
            nickname=real_name
        )
        db.add(new_user)
        db.flush()
        
        # 创建咨询师记录
        gender_str = counselor_data.get("gender", "female")
        try:
            gender = Gender(gender_str)
        except ValueError:
            gender = Gender.FEMALE
        
        new_counselor = Counselor(
            user_id=new_user.id,
            real_name=real_name,
            gender=gender,
            specialty=counselor_data.get("specialty", "").strip(),
            experience_years=int(counselor_data.get("experience_years", 1)),
            bio=counselor_data.get("bio", "").strip() or None,
            status=CounselorStatus.ACTIVE
        )
        db.add(new_counselor)
        db.commit()
        db.refresh(new_counselor)
        
        return {
            "message": "咨询师账户创建成功",
            "counselor_id": new_counselor.id,
            "username": username,
            "password": password
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"创建咨询师账户错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("/counselors/list", response_model=List[CounselorResponse])
def get_all_counselors(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """获取所有咨询师列表（管理员用，包含所有状态）"""
    try:
        from models import Appointment, AppointmentStatus
        
        counselors = db.query(Counselor).order_by(Counselor.created_at.desc()).offset(skip).limit(limit).all()
        
        # 确保 average_rating 和 review_count 不为 None（在返回前设置默认值）
        # 同时统计实际的咨询次数（从Appointment表统计已完成的数量）
        for counselor in counselors:
            if counselor.average_rating is None:
                counselor.average_rating = 0.0
            if counselor.review_count is None:
                counselor.review_count = 0
            if counselor.fee is None:
                counselor.fee = 0.0
            
            # 统计实际的咨询次数（已完成状态的预约数量）
            actual_consultations = db.query(func.count(Appointment.id)).filter(
                Appointment.counselor_id == counselor.id,
                Appointment.status == AppointmentStatus.COMPLETED
            ).scalar() or 0
            
            # 更新咨询师的咨询次数
            counselor.total_consultations = actual_consultations
        
        # 使用 schema 确保返回的数据符合规范
        from schemas import CounselorResponse
        return [CounselorResponse.model_validate(counselor) for counselor in counselors]
    except Exception as e:
        print(f"获取咨询师列表错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取咨询师列表失败: {str(e)}")


@router.delete("/counselors/{counselor_id}")
def delete_counselor(
    counselor_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """删除咨询师"""
    from models import Counselor
    
    counselor = db.query(Counselor).filter(Counselor.id == counselor_id).first()
    
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")
    
    # 删除关联的用户账户
    user = db.query(User).filter(User.id == counselor.user_id).first()
    if user:
        # 删除咨询师记录
        db.delete(counselor)
        # 删除用户账户
        db.delete(user)
    
    db.commit()
    
    return {"message": "咨询师已删除"}
