from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class PctFilterRequest(BaseModel):
    """涨跌幅筛选请求"""
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
    
    class Config:
        from_attributes = True


class PctFilterResponse(BaseModel):
    """涨跌幅筛选响应"""
    trade_date: date
    count: int
    data: list[DailyQuoteResponse]


class SyncStatusResponse(BaseModel):
    """同步状态响应"""
    message: str
    synced_count: int
