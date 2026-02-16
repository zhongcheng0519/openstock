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

#### 3. 每日基本面指标表 (`daily_basic`)

参考 Tushare `daily_basic` 接口字段进行映射，存储每日重要的基本面指标。

| **字段名**     | **类型**       | **说明**                              |
| -------------- | -------------- | ------------------------------------- |
| id             | BigInt         | **主键** (自增)                       |
| ts_code        | String(20)     | **外键/索引**，股票代码               |
| trade_date     | Date           | **索引**，交易日期 (YYYY-MM-DD)       |
| close          | Numeric(12, 4) | 当日收盘价                            |
| turnover_rate  | Numeric(8, 4)  | 换手率 (%)                            |
| turnover_rate_f| Numeric(8, 4)  | 换手率（自由流通股）                   |
| volume_ratio   | Numeric(8, 4)  | 量比                                  |
| pe             | Numeric(12, 4) | 市盈率（总市值/净利润，亏损为空）      |
| pe_ttm         | Numeric(12, 4) | 市盈率 TTM                            |
| pb             | Numeric(12, 4) | 市净率（总市值/净资产）                |
| ps             | Numeric(12, 4) | 市销率                                |
| ps_ttm         | Numeric(12, 4) | 市销率 TTM                            |
| dv_ratio       | Numeric(8, 4)  | 股息率 (%)                            |
| dv_ttm         | Numeric(8, 4)  | 股息率 TTM (%)                        |
| total_share    | Numeric(18, 4) | 总股本 (万股)                         |
| float_share    | Numeric(18, 4) | 流通股本 (万股)                       |
| free_share     | Numeric(18, 4) | 自由流通股本 (万股)                   |
| total_mv       | Numeric(20, 4) | 总市值 (万元)                         |
| circ_mv        | Numeric(20, 4) | **索引**，流通市值 (万元)             |

> **设计说明**: `circ_mv`（流通市值）和 `pe`（市盈率）、`turnover_rate`（换手率）字段添加索引，以支持策略筛选查询。

#### 4. 个股资金流向表 (`moneyflow`)

参考 Tushare `moneyflow` 接口字段进行映射，存储每日个股资金流向数据，用于分析大单小单成交情况，判别资金动向。

| **字段名**       | **类型**       | **说明**                        |
| ---------------- | -------------- | ------------------------------- |
| id               | BigInt         | **主键** (自增)                 |
| ts_code          | String(20)     | **外键/索引**，股票代码         |
| trade_date       | Date           | **索引**，交易日期 (YYYY-MM-DD) |
| buy_sm_vol       | Numeric(18, 4) | 小单买入量 (手)                 |
| buy_sm_amount    | Numeric(18, 4) | 小单买入金额 (万元)             |
| sell_sm_vol      | Numeric(18, 4) | 小单卖出量 (手)                 |
| sell_sm_amount   | Numeric(18, 4) | 小单卖出金额 (万元)             |
| buy_md_vol       | Numeric(18, 4) | 中单买入量 (手)                 |
| buy_md_amount    | Numeric(18, 4) | 中单买入金额 (万元)             |
| sell_md_vol      | Numeric(18, 4) | 中单卖出量 (手)                 |
| sell_md_amount   | Numeric(18, 4) | 中单卖出金额 (万元)             |
| buy_lg_vol       | Numeric(18, 4) | 大单买入量 (手)                 |
| buy_lg_amount    | Numeric(18, 4) | 大单买入金额 (万元)             |
| sell_lg_vol      | Numeric(18, 4) | 大单卖出量 (手)                 |
| sell_lg_amount   | Numeric(18, 4) | 大单卖出金额 (万元)             |
| buy_elg_vol      | Numeric(18, 4) | 特大单买入量 (手)               |
| buy_elg_amount   | Numeric(18, 4) | 特大单买入金额 (万元)           |
| sell_elg_vol     | Numeric(18, 4) | 特大单卖出量 (手)               |
| sell_elg_amount  | Numeric(18, 4) | 特大单卖出金额 (万元)           |
| net_mf_vol       | Numeric(18, 4) | 净流入量 (手)                   |
| net_mf_amount    | Numeric(18, 4) | **索引**，净流入额 (万元)       |

> **设计说明**: `net_mf_amount`（净流入额）字段添加索引，以支持按资金流向排序和筛选。各类别统计规则：小单（5万以下）、中单（5万～20万）、大单（20万～100万）、特大单（成交额>=100万），数据基于主动买卖单统计。

> **数据来源**: Tushare `moneyflow` 接口，数据开始于2010年，单次最大提取6000行记录，需要至少2000积分。

#### 5. 用户表 (`users`)

