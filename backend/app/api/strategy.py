from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, column, func
from loguru import logger

from app.db.base import get_db
from app.models.stock import Stock, DailyQuote, DailyBasic, Moneyflow, BakDaily, UserFavorite, TradeCalendar
from app.models.stock import User
from app.services.tushare_service import tushare_service
from app.api.auth import get_current_user
from app.api.schemas import (
    StockFilterRequest,
    StockFilterResponse, 
    DailyQuoteResponse,
    SyncStatusResponse,
    LatestTradeDateResponse,
    StockDetailResponse,
    StockHistoryResponse,
    StockHistoryItem,
    FavoriteStockResponse,
    FavoriteStockListResponse,
    AddFavoriteRequest,
    StockSearchItem,
    FirstLimitRequest,
    FirstLimitResponse,
    FirstLimitStockResponse
)

router = APIRouter(prefix="/api/v1/strategy", tags=["strategy"])

FIELD_MAPPING = {
    "pct_chg": DailyQuote.pct_chg,
    "circ_mv": DailyBasic.circ_mv,
    "pe": DailyBasic.pe,
    "turnover_rate": DailyBasic.turnover_rate,
    "net_mf_amount": Moneyflow.net_mf_amount,
    "net_mf_vol": Moneyflow.net_mf_vol,
    "vol": DailyQuote.vol,
    "amount": DailyQuote.amount,
    "change": DailyQuote.change,
}

OPERATOR_MAP = {
    "gte": lambda col, val: col >= val,
    "lte": lambda col, val: col <= val,
    "eq": lambda col, val: col == val,
    "gt": lambda col, val: col > val,
    "lt": lambda col, val: col < val,
}


@router.get("/trade-calendar/latest", response_model=LatestTradeDateResponse)
async def get_latest_trade_date(
    exchange: str = 'SSE',
    db: AsyncSession = Depends(get_db)
):
    """获取最近的交易日
    
    查询交易日历表，获取从一个月前到今天之间，is_open = True 的最后一个交易日。
    若本地数据库无数据，先调用 Tushare trade_cal 接口同步最近一个月的交易日历。
    
    Args:
        exchange: 交易所代码，默认 SSE (上交所)
        
    Returns:
        最近的交易日期（格式：YYYYMMDD）
    """
    try:
        latest_date = await tushare_service.get_latest_trade_date(db, exchange)
        if latest_date is None:
            logger.warning(f"未找到交易所 {exchange} 的最近交易日")
            raise HTTPException(
                status_code=404,
                detail="未找到最近的交易日"
            )
        logger.info(f"获取最近交易日: {latest_date} ({exchange})")
        return LatestTradeDateResponse(
            trade_date=latest_date.strftime('%Y%m%d'),
            exchange=exchange
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取最近交易日失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取交易日历失败: {str(e)}"
        )


@router.get("/trade-calendar/current", response_model=LatestTradeDateResponse)
async def get_current_trade_date(
    exchange: str = 'SSE',
    db: AsyncSession = Depends(get_db)
):
    """获取当前日期（交易日）

    如果今天is_open=1，返回今天；否则返回上一个交易日pretrade_date。
    若本地数据库无数据，先调用 Tushare trade_cal 接口同步最近一个月的交易日历。

    Args:
        exchange: 交易所代码，默认 SSE (上交所)

    Returns:
        当前交易日期（格式：YYYYMMDD）
    """
    try:
        current_date = await tushare_service.get_current_trade_date(db, exchange)
        if current_date is None:
            logger.warning(f"未找到交易所 {exchange} 的当前交易日")
            raise HTTPException(
                status_code=404,
                detail="未找到当前交易日"
            )
        logger.info(f"获取当前交易日: {current_date} ({exchange})")
        return LatestTradeDateResponse(
            trade_date=current_date.strftime('%Y%m%d'),
            exchange=exchange
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取当前交易日失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取交易日历失败: {str(e)}"
        )


