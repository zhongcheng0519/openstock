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
    daily_basics: Mapped[list["DailyBasic"]] = relationship("DailyBasic", back_populates="stock", lazy="selectin")
    moneyflows: Mapped[list["Moneyflow"]] = relationship("Moneyflow", back_populates="stock", lazy="selectin")
    
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


class Moneyflow(Base):
    """个股资金流向表"""
    __tablename__ = "moneyflow"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="主键")
    ts_code: Mapped[str] = mapped_column(String(20), ForeignKey("stocks.ts_code"), nullable=False, comment="股票代码")
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, comment="交易日期")
    buy_sm_vol: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="小单买入量(手)")
    buy_sm_amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="小单买入金额(万元)")
    sell_sm_vol: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="小单卖出量(手)")
    sell_sm_amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="小单卖出金额(万元)")
    buy_md_vol: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="中单买入量(手)")
    buy_md_amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="中单买入金额(万元)")
    sell_md_vol: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="中单卖出量(手)")
    sell_md_amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="中单卖出金额(万元)")
    buy_lg_vol: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="大单买入量(手)")
    buy_lg_amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="大单买入金额(万元)")
    sell_lg_vol: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="大单卖出量(手)")
    sell_lg_amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="大单卖出金额(万元)")
    buy_elg_vol: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="特大单买入量(手)")
    buy_elg_amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="特大单买入金额(万元)")
    sell_elg_vol: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="特大单卖出量(手)")
    sell_elg_amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="特大单卖出金额(万元)")
    net_mf_vol: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="净流入量(手)")
    net_mf_amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="净流入额(万元)")
    
    stock: Mapped[Stock] = relationship("Stock", back_populates="moneyflows")
    
    __table_args__ = (
        Index("idx_moneyflow_ts_code", "ts_code"),
        Index("idx_moneyflow_trade_date", "trade_date"),
        Index("idx_moneyflow_net_mf_amount", "net_mf_amount"),
        Index("idx_moneyflow_ts_trade", "ts_code", "trade_date", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<Moneyflow(ts_code='{self.ts_code}', trade_date='{self.trade_date}', net_mf_amount={self.net_mf_amount})>"


class DailyBasic(Base):
    """每日基本面指标表"""
    __tablename__ = "daily_basic"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="主键")
    ts_code: Mapped[str] = mapped_column(String(20), ForeignKey("stocks.ts_code"), nullable=False, comment="股票代码")
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, comment="交易日期")
    close: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="当日收盘价")
    turnover_rate: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True, comment="换手率(%)")
    turnover_rate_f: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True, comment="换手率(自由流通股)")
    volume_ratio: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True, comment="量比")
    pe: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="市盈率(总市值/净利润)")
    pe_ttm: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="市盈率TTM")
    pb: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="市净率(总市值/净资产)")
    ps: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="市销率")
    ps_ttm: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, comment="市销率TTM")
    dv_ratio: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True, comment="股息率(%)")
    dv_ttm: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True, comment="股息率TTM(%)")
    total_share: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="总股本(万股)")
    float_share: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="流通股本(万股)")
    free_share: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True, comment="自由流通股本(万股)")
    total_mv: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True, comment="总市值(万元)")
    circ_mv: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True, comment="流通市值(万元)")
    
    # 关联关系
    stock: Mapped[Stock] = relationship("Stock", back_populates="daily_basics")
    
    # 索引
    __table_args__ = (
        Index("idx_daily_basic_ts_code", "ts_code"),
        Index("idx_daily_basic_trade_date", "trade_date"),
        Index("idx_daily_basic_circ_mv", "circ_mv"),
        Index("idx_daily_basic_pe", "pe"),
        Index("idx_daily_basic_turnover_rate", "turnover_rate"),
        Index("idx_daily_basic_ts_trade", "ts_code", "trade_date", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<DailyBasic(ts_code='{self.ts_code}', trade_date='{self.trade_date}', circ_mv={self.circ_mv})>"
