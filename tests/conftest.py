import json
import os


def pytest_configure() -> None:
    os.environ["MARKET_DATA_CACHE_CONFIG"] = json.dumps(
        {"type": "redis", "url": "redis://fake-url"}
    )
    os.environ["MARKET_DATA_CLIENT_CONFIG"] = json.dumps(
        {"type": "tiingo", "api_key": "FAKE_API_KEY"}
    )
