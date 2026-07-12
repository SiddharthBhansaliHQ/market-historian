import asyncio

from caches.base_market_data_cache import BaseMarketDataCache
from clients.base_market_data_client import BaseMarketDataClient
from models.date_range import DateRange
from models.market_data_unit import MarketDataUnit


async def collect_market_data(
    client: BaseMarketDataClient,
    cache: BaseMarketDataCache,
    symbol_map: dict[str, DateRange],
) -> dict[str, list[MarketDataUnit]]:
    market_data = dict()
    cache_call_map = dict()
    api_call_map = dict()
    cache_updates = []

    for symbol, date_range in symbol_map.items():
        cache_call_map[(symbol, date_range)] = cache.get(symbol, date_range)

    for symbol_and_date_range, cache_call in cache_call_map.items():
        cache_result = await cache_call

        if cache_result is None:
            api_call_map[symbol_and_date_range] = client.fetch(
                symbol_and_date_range[0], symbol_and_date_range[1]
            )
        else:
            market_data[symbol_and_date_range[0]] = cache_result

    for symbol_and_date_range, api_call in api_call_map.items():
        api_result = await api_call
        market_data[symbol_and_date_range[0]] = api_result
        cache_updates.append(
            cache.set(symbol_and_date_range[0], symbol_and_date_range[1], api_result)
        )

    await asyncio.gather(*cache_updates)
    return market_data
