import logging

from pacifica_sdk.async_.api import AsyncHttpClient
from pacifica_sdk.constants import MAINNET_API_URL
from pacifica_sdk.models.requests import (
    GetAccountEquityHistory,
    GetAccountFundingHistory,
    GetAccountInfo,
    GetAccountPositions,
    GetAccountSettings,
    GetAccountTradeHistory,
    GetCandleData,
    GetOpenOrders,
    GetOrderHistory,
    GetOrderHistoryById,
    GetRecentTrades,
)
from pacifica_sdk.models.responses import (
    AccountEquityHistoryItem,
    AccountFundingHistoryItem,
    AccountInfo,
    AccountSettings,
    AccountTradeHistoryItem,
    ApiResponse,
    CandleInfo,
    MarketInfo,
    OpenOrderInfo,
    OrderHistoryByIdItem,
    OrderHistoryItem,
    PositionInfo,
    PriceInfo,
    TradeInfo,
)

logger = logging.getLogger("pacifica_sdk.info")


class Info(AsyncHttpClient):
    def __init__(
        self,
        public_key: str | None = None,
        base_url: str = MAINNET_API_URL,
        skip_ws: bool = False,
    ):
        super().__init__(public_key=public_key, base_url=base_url)

    async def get_market_info(self) -> list[MarketInfo]:
        res = await self._send_request("GET", "/info", response_model=ApiResponse[list[MarketInfo]])
        return res.data

    async def get_prices(self) -> list[PriceInfo]:
        res = await self._send_request("GET", "/info/prices", response_model=ApiResponse[list[PriceInfo]])
        return res.data

    async def get_candle_data(self, params: GetCandleData) -> list[CandleInfo]:
        res = await self._send_request(
            "GET",
            "/kline",
            params=params.model_dump(exclude_none=True),
            response_model=ApiResponse[list[CandleInfo]],
        )
        return res.data

    async def get_recent_trades(self, params: GetRecentTrades) -> list[TradeInfo]:
        res = await self._send_request(
            "GET",
            "/trades",
            params=params.model_dump(exclude_none=True),
            response_model=ApiResponse[list[TradeInfo]],
        )
        return res.data

    async def get_account_info(self, params: GetAccountInfo) -> AccountInfo:
        res = await self._send_request(
            "GET",
            "/account",
            params=params.model_dump(exclude_none=True),
            response_model=ApiResponse[AccountInfo],
        )
        return res.data

    async def get_account_settings(self, params: GetAccountSettings) -> list[AccountSettings]:
        res = await self._send_request(
            "GET",
            "/account/settings",
            params=params.model_dump(exclude_none=True),
            response_model=ApiResponse[list[AccountSettings]],
        )
        return res.data

    async def get_account_positions(self, params: GetAccountPositions) -> list[PositionInfo]:
        res = await self._send_request(
            "GET",
            "/positions",
            params=params.model_dump(exclude_none=True),
            response_model=ApiResponse[list[PositionInfo]],
        )
        return res.data

    async def get_account_trade_history(self, params: GetAccountTradeHistory) -> list[AccountTradeHistoryItem]:
        res = await self._send_request(
            "GET",
            "/positions/history",
            params=params.model_dump(exclude_none=True),
            response_model=ApiResponse[list[AccountTradeHistoryItem]],
        )
        return res.data

    async def get_account_funding_history(self, params: GetAccountFundingHistory) -> list[AccountFundingHistoryItem]:
        res = await self._send_request(
            "GET",
            "/funding/history",
            params=params.model_dump(exclude_none=True),
            response_model=ApiResponse[list[AccountFundingHistoryItem]],
        )
        return res.data

    async def get_account_equity_history(self, params: GetAccountEquityHistory) -> list[AccountEquityHistoryItem]:
        res = await self._send_request(
            "GET",
            "/portfolio",
            params=params.model_dump(exclude_none=True),
            response_model=ApiResponse[list[AccountEquityHistoryItem]],
        )
        return res.data

    async def get_open_orders(self, params: GetOpenOrders) -> list[OpenOrderInfo]:
        res = await self._send_request(
            "GET",
            "/orders",
            params=params.model_dump(exclude_none=True),
            response_model=ApiResponse[list[OpenOrderInfo]],
        )
        return res.data

    async def get_order_history(self, params: GetOrderHistory) -> list[OrderHistoryItem]:
        res = await self._send_request(
            "GET",
            "/orders/history",
            params=params.model_dump(exclude_none=True),
            response_model=ApiResponse[list[OrderHistoryItem]],
        )
        return res.data

    async def get_order_history_by_id(self, params: GetOrderHistoryById) -> list[OrderHistoryByIdItem]:
        res = await self._send_request(
            "GET",
            "/orders/history_by_id",
            params=params.model_dump(exclude_none=True),
            response_model=ApiResponse[list[OrderHistoryByIdItem]],
        )
        return res.data
