# 股票分析系统 (Stock Analysis System) 设计文档

## 1. 项目概述

本项目旨在构建一个前后端分离的股票分析平台。系统通过 Tushare 获取原始数据，并将其持久化到 PostgreSQL 数据库中，以支持高效的股票筛选与策略分析。系统设计需具备高度的可扩展性，以便后续接入更复杂的量化策略。

## 2. 技术栈 (Technology Stack)

### 2.1 后端 (Backend)

- **框架**: Python FastAPI (异步、高性能)
- **数据库**: **PostgreSQL 15+**
- **ORM**: SQLAlchemy 2.0 (结合 `asyncpg` 实现异步操作)
- **数据库迁移**: **Alembic** (确保数据库 Schema 的版本控制)
- **依赖管理**: **uv** (极速 Python 包管理工具)
- **数据源**: Tushare Pro SDK

### 2.2 前端 (Frontend)

- **框架**: Vue 3 (Composition API)
- **UI 库**: Tailwind CSS + Element Plus
- **状态管理**: Pinia

## 3. 系统架构 (System Architecture)

系统采用**缓存/持久化优先**策略：

1. **表现层**: 用户输入筛选条件。
2. **业务层**: 检查本地数据库是否有该日行情。若无，调用 Tushare 接口抓取并入库。
3. **持久化层**: PostgreSQL 存储股票基础信息 (`stocks`) 与日线行情 (`daily_hq`)。

## 4. 数据库设计 (Database Design)

### 4.1 核心数据表

#### 1. 股票基础信息表 (`stocks`)

| **字段名** | **类型**    | **说明**                          |
| ---------- | ----------- | --------------------------------- |
| ts_code    | String(20)  | **主键**，股票代码 (如 000001.SZ) |
| symbol     | String(20)  | 股票代码 (如 000001)              |
| name       | String(100) | 股票名称                          |
| area       | String(100) | 地域                              |
| industry   | String(100) | 所属行业                          |
| list_date  | String(10)  | 上市日期                          |

#### 2. 日线行情表 (`daily_hq`)

参考 Tushare `daily` 接口字段进行完整映射。

| **字段名** | **类型**       | **说明**                        |
| ---------- | -------------- | ------------------------------- |
| id         | BigInt         | **主键** (自增)                 |
| ts_code    | String(20)     | **外键/索引**，股票代码         |
| trade_date | Date           | **索引**，交易日期 (YYYY-MM-DD) |
| open       | Numeric(12, 4) | 开盘价                          |
| high       | Numeric(12, 4) | 最高价                          |
| low        | Numeric(12, 4) | 最低价                          |
| close      | Numeric(12, 4) | 收盘价                          |
| pre_close  | Numeric(12, 4) | 昨收价                          |
| change     | Numeric(12, 4) | 涨跌额                          |
| pct_chg    | Numeric(12, 4) | **索引**，涨跌幅 (百分比)       |
| vol        | Numeric(18, 4) | 成交量 (手)                     |
| amount     | Numeric(18, 4) | 成交额 (千元)                   |

> **设计说明**: 使用 `Numeric` 类型而非 `Float` 以避免金融计算中的精度丢失问题。

### 4.2 数据库迁移管理 (Alembic)

- **env.py 配置**: 配置 SQLAlchemy 的 `Base.metadata`，使 Alembic 能够自动检测模型变化。
- **迁移流程**:
  1. 修改 `models.py` 中的模型定义。
  2. 运行 `uv run alembic revision --autogenerate -m "add_daily_hq_table"`。
  3. 运行 `uv run alembic upgrade head`。

## 5. 核心 API 与同步逻辑

### 5.1 数据同步逻辑 (Sync Strategy)

1. **基础数据**: 首次启动或定期调用 `stock_basic` 接口，更新 `stocks` 表。
2. **行情数据 (On-Demand)**:
   - 用户请求 $D$ 日行情。
   - `Check`: `SELECT EXISTS(SELECT 1 FROM daily_hq WHERE trade_date = D)`。
   - `Missing`: 调用 Tushare `daily(trade_date=D)` 获取全量 (约 5000+ 条记录) $\rightarrow$ 批量入库 (`bulk_insert`)。
   - `Filter`: 执行 SQL `SELECT * FROM daily_hq WHERE trade_date = D AND pct_chg BETWEEN min AND max`。

## 6. API 接口定义

### 1. 股票筛选接口

- **URL**: `POST /api/v1/strategy/pct-filter`

- **Payload**:

  ```
  {
    "trade_date": "20231027",
    "min_pct": -2.0,
    "max_pct": 5.0
  }
  ```

## 7. 前端设计 (Responsive UI)

- **技术栈**: Vue 3 + Tailwind CSS。
- **适配**:
  - **Desktop**: 宽屏表格，展示所有日线字段（开、高、低、收等）。
  - **Mobile**: 紧凑卡片，仅显示名称、代码、现价及涨跌幅，点击展开详情。

## 8. 环境配置 (`uv` 依赖)

```
# 初始化环境
uv venv
source .venv/bin/activate

# 安装核心依赖
uv add fastapi uvicorn sqlalchemy asyncpg alembic tushare pydantic-settings httpx pandas

# 初始化 Alembic
alembic init alembic
```

