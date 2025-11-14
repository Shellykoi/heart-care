"""
认证和授权工具
包含密码哈希、JWT Token 生成和验证
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

# 直接使用 bcrypt，避免 passlib 的兼容性问题
# passlib 在新版本 bcrypt 上存在兼容性问题（缺少 __about__ 属性等）
_bcrypt = None

def _get_bcrypt():
    """获取 bcrypt 模块，延迟导入"""
    global _bcrypt
    if _bcrypt is None:
        import bcrypt
        _bcrypt = bcrypt
    return _bcrypt

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


def _truncate_password(password: str, max_bytes: int = 72) -> str:
    """
    将密码截断到指定的最大字节数（bcrypt限制为72字节）
    使用UTF-8编码，确保不会截断多字节字符的中间部分
    """
    if not password:
        return password
    
    # 将密码编码为UTF-8字节
    password_bytes = password.encode('utf-8')
    
    # 如果密码长度在限制内，直接返回
    if len(password_bytes) <= max_bytes:
        return password
    
    # 截断到最大字节数
    truncated_bytes = password_bytes[:max_bytes]
    
    # 尝试解码，如果截断导致不完整的UTF-8序列，移除最后一个字节直到可以解码
    while truncated_bytes:
        try:
            return truncated_bytes.decode('utf-8')
        except UnicodeDecodeError:
            truncated_bytes = truncated_bytes[:-1]
    
    # 如果所有字节都无法解码（理论上不应该发生），返回空字符串
    return ""


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    # bcrypt限制密码不能超过72字节，需要截断
    truncated_password = _truncate_password(plain_password, max_bytes=72)
    
    bcrypt = _get_bcrypt()
    try:
        # 确保 hashed_password 是字节
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(truncated_password.encode('utf-8'), hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    # bcrypt限制密码不能超过72字节，需要截断
    truncated_password = _truncate_password(password, max_bytes=72)
    
    bcrypt = _get_bcrypt()
    # 生成 salt 并哈希密码
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(truncated_password.encode('utf-8'), salt)
    # 返回字符串格式
    return hashed.decode('utf-8')


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
