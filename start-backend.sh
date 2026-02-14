#!/bin/bash

# 股票分析系统后端启动脚本

set -e

echo "🚀 启动 OpenStock 后端服务..."

cd "$(dirname "$0")/backend"

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    uv venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查依赖是否安装
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 安装依赖..."
    uv pip install -e .
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在，使用 .env.example 作为模板"
    cp .env.example .env
    echo "请编辑 .env 文件配置数据库连接和 Tushare Token"
    exit 1
fi

# 执行数据库迁移
echo "🔄 执行数据库迁移..."
uv run alembic upgrade head

# 启动服务
echo "✅ 启动 FastAPI 服务..."
echo "📖 API 文档: http://localhost:8000/docs"
uv run python -m app.main
