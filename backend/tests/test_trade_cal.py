import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date
import pandas as pd

from app.services.tushare_service import TushareService


class TestTradeCal:
    """Tests for Tushare trade_cal interface (https://tushare.pro/document/2?doc_id=26)"""

    @pytest.fixture
    def tushare_service(self):
        return TushareService()

    @pytest.mark.asyncio
    async def test_trade_cal_20260227_is_trading_day(self, tushare_service):
        """Test that 2026-02-27 is a trading day (is_open=1)"""
        mock_df = pd.DataFrame({
            'exchange': ['SSE'],
            'cal_date': ['20260227'],
            'is_open': ['1'],
            'pretrade_date': ['20260226']
        })

        with patch.object(tushare_service.pro, 'trade_cal', return_value=mock_df) as mock_trade_cal:
            result = tushare_service.pro.trade_cal(
                exchange='',
                start_date='20260227',
                end_date='20260227'
            )

            mock_trade_cal.assert_called_once_with(
                exchange='',
                start_date='20260227',
                end_date='20260227'
            )

            assert len(result) == 1
            assert result['is_open'].iloc[0] == '1'
            assert result['cal_date'].iloc[0] == '20260227'

    @pytest.mark.asyncio
    async def test_trade_cal_20260228_is_holiday(self, tushare_service):
        """Test that 2026-02-28 is a holiday (is_open=0) with pretrade_date=20260227"""
        mock_df = pd.DataFrame({
            'exchange': ['SSE'],
            'cal_date': ['20260228'],
            'is_open': ['0'],
            'pretrade_date': ['20260227']
        })

        with patch.object(tushare_service.pro, 'trade_cal', return_value=mock_df) as mock_trade_cal:
            result = tushare_service.pro.trade_cal(
                exchange='',
                start_date='20260228',
                end_date='20260228'
            )

            mock_trade_cal.assert_called_once_with(
                exchange='',
                start_date='20260228',
                end_date='20260228'
            )

            assert len(result) == 1
            assert result['is_open'].iloc[0] == '0'
            assert result['cal_date'].iloc[0] == '20260228'
            assert result['pretrade_date'].iloc[0] == '20260227'


class TestGetCurrentTradeDate:
    """Tests for get_current_trade_date method"""

    @pytest.fixture
    def tushare_service(self):
        return TushareService()

    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_current_date_is_trading_day_returns_today(self, tushare_service, mock_db):
        """Test that when today is a trading day (is_open=1), returns today"""
        mock_df = pd.DataFrame({
            'exchange': ['SSE'],
            'cal_date': ['20260227'],
            'is_open': ['1'],
            'pretrade_date': ['20260226']
        })

        with patch.object(tushare_service.pro, 'trade_cal', return_value=mock_df):
            with patch('app.services.tushare_service.date') as mock_date:
                mock_date.today.return_value = date(2026, 2, 27)
                mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

                result = await tushare_service.get_current_trade_date(mock_db)

                assert result == date(2026, 2, 27)

    @pytest.mark.asyncio
    async def test_current_date_is_holiday_returns_pretrade_date(self, tushare_service, mock_db):
        """Test that when today is not a trading day (is_open=0), returns pretrade_date"""
        mock_df = pd.DataFrame({
            'exchange': ['SSE'],
            'cal_date': ['20260228'],
            'is_open': ['0'],
            'pretrade_date': ['20260227']
        })

        with patch.object(tushare_service.pro, 'trade_cal', return_value=mock_df):
            with patch('app.services.tushare_service.date') as mock_date:
                mock_date.today.return_value = date(2026, 2, 28)
                mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

                result = await tushare_service.get_current_trade_date(mock_db)

                assert result == date(2026, 2, 27)

    @pytest.mark.asyncio
    async def test_empty_response_returns_none(self, tushare_service, mock_db):
        """Test that empty API response returns None"""
        mock_df = pd.DataFrame(columns=['exchange', 'cal_date', 'is_open', 'pretrade_date'])

        with patch.object(tushare_service.pro, 'trade_cal', return_value=mock_df):
            with patch('app.services.tushare_service.date') as mock_date:
                mock_date.today.return_value = date(2026, 2, 28)
                mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

                result = await tushare_service.get_current_trade_date(mock_db)

                assert result is None

    @pytest.mark.asyncio
    async def test_api_error_returns_none(self, tushare_service, mock_db):
        """Test that API error returns None"""
        with patch.object(tushare_service.pro, 'trade_cal', side_effect=Exception("API Error")):
            with patch('app.services.tushare_service.date') as mock_date:
                mock_date.today.return_value = date(2026, 2, 28)
                mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

                result = await tushare_service.get_current_trade_date(mock_db)

                assert result is None
