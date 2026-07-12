from datetime import timedelta

from models.date_range import DateRange
from models.market_data_unit import MarketDataUnit


def generate_mock_market_data(date_range: DateRange) -> list[MarketDataUnit]:
    market_data = []
    curr_date = date_range.start_date

    while curr_date <= date_range.end_date:
        market_data.append(
            MarketDataUnit(
                reference_date=curr_date,
                adjusted_close=((curr_date.day + curr_date.month) * curr_date.year)
                * 3.5,
            )
        )

        curr_date += timedelta(days=1)

    assert len(market_data) == (date_range.end_date - date_range.start_date).days + 1
    return market_data
