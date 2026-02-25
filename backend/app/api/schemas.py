from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator


class FilterCondition(BaseModel):
    """筛选条件"""
    field: str = Field(..., description="字段名，如 pct_chg, circ_mv, pe, turnover_rate, net_mf_amount")
    operator: str = Field(..., description="操作符：gte(>=), lte(<=), eq(==), gt(>), lt(<)")
    value: float = Field(..., description="条件值")


class StockFilterRequest(BaseModel):
    """股票筛选请求"""
    trade_date: str = Field(..., description="交易日期 (YYYYMMDD)", pattern=r"^\d{8}$")
    conditions: list[FilterCondition] = Field(
        default_factory=lambda: [
            FilterCondition(field="pct_chg", operator="gte", value=-100.0),
            FilterCondition(field="pct_chg", operator="lte", value=100.0),
        ],
        description="筛选条件列表，所有条件为 AND 关系"
    )
    vol_ratio: float | None = Field(default=None, description="当日成交量为前一日的倍数，可选，不传则不筛选")
    mf_top_n: int = Field(default=30, ge=1, le=500, description="按净流入额排名取前N只股票")


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
        if not v.replace('_', '').replace('.', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线、点、连字符')
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
        if not v.replace('_', '').replace('.', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线、点、连字符')
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


class LatestTradeDateResponse(BaseModel):
    """最新交易日响应"""
    trade_date: str
    exchange: str


class StockDetailResponse(BaseModel):
    """股票详情响应"""
    ts_code: str
    symbol: str
    name: str
    area: Optional[str] = None
    industry: Optional[str] = None
    trade_date: Optional[date] = None
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
    buy_sm_vol: Optional[float] = None
    buy_sm_amount: Optional[float] = None
    sell_sm_vol: Optional[float] = None
    sell_sm_amount: Optional[float] = None
    buy_md_vol: Optional[float] = None
    buy_md_amount: Optional[float] = None
    sell_md_vol: Optional[float] = None
    sell_md_amount: Optional[float] = None
    buy_lg_vol: Optional[float] = None
    buy_lg_amount: Optional[float] = None
    sell_lg_vol: Optional[float] = None
    sell_lg_amount: Optional[float] = None
    buy_elg_vol: Optional[float] = None
    buy_elg_amount: Optional[float] = None
    sell_elg_vol: Optional[float] = None
    sell_elg_amount: Optional[float] = None
    
    class Config:
        from_attributes = True


class FavoriteStockResponse(BaseModel):
    """自选股响应"""
    id: int
    user_id: int
    ts_code: str
    stock_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FavoriteStockListResponse(BaseModel):
    """自选股列表响应"""
    total: int
    items: list[FavoriteStockResponse]


class AddFavoriteRequest(BaseModel):
    """添加自选股请求"""
    ts_code: str = Field(..., min_length=6, max_length=20, description="股票代码(如000001.SZ)")


class StockSearchItem(BaseModel):
    """股票搜索结果项"""
    ts_code: str
    name: str
    
    class Config:
        from_attributes = True
