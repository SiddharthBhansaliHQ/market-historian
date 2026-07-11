import logging
from datetime import datetime
from typing import override

import aiohttp
from fastapi import HTTPException

from clients.base_market_data_client import BaseMarketDataClient
from models.date_range import DateRange
from models.market_data_unit import MarketDataUnit

logger = logging.getLogger(__name__)


class TiingoMarketDataClient(BaseMarketDataClient):
    def __init__(self, http_client: aiohttp.ClientSession, api_key: str) -> None:
        self._http_client = http_client
        self._api_key = api_key

    @override
    async def fetch(self, symbol: str, date_range: DateRange) -> list[MarketDataUnit]:
        symbol_market_data = []
        url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self._api_key}",
        }

        params = {
            "startDate": str(date_range.start_date),
            "endDate": str(date_range.end_date),
        }

        try:
            async with self._http_client.get(
                url, headers=headers, params=params
            ) as response:
                response.raise_for_status()

                for response_unit in await response.json():
                    symbol_market_data.append(
                        MarketDataUnit(
                            reference_date=datetime.fromisoformat(
                                response_unit["date"]
                            ),
                            adjusted_close=response_unit["adjClose"],
                        )
                    )

                return symbol_market_data
        except aiohttp.ClientError as e:
            logger.exception("Tiingo API call failed.")
            status_code = getattr(e, "status", None)

            if status_code in [400, 404]:
                raise HTTPException(
                    status_code=400, detail="Invalid security symbol(s) and/or date(s)."
                )
            elif status_code == 429:
                raise HTTPException(
                    status_code=429, detail="Rate limited. Try again later."
                )
            else:
                raise

    @override
    async def close(self) -> None:
        await self._http_client.close()