存储系统用户信息，支持管理员和普通用户角色。

| **字段名**    | **类型**      | **说明**                              |
| ------------- | ------------- | ------------------------------------- |
| id            | BigInt        | **主键** (自增)                       |
| username      | String(50)    | **唯一索引**，用户名（登录用）        |
| nickname      | String(50)    | **必填**，昵称（显示用）              |
| password_hash | String(255)   | 密码哈希 (bcrypt)                     |
| email         | String(100)   | 邮箱地址                              |
| phone         | String(20)    | 手机号（选填）                        |
| role          | String(20)    | **索引**，角色 (admin/user)           |
| is_active     | Boolean       | 是否激活，默认 True                   |
| created_at    | DateTime      | 创建时间                              |
| updated_at    | DateTime      | 更新时间                              |
| created_by    | BigInt        | **外键**，创建者用户ID (管理员)       |

> **设计说明**: 
> - 第一个注册的用户自动成为管理员 (`role='admin'`)
> - 后续注册功能关闭，只能由管理员创建用户
> - 密码使用 bcrypt 加密存储
> - 昵称为必填项，用于界面显示用户名称
> - 手机号为选填项，需验证格式（11位数字）

#### 6. 用户操作日志表 (`user_logs`)

记录用户的所有操作行为，供管理员审计。

| **字段名**    | **类型**      | **说明**                              |
| ------------- | ------------- | ------------------------------------- |
| id            | BigInt        | **主键** (自增)                       |
| user_id       | BigInt        | **外键/索引**，操作用户ID             |
| action        | String(50)    | 操作类型 (login/logout/filter/etc)    |
| resource      | String(100)   | 操作资源 (API路径)                    |
| method        | String(10)    | HTTP方法 (GET/POST/PUT/DELETE)        |
| params        | JSON          | 请求参数 (脱敏处理)                   |
| ip_address    | String(45)    | 客户端IP地址                          |
| user_agent    | String(255)   | 客户端User-Agent                      |
| status_code   | Integer       | 响应状态码                            |
| created_at    | DateTime      | **索引**，操作时间                    |

> **设计说明**: 
> - 记录所有API请求，包括登录、筛选、数据导出等操作
> - 敏感参数（如密码）需脱敏后存储
> - 按时间索引支持快速查询历史记录

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
3. **基本面指标数据 (On-Demand)**:
   - 用户请求 $D$ 日策略筛选。
   - `Check`: `SELECT EXISTS(SELECT 1 FROM daily_basic WHERE trade_date = D)`。
   - `Missing`: 调用 Tushare `daily_basic(trade_date=D)` 获取全量 $\rightarrow$ 批量入库 (`bulk_insert`)。
   - 策略筛选时，与 `daily_hq` 表联合查询。
4. **资金流向数据 (On-Demand)**:
   - 用户请求 $D$ 日策略筛选（包含资金流向条件）。
   - `Check`: `SELECT EXISTS(SELECT 1 FROM moneyflow WHERE trade_date = D)`。
   - `Missing`: 调用 Tushare `moneyflow(trade_date=D)` 获取全量 $\rightarrow$ 批量入库 (`bulk_insert`)。
   - 策略筛选时，与 `daily_hq`、`daily_basic` 表联合查询，支持按净流入额排序。

## 6. API 接口定义

### 1. 股票筛选接口

- **URL**: `POST /api/v1/strategy/filter`

- **Payload**:

  ```json
  {
    "trade_date": "20231027",
    "min_pct": -2.0,
    "max_pct": 5.0,
    "min_circ_mv": 500000.0,
    "min_pe": 0.0,
    "max_pe": 50.0,
    "min_turnover_rate": 5.0,
    "min_net_mf_amount": null,
    "mf_top_n": 30
  }
  ```

- **参数说明**:

  | **参数名**         | **类型** | **必填** | **默认值**  | **说明**                       |
  | ------------------ | -------- | -------- | ----------- | ------------------------------ |
  | trade_date         | string   | 是       | -           | 交易日期 (YYYYMMDD)            |
  | min_pct            | float    | 否       | -100.0      | 最小涨跌幅 (%)                 |
  | max_pct            | float    | 否       | 100.0       | 最大涨跌幅 (%)                 |
  | min_circ_mv        | float    | 否       | 500000.0    | 最小流通市值 (万元，默认50亿)   |
  | max_circ_mv        | float    | 否       | null        | 最大流通市值 (万元)            |
  | min_pe             | float    | 否       | 0.0         | 最小市盈率                     |
  | max_pe             | float    | 否       | 50.0        | 最大市盈率                     |
  | min_turnover_rate  | float    | 否       | 5.0         | 最小换手率 (%)                 |
  | max_turnover_rate  | float    | 否       | null        | 最大换手率 (%)                 |
  | min_net_mf_amount  | float    | 否       | null        | 最小净流入额 (万元)            |
  | mf_top_n           | int      | 否       | 30          | 按净流入额排名取前N只股票       |

