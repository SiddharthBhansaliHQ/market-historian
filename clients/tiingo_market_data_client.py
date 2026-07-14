import logging
from datetime import datetime
from typing import override

import httpx2
from fastapi import HTTPException

from clients.base_market_data_client import BaseMarketDataClient
from models.date_range import DateRange
from models.market_data_unit import MarketDataUnit

logger = logging.getLogger(__name__)


class TiingoMarketDataClient(BaseMarketDataClient):
    def __init__(self, http_client_async: httpx2.AsyncClient, api_key: str) -> None:
        self._http_client_async = http_client_async
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
            response = await self._http_client_async.get(
                url, headers=headers, params=params
            )

            response.raise_for_status()

            for response_unit in response.json():
                symbol_market_data.append(
                    MarketDataUnit(
                        reference_date=datetime.fromisoformat(response_unit["date"]),
                        adjusted_close=response_unit["adjClose"],
                    )
                )
        except httpx2.HTTPStatusError as e:
            logger.exception("Tiingo API call failed.")
            status_code = e.response.status_code

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

        return symbol_market_data
