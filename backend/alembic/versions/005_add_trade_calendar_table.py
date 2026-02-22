"""add trade_calendar table

Revision ID: 005
Revises: 004
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('trade_calendar',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
    sa.Column('exchange', sa.String(length=20), nullable=False, comment='交易所代码'),
    sa.Column('cal_date', sa.Date(), nullable=False, comment='日历日期'),
    sa.Column('is_open', sa.Boolean(), nullable=False, comment='是否交易日'),
    sa.Column('pretrade_date', sa.Date(), nullable=True, comment='上一个交易日'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_trade_calendar_cal_date', 'trade_calendar', ['cal_date'], unique=False)
    op.create_index('idx_trade_calendar_exchange', 'trade_calendar', ['exchange'], unique=False)
    op.create_index('idx_trade_calendar_exchange_date', 'trade_calendar', ['exchange', 'cal_date'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_trade_calendar_exchange_date', table_name='trade_calendar')
    op.drop_index('idx_trade_calendar_exchange', table_name='trade_calendar')
    op.drop_index('idx_trade_calendar_cal_date', table_name='trade_calendar')
    op.drop_table('trade_calendar')
