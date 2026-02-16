"""add moneyflow table

Revision ID: 003
Revises: 002
Create Date: 2024-01-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('moneyflow',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
    sa.Column('ts_code', sa.String(length=20), nullable=False, comment='股票代码'),
    sa.Column('trade_date', sa.Date(), nullable=False, comment='交易日期'),
    sa.Column('buy_sm_vol', sa.Numeric(precision=18, scale=4), nullable=True, comment='小单买入量(手)'),
    sa.Column('buy_sm_amount', sa.Numeric(precision=18, scale=4), nullable=True, comment='小单买入金额(万元)'),
    sa.Column('sell_sm_vol', sa.Numeric(precision=18, scale=4), nullable=True, comment='小单卖出量(手)'),
    sa.Column('sell_sm_amount', sa.Numeric(precision=18, scale=4), nullable=True, comment='小单卖出金额(万元)'),
    sa.Column('buy_md_vol', sa.Numeric(precision=18, scale=4), nullable=True, comment='中单买入量(手)'),
    sa.Column('buy_md_amount', sa.Numeric(precision=18, scale=4), nullable=True, comment='中单买入金额(万元)'),
    sa.Column('sell_md_vol', sa.Numeric(precision=18, scale=4), nullable=True, comment='中单卖出量(手)'),
    sa.Column('sell_md_amount', sa.Numeric(precision=18, scale=4), nullable=True, comment='中单卖出金额(万元)'),
    sa.Column('buy_lg_vol', sa.Numeric(precision=18, scale=4), nullable=True, comment='大单买入量(手)'),
    sa.Column('buy_lg_amount', sa.Numeric(precision=18, scale=4), nullable=True, comment='大单买入金额(万元)'),
    sa.Column('sell_lg_vol', sa.Numeric(precision=18, scale=4), nullable=True, comment='大单卖出量(手)'),
    sa.Column('sell_lg_amount', sa.Numeric(precision=18, scale=4), nullable=True, comment='大单卖出金额(万元)'),
    sa.Column('buy_elg_vol', sa.Numeric(precision=18, scale=4), nullable=True, comment='特大单买入量(手)'),
    sa.Column('buy_elg_amount', sa.Numeric(precision=18, scale=4), nullable=True, comment='特大单买入金额(万元)'),
    sa.Column('sell_elg_vol', sa.Numeric(precision=18, scale=4), nullable=True, comment='特大单卖出量(手)'),
    sa.Column('sell_elg_amount', sa.Numeric(precision=18, scale=4), nullable=True, comment='特大单卖出金额(万元)'),
    sa.Column('net_mf_vol', sa.Numeric(precision=18, scale=4), nullable=True, comment='净流入量(手)'),
    sa.Column('net_mf_amount', sa.Numeric(precision=18, scale=4), nullable=True, comment='净流入额(万元)'),
    sa.ForeignKeyConstraint(['ts_code'], ['stocks.ts_code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_moneyflow_ts_code', 'moneyflow', ['ts_code'], unique=False)
    op.create_index('idx_moneyflow_trade_date', 'moneyflow', ['trade_date'], unique=False)
    op.create_index('idx_moneyflow_net_mf_amount', 'moneyflow', ['net_mf_amount'], unique=False)
    op.create_index('idx_moneyflow_ts_trade', 'moneyflow', ['ts_code', 'trade_date'], unique=True)


def downgrade() -> None:
    op.drop_index('idx_moneyflow_ts_trade', table_name='moneyflow')
    op.drop_index('idx_moneyflow_net_mf_amount', table_name='moneyflow')
    op.drop_index('idx_moneyflow_trade_date', table_name='moneyflow')
    op.drop_index('idx_moneyflow_ts_code', table_name='moneyflow')
    op.drop_table('moneyflow')
