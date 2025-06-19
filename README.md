# Pacifica SDK

**Pacifica SDK** is a Python library for interacting with the [Pacifica.fi](https://pacifica.fi) exchange API and WebSocket.  
The SDK supports asynchronous requests, convenient order management, account operations, market data retrieval, and real-time data streams.

---

## Installation

```bash
pip install pacifica-sdk
```

> **Dependencies:**  
> - Python 3.10+  
> - [aiohttp](https://pypi.org/project/aiohttp/)  
> - [pydantic](https://pypi.org/project/pydantic/)  
> - [solders](https://pypi.org/project/solders/)  
> - (optional) [orjson](https://pypi.org/project/orjson/)

---

## Quick Start

### Get Market Information

```python
import asyncio
from pacifica_sdk.async_.info import Info

async def main():
    info = Info()
    markets = await info.get_market_info()
    for market in markets:
        print(market.symbol, market.max_leverage)
    await info.close()

asyncio.run(main())
```

### Create a Limit Order

```python
import asyncio
from pacifica_sdk.async_.exchange import Exchange
from pacifica_sdk.models.requests import CreateLimitOrder, Side, TIF

PRIVATE_KEY = "YOUR_PRIVATE_KEY"

async def main():
    exchange = Exchange(private_key=PRIVATE_KEY)
    order = CreateLimitOrder(
        symbol="BTCUSDT",
        price="30000",
        amount="0.01",
        side=Side.BID,
        tif=TIF.GTC,
    )
    response = await exchange.create_order(order)
    print("Order ID:", response.data.order_id)
    await exchange.close()

asyncio.run(main())
```

### Subscribe to Price Stream via WebSocket

```python
import asyncio
from pacifica_sdk.async_.websocket_manager import WebsocketManager
from pacifica_sdk.models.ws_subscribe import WSPricesSubscribe

async def on_prices_update(data):
    print("Prices update:", data)

async def main():
    ws_manager = WebsocketManager()
    params = WSPricesSubscribe()
    await ws_manager.subscribe(params, on_prices_update)
    await asyncio.sleep(60)
    await ws_manager.close()

asyncio.run(main())
```

---

## Error Handling

The SDK raises custom exceptions:
- `ApiError` — for API errors (4xx)
- `ServerError` — for server errors (5xx)

```python
from pacifica_sdk.utils.error import ApiError, ServerError

try:
    # Your code here
    ...
except ApiError as e:
    print("API error:", e)
except ServerError as e:
    print("Server error:", e)
```

---

## Package Structure

- `pacifica_sdk.async_` — asynchronous clients (API, Exchange, Info, WebSocket)
- `pacifica_sdk.models` — Pydantic models for requests, responses, and streams
- `pacifica_sdk.utils` — utilities, error handling, message signing
- `pacifica_sdk.enums` — enums for statuses, order types, etc.
- `pacifica_sdk.constants` — constants (URLs, etc.)

---

## Documentation

- [API Reference](https://docs.pacifica.fi/api-documentation/)
- [WebSocket Reference](https://docs.pacifica.fi/api-documentation/api/websocket)

---

## Roadmap / Upcoming Features

The following features are planned for future releases:

- **Trading operations via WebSocket:**  
  Place, modify, and cancel orders in real time using the WebSocket API.

- **Comprehensive docstrings:**  
  All public classes and functions will include detailed docstrings for better developer experience and IDE support.

- **More usage examples:**  
  The documentation and repository will include more practical code samples for common SDK use cases.

- **Price and order size rounding utilities:**  
  Helper functions for correct rounding of prices and order sizes according to market requirements.

- **Synchronous client:**  
  (Planned) Support for synchronous (non-async) usage for simpler integration in legacy projects.

- **Extensive test coverage:**  
  More unit and integration tests to ensure reliability and stability.

- **Type hints and static analysis improvements:**  
  Even stricter type checking and mypy compatibility.

- **Logging in all modules:**  
  Consistent and configurable logging will be added across all SDK modules for better debugging and monitoring.

If you have feature requests or suggestions, feel free to open an issue or contact us!

---

## License

MIT License

---

## Contacts

- Telegram: [@hedgehog](https://t.me/thehhog)

---

> Pull requests and bug reports are welcome!
