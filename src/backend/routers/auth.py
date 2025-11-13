"""
认证路由 - 登录、注册、Token管理
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserRole
from schemas import UserCreate, UserLogin, Token, UserResponse
from auth import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    - 支持手机号/邮箱/学号注册
    - 自动分配普通用户角色
    """
    try:
        # 检查用户名是否已存在
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查手机号是否已存在
        if user_data.phone and db.query(User).filter(User.phone == user_data.phone).first():
            raise HTTPException(status_code=400, detail="手机号已被注册")
        
        # 检查邮箱是否已存在
        if user_data.email and db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            phone=user_data.phone,
            email=user_data.email,
            student_id=user_data.student_id,
            password_hash=hashed_password,
            nickname=user_data.username,
            role=UserRole.USER
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 生成 Token
        access_token = create_access_token(data={"sub": new_user.id})
        
        # 返回 Token 对象（FastAPI 会自动使用 Token schema 序列化）
        from schemas import Token, UserResponse
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_info=UserResponse.model_validate(new_user)
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录
    - 支持用户名/手机号/邮箱登录
    - 返回 JWT Token 和用户信息
    """
    # 查找用户（支持多种登录方式）
    user = db.query(User).filter(
        (User.username == login_data.account) |
        (User.nickname == login_data.account) |
        (User.phone == login_data.account) |
        (User.email == login_data.account)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误"
        )
    
    # 验证密码
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误"
        )
    
    # 检查账户状态
    if not user.is_active:
        raise HTTPException(status_code=400, detail="账户已被禁用")
    
    # 生成 Token
    access_token = create_access_token(data={"sub": user.id})
    
    # 返回 Token 对象（FastAPI 会自动使用 Token schema 序列化）
    from schemas import Token, UserResponse
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_info=UserResponse.model_validate(user)
    )


@router.post("/logout")
def logout():
    """
    用户登出
    - 前端应删除本地存储的 Token
    """
    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return current_user