async def _ensure_data_synced(
    db: AsyncSession,
    trade_date: date,
    data_type: str,
    check_fn,
    sync_fn,
) -> None:
    """确保指定日期的数据已同步到本地，不存在则自动同步
    
    Args:
        db: 数据库会话
        trade_date: 交易日期
        data_type: 数据类型名称（用于日志）
        check_fn: 检查数据是否存在的异步函数
        sync_fn: 同步数据的异步函数
    """
    if await check_fn(db, trade_date):
        return
    
    logger.info(f"本地无 {trade_date} {data_type}，开始同步...")
    try:
        synced_count = await sync_fn(db, trade_date)
        if synced_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"未找到 {trade_date} 的{data_type}"
            )
        logger.info(f"{data_type}同步完成: {synced_count} 条")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"同步{data_type}失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"同步{data_type}失败: {str(e)}"
        )


@router.post("/filter", response_model=StockFilterResponse)
async def stock_filter(
    request: StockFilterRequest,
    db: AsyncSession = Depends(get_db)
):
    """多条件筛选股票
    
    所有条件之间为且(AND)关系，股票需同时满足所有条件才会被筛选出来。
    如果本地没有该日期的数据，会自动从 Tushare 同步。
    结果按净流入额降序排序，返回前 mf_top_n 条记录。
    
    条件格式示例:
    [
        {"field": "pct_chg", "operator": "gte", "value": -5.0},
        {"field": "pct_chg", "operator": "lte", "value": 5.0},
        {"field": "circ_mv", "operator": "gte", "value": 500000},
        {"field": "pe", "operator": "gte", "value": 0},
        {"field": "pe", "operator": "lte", "value": 50},
        {"field": "turnover_rate", "operator": "gte", "value": 5.0},
        {"field": "net_mf_amount", "operator": "gte", "value": 0}
    ]
    """
    trade_date = datetime.strptime(request.trade_date, "%Y%m%d").date()
    logger.info(f"股票筛选请求: 日期={request.trade_date}, 条件数={len(request.conditions)}, vol_ratio={request.vol_ratio}, 条件={request.conditions}")

    await _ensure_data_synced(
        db, trade_date, "行情数据",
        tushare_service.check_data_exists,
        tushare_service.sync_daily_quotes,
    )
    await _ensure_data_synced(
        db, trade_date, "基本面数据",
        tushare_service.check_basic_data_exists,
        tushare_service.sync_daily_basic,
    )
    await _ensure_data_synced(
        db, trade_date, "资金流向数据",
        tushare_service.check_moneyflow_data_exists,
        tushare_service.sync_moneyflow,
    )
    await _ensure_data_synced(
        db, trade_date, "备用行情数据",
        tushare_service.check_bak_daily_data_exists,
        tushare_service.sync_bak_daily,
    )

    conditions = [DailyQuote.trade_date == trade_date]
    
    for cond in request.conditions:
        if cond.field not in FIELD_MAPPING:
            raise HTTPException(
                status_code=400,
                detail=f"未知字段: {cond.field}"
            )
        if cond.operator not in OPERATOR_MAP:
            raise HTTPException(
                status_code=400,
                detail=f"未知操作符: {cond.operator}"
            )
        column = FIELD_MAPPING[cond.field]
        conditions.append(OPERATOR_MAP[cond.operator](column, cond.value))

    if request.vol_ratio is not None:
        conditions.append(DailyBasic.volume_ratio >= request.vol_ratio)

    query = (
        select(DailyQuote, DailyBasic, Stock, Moneyflow, BakDaily)
        .join(DailyBasic, and_(
            DailyQuote.ts_code == DailyBasic.ts_code,
            DailyQuote.trade_date == DailyBasic.trade_date
        ))
        .join(Stock, DailyQuote.ts_code == Stock.ts_code)
        .join(Moneyflow, and_(
            DailyQuote.ts_code == Moneyflow.ts_code,
            DailyQuote.trade_date == Moneyflow.trade_date
        ))
        .outerjoin(BakDaily, and_(
            DailyQuote.ts_code == BakDaily.ts_code,
            DailyQuote.trade_date == BakDaily.trade_date
        ))
        .where(and_(*conditions))
        .order_by(Moneyflow.net_mf_amount.desc())
        .limit(request.mf_top_n)
    )

    result = await db.execute(query)
    rows = result.all()

    data = []
    for daily_quote, daily_basic, stock, moneyflow, bak_daily in rows:
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
            volume_ratio=float(daily_basic.volume_ratio) if daily_basic.volume_ratio else None,
            net_mf_amount=float(moneyflow.net_mf_amount) if moneyflow.net_mf_amount else None,
            net_mf_vol=float(moneyflow.net_mf_vol) if moneyflow.net_mf_vol else None,
            selling=float(bak_daily.selling) if bak_daily and bak_daily.selling else None,
            buying=float(bak_daily.buying) if bak_daily and bak_daily.buying else None,
        ))

    logger.info(f"股票筛选完成: 日期={trade_date}, 结果={len(data)} 条")
    return StockFilterResponse(
        trade_date=trade_date,
        count=len(data),
        data=data
    )


