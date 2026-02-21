from datetime import datetime, timedelta
from typing import Optional
import re

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import bcrypt
from jose import jwt

from app.db.base import get_db
from app.models.stock import User, UserLog
from app.api.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    PasswordChangeRequest,
    ProfileUpdateRequest,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

security = HTTPBearer(auto_error=False)

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r'[a-zA-Z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证信息",
        )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证信息",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证信息已过期",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证信息",
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user


async def log_user_action(
    db: AsyncSession,
    user_id: Optional[int],
    action: str,
    request: Request,
    status_code: int = 200,
    params: Optional[dict] = None
):
    log = UserLog(
        user_id=user_id,
        action=action,
        resource=str(request.url.path),
        method=request.method,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:255],
        status_code=status_code,
        params=params,
    )
    db.add(log)
    await db.commit()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(func.count()).select_from(User))
    user_count = result.scalar()
    
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="系统已完成初始化，无法注册新用户"
        )
    
    if not validate_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码至少8位，需包含字母和数字"
        )
    
    hashed_password = get_password_hash(data.password)
    
    user = User(
        username=data.username,
        nickname=data.nickname,
        password_hash=hashed_password,
        email=data.email,
        phone=data.phone,
        role="admin",
        is_active=True,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    await log_user_action(db, user.id, "register", request, 201)
    
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    data: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(data.password, user.password_hash):
        await log_user_action(db, None, "login_failed", request, 401)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        await log_user_action(db, user.id, "login_blocked", request, 403)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    access_token = create_access_token(data={"sub": user.id})
    
    await log_user_action(db, user.id, "login", request, 200)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await log_user_action(db, current_user.id, "logout", request, 200)
    return {"message": "已成功登出"}


@router.put("/password")
async def change_password(
    request: Request,
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    if not validate_password(data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码至少8位，需包含字母和数字"
        )
    
    current_user.password_hash = get_password_hash(data.new_password)
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    
    await log_user_action(db, current_user.id, "password_change", request, 200)
    
    return {"message": "密码修改成功"}


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: Request,
    data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    current_user.nickname = data.nickname
    current_user.email = data.email
    current_user.phone = data.phone
    current_user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(current_user)
    
    await log_user_action(db, current_user.id, "profile_update", request, 200)
    
    return UserResponse.model_validate(current_user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return UserResponse.model_validate(current_user)
