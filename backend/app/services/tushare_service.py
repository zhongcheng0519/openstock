import tushare as ts
import pandas as pd
from datetime import date, timedelta, datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from loguru import logger

from app.core.config import get_settings
from app.models.stock import Stock, DailyQuote, DailyBasic, Moneyflow, TradeCalendar

settings = get_settings()


class TushareService:
    """Tushare 数据服务"""
    
    def __init__(self):
        self.pro = ts.pro_api(settings.TUSHARE_TOKEN)
    
    async def sync_stock_basic(self, db: AsyncSession) -> int:
        """同步股票基础信息
        
        Returns:
            同步的股票数量
        """
        logger.info("开始同步股票基础信息")
        # 获取所有股票基础信息
        df = self.pro.stock_basic(exchange='', list_status='L', 
                                   fields='ts_code,symbol,name,area,industry,list_date')
        
        if df is None or df.empty:
            logger.warning("未获取到股票基础信息数据")
            return 0
        
        logger.info(f"获取到 {len(df)} 条股票基础信息")
        
        # 转换为字典列表
        stocks_data = df.to_dict('records')
        
        # 批量插入或更新
        count = 0
        for stock_data in stocks_data:
            # 检查是否已存在
            result = await db.execute(
                select(Stock).where(Stock.ts_code == stock_data['ts_code'])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # 更新现有记录
                existing.symbol = stock_data['symbol']
                existing.name = stock_data['name']
                existing.area = stock_data.get('area')
                existing.industry = stock_data.get('industry')
                existing.list_date = stock_data.get('list_date')
            else:
                # 创建新记录
                new_stock = Stock(
                    ts_code=stock_data['ts_code'],
                    symbol=stock_data['symbol'],
                    name=stock_data['name'],
                    area=stock_data.get('area'),
                    industry=stock_data.get('industry'),
                    list_date=stock_data.get('list_date')
                )
                db.add(new_stock)
                count += 1
        
        await db.commit()
        logger.info(f"股票基础信息同步完成，新增 {count} 条")
        return count
    
    async def sync_daily_quotes(self, db: AsyncSession, trade_date: date) -> int:
        """同步指定日期的日线行情
        
        Args:
            db: 数据库会话
            trade_date: 交易日期
            
        Returns:
            同步的记录数量
        """
        # 格式化日期为字符串 (YYYYMMDD)
        date_str = trade_date.strftime('%Y%m%d')
        
        logger.info(f"开始同步日线行情: {date_str}")
        
        # 从 Tushare 获取数据
        df = self.pro.daily(trade_date=date_str)
        
        if df is None or df.empty:
            logger.warning(f"未获取到日期 {date_str} 的日线行情数据")
            return 0
        
        existing_codes = set()
        result = await db.execute(select(Stock.ts_code))
        for row in result:
            existing_codes.add(row[0])
        
        # 检查是否已有数据
        result = await db.execute(
            select(DailyQuote).where(DailyQuote.trade_date == trade_date).limit(1)
        )
        if result.scalar_one_or_none():
            # 已有数据，先删除旧数据
            await db.execute(
                DailyQuote.__table__.delete().where(DailyQuote.trade_date == trade_date)
            )
        
        # 批量插入数据
        quotes_data = []
        for _, row in df.iterrows():
            if row['ts_code'] not in existing_codes:
                continue
            quote = {
                'ts_code': row['ts_code'],
                'trade_date': trade_date,
                'open': float(row['open']) if pd.notna(row['open']) else None,
                'high': float(row['high']) if pd.notna(row['high']) else None,
                'low': float(row['low']) if pd.notna(row['low']) else None,
                'close': float(row['close']) if pd.notna(row['close']) else None,
                'pre_close': float(row['pre_close']) if pd.notna(row['pre_close']) else None,
                'change': float(row['change']) if pd.notna(row['change']) else None,
                'pct_chg': float(row['pct_chg']) if pd.notna(row['pct_chg']) else None,
                'vol': float(row['vol']) if pd.notna(row['vol']) else None,
                'amount': float(row['amount']) if pd.notna(row['amount']) else None,
            }
            quotes_data.append(quote)
        
        if quotes_data:
            await db.execute(insert(DailyQuote), quotes_data)
            await db.commit()
        
        logger.info(f"日线行情同步完成: {len(quotes_data)} 条")
        return len(quotes_data)
    
    async def check_data_exists(self, db: AsyncSession, trade_date: date) -> bool:
        """检查指定日期的数据是否已存在"""
        result = await db.execute(
            select(DailyQuote).where(DailyQuote.trade_date == trade_date).limit(1)
        )
        return result.scalar_one_or_none() is not None
    
    async def sync_daily_basic(self, db: AsyncSession, trade_date: date) -> int:
        """同步指定日期的每日基本面指标
        
        Args:
            db: 数据库会话
            trade_date: 交易日期
            
        Returns:
            同步的记录数量
        """
        date_str = trade_date.strftime('%Y%m%d')
        
        logger.info(f"开始同步每日基本面指标: {date_str}")
        
        df = self.pro.daily_basic(trade_date=date_str)
        
        if df is None or df.empty:
            logger.warning(f"未获取到日期 {date_str} 的基本面数据")
            return 0
        
        existing_codes = set()
        result = await db.execute(select(Stock.ts_code))
        for row in result:
            existing_codes.add(row[0])
        
        result = await db.execute(
            select(DailyBasic).where(DailyBasic.trade_date == trade_date).limit(1)
        )
        if result.scalar_one_or_none():
            await db.execute(
                DailyBasic.__table__.delete().where(DailyBasic.trade_date == trade_date)
            )
        
        basics_data = []
        for _, row in df.iterrows():
            if row['ts_code'] not in existing_codes:
                continue
            basic = {
                'ts_code': row['ts_code'],
                'trade_date': trade_date,
                'close': float(row['close']) if pd.notna(row.get('close')) else None,
                'turnover_rate': float(row['turnover_rate']) if pd.notna(row.get('turnover_rate')) else None,
                'turnover_rate_f': float(row['turnover_rate_f']) if pd.notna(row.get('turnover_rate_f')) else None,
                'volume_ratio': float(row['volume_ratio']) if pd.notna(row.get('volume_ratio')) else None,
                'pe': float(row['pe']) if pd.notna(row.get('pe')) else None,
                'pe_ttm': float(row['pe_ttm']) if pd.notna(row.get('pe_ttm')) else None,
                'pb': float(row['pb']) if pd.notna(row.get('pb')) else None,
                'ps': float(row['ps']) if pd.notna(row.get('ps')) else None,
                'ps_ttm': float(row['ps_ttm']) if pd.notna(row.get('ps_ttm')) else None,
                'dv_ratio': float(row['dv_ratio']) if pd.notna(row.get('dv_ratio')) else None,
                'dv_ttm': float(row['dv_ttm']) if pd.notna(row.get('dv_ttm')) else None,
                'total_share': float(row['total_share']) if pd.notna(row.get('total_share')) else None,
                'float_share': float(row['float_share']) if pd.notna(row.get('float_share')) else None,
                'free_share': float(row['free_share']) if pd.notna(row.get('free_share')) else None,
                'total_mv': float(row['total_mv']) if pd.notna(row.get('total_mv')) else None,
                'circ_mv': float(row['circ_mv']) if pd.notna(row.get('circ_mv')) else None,
            }
            basics_data.append(basic)
        
        if basics_data:
            await db.execute(insert(DailyBasic), basics_data)
            await db.commit()
        
        logger.info(f"每日基本面指标同步完成: {len(basics_data)} 条")
        return len(basics_data)
    
    async def check_basic_data_exists(self, db: AsyncSession, trade_date: date) -> bool:
        """检查指定日期的基本面数据是否已存在"""
        result = await db.execute(
            select(DailyBasic).where(DailyBasic.trade_date == trade_date).limit(1)
        )
        return result.scalar_one_or_none() is not None
    
    async def sync_moneyflow(self, db: AsyncSession, trade_date: date) -> int:
        """同步指定日期的个股资金流向数据
        
        Args:
            db: 数据库会话
            trade_date: 交易日期
            
        Returns:
            同步的记录数量
        """
        date_str = trade_date.strftime('%Y%m%d')
        
        logger.info(f"开始同步资金流向数据: {date_str}")
        
        df = self.pro.moneyflow(trade_date=date_str)
        
        if df is None or df.empty:
            logger.warning(f"未获取到日期 {date_str} 的资金流向数据")
            return 0
        
        existing_codes = set()
        result = await db.execute(select(Stock.ts_code))
        for row in result:
            existing_codes.add(row[0])
        
        result = await db.execute(
            select(Moneyflow).where(Moneyflow.trade_date == trade_date).limit(1)
        )
        if result.scalar_one_or_none():
            await db.execute(
                Moneyflow.__table__.delete().where(Moneyflow.trade_date == trade_date)
            )
        
        moneyflow_data = []
        for _, row in df.iterrows():
            if row['ts_code'] not in existing_codes:
                continue
            mf = {
                'ts_code': row['ts_code'],
                'trade_date': trade_date,
                'buy_sm_vol': float(row['buy_sm_vol']) if pd.notna(row.get('buy_sm_vol')) else None,
                'buy_sm_amount': float(row['buy_sm_amount']) if pd.notna(row.get('buy_sm_amount')) else None,
                'sell_sm_vol': float(row['sell_sm_vol']) if pd.notna(row.get('sell_sm_vol')) else None,
                'sell_sm_amount': float(row['sell_sm_amount']) if pd.notna(row.get('sell_sm_amount')) else None,
                'buy_md_vol': float(row['buy_md_vol']) if pd.notna(row.get('buy_md_vol')) else None,
                'buy_md_amount': float(row['buy_md_amount']) if pd.notna(row.get('buy_md_amount')) else None,
                'sell_md_vol': float(row['sell_md_vol']) if pd.notna(row.get('sell_md_vol')) else None,
                'sell_md_amount': float(row['sell_md_amount']) if pd.notna(row.get('sell_md_amount')) else None,
                'buy_lg_vol': float(row['buy_lg_vol']) if pd.notna(row.get('buy_lg_vol')) else None,
                'buy_lg_amount': float(row['buy_lg_amount']) if pd.notna(row.get('buy_lg_amount')) else None,
                'sell_lg_vol': float(row['sell_lg_vol']) if pd.notna(row.get('sell_lg_vol')) else None,
                'sell_lg_amount': float(row['sell_lg_amount']) if pd.notna(row.get('sell_lg_amount')) else None,
                'buy_elg_vol': float(row['buy_elg_vol']) if pd.notna(row.get('buy_elg_vol')) else None,
                'buy_elg_amount': float(row['buy_elg_amount']) if pd.notna(row.get('buy_elg_amount')) else None,
                'sell_elg_vol': float(row['sell_elg_vol']) if pd.notna(row.get('sell_elg_vol')) else None,
                'sell_elg_amount': float(row['sell_elg_amount']) if pd.notna(row.get('sell_elg_amount')) else None,
                'net_mf_vol': float(row['net_mf_vol']) if pd.notna(row.get('net_mf_vol')) else None,
                'net_mf_amount': float(row['net_mf_amount']) if pd.notna(row.get('net_mf_amount')) else None,
            }
            moneyflow_data.append(mf)
        
        if moneyflow_data:
            await db.execute(insert(Moneyflow), moneyflow_data)
            await db.commit()
        
        logger.info(f"资金流向数据同步完成: {len(moneyflow_data)} 条")
        return len(moneyflow_data)
    
    async def check_moneyflow_data_exists(self, db: AsyncSession, trade_date: date) -> bool:
        """检查指定日期的资金流向数据是否已存在"""
        result = await db.execute(
            select(Moneyflow).where(Moneyflow.trade_date == trade_date).limit(1)
        )
        return result.scalar_one_or_none() is not None
    
    async def sync_trade_calendar(
        self, 
        db: AsyncSession, 
        exchange: str = 'SSE',
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> int:
        """同步交易日历数据
        
        Args:
            db: 数据库会话
            exchange: 交易所代码，默认 SSE
            start_date: 开始日期，默认两个月前
            end_date: 结束日期，默认今天
            
        Returns:
            同步的记录数量
        """
        if start_date is None:
            start_date = date.today() - timedelta(days=60)
        if end_date is None:
            end_date = date.today()
        
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        
        try:
            df = self.pro.trade_cal(exchange='', start_date=start_str, end_date=end_str)
        except Exception as e:
            logger.error(f"获取交易日历失败: {e}")
            return 0
        
        if df is None or df.empty:
            return 0
        
        calendar_data = []
        for _, row in df.iterrows():
            if exchange and row['exchange'] != exchange:
                continue
            cal_date = datetime.strptime(row['cal_date'], '%Y%m%d').date()
            pretrade_date = None
            if pd.notna(row.get('pretrade_date')) and row['pretrade_date']:
                pretrade_date = datetime.strptime(str(row['pretrade_date']), '%Y%m%d').date()
            
            is_open_val = row['is_open']
            is_open = (str(is_open_val) == '1') or (is_open_val == 1) or (is_open_val is True)
            
            calendar_data.append({
                'exchange': row['exchange'],
                'cal_date': cal_date,
                'is_open': is_open,
                'pretrade_date': pretrade_date,
            })
        
        if calendar_data:
            for cal in calendar_data:
                result = await db.execute(
                    select(TradeCalendar).where(
                        TradeCalendar.exchange == cal['exchange'],
                        TradeCalendar.cal_date == cal['cal_date']
                    )
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    existing.is_open = cal['is_open']
                    existing.pretrade_date = cal['pretrade_date']
                else:
                    new_cal = TradeCalendar(**cal)
                    db.add(new_cal)
            
            await db.commit()
        
        return len(calendar_data)
    
    async def check_trade_calendar_exists(
        self, 
        db: AsyncSession, 
        exchange: str = 'SSE',
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> bool:
        """检查指定日期范围的交易日历数据是否已存在"""
        if start_date is None:
            start_date = date.today() - timedelta(days=60)
        if end_date is None:
            end_date = date.today()
        
        result = await db.execute(
            select(TradeCalendar).where(
                TradeCalendar.exchange == exchange,
                TradeCalendar.cal_date >= start_date,
                TradeCalendar.cal_date <= end_date
            ).limit(1)
        )
        return result.scalar_one_or_none() is not None
    
    async def get_latest_trade_date(self, db: AsyncSession, exchange: str = 'SSE') -> Optional[date]:
        """获取最近的交易日

        直接查询Tushare API，不依赖本地数据库。

        Args:
            db: 数据库会话
            exchange: 交易所代码，默认 SSE

        Returns:
            最近的交易日期，如果没有返回 None
        """
        today = date.today()
        start_date = today - timedelta(days=60)
        start_str = start_date.strftime('%Y%m%d')
        end_str = today.strftime('%Y%m%d')

        try:
            df = self.pro.trade_cal(exchange='', start_date=start_str, end_date=end_str)
        except Exception as e:
            logger.error(f"获取交易日历失败: {e}")
            return None

        if df is None or df.empty:
            return None

        trading_days = df[df['is_open'].astype(str) == '1']
        if trading_days.empty:
            return None

        latest_date_str = trading_days['cal_date'].max()
        return datetime.strptime(str(latest_date_str), '%Y%m%d').date()

    async def get_current_trade_date(self, db: AsyncSession, exchange: str = 'SSE') -> Optional[date]:
        """获取当前日期（交易日），如果今天不是交易日则返回上一个交易日

        如果今天is_open=1，返回今天；否则返回pretrade_date。
        直接查询Tushare API，不依赖本地数据库。

        Args:
            db: 数据库会话
            exchange: 交易所代码，默认 SSE

        Returns:
            当前交易日期，如果没有返回 None
        """
        today = date.today()
        today_str = today.strftime('%Y%m%d')

        try:
            df = self.pro.trade_cal(exchange='', start_date=today_str, end_date=today_str)
        except Exception as e:
            logger.error(f"获取交易日历失败: {e}")
            return None

        if df is None or df.empty:
            return None

        row = df.iloc[0]
        is_open = str(row['is_open']) == '1' or row['is_open'] == 1 or row['is_open'] is True

        if is_open:
            return today

        pretrade_date = row.get('pretrade_date')
        if pretrade_date and pd.notna(pretrade_date):
            return datetime.strptime(str(pretrade_date), '%Y%m%d').date()

        return None


tushare_service = TushareService()