@router.post("/first-limit", response_model=FirstLimitResponse)
async def first_limit_filter(
    request: FirstLimitRequest,
    db: AsyncSession = Depends(get_db)
):
    """首板选股筛选
    
    在指定时间范围内筛选首次出现涨停的股票。
    根据 limit_count 参数筛选第N次涨停的股票（如1表示首板，2表示二连板）。
    如果本地没有数据，会自动从 Tushare 同步。
    
    Args:
        start_date: 起始时间 (YYYYMMDD)
        end_date: 终止时间 (YYYYMMDD)
        limit_count: 出现过x次涨停（默认1，即首板）
    """
    start_date = datetime.strptime(request.start_date, "%Y%m%d").date()
    end_date = datetime.strptime(request.end_date, "%Y%m%d").date()
    limit_count = request.limit_count
    
    logger.info(f"首板选股请求: 起始={request.start_date}, 终止={request.end_date}, 涨停次数={limit_count}")

    # 获取时间范围内的所有交易日
    trade_dates_result = await db.execute(
        select(TradeCalendar.cal_date)
        .where(
            TradeCalendar.exchange == 'SSE',
            TradeCalendar.is_open == True,
            TradeCalendar.cal_date >= start_date,
            TradeCalendar.cal_date <= end_date
        )
        .order_by(TradeCalendar.cal_date.asc())
    )
    trade_dates = [row[0] for row in trade_dates_result.all()]
    
    if not trade_dates:
        raise HTTPException(
            status_code=400,
            detail="指定时间范围内无交易日"
        )

    # 确保所有交易日的数据都已同步
    for trade_date in trade_dates:
        await _ensure_data_synced(
            db, trade_date, "行情数据",
            tushare_service.check_data_exists,
            tushare_service.sync_daily_quotes,
        )
        await _ensure_data_synced(
            db, trade_date, "基本面数据",
            tushare_service.check_basic_data_exists,
            tushare_service.sync_daily_basic,
        )

    # 查询时间范围内所有涨停的股票
    limit_up_query = (
        select(
            DailyQuote.ts_code,
            DailyQuote.trade_date,
            func.row_number().over(
                partition_by=DailyQuote.ts_code,
                order_by=DailyQuote.trade_date.asc()
            ).label('limit_order')
        )
        .where(
            DailyQuote.trade_date >= start_date,
            DailyQuote.trade_date <= end_date,
            DailyQuote.pct_chg >= 9.9
        )
        .subquery()
    )

    # 筛选第N次涨停的股票
    target_stocks_query = (
        select(limit_up_query.c.ts_code, limit_up_query.c.trade_date.label('first_limit_date'))
        .where(limit_up_query.c.limit_order == limit_count)
        .subquery()
    )

    # 构建主查询（首板选股不需要额外筛选条件）
    query = (
        select(DailyQuote, Stock, target_stocks_query.c.first_limit_date)
        .join(target_stocks_query, and_(
            DailyQuote.ts_code == target_stocks_query.c.ts_code,
            DailyQuote.trade_date == target_stocks_query.c.first_limit_date
        ))
        .join(Stock, DailyQuote.ts_code == Stock.ts_code)
        .join(DailyBasic, and_(
            DailyQuote.ts_code == DailyBasic.ts_code,
            DailyQuote.trade_date == DailyBasic.trade_date
        ))
        .order_by(target_stocks_query.c.first_limit_date.desc())
    )

    result = await db.execute(query)
    rows = result.all()

    data = []
    for daily_quote, stock, first_limit_date in rows:
        # 获取基本面数据
        basic_result = await db.execute(
            select(DailyBasic).where(
                DailyBasic.ts_code == daily_quote.ts_code,
                DailyBasic.trade_date == daily_quote.trade_date
            )
        )
        daily_basic = basic_result.scalar_one_or_none()
        
        data.append(FirstLimitStockResponse(
            ts_code=daily_quote.ts_code,
            symbol=stock.symbol,
            name=stock.name,
            trade_date=daily_quote.trade_date,
            first_limit_date=first_limit_date,
            open=float(daily_quote.open) if daily_quote.open else None,
            high=float(daily_quote.high) if daily_quote.high else None,
            low=float(daily_quote.low) if daily_quote.low else None,
            close=float(daily_quote.close) if daily_quote.close else None,
            pre_close=float(daily_quote.pre_close) if daily_quote.pre_close else None,
            change=float(daily_quote.change) if daily_quote.change else None,
            pct_chg=float(daily_quote.pct_chg) if daily_quote.pct_chg else None,
            vol=float(daily_quote.vol) if daily_quote.vol else None,
            amount=float(daily_quote.amount) if daily_quote.amount else None,
            circ_mv=float(daily_basic.circ_mv) if daily_basic and daily_basic.circ_mv else None,
            pe=float(daily_basic.pe) if daily_basic and daily_basic.pe else None,
            turnover_rate=float(daily_basic.turnover_rate) if daily_basic and daily_basic.turnover_rate else None,
        ))

    logger.info(f"首板选股完成: 起始={start_date}, 终止={end_date}, 涨停次数={limit_count}, 结果={len(data)} 条")
    return FirstLimitResponse(
        start_date=start_date,
        end_date=end_date,
        limit_count=limit_count,
        count=len(data),
        data=data
    )


