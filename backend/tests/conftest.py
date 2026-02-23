import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_db():
    db = AsyncMock(spec=AsyncSession)
    db.execute = AsyncMock()
    return db


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture
def sample_stock_data():
    from app.models.stock import Stock, DailyQuote, DailyBasic, Moneyflow
    
    stock = Stock(
        ts_code="000001.SZ",
        symbol="000001",
        name="平安银行",
        area="深圳",
        industry="银行"
    )
    
    daily_quote = DailyQuote(
        ts_code="000001.SZ",
        trade_date=date(2025, 2, 21),
        open=12.50,
        high=12.80,
        low=12.30,
        close=12.60,
        pre_close=12.40,
        change=0.20,
        pct_chg=1.61,
        vol=1234567.0,
        amount=12345678.0
    )
    
    daily_basic = DailyBasic(
        ts_code="000001.SZ",
        trade_date=date(2025, 2, 21),
        circ_mv=500000.0,
        pe=8.5,
        turnover_rate=5.2
    )
    
    moneyflow = Moneyflow(
        ts_code="000001.SZ",
        trade_date=date(2025, 2, 21),
        net_mf_amount=1234567.0,
        net_mf_vol=98765.0
    )
    
    return stock, daily_quote, daily_basic, moneyflow
