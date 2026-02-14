from datetime import date
from sqlalchemy import String, Numeric, Date, BigInteger, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Stock(Base):
    """股票基础信息表"""
    __tablename__ = "stocks"
    
    ts_code: Mapped[str] = mapped_column(String(20), primary_key=True, comment="股票代码(如000001.SZ)")
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, comment="股票代码(如000001)")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="股票名称")
    area: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="地域")
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="所属行业")
    list_date: Mapped[str | None] = mapped_column(String(10), nullable=True, comment="上市日期")
    
    # 关联关系
    daily_quotes: Mapped[list["DailyQuote"]] = relationship("DailyQuote", back_populates="stock", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Stock(ts_code='{self.ts_code}', name='{self.name}')>"


class DailyQuote(Base):
    """日线行情表"""
    __tablename__ = "daily_hq"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="主键")
    ts_code: Mapped[str] = mapped_column(String(20), ForeignKey("stocks.ts_code"), nullable=False, comment="股票代码")
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, comment="交易日期")
    open: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="开盘价")
    high: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="最高价")
    low: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="最低价")
    close: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="收盘价")
    pre_close: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="昨收价")
    change: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="涨跌额")
    pct_chg: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="涨跌幅(百分比)")
    vol: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="成交量(手)")
    amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="成交额(千元)")
    
    # 关联关系
    stock: Mapped[Stock] = relationship("Stock", back_populates="daily_quotes")
    
    # 索引
    __table_args__ = (
        Index("idx_daily_hq_ts_code", "ts_code"),
        Index("idx_daily_hq_trade_date", "trade_date"),
        Index("idx_daily_hq_pct_chg", "pct_chg"),
        Index("idx_daily_hq_ts_trade", "ts_code", "trade_date", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<DailyQuote(ts_code='{self.ts_code}', trade_date='{self.trade_date}', close={self.close})>"
