import aiohttp
import redis

from caches.base_market_data_cache import BaseMarketDataCache
from caches.redis_market_data_cache import RedisMarketDataCache
from clients.base_market_data_client import BaseMarketDataClient
from clients.tiingo_market_data_client import TiingoMarketDataClient


async def create_market_data_cache(config: dict[str, str]) -> BaseMarketDataCache:
    if config["type"] == "redis":
        return RedisMarketDataCache(redis.asyncio.Redis.from_url(config["url"]))
    else:
        raise ValueError("Invalid market data cache type.")


async def create_market_data_client(
    config: dict[str, str],
) -> BaseMarketDataClient:
    http_client: aiohttp.ClientSession = aiohttp.ClientSession()

    if config["type"] == "tiingo":
        return TiingoMarketDataClient(http_client, config["api_key"])
    else:
        raise ValueError("Invalid market data client type.")