@router.post("/sync-stocks", response_model=SyncStatusResponse)
async def sync_stocks(db: AsyncSession = Depends(get_db)):
    """同步股票基础信息"""
    logger.info("开始同步股票基础信息")
    try:
        count = await tushare_service.sync_stock_basic(db)
        logger.info(f"股票基础信息同步完成: {count} 条")
        return SyncStatusResponse(
            message="股票基础信息同步成功",
            synced_count=count
        )
    except Exception as e:
        logger.error(f"同步股票基础信息失败: {e}")
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
    logger.info(f"开始同步日线行情: {trade_date}")
    try:
        date_obj = datetime.strptime(trade_date, "%Y%m%d").date()
        count = await tushare_service.sync_daily_quotes(db, date_obj)
        logger.info(f"日线行情同步完成: {trade_date}, {count} 条")
        return SyncStatusResponse(
            message=f"{trade_date} 日线行情同步成功",
            synced_count=count
        )
    except ValueError:
        logger.warning(f"日期格式错误: {trade_date}")
        raise HTTPException(
            status_code=400,
            detail="日期格式错误，请使用 YYYYMMDD 格式"
        )
    except Exception as e:
        logger.error(f"同步日线行情失败: {trade_date}, {e}")
        raise HTTPException(
            status_code=500,
            detail=f"同步失败: {str(e)}"
        )


