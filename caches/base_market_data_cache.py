from abc import ABC, abstractmethod

from pydantic import TypeAdapter

from models.date_range import DateRange
from models.market_data_unit import MarketDataUnit


class BaseMarketDataCache(ABC):
    _TYPE_ADAPTER = TypeAdapter(list[MarketDataUnit])

    @abstractmethod
    async def get(
        self, symbol: str, date_range: DateRange
    ) -> list[MarketDataUnit] | None: ...

    @abstractmethod
    async def set(
        self,
        symbol: str,
        date_range: DateRange,
        value: list[MarketDataUnit],
    ) -> None: ...

    @abstractmethod
    async def aclose(self) -> None: ...
