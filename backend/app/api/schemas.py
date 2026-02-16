from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


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
