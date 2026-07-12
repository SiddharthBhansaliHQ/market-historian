import math

from models.market_data_unit import MarketDataUnit
from models.security_statistics import SecurityStatistics


def calculate_security_statistics(
    market_data: dict[str, list[MarketDataUnit]],
) -> dict[str, SecurityStatistics]:
    security_statistics_map = dict()

    for symbol, symbol_market_data in market_data.items():
        if len(symbol_market_data) < 1:
            continue

        symbol_market_data.sort(key=lambda x: x.reference_date)

        security_statistics_map[symbol] = SecurityStatistics(
            start_date=symbol_market_data[0].reference_date,
            end_date=symbol_market_data[-1].reference_date,
            rate_of_return=get_rate_of_return(symbol_market_data),
            annualized_log_rate_of_return=get_annualized_log_rate_of_return(
                symbol_market_data
            ),
            annualized_log_volatility=get_annualized_log_volatility(symbol_market_data),
            annualized_log_sharpe_ratio_rf_zero=get_annualized_log_sharpe_ratio_rf_zero(
                symbol_market_data
            ),
        )

    return security_statistics_map


def get_rate_of_return(symbol_market_data: list[MarketDataUnit]) -> float:
    if len(symbol_market_data) < 1:
        return math.nan

    start_price = symbol_market_data[0].adjusted_close
    end_price = symbol_market_data[-1].adjusted_close

    if start_price == 0.0:
        return math.nan

    return (end_price - start_price) / start_price


def get_annualized_log_rate_of_return(
    symbol_market_data: list[MarketDataUnit],
) -> float:
    if len(symbol_market_data) < 2:
        return math.nan

    start_price = symbol_market_data[0].adjusted_close
    end_price = symbol_market_data[-1].adjusted_close

    if start_price == 0.0:
        return math.nan

    return math.log(end_price / start_price) * (365.0 / (len(symbol_market_data) - 1))


def get_annualized_log_volatility(
    symbol_market_data: list[MarketDataUnit],
) -> float:
    if len(symbol_market_data) < 2:
        return math.nan

    daily_returns = []

    for i in range(1, len(symbol_market_data)):
        curr_price = symbol_market_data[i].adjusted_close
        prev_price = symbol_market_data[i - 1].adjusted_close

        if prev_price == 0.0:
            return math.nan

        daily_returns.append(math.log(curr_price / prev_price))

    mean_return = sum(daily_returns) / len(daily_returns)

    std_dev = (
        sum([(d_r - mean_return) ** 2.0 for d_r in daily_returns])
        / (len(symbol_market_data) - 1)
    ) ** 0.5

    return std_dev * (252.0**0.5)


def get_annualized_log_sharpe_ratio_rf_zero(
    symbol_market_data: list[MarketDataUnit],
) -> float:
    numerator = get_annualized_log_rate_of_return(symbol_market_data)
    denominator = get_annualized_log_volatility(symbol_market_data)

    if numerator == math.nan or denominator == math.nan or denominator == 0.0:
        return math.nan

    return numerator / denominator
