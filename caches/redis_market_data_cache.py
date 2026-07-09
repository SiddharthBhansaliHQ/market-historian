from typing import override

import redis.asyncio

from caches.base_market_data_cache import BaseMarketDataCache
from models.date_range import DateRange
from models.market_data_unit import MarketDataUnit


class RedisMarketDataCache(BaseMarketDataCache):
    def __init__(self, redis_client: redis.asyncio.Redis) -> None:
        self._redis_client = redis_client

    @override
    async def get(
        self, symbol: str, date_range: DateRange
    ) -> list[MarketDataUnit] | None:
        lookup: bytes | str | None = await self._redis_client.get(
            self._generate_key(symbol, date_range)
        )

        if lookup is None:
            return None
        else:
            return self._TYPE_ADAPTER.validate_json(lookup)

    @override
    async def set(
        self,
        symbol: str,
        date_range: DateRange,
        value: list[MarketDataUnit],
    ) -> None:
        await self._redis_client.set(
            self._generate_key(symbol, date_range),
            self._TYPE_ADAPTER.dump_json(value).decode(),
            ex=60 * 60,
            nx=True,
        )

    @override
    async def close(self) -> None:
        await self._redis_client.aclose()

    def _generate_key(self, symbol: str, date_range: DateRange) -> str:
        return f"{symbol}:{date_range.start_date}:{date_range.end_date}"
