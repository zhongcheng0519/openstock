from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator


class StockFilterRequest(BaseModel):
    """股票筛选请求"""
    trade_date: str = Field(..., description="交易日期 (YYYYMMDD)", pattern=r"^\d{8}$")
    min_pct: float = Field(default=-100.0, description="最小涨跌幅(%)")
    max_pct: float = Field(default=100.0, description="最大涨跌幅(%)")
    min_circ_mv: float = Field(default=500000.0, description="最小流通市值(万元，默认50亿)")
    max_circ_mv: Optional[float] = Field(default=None, description="最大流通市值(万元)")
    min_pe: float = Field(default=0.0, description="最小市盈率")
    max_pe: float = Field(default=50.0, description="最大市盈率")
    min_turnover_rate: float = Field(default=5.0, description="最小换手率(%)")
    max_turnover_rate: Optional[float] = Field(default=None, description="最大换手率(%)")
    min_net_mf_amount: Optional[float] = Field(default=None, description="最小净流入额(万元)")
    mf_top_n: int = Field(default=30, ge=1, le=500, description="按净流入额排名取前N只股票")


class PctFilterRequest(BaseModel):
    """涨跌幅筛选请求（兼容旧接口）"""
    trade_date: str = Field(..., description="交易日期 (YYYYMMDD)", pattern=r"^\d{8}$")
    min_pct: float = Field(default=-10.0, description="最小涨跌幅(%)")
    max_pct: float = Field(default=10.0, description="最大涨跌幅(%)")


class StockInfo(BaseModel):
    """股票信息"""
    ts_code: str
    symbol: str
    name: str
    area: Optional[str] = None
    industry: Optional[str] = None
    
    class Config:
        from_attributes = True


class DailyQuoteResponse(BaseModel):
    """日线行情响应"""
    ts_code: str
    symbol: str
    name: str
    trade_date: date
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    pre_close: Optional[float] = None
    change: Optional[float] = None
    pct_chg: Optional[float] = None
    vol: Optional[float] = None
    amount: Optional[float] = None
    circ_mv: Optional[float] = None
    pe: Optional[float] = None
    turnover_rate: Optional[float] = None
    net_mf_amount: Optional[float] = None
    net_mf_vol: Optional[float] = None
    
    class Config:
        from_attributes = True


class StockFilterResponse(BaseModel):
    """股票筛选响应"""
    trade_date: date
    count: int
    data: list[DailyQuoteResponse]


class PctFilterResponse(BaseModel):
    """涨跌幅筛选响应（兼容旧接口）"""
    trade_date: date
    count: int
    data: list[DailyQuoteResponse]


class SyncStatusResponse(BaseModel):
    """同步状态响应"""
    message: str
    synced_count: int


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    nickname: str = Field(..., min_length=1, max_length=50, description="昵称")
    password: str = Field(..., min_length=8, max_length=100, description="密码")
    email: EmailStr = Field(..., description="邮箱地址")
    phone: Optional[str] = Field(default=None, max_length=11, description="手机号")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('手机号必须为数字')
        if v and len(v) != 11:
            raise ValueError('手机号必须为11位')
        return v


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    nickname: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: UserResponse


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密码")


class ProfileUpdateRequest(BaseModel):
    """更新个人信息请求"""
    nickname: str = Field(..., min_length=1, max_length=50, description="昵称")
    email: EmailStr = Field(..., description="邮箱地址")
    phone: Optional[str] = Field(default=None, max_length=11, description="手机号")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('手机号必须为数字')
        if v and len(v) != 11:
            raise ValueError('手机号必须为11位')
        return v


class UserCreateRequest(BaseModel):
    """管理员创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    nickname: str = Field(..., min_length=1, max_length=50, description="昵称")
    password: str = Field(..., min_length=8, max_length=100, description="密码")
    email: EmailStr = Field(..., description="邮箱地址")
    phone: Optional[str] = Field(default=None, max_length=11, description="手机号")
    role: str = Field(default="user", description="角色(admin/user)")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('手机号必须为数字')
        if v and len(v) != 11:
            raise ValueError('手机号必须为11位')
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['admin', 'user']:
            raise ValueError('角色只能是 admin 或 user')
        return v


class UserStatusUpdateRequest(BaseModel):
    """更新用户状态请求"""
    is_active: bool = Field(..., description="是否激活")


class PasswordResetRequest(BaseModel):
    """重置密码请求"""
    new_password: str = Field(..., min_length=8, max_length=100, description="新密码")


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int
    page: int
    page_size: int
    items: list[UserResponse]


class UserLogResponse(BaseModel):
    """操作日志响应"""
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    resource: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    status_code: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogListResponse(BaseModel):
    """操作日志列表响应"""
    total: int
    page: int
    page_size: int
    items: list[UserLogResponse]


class LogStatisticsResponse(BaseModel):
    """操作统计响应"""
    total_requests: int
    unique_users: int
    by_action: dict[str, int]
    by_user: list[dict]
