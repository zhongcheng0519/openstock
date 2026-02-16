# OpenStock 股票分析系统

一个前后端分离的股票分析平台，支持股票筛选、数据同步和策略分析。

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.10+)
- **数据库**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0 (异步)
- **迁移工具**: Alembic
- **数据源**: Tushare Pro
- **包管理**: uv

### 前端
- **框架**: Vue 3 (Composition API + TypeScript)
- **UI 库**: Element Plus + Tailwind CSS
- **状态管理**: Pinia
- **构建工具**: Vite

## 项目结构

```
openstock/
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/            # API 路由和 Schema
│   │   ├── core/           # 配置文件
│   │   ├── db/             # 数据库配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 应用入口
│   ├── alembic/            # 数据库迁移
│   ├── alembic.ini         # Alembic 配置
│   ├── pyproject.toml      # 项目依赖
│   └── .env.example        # 环境变量示例
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── api/            # API 客户端
│   │   ├── views/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   └── main.ts         # 应用入口
│   ├── package.json
│   └── vite.config.ts
└── DESIGN.md               # 设计文档
```

## 快速开始

### 环境要求
- Python 3.10+
- PostgreSQL 15+
- Node.js 18+
- Tushare Pro API Token
- Docker & Docker Compose (可选，用于容器化部署)

---

## 部署方式

### 方式一：使用 Makefile 和 Docker（推荐）

最简单的一键部署方式：

```bash
# 1. 配置环境变量
cp .env.docker.example .env.docker
# 编辑 .env.docker，填写 Tushare Token

# 2. 一键部署
make deploy

# 3. 查看服务状态
make status
```

访问地址：
- 前端: http://localhost
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

常用命令：
```bash
make up-d           # 后台启动所有服务
make down           # 停止服务
make logs           # 查看日志
make restart        # 重启服务
make migrate        # 执行数据库迁移
make clean          # 清理容器
```

### 方式二：使用启动脚本（本地开发）

```bash
# 启动后端（会自动安装依赖、执行迁移）
./start-backend.sh

# 启动前端（新终端）
./start-frontend.sh
```

### 方式三：手动部署

#### 后端部署

1. 进入后端目录并创建虚拟环境:
```bash
cd backend
uv venv
source .venv/bin/activate
```

2. 安装依赖:
```bash
uv pip install -e .
```

3. 配置环境变量:
```bash
cp .env.example .env
# 编辑 .env 文件，填写数据库连接和 Tushare Token
```

4. 执行数据库迁移:
```bash
uv run alembic upgrade head
```

5. 启动服务:
```bash
uv run python -m app.main
```

后端服务将在 http://localhost:8000 启动，API 文档访问 http://localhost:8000/docs

#### 前端部署

1. 进入前端目录并安装依赖:
```bash
cd frontend
npm install
```

2. 启动开发服务器:
```bash
npm run dev
```

前端服务将在 http://localhost:5173 启动

---

## Makefile 命令参考

```bash
make help              # 显示所有可用命令

# 开发命令
make install           # 安装前后端依赖
make dev               # 本地开发模式启动
make dev-backend       # 仅启动后端
make dev-frontend      # 仅启动前端

# Docker 命令
make build             # 构建 Docker 镜像
make up                # 前台启动服务
make up-d              # 后台启动服务
make down              # 停止服务
make restart           # 重启服务

# 日志命令
make logs              # 查看所有日志
make logs-backend      # 查看后端日志
make logs-frontend     # 查看前端日志
make logs-db           # 查看数据库日志

# 数据库命令
make migrate           # 执行数据库迁移
make migrate-rollback  # 回滚迁移
make shell-db          # 进入数据库容器

# 清理命令
make clean             # 清理容器
make clean-all         # 彻底清理（包括数据）
make prune             # 清理未使用的 Docker 资源

# 部署命令
make deploy            # 生产部署
make update            # 更新部署
```

## 主要功能

### 1. 股票基础信息同步
- 从 Tushare 同步所有上市股票的基础信息
- 包括股票代码、名称、地域、行业等

### 2. 日线行情数据
- 自动按需同步指定日期的日线行情
- 支持开盘价、最高价、最低价、收盘价、成交量等字段

### 3. 每日基本面指标
- 自动按需同步指定日期的基本面指标
- 包括流通市值、市盈率、换手率、量比等

### 4. 多条件股票筛选
- 支持按日期、涨跌幅、流通市值、市盈率、换手率等多条件筛选
- 所有条件之间为且(AND)关系
- 桌面端表格展示，移动端卡片展示
- 自动数据同步，无需手动导入

### 5. 资金流向数据
- 自动按需同步指定日期的个股资金流向
- 包括小单、中单、大单、特大单的买卖量和金额
- 支持按净流入额筛选和排序
- 默认返回净流入额排名前30的股票

## API 接口

