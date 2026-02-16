from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.db.base import get_db
from app.models.stock import User, UserLog
from app.api.auth import (
    get_current_admin_user,
    get_password_hash,
    log_user_action,
    validate_password,
)
from app.api.schemas import (
    UserCreateRequest,
    UserResponse,
    UserListResponse,
    UserStatusUpdateRequest,
    PasswordResetRequest,
    UserLogResponse,
    UserLogListResponse,
    LogStatisticsResponse,
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/users", response_model=UserListResponse)
async def list_users(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    role: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    conditions = []
    if role:
        conditions.append(User.role == role)
    if is_active is not None:
        conditions.append(User.is_active == is_active)
    
    count_query = select(func.count()).select_from(User)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    result = await db.execute(count_query)
    total = result.scalar()
    
    query = select(User).order_by(User.created_at.desc())
    if conditions:
        query = query.where(and_(*conditions))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    await log_user_action(db, current_user.id, "list_users", request, 200)
    
    return UserListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[UserResponse.model_validate(u) for u in users]
    )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    data: UserCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
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
        role=data.role,
        is_active=True,
        created_by=current_user.id,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    await log_user_action(
        db, current_user.id, "user_create", request, 201,
        params={"created_user_id": user.id, "username": user.username}
    )
    
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_status(
    user_id: int,
    request: Request,
    data: UserStatusUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能修改自己的状态"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if not data.is_active and user.role == "admin":
        result = await db.execute(
            select(func.count()).select_from(User).where(
                and_(User.role == "admin", User.is_active == True)
            )
        )
        active_admin_count = result.scalar()
        if active_admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能禁用最后一个管理员"
            )
    
    user.is_active = data.is_active
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    
    await log_user_action(
        db, current_user.id, "user_update", request, 200,
        params={"target_user_id": user_id, "is_active": data.is_active}
    )
    
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    request: Request,
    data: PasswordResetRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if not validate_password(data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码至少8位，需包含字母和数字"
        )
    
    user.password_hash = get_password_hash(data.new_password)
    user.updated_at = datetime.utcnow()
    await db.commit()
    
    await log_user_action(
        db, current_user.id, "password_reset", request, 200,
        params={"target_user_id": user_id}
    )
    
    return {"message": "密码重置成功"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if user.role == "admin":
        result = await db.execute(
            select(func.count()).select_from(User).where(
                and_(User.role == "admin", User.is_active == True)
            )
        )
        active_admin_count = result.scalar()
        if active_admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除最后一个管理员"
            )
    
    await db.delete(user)
    await db.commit()
    
    await log_user_action(
        db, current_user.id, "user_delete", request, 200,
        params={"deleted_user_id": user_id, "username": user.username}
    )
    
    return {"message": "用户已删除"}


@router.get("/logs", response_model=UserLogListResponse)
async def list_logs(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    user_id: Optional[int] = Query(default=None),
    action: Optional[str] = Query(default=None),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    conditions = []
    
    if user_id:
        conditions.append(UserLog.user_id == user_id)
    if action:
        conditions.append(UserLog.action == action)
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            conditions.append(UserLog.created_at >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            conditions.append(UserLog.created_at < end_dt)
        except ValueError:
            pass
    
    count_query = select(func.count()).select_from(UserLog)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    result = await db.execute(count_query)
    total = result.scalar()
    
    query = (
        select(UserLog)
        .options(selectinload(UserLog.user))
        .order_by(UserLog.created_at.desc())
    )
    if conditions:
        query = query.where(and_(*conditions))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    items = []
    for log in logs:
        items.append(UserLogResponse(
            id=log.id,
            user_id=log.user_id,
            username=log.user.username if log.user else None,
            action=log.action,
            resource=log.resource,
            method=log.method,
            ip_address=log.ip_address,
            status_code=log.status_code,
            created_at=log.created_at,
        ))
    
    await log_user_action(db, current_user.id, "list_logs", request, 200)
    
    return UserLogListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/logs/statistics", response_model=LogStatisticsResponse)
async def get_log_statistics(
    request: Request,
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    conditions = []
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            conditions.append(UserLog.created_at >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            conditions.append(UserLog.created_at < end_dt)
        except ValueError:
            pass
    
    base_query = select(UserLog)
    if conditions:
        base_query = base_query.where(and_(*conditions))
    
    total_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total_requests = total_result.scalar()
    
    unique_users_result = await db.execute(
        select(func.count(func.distinct(UserLog.user_id)))
        .select_from(UserLog)
    )
    if conditions:
        unique_users_result = await db.execute(
            select(func.count(func.distinct(UserLog.user_id)))
            .select_from(UserLog)
            .where(and_(*conditions))
        )
    unique_users = unique_users_result.scalar() or 0
    
    by_action_query = (
        select(UserLog.action, func.count().label("count"))
        .group_by(UserLog.action)
    )
    if conditions:
        by_action_query = by_action_query.where(and_(*conditions))
    by_action_result = await db.execute(by_action_query)
    by_action = {row.action: row.count for row in by_action_result}
    
    by_user_query = (
        select(User.username, UserLog.user_id, func.count().label("count"))
        .join(User, UserLog.user_id == User.id, isouter=True)
        .group_by(UserLog.user_id, User.username)
        .order_by(func.count().desc())
        .limit(10)
    )
    if conditions:
        by_user_query = by_user_query.where(and_(*conditions))
    by_user_result = await db.execute(by_user_query)
    by_user = [
        {"user_id": row.user_id, "username": row.username or "匿名", "count": row.count}
        for row in by_user_result
    ]
    
    await log_user_action(db, current_user.id, "log_statistics", request, 200)
    
    return LogStatisticsResponse(
        total_requests=total_requests,
        unique_users=unique_users,
        by_action=by_action,
        by_user=by_user
    )
