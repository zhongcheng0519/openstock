# AGENTS.md - OpenStock

Guidelines for AI agents working on this stock analysis platform.

## Tech Stack

- **Backend**: Python 3.10+ / FastAPI / SQLAlchemy 2.0 (async) / PostgreSQL / Alembic
- **Frontend**: Vue 3 / TypeScript / Tailwind CSS 4 / Element Plus / Pinia
- **Package Managers**: uv (Python), npm (Node.js)

## Commands

### Backend

```bash
cd backend

# Dependencies
uv pip install -e .

# Development server
uv run python -m app.main

# Database migrations
uv run alembic upgrade head                           # Apply migrations
uv run alembic downgrade -1                           # Rollback one
uv run alembic revision --autogenerate -m "msg"       # Create new

# Testing
uv run pytest                                         # All tests
uv run pytest tests/test_file.py                      # Single file
uv run pytest tests/test_file.py::test_name           # Single test
uv run pytest -k "pattern"                            # Match pattern
uv run pytest -x -v                                   # Stop on first, verbose
```

### Frontend

```bash
cd frontend

# Dependencies
npm install

# Development
npm run dev                                           # Start Vite dev server

# Build
npm run build                                         # Full build (type-check + build)
npm run build-only                                    # Build only
npm run type-check                                    # TypeScript only

# Linting & Formatting
npm run lint                                          # oxlint + eslint
npm run lint:oxlint                                   # Oxlint only
npm run lint:eslint                                   # ESLint only
npm run format                                        # Prettier
```

### Docker

```bash
make up-d                                             # Start services (background)
make down                                             # Stop services
make logs                                             # View logs
make migrate                                          # Run migrations
make shell-backend                                    # Backend container shell
make test                                             # Run backend tests in container
```

## Code Style

### Python

**Imports** (grouped, ordered):
```python
# 1. Standard library
from datetime import date

# 2. Third-party
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Internal (absolute imports from `app`)
from app.db.base import get_db
from app.models.stock import Stock
```

**Naming**: Files `snake_case.py`, Classes `PascalCase`, Functions/Variables `snake_case`, Constants `UPPER_SNAKE_CASE`

**Types**: Use `str | None` (not `Optional[str]`), always annotate parameters and return values. SQLAlchemy: `Mapped[str]`

**SQLAlchemy Models**:
```python
class Stock(Base):
    """股票基础信息表"""
    __tablename__ = "stocks"
    
    ts_code: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[str | None] = mapped_column(String(100), nullable=True)
```

**Pydantic Schemas**:
```python
class UserRequest(BaseModel):
    username: str = Field(..., min_length=3, description="用户名")
    email: str | None = Field(default=None, description="邮箱")
    
    class Config:
        from_attributes = True
```

**Error Handling**: Use `HTTPException`, Chinese messages for user-facing errors

### TypeScript/Vue

**Imports**:
```typescript
// 1. Vue/core
import { ref, reactive } from 'vue'
// 2. Third-party
import { ElMessage } from 'element-plus'
// 3. Internal (@/ -> ./src/)
import { strategyApi } from '@/api/client'
import type { DailyQuote } from '@/api/client'
```

**Naming**: Components `PascalCase.vue`, Utilities `camelCase.ts`, Composables `useCamelCase`, Types `PascalCase`

**Vue 3 Composition API**:
```vue
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import type { DailyQuote } from '@/api/client'

const loading = ref(false)
const results = ref<DailyQuote[]>([])
const form = reactive({ trade_date: '', min_pct: -2 })

const handleSubmit = async () => {
  loading.value = true
  try {
    const response = await strategyApi.filter(form)
    results.value = response.data.data
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>
```

**Error Handling**: Use `ElMessage`, always try-catch async operations, reset loading in `finally`

## Project Structure

```
openstock/
├── backend/app/{api,core,db,models,services}/
├── backend/alembic/
├── frontend/src/{api,components,views,router,stores}/
└── Makefile
```

## Key Files

| File | Purpose |
|------|---------|
| `backend/pyproject.toml` | Python dependencies |
| `frontend/eslint.config.ts` | ESLint + Vue + TS + Oxlint |
| `frontend/.prettierrc.json` | No semis, single quotes, width 100 |
| `frontend/tsconfig.app.json` | Path alias `@/` → `./src/` |

## Notes

1. **Chinese comments** for business logic
2. **SQLAlchemy 2.0 style**: `Mapped[]`, `mapped_column()`
3. **Element Plus** for UI components
4. **Always manage loading states** in async operations
5. **No semicolons** in TypeScript
6. **Single quotes** in TypeScript
