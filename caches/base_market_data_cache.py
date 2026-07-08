from abc import ABC, abstractmethod
from datetime import date

from models.date_range import DateRange
from models.market_data_unit import MarketDataUnit


class BaseMarketDataCache(ABC):
    @abstractmethod
    async def get(
        self, symbol: str, date_range: DateRange
    ) -> dict[date, MarketDataUnit] | None: ...

    @abstractmethod
    async def set(
        self,
        symbol: str,
        date_range: DateRange,
        value: dict[date, MarketDataUnit],
    ) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...