### 多条件股票筛选
```
POST /api/v1/strategy/filter
Content-Type: application/json

{
  "trade_date": "20231027",
  "min_pct": -100.0,
  "max_pct": 100.0,
  "min_circ_mv": 500000.0,
  "max_circ_mv": null,
  "min_pe": 0.0,
  "max_pe": 50.0,
  "min_turnover_rate": 5.0,
  "max_turnover_rate": null,
  "min_net_mf_amount": null,
  "mf_top_n": 30
}
```

筛选结果按净流入额降序排序，返回前 `mf_top_n` 条记录。

### 涨跌幅筛选（兼容旧接口）
```
POST /api/v1/strategy/pct-filter
Content-Type: application/json

{
  "trade_date": "20231027",
  "min_pct": -2.0,
  "max_pct": 5.0
}
```

### 同步股票列表
```
POST /api/v1/strategy/sync-stocks
```

### 同步日线行情
```
POST /api/v1/strategy/sync-daily/{trade_date}
```

## 数据库设计

### stocks 表 - 股票基础信息
| 字段 | 类型 | 说明 |
|------|------|------|
| ts_code | VARCHAR(20) | 股票代码(主键) |
| symbol | VARCHAR(20) | 股票代码 |
| name | VARCHAR(100) | 股票名称 |
| area | VARCHAR(100) | 地域 |
| industry | VARCHAR(100) | 所属行业 |
| list_date | VARCHAR(10) | 上市日期 |

### daily_hq 表 - 日线行情
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键(自增) |
| ts_code | VARCHAR(20) | 股票代码 |
| trade_date | DATE | 交易日期 |
| open | NUMERIC(12,4) | 开盘价 |
| high | NUMERIC(12,4) | 最高价 |
| low | NUMERIC(12,4) | 最低价 |
| close | NUMERIC(12,4) | 收盘价 |
| pct_chg | NUMERIC(12,4) | 涨跌幅 |
| vol | NUMERIC(18,4) | 成交量 |
| amount | NUMERIC(18,4) | 成交额 |

### daily_basic 表 - 每日基本面指标
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键(自增) |
| ts_code | VARCHAR(20) | 股票代码 |
| trade_date | DATE | 交易日期 |
| close | NUMERIC(12,4) | 当日收盘价 |
| turnover_rate | NUMERIC(8,4) | 换手率(%) |
| volume_ratio | NUMERIC(8,4) | 量比 |
| pe | NUMERIC(12,4) | 市盈率 |
| pb | NUMERIC(12,4) | 市净率 |
| circ_mv | NUMERIC(20,4) | 流通市值(万元) |
| total_mv | NUMERIC(20,4) | 总市值(万元) |

### moneyflow 表 - 个股资金流向
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键(自增) |
| ts_code | VARCHAR(20) | 股票代码 |
| trade_date | DATE | 交易日期 |
| buy_sm_vol | NUMERIC(18,4) | 小单买入量(手) |
| buy_sm_amount | NUMERIC(18,4) | 小单买入金额(万元) |
| sell_sm_vol | NUMERIC(18,4) | 小单卖出量(手) |
| sell_sm_amount | NUMERIC(18,4) | 小单卖出金额(万元) |
| buy_md_vol | NUMERIC(18,4) | 中单买入量(手) |
| buy_md_amount | NUMERIC(18,4) | 中单买入金额(万元) |
| sell_md_vol | NUMERIC(18,4) | 中单卖出量(手) |
| sell_md_amount | NUMERIC(18,4) | 中单卖出金额(万元) |
| buy_lg_vol | NUMERIC(18,4) | 大单买入量(手) |
| buy_lg_amount | NUMERIC(18,4) | 大单买入金额(万元) |
| sell_lg_vol | NUMERIC(18,4) | 大单卖出量(手) |
| sell_lg_amount | NUMERIC(18,4) | 大单卖出金额(万元) |
| buy_elg_vol | NUMERIC(18,4) | 特大单买入量(手) |
| buy_elg_amount | NUMERIC(18,4) | 特大单买入金额(万元) |
| sell_elg_vol | NUMERIC(18,4) | 特大单卖出量(手) |
| sell_elg_amount | NUMERIC(18,4) | 特大单卖出金额(万元) |
| net_mf_vol | NUMERIC(18,4) | 净流入量(手) |
| net_mf_amount | NUMERIC(18,4) | 净流入额(万元) |

## 开发计划

- [x] 项目基础架构
- [x] 数据库设计与迁移
- [x] Tushare 数据同步
- [x] 涨跌幅筛选 API
- [x] 前端页面实现
- [x] 多条件筛选策略（流通市值、市盈率、换手率）
- [x] 资金流向筛选策略（净流入额排名）
- [ ] 更多筛选策略
- [ ] 数据可视化图表
- [ ] 用户认证系统

## License

MIT
