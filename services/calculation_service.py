from models.market_data_unit import MarketDataUnit
from models.security_statistics import SecurityStatistics


def calculate_security_statistics(
    market_data: dict[str, list[MarketDataUnit]],
) -> dict[str, SecurityStatistics]:
    security_statistics_map: dict[str, SecurityStatistics] = dict()

    for symbol, symbol_market_data in market_data.items():
        symbol_market_data.sort(key=lambda x: x.reference_date)

        security_statistics_map[symbol] = SecurityStatistics(
            start_date=symbol_market_data[0].reference_date,
            end_date=symbol_market_data[-1].reference_date,
            rate_of_return=get_rate_of_return(symbol_market_data),
        )

    return security_statistics_map


def get_rate_of_return(symbol_market_data: list[MarketDataUnit]) -> float:
    start_price: float = symbol_market_data[0].adjusted_close
    end_price: float = symbol_market_data[-1].adjusted_close
    return (end_price - start_price) / start_price
