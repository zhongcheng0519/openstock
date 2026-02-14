import tushare as ts
import pandas as pd
from datetime import date
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

from app.core.config import get_settings
from app.models.stock import Stock, DailyQuote

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


# 单例实例
tushare_service = TushareService()
