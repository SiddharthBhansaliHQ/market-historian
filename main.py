import asyncio
import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from datetime import date
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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app.state.settings = config.Settings()
    app.state.process_pool_executor = ProcessPoolExecutor(
        mp_context=multiprocessing.get_context("spawn")
    )

    app.state.market_data_cache = (
        await factories.market_data_factory.create_market_data_cache(
            app.state.settings.market_data_cache_config
        )
    )
    app.state.market_data_client = (
        await factories.market_data_factory.create_market_data_client(
            app.state.settings.market_data_client_config
        )
    )

    yield

    app.state.process_pool_executor.shutdown(wait=True)
    await app.state.market_data_cache.close()
    await app.state.market_data_client.close()


app = FastAPI(
    lifespan=lifespan,
    docs_url="/",
    title="Market Historian",
)


def get_market_data_cache() -> BaseMarketDataCache:
    return app.state.market_data_cache


def get_market_data_client() -> BaseMarketDataClient:
    return app.state.market_data_client


@app.post("/statistics")
async def compute_security_statistics(
    payload: Annotated[
        dict[Annotated[str, Field(min_length=1)], DateRange],
        Field(
            min_length=1,
            max_length=5,
            examples=[
                {
                    "NVDA": DateRange(
                        start_date=date(2020, 2, 28), end_date=date(2026, 4, 17)
                    ),
                    "TSLA": DateRange(
                        start_date=date(2016, 7, 14), end_date=date(2022, 3, 1)
                    ),
                    "VTI": DateRange(
                        start_date=date(2002, 12, 2), end_date=date(2019, 6, 25)
                    ),
                    "SPY": DateRange(
                        start_date=date(2010, 8, 9), end_date=date(2017, 11, 13)
                    ),
                }
            ],
        ),
    ],
    market_data_client: BaseMarketDataClient = Depends(get_market_data_client),
    market_data_cache: BaseMarketDataCache = Depends(get_market_data_cache),
) -> dict[str, SecurityStatistics]:
    market_data = await market_data_service.collect_market_data(
        market_data_client, market_data_cache, payload
    )

    return await asyncio.get_running_loop().run_in_executor(
        app.state.process_pool_executor,
        calculation_service.calculate_security_statistics,
        market_data,
    )
