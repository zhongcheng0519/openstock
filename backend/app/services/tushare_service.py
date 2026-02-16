import tushare as ts
import pandas as pd
from datetime import date
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

from app.core.config import get_settings
from app.models.stock import Stock, DailyQuote, DailyBasic, Moneyflow

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
        # 获取所有股票基础信息
        df = self.pro.stock_basic(exchange='', list_status='L', 
                                   fields='ts_code,symbol,name,area,industry,list_date')
        
        if df is None or df.empty:
            return 0
        
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
        
        # 从 Tushare 获取数据
        df = self.pro.daily(trade_date=date_str)
        
        if df is None or df.empty:
            return 0
        
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
        
        df = self.pro.daily_basic(trade_date=date_str)
        
        if df is None or df.empty:
            return 0
        
        result = await db.execute(
            select(DailyBasic).where(DailyBasic.trade_date == trade_date).limit(1)
        )
        if result.scalar_one_or_none():
            await db.execute(
                DailyBasic.__table__.delete().where(DailyBasic.trade_date == trade_date)
            )
        
        basics_data = []
        for _, row in df.iterrows():
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
        
        df = self.pro.moneyflow(trade_date=date_str)
        
        if df is None or df.empty:
            return 0
        
        result = await db.execute(
            select(Moneyflow).where(Moneyflow.trade_date == trade_date).limit(1)
        )
        if result.scalar_one_or_none():
            await db.execute(
                Moneyflow.__table__.delete().where(Moneyflow.trade_date == trade_date)
            )
        
        moneyflow_data = []
        for _, row in df.iterrows():
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
        
        return len(moneyflow_data)
    
    async def check_moneyflow_data_exists(self, db: AsyncSession, trade_date: date) -> bool:
        """检查指定日期的资金流向数据是否已存在"""
        result = await db.execute(
            select(Moneyflow).where(Moneyflow.trade_date == trade_date).limit(1)
        )
        return result.scalar_one_or_none() is not None


# 单例实例
tushare_service = TushareService()
