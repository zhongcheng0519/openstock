# AGENTS.md - OpenStock 股票分析系统

This document provides guidelines for AI agents working on the OpenStock codebase.

## Project Overview

OpenStock is a stock analysis platform with:
- **Backend**: Python FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL
- **Frontend**: Vue 3 + TypeScript + Tailwind CSS + Element Plus
- **Package Managers**: uv (Python), npm (Node.js)

## Build/Lint/Test Commands

### Backend (Python)

```bash
cd backend

# Install dependencies
uv pip install -e .

# Run development server
uv run python -m app.main

# Database migrations
uv run alembic upgrade head              # Apply migrations
uv run alembic downgrade -1              # Rollback one migration
uv run alembic revision --autogenerate -m "description"  # Create new migration

# Testing (pytest)
uv run pytest                            # Run all tests
uv run pytest path/to/test_file.py       # Run specific test file
uv run pytest -k "test_name"             # Run tests matching pattern
uv run pytest -x                         # Stop on first failure
uv run pytest -v                         # Verbose output

# Type checking
# (No mypy configured - rely on IDE/strict type hints)
```

### Frontend (Vue/TypeScript)

```bash
cd frontend

# Install dependencies
npm install

# Development
npm run dev                              # Start dev server (Vite)

# Building
npm run build                            # Full build with type check
npm run build-only                       # Build without type check
npm run type-check                       # TypeScript check only

# Linting & Formatting
npm run lint                             # Run all linters (oxlint + eslint)
npm run lint:oxlint                      # Run oxlint only
npm run lint:eslint                      # Run ESLint only
npm run format                           # Format with Prettier

# Testing
npm run test                             # Run all tests (if configured)
```

### Docker (Full Stack)

```bash
# Development via Docker
make up-d                                # Start all services in background
make down                                # Stop all services
make logs                                # View logs
make restart                             # Restart services
make migrate                             # Run DB migrations
make shell-backend                       # Enter backend container
make test                                # Run backend tests in container
```

## Code Style Guidelines

### Python (Backend)

**Imports** - Grouped and ordered:
```python
# 1. Standard library
from datetime import date, datetime
from typing import Optional

# 2. Third-party packages
from fastapi import FastAPI, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Internal modules (use absolute imports from `app`)
from app.core.config import get_settings
from app.models.stock import Stock
```

**Naming Conventions**:
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

**Type Hints**:
- Use Python 3.10+ union syntax: `str | None` instead of `Optional[str]`
- Always type function parameters and return values
- Use `Mapped[T]` for SQLAlchemy model columns

**SQLAlchemy Models**:
```python
class Stock(Base):
    """股票基础信息表"""
    __tablename__ = "stocks"
    
    ts_code: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[str | None] = mapped_column(String(100), nullable=True)
```

**Error Handling**:
- Use FastAPI's `HTTPException` for API errors
- Log exceptions before raising HTTP errors
- Return meaningful error messages in Chinese for user-facing errors

### TypeScript/Vue (Frontend)

**Imports**:
```typescript
// 1. Vue/core libraries
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'

// 2. Third-party
import { ElMessage } from 'element-plus'

// 3. Internal (@/ alias maps to ./src)
import { strategyApi } from '@/api/client'
import type { DailyQuote } from '@/api/client'
```

**Naming Conventions**:
- Files: `PascalCase.vue` for components, `camelCase.ts` for utilities
- Components: `PascalCase`
- Composables: `useCamelCase`
- Types/Interfaces: `PascalCase`
- Variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`

**Vue 3 Composition API Pattern**:
```vue
<script setup lang="ts">
import { ref, reactive } from 'vue'

// Type imports
import type { DailyQuote } from '@/api/client'

// Reactive state
const loading = ref(false)
const results = ref<DailyQuote[]>([])

// Reactive object for forms
const filterForm = reactive({
  trade_date: '',
  min_pct: -2,
  max_pct: 5,
})

// Async handlers with error handling
const handleFilter = async () => {
  loading.value = true
  try {
    const response = await strategyApi.pctFilter(filterForm)
    results.value = response.data.data
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>
```

**Error Handling**:
- Use `ElMessage` from Element Plus for user notifications
- Always wrap async calls in try-catch
- Use `finally` to reset loading states

## Project Structure

```
openstock/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes & schemas
│   │   ├── core/          # Config (Settings)
│   │   ├── db/            # Database setup (base.py)
│   │   ├── models/        # SQLAlchemy models
│   │   ├── services/      # Business logic
│   │   └── main.py        # App entry
│   ├── alembic/           # DB migrations
│   └── pyproject.toml     # Dependencies
│
├── frontend/
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # Vue components
│   │   ├── views/         # Page components
│   │   ├── router/        # Vue Router config
│   │   ├── stores/        # Pinia stores
│   │   └── main.ts        # Entry point
│   └── package.json
│
└── Makefile               # Common commands
```

## Key Configuration Files

- `backend/pyproject.toml` - Python deps, no lint tools configured
- `frontend/eslint.config.ts` - ESLint + Vue + TypeScript + Oxlint
- `frontend/.prettierrc.json` - Prettier: no semis, single quotes, 100 width
- `frontend/tsconfig.app.json` - Path alias `@/` → `./src/`

## Notes for Agents

1. **Use Chinese comments** for business logic (project language convention)
2. **Prefer SQLAlchemy 2.0 style** with `Mapped[]` and `mapped_column()`
3. **Use Element Plus components** for UI consistency
4. **Handle loading states** - always set/clear loading flags in async operations
5. **No trailing semicolons** in TypeScript (per Prettier config)
6. **Single quotes** preferred in TypeScript
