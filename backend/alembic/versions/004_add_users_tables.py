"""add users and user_logs tables

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
    sa.Column('username', sa.String(length=50), nullable=False, comment='用户名'),
    sa.Column('nickname', sa.String(length=50), nullable=False, comment='昵称'),
    sa.Column('password_hash', sa.String(length=255), nullable=False, comment='密码哈希'),
    sa.Column('email', sa.String(length=100), nullable=True, comment='邮箱地址'),
    sa.Column('phone', sa.String(length=20), nullable=True, comment='手机号'),
    sa.Column('role', sa.String(length=20), nullable=False, comment='角色(admin/user)'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='是否激活'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
    sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建者用户ID'),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index('idx_users_role', 'users', ['role'], unique=False)
    op.create_index('idx_users_username', 'users', ['username'], unique=False)
    
    op.create_table('user_logs',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False, comment='主键'),
    sa.Column('user_id', sa.BigInteger(), nullable=True, comment='操作用户ID'),
    sa.Column('action', sa.String(length=50), nullable=False, comment='操作类型'),
    sa.Column('resource', sa.String(length=100), nullable=True, comment='操作资源(API路径)'),
    sa.Column('method', sa.String(length=10), nullable=True, comment='HTTP方法'),
    sa.Column('params', sa.JSON(), nullable=True, comment='请求参数(脱敏处理)'),
    sa.Column('ip_address', sa.String(length=45), nullable=True, comment='客户端IP地址'),
    sa.Column('user_agent', sa.String(length=255), nullable=True, comment='客户端User-Agent'),
    sa.Column('status_code', sa.BigInteger(), nullable=True, comment='响应状态码'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='操作时间'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_logs_action', 'user_logs', ['action'], unique=False)
    op.create_index('idx_user_logs_created_at', 'user_logs', ['created_at'], unique=False)
    op.create_index('idx_user_logs_user_id', 'user_logs', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_user_logs_user_id', table_name='user_logs')
    op.drop_index('idx_user_logs_created_at', table_name='user_logs')
    op.drop_index('idx_user_logs_action', table_name='user_logs')
    op.drop_table('user_logs')
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_role', table_name='users')
    op.drop_table('users')
