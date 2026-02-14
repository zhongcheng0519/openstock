# 后端 Dockerfile
FROM python:3.11-slim as builder

# 安装 uv
RUN pip install uv

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY pyproject.toml ./

# 创建虚拟环境并安装依赖
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv pip install -e .

# 生产镜像
FROM python:3.11-slim

# 安装 PostgreSQL 客户端（用于等待数据库）
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 从 builder 复制虚拟环境
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# 复制应用代码
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# 创建启动脚本
RUN echo '#!/bin/bash\n\
echo "等待数据库就绪..."\n\
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do\n\
  sleep 1\n\
done\n\
echo "执行数据库迁移..."\n\
alembic upgrade head\n\
echo "启动应用..."\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh && chmod +x /app/start.sh

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["/app/start.sh"]
