import asyncio
import os
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

import certifi
from fastapi import Depends, FastAPI
from pydantic import Field

import config
import factories.market_data_factory
from caches.base_market_data_cache import BaseMarketDataCache
from clients.base_market_data_client import BaseMarketDataClient
from models.date_range import DateRange
from models.security_statistics import SecurityStatistics
from services import calculation_service, market_data_service

os.environ["SSL_CERT_FILE"] = certifi.where()
MARKET_DATA_CACHE = None
MARKET_DATA_CLIENT = None
SETTINGS = config.Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global MARKET_DATA_CACHE, MARKET_DATA_CLIENT

    MARKET_DATA_CACHE = await factories.market_data_factory.create_market_data_cache(
        SETTINGS.market_data_cache_config
    )
    MARKET_DATA_CLIENT = await factories.market_data_factory.create_market_data_client(
        SETTINGS.market_data_client_config
    )

    yield

    await MARKET_DATA_CACHE.close()
    await MARKET_DATA_CLIENT.close()


app: FastAPI = FastAPI(lifespan=lifespan)


def get_market_data_cache() -> BaseMarketDataCache:
    if MARKET_DATA_CACHE is None:
        raise RuntimeError("Failed to initialize market data cache.")
    else:
        return MARKET_DATA_CACHE


def get_market_data_client() -> BaseMarketDataClient:
    if MARKET_DATA_CLIENT is None:
        raise RuntimeError("Failed to initialize market data client.")
    else:
        return MARKET_DATA_CLIENT


@app.post("/statistics")
async def compute_security_statistics(
    payload: Annotated[dict[str, DateRange], Field(min_length=1, max_length=5)],
    market_data_client: BaseMarketDataClient = Depends(get_market_data_client),
    market_data_cache: BaseMarketDataCache = Depends(get_market_data_cache),
) -> dict[str, SecurityStatistics]:
    market_data = await market_data_service.collect_market_data(
        market_data_client, market_data_cache, payload
    )

    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor() as executor:
        return await loop.run_in_executor(
            executor, calculation_service.calculate_security_statistics, market_data
        )
