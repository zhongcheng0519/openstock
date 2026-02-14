# OpenStock 股票分析系统 Makefile
# 提供开发、构建、部署等常用命令

.PHONY: help install dev build up down logs clean migrate shell

# 默认目标
help:
	@echo "OpenStock 股票分析系统 - 可用命令:"
	@echo ""
	@echo "  make install          - 安装前后端依赖"
	@echo "  make dev              - 本地开发模式启动前后端"
	@echo "  make dev-backend      - 仅启动后端开发服务"
	@echo "  make dev-frontend     - 仅启动前端开发服务"
	@echo ""
	@echo "  make build            - 构建 Docker 镜像"
	@echo "  make up               - Docker  compose 启动所有服务"
	@echo "  make up-d             - Docker compose 后台启动"
	@echo "  make down             - 停止 Docker 服务"
	@echo "  make restart          - 重启 Docker 服务"
	@echo ""
	@echo "  make logs             - 查看 Docker 日志"
	@echo "  make logs-backend     - 仅查看后端日志"
	@echo "  make logs-frontend    - 仅查看前端日志"
	@echo "  make logs-db          - 仅查看数据库日志"
	@echo ""
	@echo "  make migrate          - 执行数据库迁移"
	@echo "  make migrate-rollback - 回滚数据库迁移"
	@echo "  make shell-backend    - 进入后端容器 Shell"
	@echo "  make shell-db         - 进入数据库容器"
	@echo ""
	@echo "  make clean            - 清理 Docker 容器和镜像"
	@echo "  make clean-all        - 彻底清理（包括数据卷）"
	@echo "  make prune            - 清理未使用的 Docker 资源"
	@echo ""
	@echo "  make status           - 查看服务状态"
	@echo "  make test             - 运行测试"
	@echo ""

# ==================== 开发命令 ====================

# 安装依赖
install:
	@echo "📦 安装后端依赖..."
	cd backend && uv pip install -e .
	@echo "📦 安装前端依赖..."
	cd frontend && npm install

# 开发模式启动
dev:
	@echo "🚀 启动开发环境..."
	make dev-backend & make dev-frontend

# 仅启动后端
dev-backend:
	@echo "🚀 启动后端服务..."
	./start-backend.sh

# 仅启动前端
dev-frontend:
	@echo "🚀 启动前端服务..."
	./start-frontend.sh

# ==================== Docker 构建命令 ====================

# 构建镜像
build:
	@echo "🔨 构建 Docker 镜像..."
	docker-compose build

# 拉取最新镜像
pull:
	@echo "📥 拉取最新镜像..."
	docker-compose pull

# ==================== Docker 运行命令 ====================

# 启动服务（前台）
up:
	@echo "🚀 启动所有服务..."
	@if [ ! -f .env.docker ]; then \
		echo "⚠️  .env.docker 不存在，使用示例文件创建..."; \
		cp .env.docker.example .env.docker; \
		echo "请编辑 .env.docker 文件配置 Tushare Token"; \
		exit 1; \
	fi
	docker-compose --env-file .env.docker up

# 后台启动
up-d:
	@echo "🚀 后台启动所有服务..."
	@if [ ! -f .env.docker ]; then \
		echo "⚠️  .env.docker 不存在，使用示例文件创建..."; \
		cp .env.docker.example .env.docker; \
		echo "请编辑 .env.docker 文件配置 Tushare Token"; \
		exit 1; \
	fi
	docker-compose --env-file .env.docker up -d
	@echo "✅ 服务已启动"
	@echo "   前端: http://localhost"
	@echo "   后端 API: http://localhost:8000"
	@echo "   API 文档: http://localhost:8000/docs"

# 停止服务
down:
	@echo "🛑 停止所有服务..."
	docker-compose down

# 重启服务
restart: down up-d

# ==================== 日志命令 ====================

# 查看所有日志
logs:
	docker-compose logs -f

# 查看后端日志
logs-backend:
	docker-compose logs -f backend

# 查看前端日志
logs-frontend:
	docker-compose logs -f frontend

# 查看数据库日志
logs-db:
	docker-compose logs -f db

# ==================== 数据库命令 ====================

# 执行迁移
migrate:
	@echo "🔄 执行数据库迁移..."
	docker-compose exec backend alembic upgrade head

# 回滚迁移
migrate-rollback:
	@echo "⏪ 回滚数据库迁移..."
	docker-compose exec backend alembic downgrade -1

# 创建新的迁移
migrate-create:
	@read -p "输入迁移名称: " name; \
	docker-compose exec backend alembic revision --autogenerate -m "$$name"

# ==================== 容器操作命令 ====================

# 进入后端容器
shell-backend:
	docker-compose exec backend /bin/bash

# 进入数据库容器
shell-db:
	docker-compose exec db psql -U openstock -d openstock

# 查看服务状态
status:
	@echo "📊 服务状态:"
	docker-compose ps
	@echo ""
	@echo "🌐 服务地址:"
	@echo "   前端: http://localhost"
	@echo "   后端: http://localhost:8000"
	@echo "   API 文档: http://localhost:8000/docs"

# ==================== 清理命令 ====================

# 清理容器
clean:
	@echo "🧹 清理 Docker 容器..."
	docker-compose down --remove-orphans

# 彻底清理（包括数据卷）
clean-all:
	@echo "🧹 彻底清理（包括数据卷）..."
	docker-compose down -v --remove-orphans
	docker rmi openstock-backend openstock-frontend 2>/dev/null || true

# 清理未使用的 Docker 资源
prune:
	@echo "🧹 清理未使用的 Docker 资源..."
	docker system prune -f
	docker volume prune -f

# ==================== 测试命令 ====================

test:
	@echo "🧪 运行测试..."
	cd backend && uv run pytest

test-frontend:
	@echo "🧪 运行前端测试..."
	cd frontend && npm run test

# ==================== 部署命令 ====================

# 生产部署
deploy:
	@echo "🚀 生产部署..."
	make build
	make up-d
	make migrate

# 更新部署（拉取最新代码后）
update:
	@echo "🔄 更新部署..."
	git pull
	make build
	make restart
	make migrate
