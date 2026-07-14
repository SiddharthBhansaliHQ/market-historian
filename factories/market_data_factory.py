import httpx2
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
    config: dict[str, str], http_client_async: httpx2.AsyncClient
) -> BaseMarketDataClient:
    if config["type"] == "tiingo":
        return TiingoMarketDataClient(http_client_async, config["api_key"])
    else:
        raise ValueError("Invalid market data client type.")
