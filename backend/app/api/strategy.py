from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.base import get_db
from app.models.stock import Stock, DailyQuote, DailyBasic, Moneyflow
from app.services.tushare_service import tushare_service
from app.api.schemas import (
    StockFilterRequest,
    StockFilterResponse,
    PctFilterRequest, 
    PctFilterResponse, 
    DailyQuoteResponse,
    SyncStatusResponse
)

router = APIRouter(prefix="/api/v1/strategy", tags=["strategy"])


@router.post("/filter", response_model=StockFilterResponse)
async def stock_filter(
    request: StockFilterRequest,
    db: AsyncSession = Depends(get_db)
):
    """多条件筛选股票
    
    所有条件之间为且(AND)关系，股票需同时满足所有条件才会被筛选出来。
    如果本地没有该日期的数据，会自动从 Tushare 同步。
    结果按净流入额降序排序，返回前 mf_top_n 条记录。
    """
    trade_date = datetime.strptime(request.trade_date, "%Y%m%d").date()
    
    hq_exists = await tushare_service.check_data_exists(db, trade_date)
    if not hq_exists:
        try:
            synced_count = await tushare_service.sync_daily_quotes(db, trade_date)
            if synced_count == 0:
                raise HTTPException(
                    status_code=404, 
                    detail=f"未找到 {request.trade_date} 的交易数据"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"同步行情数据失败: {str(e)}"
            )
    
    basic_exists = await tushare_service.check_basic_data_exists(db, trade_date)
    if not basic_exists:
        try:
            synced_count = await tushare_service.sync_daily_basic(db, trade_date)
            if synced_count == 0:
                raise HTTPException(
                    status_code=404, 
                    detail=f"未找到 {request.trade_date} 的基本面数据"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"同步基本面数据失败: {str(e)}"
            )
    
    mf_exists = await tushare_service.check_moneyflow_data_exists(db, trade_date)
    if not mf_exists:
        try:
            synced_count = await tushare_service.sync_moneyflow(db, trade_date)
            if synced_count == 0:
                raise HTTPException(
                    status_code=404, 
                    detail=f"未找到 {request.trade_date} 的资金流向数据"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"同步资金流向数据失败: {str(e)}"
            )
    
    conditions = [
        DailyQuote.trade_date == trade_date,
        DailyQuote.pct_chg >= request.min_pct,
        DailyQuote.pct_chg <= request.max_pct,
        DailyBasic.circ_mv >= request.min_circ_mv,
        DailyBasic.pe >= request.min_pe,
        DailyBasic.pe <= request.max_pe,
        DailyBasic.turnover_rate >= request.min_turnover_rate,
    ]
    
    if request.max_circ_mv is not None:
        conditions.append(DailyBasic.circ_mv <= request.max_circ_mv)
    
    if request.max_turnover_rate is not None:
        conditions.append(DailyBasic.turnover_rate <= request.max_turnover_rate)
    
    if request.min_net_mf_amount is not None:
        conditions.append(Moneyflow.net_mf_amount >= request.min_net_mf_amount)
    
    query = (
        select(DailyQuote, DailyBasic, Stock, Moneyflow)
        .join(DailyBasic, and_(
            DailyQuote.ts_code == DailyBasic.ts_code,
            DailyQuote.trade_date == DailyBasic.trade_date
        ))
        .join(Stock, DailyQuote.ts_code == Stock.ts_code)
        .join(Moneyflow, and_(
            DailyQuote.ts_code == Moneyflow.ts_code,
            DailyQuote.trade_date == Moneyflow.trade_date
        ))
        .where(and_(*conditions))
        .order_by(Moneyflow.net_mf_amount.desc())
        .limit(request.mf_top_n)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    data = []
    for daily_quote, daily_basic, stock, moneyflow in rows:
        data.append(DailyQuoteResponse(
            ts_code=daily_quote.ts_code,
            symbol=stock.symbol,
            name=stock.name,
            trade_date=daily_quote.trade_date,
            open=float(daily_quote.open) if daily_quote.open else None,
            high=float(daily_quote.high) if daily_quote.high else None,
            low=float(daily_quote.low) if daily_quote.low else None,
            close=float(daily_quote.close) if daily_quote.close else None,
            pre_close=float(daily_quote.pre_close) if daily_quote.pre_close else None,
            change=float(daily_quote.change) if daily_quote.change else None,
            pct_chg=float(daily_quote.pct_chg) if daily_quote.pct_chg else None,
            vol=float(daily_quote.vol) if daily_quote.vol else None,
            amount=float(daily_quote.amount) if daily_quote.amount else None,
            circ_mv=float(daily_basic.circ_mv) if daily_basic.circ_mv else None,
            pe=float(daily_basic.pe) if daily_basic.pe else None,
            turnover_rate=float(daily_basic.turnover_rate) if daily_basic.turnover_rate else None,
            net_mf_amount=float(moneyflow.net_mf_amount) if moneyflow.net_mf_amount else None,
            net_mf_vol=float(moneyflow.net_mf_vol) if moneyflow.net_mf_vol else None,
        ))
    
    return StockFilterResponse(
        trade_date=trade_date,
        count=len(data),
        data=data
    )


@router.post("/pct-filter", response_model=PctFilterResponse)
async def pct_filter(
    request: PctFilterRequest,
    db: AsyncSession = Depends(get_db)
):
    """根据涨跌幅筛选股票（兼容旧接口）
    
    如果本地没有该日期的数据，会自动从 Tushare 同步
    """
    trade_date = datetime.strptime(request.trade_date, "%Y%m%d").date()
    
    exists = await tushare_service.check_data_exists(db, trade_date)
    if not exists:
        try:
            synced_count = await tushare_service.sync_daily_quotes(db, trade_date)
            if synced_count == 0:
                raise HTTPException(
                    status_code=404, 
                    detail=f"未找到 {request.trade_date} 的交易数据"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"同步数据失败: {str(e)}"
            )
    
    query = (
        select(DailyQuote, Stock)
        .join(Stock, DailyQuote.ts_code == Stock.ts_code)
        .where(
            and_(
                DailyQuote.trade_date == trade_date,
                DailyQuote.pct_chg >= request.min_pct,
                DailyQuote.pct_chg <= request.max_pct
            )
        )
        .order_by(DailyQuote.pct_chg.desc())
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    data = []
    for daily_quote, stock in rows:
        data.append(DailyQuoteResponse(
            ts_code=daily_quote.ts_code,
            symbol=stock.symbol,
            name=stock.name,
            trade_date=daily_quote.trade_date,
            open=float(daily_quote.open) if daily_quote.open else None,
            high=float(daily_quote.high) if daily_quote.high else None,
            low=float(daily_quote.low) if daily_quote.low else None,
            close=float(daily_quote.close) if daily_quote.close else None,
            pre_close=float(daily_quote.pre_close) if daily_quote.pre_close else None,
            change=float(daily_quote.change) if daily_quote.change else None,
            pct_chg=float(daily_quote.pct_chg) if daily_quote.pct_chg else None,
            vol=float(daily_quote.vol) if daily_quote.vol else None,
            amount=float(daily_quote.amount) if daily_quote.amount else None,
        ))
    
    return PctFilterResponse(
        trade_date=trade_date,
        count=len(data),
        data=data
    )


@router.post("/sync-stocks", response_model=SyncStatusResponse)
async def sync_stocks(db: AsyncSession = Depends(get_db)):
    """同步股票基础信息"""
    try:
        count = await tushare_service.sync_stock_basic(db)
        return SyncStatusResponse(
            message="股票基础信息同步成功",
            synced_count=count
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"同步失败: {str(e)}"
        )


@router.post("/sync-daily/{trade_date}", response_model=SyncStatusResponse)
async def sync_daily(
    trade_date: str,
    db: AsyncSession = Depends(get_db)
):
    """同步指定日期的日线行情
    
    Args:
        trade_date: 交易日期 (YYYYMMDD)
    """
    try:
        date_obj = datetime.strptime(trade_date, "%Y%m%d").date()
        count = await tushare_service.sync_daily_quotes(db, date_obj)
        return SyncStatusResponse(
            message=f"{trade_date} 日线行情同步成功",
            synced_count=count
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="日期格式错误，请使用 YYYYMMDD 格式"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"同步失败: {str(e)}"
        )
