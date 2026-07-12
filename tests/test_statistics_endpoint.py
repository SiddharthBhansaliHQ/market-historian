from datetime import date
from typing import Iterator
from unittest.mock import AsyncMock, call

import helpers
import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from main import app, get_market_data_cache, get_market_data_client
from models.date_range import DateRange
from models.market_data_unit import MarketDataUnit
from services import calculation_service


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as tc:
        yield tc


@pytest.fixture
def mock_market_data_client() -> Iterator[AsyncMock]:
    async def mock_fetch(symbol: str, date_range: DateRange) -> list[MarketDataUnit]:
        return helpers.generate_mock_market_data(date_range)

    mock = AsyncMock()
    mock.fetch = AsyncMock(side_effect=mock_fetch)
    app.dependency_overrides[get_market_data_client] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


@pytest.fixture
def mock_market_data_cache() -> Iterator[AsyncMock]:
    async def mock_get(
        symbol: str, date_range: DateRange
    ) -> list[MarketDataUnit] | None:
        if date_range.start_date.year == 2000 and date_range.end_date.year == 2000:
            return helpers.generate_mock_market_data(date_range)
        else:
            return None

    async def mock_set(
        symbol: str, date_range: DateRange, value: list[MarketDataUnit]
    ) -> None: ...

    mock = AsyncMock()
    mock.get = AsyncMock(side_effect=mock_get)
    mock.set = AsyncMock(side_effect=mock_set)
    app.dependency_overrides[get_market_data_cache] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


def test_payload_max_size_happy_path(
    client: TestClient,
    mock_market_data_cache: AsyncMock,
    mock_market_data_client: AsyncMock,
) -> None:
    response = client.post(
        "/statistics",
        json={
            "1": {"start_date": "1000-01-01", "end_date": "1000-01-10"},
            "2": {"start_date": "2000-01-01", "end_date": "2000-01-10"},
            "3": {"start_date": "1000-01-01", "end_date": "1000-01-10"},
            "4": {"start_date": "2000-01-01", "end_date": "2000-01-10"},
            "5": {"start_date": "1000-01-01", "end_date": "1000-01-10"},
        },
    )

    assert response.status_code == 200
    assert response.json() == jsonable_encoder(
        calculation_service.calculate_security_statistics(
            {
                "1": helpers.generate_mock_market_data(
                    DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10))
                ),
                "2": helpers.generate_mock_market_data(
                    DateRange(start_date=date(2000, 1, 1), end_date=date(2000, 1, 10))
                ),
                "3": helpers.generate_mock_market_data(
                    DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10))
                ),
                "4": helpers.generate_mock_market_data(
                    DateRange(start_date=date(2000, 1, 1), end_date=date(2000, 1, 10))
                ),
                "5": helpers.generate_mock_market_data(
                    DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10))
                ),
            }
        )
    )

    assert mock_market_data_cache.get.await_count == 5
    mock_market_data_cache.get.assert_has_awaits(
        [
            call(
                "1", DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10))
            ),
            call(
                "2", DateRange(start_date=date(2000, 1, 1), end_date=date(2000, 1, 10))
            ),
            call(
                "3", DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10))
            ),
            call(
                "4", DateRange(start_date=date(2000, 1, 1), end_date=date(2000, 1, 10))
            ),
            call(
                "5", DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10))
            ),
        ]
    )

    assert mock_market_data_client.fetch.await_count == 3
    mock_market_data_client.fetch.assert_has_awaits(
        [
            call(
                "1", DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10))
            ),
            call(
                "3", DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10))
            ),
            call(
                "5", DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10))
            ),
        ]
    )

    assert mock_market_data_cache.set.await_count == 3
    mock_market_data_cache.set.assert_has_awaits(
        [
            call(
                "1",
                DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10)),
                helpers.generate_mock_market_data(
                    DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10))
                ),
            ),
            call(
                "3",
                DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10)),
                helpers.generate_mock_market_data(
                    DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10))
                ),
            ),
            call(
                "5",
                DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10)),
                helpers.generate_mock_market_data(
                    DateRange(start_date=date(1000, 1, 1), end_date=date(1000, 1, 10))
                ),
            ),
        ]
    )


def test_payload_min_size_happy_path(
    client: TestClient,
    mock_market_data_cache: AsyncMock,
    mock_market_data_client: AsyncMock,
) -> None:
    response = client.post(
        "/statistics",
        json={"1": {"start_date": "1000-01-01", "end_date": "1000-01-10"}},
    )

    assert response.status_code == 200


def test_payload_too_large(client: TestClient) -> None:
    response = client.post(
        "/statistics",
        json={
            "1": {"start_date": "1000-01-01", "end_date": "2000-01-01"},
            "2": {"start_date": "1000-01-01", "end_date": "2000-01-01"},
            "3": {"start_date": "1000-01-01", "end_date": "2000-01-01"},
            "4": {"start_date": "1000-01-01", "end_date": "2000-01-01"},
            "5": {"start_date": "1000-01-01", "end_date": "2000-01-01"},
            "6": {"start_date": "1000-01-01", "end_date": "2000-01-01"},
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "too_long"
    assert response.json()["detail"][0]["loc"][0] == "body"


def test_payload_too_small(client: TestClient) -> None:
    response = client.post(
        "/statistics",
        json={},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "too_short"
    assert response.json()["detail"][0]["loc"][0] == "body"


def test_no_payload(client: TestClient) -> None:
    response = client.post("/statistics")

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "missing"
    assert response.json()["detail"][0]["loc"][0] == "body"


def test_payload_missing_dates(client: TestClient) -> None:
    response = client.post(
        "/statistics",
        json={
            "1": {"start_date": "1000-01-01"},
            "2": {"end_date": "2000-01-01"},
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "missing"
    assert response.json()["detail"][0]["loc"][2] == "end_date"
    assert response.json()["detail"][1]["type"] == "missing"
    assert response.json()["detail"][1]["loc"][2] == "start_date"


def test_payload_blank_symbol(client: TestClient) -> None:
    response = client.post(
        "/statistics",
        json={
            "": {"start_date": "1000-01-01", "end_date": "2000-01-01"},
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "string_too_short"
