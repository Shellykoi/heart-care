"""
认证和授权工具
包含密码哈希、JWT Token 生成和验证
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 默认初始化密码（咨询师账户等统一使用）
DEFAULT_COUNSELOR_PASSWORD = "123456"


def get_default_counselor_password() -> str:
    """返回咨询师账户默认初始密码。"""
    return DEFAULT_COUNSELOR_PASSWORD

# JWT 配置
SECRET_KEY = "your-secret-key-change-this-in-production"  # 生产环境请更换
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# 配置 OAuth2PasswordBearer，允许 token 为空（由 get_current_user 处理）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    # 确保sub是字符串（JWT标准要求）
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据，请先登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 如果 token 为空，直接抛出认证异常
    if not token:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        # 将字符串转换为整数
        user_id: int = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前激活用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="账户已被禁用")
    return current_user


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前用户（可选，未登录时返回None）"""
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        user_id: int = int(user_id_str)
    except (JWTError, ValueError):
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        return None
    
    return user


def require_role(required_role: str):
    """角色权限验证装饰器"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker
