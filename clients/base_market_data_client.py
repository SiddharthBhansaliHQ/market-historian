from abc import ABC, abstractmethod
from datetime import date

from models.date_range import DateRange
from models.market_data_unit import MarketDataUnit


class BaseMarketDataClient(ABC):
    @abstractmethod
    async def fetch(
        self, symbol: str, date_range: DateRange
    ) -> dict[date, MarketDataUnit]: ...

    @abstractmethod
    async def close(self) -> None: ...
