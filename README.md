# Market Historian

Market Historian is a FastAPI-based financial analytics microservice. It consumes a map of security symbols to date ranges and returns detailed statistics for each security over its corresponding date range.

# Demo

There is a live version of the microservice deployed to GCP Cloud Run at the below link. You can find a Swagger page here; it has default inputs on the `/statistics` endpoint. Note it may take a few seconds to load if a cold start happens.

[https://market-historian-498335171508.us-central1.run.app](https://market-historian-498335171508.us-central1.run.app)

# Key Features

- Currently outputs: `rate_of_return`, `annualized_log_rate_of_return`, `annualized_log_volatility`, `annualized_log_sharpe_ratio_rf_zero` for each security
- Concurrent market data API calls + caching
- Abstraction layers for market data providers and caches
    - Currently supports Tiingo for market data and Redis for caching
- Lightweight FastAPI architecture with minimal dependencies
- Dockerfile included for portability between platforms

# Configuration/Running

In order to run your own instance of Market Historian, you must first point it at a market data provider and a cache. You can take a look at `factories/market_data_factory.py` and `config.py` to see how to configure your environment variables. Here is an example of environment variables using Tiingo as the market data provider and Redis as the cache:

`MARKET_DATA_CACHE_CONFIG={"type":"redis", "url":"redis://fake-url"}`

`MARKET_DATA_CLIENT_CONFIG={"type":"tiingo", "api_key":"FAKE_API_KEY"}`

Once you have your environment variables figured out, you can run it either using the Dockerfile, or by just using the provided `run_local.sh` script. The Dockerfile can also be used for easy cloud deployments.

NOTE: This was developed on Python 3.13 and has only been tested on Python 3.13.
