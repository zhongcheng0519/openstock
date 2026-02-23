import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date

from app.api.strategy import stock_filter, FIELD_MAPPING, OPERATOR_MAP
from app.api.schemas import StockFilterRequest, FilterCondition
from app.models.stock import Stock, DailyQuote, DailyBasic, Moneyflow


class TestFieldMapping:
    def test_field_mapping_contains_expected_fields(self):
        expected_fields = ["pct_chg", "circ_mv", "pe", "turnover_rate", "net_mf_amount"]
        for field in expected_fields:
            assert field in FIELD_MAPPING

    def test_field_mapping_values_are_columns(self):
        assert FIELD_MAPPING["pct_chg"] == DailyQuote.pct_chg
        assert FIELD_MAPPING["circ_mv"] == DailyBasic.circ_mv
        assert FIELD_MAPPING["pe"] == DailyBasic.pe
        assert FIELD_MAPPING["turnover_rate"] == DailyBasic.turnover_rate
        assert FIELD_MAPPING["net_mf_amount"] == Moneyflow.net_mf_amount


class TestOperatorMap:
    def test_operator_map_contains_expected_operators(self):
        expected_operators = ["gte", "lte", "eq", "gt", "lt"]
        for op in expected_operators:
            assert op in OPERATOR_MAP


class TestStockFilterRequest:
    def test_default_conditions(self):
        request = StockFilterRequest(trade_date="20250221")
        assert len(request.conditions) == 2
        assert request.conditions[0].field == "pct_chg"
        assert request.conditions[0].operator == "gte"
        assert request.conditions[0].value == -100.0
        assert request.conditions[1].field == "pct_chg"
        assert request.conditions[1].operator == "lte"
        assert request.conditions[1].value == 100.0

    def test_custom_conditions(self):
        conditions = [
            FilterCondition(field="pct_chg", operator="gte", value=-5.0),
            FilterCondition(field="circ_mv", operator="gte", value=100000),
            FilterCondition(field="pe", operator="lte", value=30),
        ]
        request = StockFilterRequest(
            trade_date="20250221",
            conditions=conditions,
            mf_top_n=50
        )
        assert len(request.conditions) == 3
        assert request.mf_top_n == 50

    def test_empty_conditions(self):
        request = StockFilterRequest(trade_date="20250221", conditions=[])
        assert len(request.conditions) == 0


class TestStockFilter:
    @pytest.mark.asyncio
    async def test_unknown_field_raises_error(self, mock_db):
        request = StockFilterRequest(
            trade_date="20250221",
            conditions=[FilterCondition(field="unknown_field", operator="gte", value=10)]
        )
        
        with patch("app.api.strategy._ensure_data_synced", new_callable=AsyncMock):
            with pytest.raises(Exception) as exc_info:
                await stock_filter(request, mock_db)
            assert "未知字段" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_unknown_operator_raises_error(self, mock_db):
        request = StockFilterRequest(
            trade_date="20250221",
            conditions=[FilterCondition(field="pct_chg", operator="invalid_op", value=10)]
        )
        
        with patch("app.api.strategy._ensure_data_synced", new_callable=AsyncMock):
            with pytest.raises(Exception) as exc_info:
                await stock_filter(request, mock_db)
            assert "未知操作符" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_successful_filter_with_valid_conditions(self, mock_db, sample_stock_data):
        stock, daily_quote, daily_basic, moneyflow = sample_stock_data
        
        mock_result = MagicMock()
        mock_result.all.return_value = [(daily_quote, daily_basic, stock, moneyflow)]
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        request = StockFilterRequest(
            trade_date="20250221",
            conditions=[
                FilterCondition(field="pct_chg", operator="gte", value=-5.0),
                FilterCondition(field="pct_chg", operator="lte", value=5.0),
            ],
            mf_top_n=30
        )
        
        with patch("app.api.strategy._ensure_data_synced", new_callable=AsyncMock):
            response = await stock_filter(request, mock_db)
        
        assert response.count == 1
        assert response.data[0].ts_code == "000001.SZ"
        assert response.data[0].name == "平安银行"

    @pytest.mark.asyncio
    async def test_empty_conditions_returns_all_stocks(self, mock_db, sample_stock_data):
        stock, daily_quote, daily_basic, moneyflow = sample_stock_data
        
        mock_result = MagicMock()
        mock_result.all.return_value = [(daily_quote, daily_basic, stock, moneyflow)]
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        request = StockFilterRequest(
            trade_date="20250221",
            conditions=[],
            mf_top_n=30
        )
        
        with patch("app.api.strategy._ensure_data_synced", new_callable=AsyncMock):
            response = await stock_filter(request, mock_db)
        
        mock_db.execute.assert_called_once()
        call_args = mock_db.execute.call_args
        query = call_args[0][0]
        assert "ORDER BY" in str(query)
        assert "LIMIT" in str(query)

    @pytest.mark.asyncio
    async def test_all_supported_fields(self, mock_db, sample_stock_data):
        stock, daily_quote, daily_basic, moneyflow = sample_stock_data
        
        mock_result = MagicMock()
        mock_result.all.return_value = [(daily_quote, daily_basic, stock, moneyflow)]
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        request = StockFilterRequest(
            trade_date="20250221",
            conditions=[
                FilterCondition(field="pct_chg", operator="gte", value=-5.0),
                FilterCondition(field="pct_chg", operator="lte", value=5.0),
                FilterCondition(field="circ_mv", operator="gte", value=100000),
                FilterCondition(field="pe", operator="gte", value=0),
                FilterCondition(field="pe", operator="lte", value=50),
                FilterCondition(field="turnover_rate", operator="gte", value=3.0),
                FilterCondition(field="net_mf_amount", operator="gte", value=0),
            ],
            mf_top_n=30
        )
        
        with patch("app.api.strategy._ensure_data_synced", new_callable=AsyncMock):
            response = await stock_filter(request, mock_db)
        
        assert response.count == 1
