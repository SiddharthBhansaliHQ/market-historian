from datetime import date

import pytest

from models.market_data_unit import MarketDataUnit
from services import calculation_service

MOCK_MARKET_DATA = {
    "A": [
        MarketDataUnit(reference_date=date(2020, 1, 4), adjusted_close=100.1),
        MarketDataUnit(reference_date=date(2020, 1, 3), adjusted_close=100.2),
        MarketDataUnit(reference_date=date(2020, 1, 2), adjusted_close=100.3),
        MarketDataUnit(reference_date=date(2020, 1, 1), adjusted_close=100.4),
    ],
    "B": [
        MarketDataUnit(reference_date=date(2020, 1, 3), adjusted_close=100.1),
        MarketDataUnit(reference_date=date(2020, 1, 2), adjusted_close=100.2),
        MarketDataUnit(reference_date=date(2020, 1, 1), adjusted_close=100.3),
        MarketDataUnit(reference_date=date(2020, 1, 4), adjusted_close=100.4),
    ],
    "C": [
        MarketDataUnit(reference_date=date(2020, 1, 1), adjusted_close=100.1),
        MarketDataUnit(reference_date=date(2020, 1, 2), adjusted_close=100.2),
        MarketDataUnit(reference_date=date(2020, 1, 3), adjusted_close=100.3),
        MarketDataUnit(reference_date=date(2020, 1, 4), adjusted_close=100.4),
    ],
}


def test_calculate_security_statistics() -> None:
    security_statistics = calculation_service.calculate_security_statistics(
        MOCK_MARKET_DATA
    )

    for symbol, symbol_market_data in MOCK_MARKET_DATA.items():
        symbol_market_data.sort(key=lambda x: x.reference_date)

        assert (
            security_statistics[symbol].start_date
            == symbol_market_data[0].reference_date
        )

        assert (
            security_statistics[symbol].end_date
            == symbol_market_data[-1].reference_date
        )

        assert security_statistics[
            symbol
        ].rate_of_return == calculation_service.get_rate_of_return(symbol_market_data)

        assert (
            security_statistics[symbol].annualized_log_rate_of_return
            == calculation_service.get_annualized_log_rate_of_return(symbol_market_data)
        )

        assert (
            security_statistics[symbol].annualized_log_volatility
            == calculation_service.get_annualized_log_volatility(symbol_market_data)
        )

        assert (
            security_statistics[symbol].annualized_log_sharpe_ratio_rf_zero
            == calculation_service.get_annualized_log_sharpe_ratio_rf_zero(
                symbol_market_data
            )
        )


def test_rate_of_return() -> None:
    assert calculation_service.get_rate_of_return(
        MOCK_MARKET_DATA["B"]
    ) == pytest.approx(0.000997008)


def test_annualized_log_rate_of_return() -> None:
    assert calculation_service.get_annualized_log_rate_of_return(
        MOCK_MARKET_DATA["B"]
    ) == pytest.approx(0.12124232)


def test_annualized_log_volatility() -> None:
    assert calculation_service.get_annualized_log_volatility(
        MOCK_MARKET_DATA["B"]
    ) == pytest.approx(0.029862357)


def test_annualized_log_sharpe_ratio_rf_zero() -> None:
    assert calculation_service.get_annualized_log_sharpe_ratio_rf_zero(
        MOCK_MARKET_DATA["B"]
    ) == pytest.approx(4.0600387)