@router.get("/stock/{ts_code}", response_model=StockDetailResponse)
async def get_stock_detail(
    ts_code: str,
    trade_date: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """获取股票详情
    
    根据股票代码和交易日期获取股票的详细信息，包括：
    - 股票基本信息（代码、名称、地域、行业）
    - 行情数据（收盘价、涨跌幅、换手率等）
    - 资金流向数据（大单、中单、小单、特大单的买入/卖出量和金额）
    
    Args:
        ts_code: 股票代码（如 000001.SZ）
        trade_date: 交易日期 (YYYYMMDD)，可选，默认最新交易日
    """
    if trade_date is None:
        latest_date = await tushare_service.get_latest_trade_date(db, 'SSE')
        if latest_date is None:
            raise HTTPException(
                status_code=404,
                detail="未找到最近的交易日"
            )
        trade_date = latest_date.strftime('%Y%m%d')
    
    if trade_date:
        trade_date = trade_date.replace('-', '')
    
    trade_date_obj = datetime.strptime(trade_date, "%Y%m%d").date()
    logger.info(f"获取股票详情: ts_code={ts_code}, 日期={trade_date}")

    await _ensure_data_synced(
        db, trade_date_obj, "行情数据",
        tushare_service.check_data_exists,
        tushare_service.sync_daily_quotes,
    )
    await _ensure_data_synced(
        db, trade_date_obj, "基本面数据",
        tushare_service.check_basic_data_exists,
        tushare_service.sync_daily_basic,
    )
    await _ensure_data_synced(
        db, trade_date_obj, "资金流向数据",
        tushare_service.check_moneyflow_data_exists,
        tushare_service.sync_moneyflow,
    )
    await _ensure_data_synced(
        db, trade_date_obj, "备用行情数据",
        tushare_service.check_bak_daily_data_exists,
        tushare_service.sync_bak_daily,
    )

    query = (
        select(Stock, DailyQuote, DailyBasic, Moneyflow, BakDaily)
        .join(DailyQuote, and_(
            Stock.ts_code == DailyQuote.ts_code,
            DailyQuote.trade_date == trade_date_obj
        ))
        .join(DailyBasic, and_(
            Stock.ts_code == DailyBasic.ts_code,
            DailyBasic.trade_date == trade_date_obj
        ))
        .join(Moneyflow, and_(
            Stock.ts_code == Moneyflow.ts_code,
            Moneyflow.trade_date == trade_date_obj
        ))
        .outerjoin(BakDaily, and_(
            Stock.ts_code == BakDaily.ts_code,
            BakDaily.trade_date == trade_date_obj
        ))
        .where(Stock.ts_code == ts_code)
    )

    result = await db.execute(query)
    row = result.first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"未找到股票 {ts_code} 在 {trade_date} 的数据"
        )

    stock, daily_quote, daily_basic, moneyflow, bak_daily = row

    return StockDetailResponse(
        ts_code=stock.ts_code,
        symbol=stock.symbol,
        name=stock.name,
        area=stock.area,
        industry=stock.industry,
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
        buy_sm_vol=float(moneyflow.buy_sm_vol) if moneyflow.buy_sm_vol else None,
        buy_sm_amount=float(moneyflow.buy_sm_amount) if moneyflow.buy_sm_amount else None,
        sell_sm_vol=float(moneyflow.sell_sm_vol) if moneyflow.sell_sm_vol else None,
        sell_sm_amount=float(moneyflow.sell_sm_amount) if moneyflow.sell_sm_amount else None,
        buy_md_vol=float(moneyflow.buy_md_vol) if moneyflow.buy_md_vol else None,
        buy_md_amount=float(moneyflow.buy_md_amount) if moneyflow.buy_md_amount else None,
        sell_md_vol=float(moneyflow.sell_md_vol) if moneyflow.sell_md_vol else None,
        sell_md_amount=float(moneyflow.sell_md_amount) if moneyflow.sell_md_amount else None,
        buy_lg_vol=float(moneyflow.buy_lg_vol) if moneyflow.buy_lg_vol else None,
        buy_lg_amount=float(moneyflow.buy_lg_amount) if moneyflow.buy_lg_amount else None,
        sell_lg_vol=float(moneyflow.sell_lg_vol) if moneyflow.sell_lg_vol else None,
        sell_lg_amount=float(moneyflow.sell_lg_amount) if moneyflow.sell_lg_amount else None,
        buy_elg_vol=float(moneyflow.buy_elg_vol) if moneyflow.buy_elg_vol else None,
        buy_elg_amount=float(moneyflow.buy_elg_amount) if moneyflow.buy_elg_amount else None,
        sell_elg_vol=float(moneyflow.sell_elg_vol) if moneyflow.sell_elg_vol else None,
        sell_elg_amount=float(moneyflow.sell_elg_amount) if moneyflow.sell_elg_amount else None,
        selling=float(bak_daily.selling) if bak_daily and bak_daily.selling else None,
        buying=float(bak_daily.buying) if bak_daily and bak_daily.buying else None,
    )


