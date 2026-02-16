"""add daily_basic table

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('daily_basic',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
    sa.Column('ts_code', sa.String(length=20), nullable=False, comment='股票代码'),
    sa.Column('trade_date', sa.Date(), nullable=False, comment='交易日期'),
    sa.Column('close', sa.Numeric(precision=12, scale=4), nullable=True, comment='当日收盘价'),
    sa.Column('turnover_rate', sa.Numeric(precision=8, scale=4), nullable=True, comment='换手率(%)'),
    sa.Column('turnover_rate_f', sa.Numeric(precision=8, scale=4), nullable=True, comment='换手率(自由流通股)'),
    sa.Column('volume_ratio', sa.Numeric(precision=8, scale=4), nullable=True, comment='量比'),
    sa.Column('pe', sa.Numeric(precision=12, scale=4), nullable=True, comment='市盈率(总市值/净利润)'),
    sa.Column('pe_ttm', sa.Numeric(precision=12, scale=4), nullable=True, comment='市盈率TTM'),
    sa.Column('pb', sa.Numeric(precision=12, scale=4), nullable=True, comment='市净率(总市值/净资产)'),
    sa.Column('ps', sa.Numeric(precision=12, scale=4), nullable=True, comment='市销率'),
    sa.Column('ps_ttm', sa.Numeric(precision=12, scale=4), nullable=True, comment='市销率TTM'),
    sa.Column('dv_ratio', sa.Numeric(precision=8, scale=4), nullable=True, comment='股息率(%)'),
    sa.Column('dv_ttm', sa.Numeric(precision=8, scale=4), nullable=True, comment='股息率TTM(%)'),
    sa.Column('total_share', sa.Numeric(precision=18, scale=4), nullable=True, comment='总股本(万股)'),
    sa.Column('float_share', sa.Numeric(precision=18, scale=4), nullable=True, comment='流通股本(万股)'),
    sa.Column('free_share', sa.Numeric(precision=18, scale=4), nullable=True, comment='自由流通股本(万股)'),
    sa.Column('total_mv', sa.Numeric(precision=20, scale=4), nullable=True, comment='总市值(万元)'),
    sa.Column('circ_mv', sa.Numeric(precision=20, scale=4), nullable=True, comment='流通市值(万元)'),
    sa.ForeignKeyConstraint(['ts_code'], ['stocks.ts_code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_daily_basic_ts_code', 'daily_basic', ['ts_code'], unique=False)
    op.create_index('idx_daily_basic_trade_date', 'daily_basic', ['trade_date'], unique=False)
    op.create_index('idx_daily_basic_circ_mv', 'daily_basic', ['circ_mv'], unique=False)
    op.create_index('idx_daily_basic_pe', 'daily_basic', ['pe'], unique=False)
    op.create_index('idx_daily_basic_turnover_rate', 'daily_basic', ['turnover_rate'], unique=False)
    op.create_index('idx_daily_basic_ts_trade', 'daily_basic', ['ts_code', 'trade_date'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_daily_basic_ts_trade', table_name='daily_basic')
    op.drop_index('idx_daily_basic_turnover_rate', table_name='daily_basic')
    op.drop_index('idx_daily_basic_pe', table_name='daily_basic')
    op.drop_index('idx_daily_basic_circ_mv', table_name='daily_basic')
    op.drop_index('idx_daily_basic_trade_date', table_name='daily_basic')
    op.drop_index('idx_daily_basic_ts_code', table_name='daily_basic')
    op.drop_table('daily_basic')
