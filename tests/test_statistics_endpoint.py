from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as tc:
        yield tc


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