@router.get("/stock/{ts_code}/history", response_model=StockHistoryResponse)
async def get_stock_history(
    ts_code: str,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """获取股票近N个交易日的历史数据

    包含行情、资金流向、单笔成交明细，每行一个交易日，按日期倒序排列。

    Args:
        ts_code: 股票代码（如 000001.SZ）
        days: 返回天数，默认30
    """
    stock_result = await db.execute(
        select(Stock).where(Stock.ts_code == ts_code)
    )
    stock = stock_result.scalar_one_or_none()
    if stock is None:
        raise HTTPException(status_code=404, detail=f"股票 {ts_code} 不存在")

    max_cal_result = await db.execute(
        select(func.max(TradeCalendar.cal_date)).where(
            TradeCalendar.exchange == 'SSE'
        )
    )
    max_cal_date = max_cal_result.scalar()
    if max_cal_date is None or max_cal_date < date.today():
        await tushare_service.sync_trade_calendar(db, exchange='SSE')

    trade_dates_result = await db.execute(
        select(TradeCalendar.cal_date)
        .where(
            TradeCalendar.exchange == 'SSE',
            TradeCalendar.is_open == True,
            TradeCalendar.cal_date <= date.today()
        )
        .order_by(TradeCalendar.cal_date.desc())
        .limit(days)
    )
    trade_dates = [row[0] for row in trade_dates_result.all()]

    if not trade_dates:
        return StockHistoryResponse(ts_code=ts_code, name=stock.name, count=0, data=[])

    valid_dates = []
    for td in trade_dates:
        try:
            await _ensure_data_synced(
                db, td, "行情数据",
                tushare_service.check_data_exists,
                tushare_service.sync_daily_quotes,
            )
            await _ensure_data_synced(
                db, td, "资金流向数据",
                tushare_service.check_moneyflow_data_exists,
                tushare_service.sync_moneyflow,
            )
            valid_dates.append(td)
        except HTTPException:
            logger.warning(f"跳过无数据的交易日: {td}")
            continue
    trade_dates = valid_dates

    query = (
        select(DailyQuote, Moneyflow)
        .join(Moneyflow, and_(
            DailyQuote.ts_code == Moneyflow.ts_code,
            DailyQuote.trade_date == Moneyflow.trade_date
        ))
        .where(
            DailyQuote.ts_code == ts_code,
            DailyQuote.trade_date.in_(trade_dates)
        )
        .order_by(DailyQuote.trade_date.desc())
    )

    result = await db.execute(query)
    rows = result.all()

    data = []
    for daily_quote, moneyflow in rows:
        data.append(StockHistoryItem(
            trade_date=daily_quote.trade_date,
            open=float(daily_quote.open) if daily_quote.open else None,
            high=float(daily_quote.high) if daily_quote.high else None,
            low=float(daily_quote.low) if daily_quote.low else None,
            close=float(daily_quote.close) if daily_quote.close else None,
            pct_chg=float(daily_quote.pct_chg) if daily_quote.pct_chg else None,
            vol=float(daily_quote.vol) if daily_quote.vol else None,
            net_mf_amount=float(moneyflow.net_mf_amount) if moneyflow.net_mf_amount else None,
            net_mf_vol=float(moneyflow.net_mf_vol) if moneyflow.net_mf_vol else None,
            buy_sm_vol=float(moneyflow.buy_sm_vol) if moneyflow.buy_sm_vol else None,
            buy_sm_amount=float(moneyflow.buy_sm_amount) if moneyflow.buy_sm_amount else None,
            sell_sm_vol=float(moneyflow.sell_sm_vol) if moneyflow.sell_sm_vol else None,
            sell_sm_amount=float(moneyflow.sell_sm_amount) if moneyflow.sell_sm_amount else None,
            buy_md_vol=float(moneyflow.buy_md_vol) if moneyflow.buy_md_vol else None,
            buy_md_amount=float(moneyflow.buy_md_amount) if moneyflow.buy_md_amount else None,
            sell_md_vol=float(moneyflow.sell_md_vol) if moneyflow.sell_md_vol else None,
            sell_md_amount=float(moneyflow.sell_md_amount) if moneyflow.sell_md_amount else None,
            buy_lg_vol=float(moneyflow.buy_lg_vol) if moneyflow.buy_lg_vol else None,
            buy_lg_amount=float(moneyflow.buy_lg_amount) if moneyflow.buy_lg_amount else None,
            sell_lg_vol=float(moneyflow.sell_lg_vol) if moneyflow.sell_lg_vol else None,
            sell_lg_amount=float(moneyflow.sell_lg_amount) if moneyflow.sell_lg_amount else None,
            buy_elg_vol=float(moneyflow.buy_elg_vol) if moneyflow.buy_elg_vol else None,
            buy_elg_amount=float(moneyflow.buy_elg_amount) if moneyflow.buy_elg_amount else None,
            sell_elg_vol=float(moneyflow.sell_elg_vol) if moneyflow.sell_elg_vol else None,
            sell_elg_amount=float(moneyflow.sell_elg_amount) if moneyflow.sell_elg_amount else None,
        ))

    logger.info(f"获取股票历史数据: ts_code={ts_code}, 天数={days}, 结果={len(data)} 条")
    return StockHistoryResponse(
        ts_code=ts_code,
        name=stock.name,
        count=len(data),
        data=data
    )


@router.get("/favorites", response_model=FavoriteStockListResponse)
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的自选股列表"""
    query = (
        select(UserFavorite, Stock)
        .outerjoin(Stock, UserFavorite.ts_code == Stock.ts_code)
        .where(UserFavorite.user_id == current_user.id)
        .order_by(UserFavorite.created_at.desc())
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    items = []
    for favorite, stock in rows:
        items.append(FavoriteStockResponse(
            id=favorite.id,
            user_id=favorite.user_id,
            ts_code=favorite.ts_code,
            stock_name=stock.name if stock else None,
            created_at=favorite.created_at
        ))
    
    return FavoriteStockListResponse(
        total=len(items),
        items=items
    )


@router.post("/favorites", response_model=FavoriteStockResponse)
async def add_favorite(
    request: AddFavoriteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加自选股"""
    stock_result = await db.execute(
        select(Stock).where(Stock.ts_code == request.ts_code)
    )
    stock = stock_result.scalar_one_or_none()
    
    if stock is None:
        raise HTTPException(
            status_code=404,
            detail=f"股票 {request.ts_code} 不存在"
        )
    
    existing = await db.execute(
        select(UserFavorite).where(
            and_(
                UserFavorite.user_id == current_user.id,
                UserFavorite.ts_code == request.ts_code
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="该股票已在自选股中"
        )
    
    favorite = UserFavorite(
        user_id=current_user.id,
        ts_code=request.ts_code
    )
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    
    logger.info(f"用户 {current_user.id} 添加自选股: {request.ts_code}")
    
    return FavoriteStockResponse(
        id=favorite.id,
        user_id=favorite.user_id,
        ts_code=favorite.ts_code,
        stock_name=stock.name,
        created_at=favorite.created_at
    )


@router.delete("/favorites/{ts_code}")
async def remove_favorite(
    ts_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除自选股"""
    result = await db.execute(
        select(UserFavorite).where(
            and_(
                UserFavorite.user_id == current_user.id,
                UserFavorite.ts_code == ts_code
            )
        )
    )
    favorite = result.scalar_one_or_none()
    
    if favorite is None:
        raise HTTPException(
            status_code=404,
            detail="自选股不存在"
        )
    
    await db.delete(favorite)
    await db.commit()
    
    logger.info(f"用户 {current_user.id} 删除自选股: {ts_code}")
    
    return {"message": "删除成功"}


@router.get("/favorites/{ts_code}/status")
async def check_favorite_status(
    ts_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """检查股票是否在自选股中"""
    result = await db.execute(
        select(UserFavorite).where(
            and_(
                UserFavorite.user_id == current_user.id,
                UserFavorite.ts_code == ts_code
            )
        )
    )
    favorite = result.scalar_one_or_none()
    
    return {"is_favorited": favorite is not None}


@router.get("/stocks/search", response_model=list[StockSearchItem])
async def search_stocks(
    q: str = "",
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """搜索股票，支持按代码或名称模糊搜索"""
    if not q or len(q) < 1:
        return []
    
    pattern = f"%{q}%"
    result = await db.execute(
        select(Stock).where(
            (Stock.ts_code.ilike(pattern)) | 
            (Stock.name.ilike(pattern))
        ).limit(limit)
    )
    stocks = result.scalars().all()
    
    return [
        StockSearchItem(ts_code=stock.ts_code, name=stock.name)
        for stock in stocks
    ]