- **筛选逻辑**:

  所有条件之间为 **且 (AND)** 关系，即股票需同时满足所有条件才会被筛选出来。

  ```sql
  SELECT h.*, b.circ_mv, b.pe, b.turnover_rate, m.net_mf_amount, m.net_mf_vol
  FROM daily_hq h
  JOIN daily_basic b ON h.ts_code = b.ts_code AND h.trade_date = b.trade_date
  JOIN moneyflow m ON h.ts_code = m.ts_code AND h.trade_date = m.trade_date
  WHERE h.trade_date = :trade_date
    AND h.pct_chg BETWEEN :min_pct AND :max_pct
    AND b.circ_mv >= :min_circ_mv
    AND b.pe BETWEEN :min_pe AND :max_pe
    AND b.turnover_rate >= :min_turnover_rate
    AND (:min_net_mf_amount IS NULL OR m.net_mf_amount >= :min_net_mf_amount)
  ORDER BY m.net_mf_amount DESC
  LIMIT :mf_top_n
  ```

### 2. 用户认证接口

#### 2.1 用户注册（首次初始化）

- **URL**: `POST /api/v1/auth/register`
- **说明**: 仅当系统无用户时允许调用，第一个注册用户自动成为管理员

- **Payload**:
  ```json
  {
    "username": "admin",
    "nickname": "管理员",
    "password": "your_password",
    "email": "admin@example.com",
    "phone": "13800138000"
  }
  ```

- **Response**:
  ```json
  {
    "id": 1,
    "username": "admin",
    "nickname": "管理员",
    "email": "admin@example.com",
    "phone": "13800138000",
    "role": "admin",
    "created_at": "2024-01-01T00:00:00Z"
  }
  ```

#### 2.2 用户登录

- **URL**: `POST /api/v1/auth/login`
- **Payload**:
  ```json
  {
    "username": "admin",
    "password": "your_password"
  }
  ```

- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
  ```

#### 2.3 用户登出

- **URL**: `POST /api/v1/auth/logout`
- **Header**: `Authorization: Bearer <token>`

#### 2.4 修改密码

- **URL**: `PUT /api/v1/auth/password`
- **Header**: `Authorization: Bearer <token>`
- **Payload**:
  ```json
  {
    "old_password": "current_password",
    "new_password": "new_password"
  }
  ```

#### 2.5 修改个人信息

- **URL**: `PUT /api/v1/auth/profile`
- **Header**: `Authorization: Bearer <token>`
- **Payload**:
  ```json
  {
    "nickname": "新昵称",
    "email": "newemail@example.com",
    "phone": "13800138001"
  }
  ```

- **Response**:
  ```json
  {
    "id": 1,
    "username": "admin",
    "nickname": "新昵称",
    "email": "newemail@example.com",
    "phone": "13800138001",
    "role": "admin",
    "updated_at": "2024-01-15T10:30:00Z"
  }
  ```

### 3. 用户管理接口（仅管理员）

#### 3.1 获取用户列表

- **URL**: `GET /api/v1/admin/users`
- **Header**: `Authorization: Bearer <token>` (需管理员权限)
- **Query Parameters**:
  | **参数名**  | **类型** | **必填** | **说明**           |
  | ----------- | -------- | -------- | ------------------ |
  | page        | int      | 否       | 页码，默认 1       |
  | page_size   | int      | 否       | 每页数量，默认 20  |
  | role        | string   | 否       | 按角色筛选         |
  | is_active   | bool     | 否       | 按状态筛选         |

- **Response**:
  ```json
  {
    "total": 10,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "username": "admin",
        "nickname": "管理员",
        "email": "admin@example.com",
        "phone": "13800138000",
        "role": "admin",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-15T10:30:00Z"
      }
    ]
  }
  ```

#### 3.2 创建用户

- **URL**: `POST /api/v1/admin/users`
- **Header**: `Authorization: Bearer <token>` (需管理员权限)
- **Payload**:
  ```json
  {
    "username": "newuser",
    "nickname": "新用户",
    "password": "initial_password",
    "email": "user@example.com",
    "phone": "13900139000",
    "role": "user"
  }
  ```

#### 3.3 更新用户状态

- **URL**: `PUT /api/v1/admin/users/{user_id}`
- **Header**: `Authorization: Bearer <token>` (需管理员权限)
- **Payload**:
  ```json
  {
    "is_active": false
  }
  ```

#### 3.4 重置用户密码

- **URL**: `PUT /api/v1/admin/users/{user_id}/reset-password`
- **Header**: `Authorization: Bearer <token>` (需管理员权限)
- **Payload**:
  ```json
  {
    "new_password": "reset_password"
  }
  ```

#### 3.5 删除用户

- **URL**: `DELETE /api/v1/admin/users/{user_id}`
- **Header**: `Authorization: Bearer <token>` (需管理员权限)
- **说明**: 不允许删除自己，不允许删除最后一个管理员

### 4. 操作日志接口（仅管理员）

#### 4.1 查询操作日志

- **URL**: `GET /api/v1/admin/logs`
- **Header**: `Authorization: Bearer <token>` (需管理员权限)
- **Query Parameters**:
  | **参数名**   | **类型** | **必填** | **说明**                    |
  | ------------ | -------- | -------- | --------------------------- |
  | page         | int      | 否       | 页码，默认 1                |
  | page_size    | int      | 否       | 每页数量，默认 50           |
  | user_id      | int      | 否       | 按用户ID筛选                |
  | action       | string   | 否       | 按操作类型筛选              |
  | start_date   | string   | 否       | 开始日期 (YYYY-MM-DD)       |
  | end_date     | string   | 否       | 结束日期 (YYYY-MM-DD)       |

- **Response**:
  ```json
  {
    "total": 1000,
    "page": 1,
    "page_size": 50,
    "items": [
      {
        "id": 1,
        "user_id": 2,
        "username": "user1",
        "action": "filter",
        "resource": "/api/v1/strategy/filter",
        "method": "POST",
        "ip_address": "192.168.1.100",
        "status_code": 200,
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
  ```

#### 4.2 操作统计

- **URL**: `GET /api/v1/admin/logs/statistics`
- **Header**: `Authorization: Bearer <token>` (需管理员权限)
- **Query Parameters**:
  | **参数名**   | **类型** | **必填** | **说明**              |
  | ------------ | -------- | -------- | --------------------- |
  | start_date   | string   | 否       | 开始日期              |
  | end_date     | string   | 否       | 结束日期              |

- **Response**:
  ```json
  {
    "total_requests": 5000,
    "unique_users": 10,
    "by_action": {
      "login": 100,
      "filter": 4500,
      "export": 400
    },
    "by_user": [
      {"user_id": 1, "username": "admin", "count": 500},
      {"user_id": 2, "username": "user1", "count": 4500}
    ]
  }
  ```

## 7. 前端设计 (Responsive UI)

- **技术栈**: Vue 3 + Tailwind CSS。
- **主题色**: 红色（象征红红火火）
  - 主色调: `#DC2626` (Tailwind red-600)
  - 辅助色: `#EF4444` (red-500)、`#B91C1C` (red-700)
  - 用于按钮、链接、重要信息高亮
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

# 安装认证相关依赖
uv add python-jose[cryptography] passlib[bcrypt] python-multipart

# 初始化 Alembic
alembic init alembic
```

## 9. 认证与授权设计

### 9.1 认证机制

- **JWT Token**: 使用 JSON Web Token 进行无状态认证
- **Token 有效期**: 默认 1 小时，可配置
- **密码加密**: bcrypt 算法，cost factor = 12

### 9.2 权限控制

| **角色** | **权限**                                                   |
| -------- | ---------------------------------------------------------- |
| admin    | 用户管理、查看所有操作日志、股票筛选、数据导出             |
| user     | 股票筛选、数据导出、修改个人密码、修改个人信息             |

### 9.3 中间件设计

```python
# 认证中间件流程
1. 检查请求路径是否需要认证
2. 从 Header 提取 Bearer Token
3. 验证 Token 有效性和过期时间
4. 加载用户信息到 request.state.user
5. 检查用户角色是否有权限访问该资源
6. 记录操作日志到 user_logs 表
```

### 9.4 操作日志记录策略

| **操作类型** | **说明**                     | **记录内容**              |
| ------------ | ---------------------------- | ------------------------- |
| login        | 用户登录                     | IP、User-Agent            |
| logout       | 用户登出                     | IP                        |
| filter       | 股票筛选                     | 筛选参数                  |
| export       | 数据导出                     | 导出范围                  |
| create_user  | 创建用户（管理员）           | 新用户信息                |
| reset_pwd    | 重置密码（管理员/用户自己）  | 目标用户ID                |
| update_profile | 修改个人信息               | 修改的字段                |
| disable_user | 禁用用户（管理员）           | 目标用户ID                |

