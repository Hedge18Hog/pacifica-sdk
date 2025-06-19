from typing import Literal

from pydantic import UUID4, BaseModel, ConfigDict, model_validator

from pacifica_sdk.enums import TIF, CandleInterval, Side


class _BaseRequest(BaseModel):
    model_config = ConfigDict(
        json_encoders={UUID4: lambda u: str(u)},
    )


# -----------------------------------------------
# --------------- INFO MODELS -------------------
# -----------------------------------------------
class GetCandleData(_BaseRequest):
    symbol: str
    interval: CandleInterval
    start_time: int
    end_time: int | None = None


class GetRecentTrades(_BaseRequest):
    symbol: str


class GetAccountInfo(_BaseRequest):
    account: str


class GetAccountSettings(_BaseRequest):
    account: str


class GetAccountPositions(_BaseRequest):
    account: str


class GetAccountTradeHistory(_BaseRequest):
    account: str
    symbol: str | None = None
    start_time: int | None = None
    end_time: int | None = None
    limit: int | None = None
    offset: int | None = None


class GetAccountFundingHistory(_BaseRequest):
    account: str
    limit: int | None = None
    offset: int | None = None


class GetAccountEquityHistory(_BaseRequest):
    account: str
    start_time: int | None = None
    end_time: int | None = None
    granularity_in_minutes: int | None = None
    limit: int | None = None
    offset: int | None = None


class GetOpenOrders(_BaseRequest):
    account: str


class GetOrderHistory(_BaseRequest):
    account: str
    limit: int | None = None
    offset: int | None = None


class GetOrderHistoryById(_BaseRequest):
    order_id: int


# -----------------------------------------------
# --------------- EXCHANGE MODELS ---------------
# -----------------------------------------------
class StopOrderInfo(_BaseRequest):
    stop_price: str
    limit_price: str | None = None
    client_order_id: UUID4 | None = None


class _BaseCreateOrder(_BaseRequest):
    symbol: str
    price: str
    amount: str
    side: Side
    tif: TIF
    reduce_only: bool = False
    client_order_id: UUID4 | None = None
    take_profit: StopOrderInfo | None = None
    stop_loss: StopOrderInfo | None = None


class CreateLimitOrder(_BaseCreateOrder):
    pass


class CreateMarketOrder(_BaseCreateOrder):
    price: str
    tif: Literal[TIF.IOC] = TIF.IOC
    slippage: float = 0.05


class CreateStopOrder(_BaseRequest):
    symbol: str
    side: Side
    reduce_only: bool
    stop_order: StopOrderInfo
    amount: str


class CreateTPSLOrder(_BaseRequest):
    symbol: str
    side: Side
    take_profit: StopOrderInfo | None = None
    stop_loss: StopOrderInfo | None = None

    @model_validator(mode="before")
    def at_least_one_stop(cls, values):
        if not values.get("take_profit") and not values.get("stop_loss"):
            raise ValueError("At least one of 'take_profit' or 'stop_loss' must be provided.")
        return values


class CancelOrder(_BaseRequest):
    symbol: str
    order_id: int | None = None
    client_order_id: UUID4 | None = None

    @model_validator(mode="before")
    def check_order_ids(cls, values):
        order_id = values.get("order_id")
        client_order_id = values.get("client_order_id")
        if order_id is None and client_order_id is None:
            raise ValueError("Either 'order_id' or 'client_order_id' must be provided.")
        return values


class CancelAllOrders(_BaseRequest):
    all_symbols: bool
    exclude_reduce_only: bool
    symbol: str | None = None

    @model_validator(mode="before")
    def check_symbol_required(cls, values):
        all_symbols = values.get("all_symbols")
        symbol = values.get("symbol")
        if not all_symbols and not symbol:
            raise ValueError("Field 'symbol' is required when 'all_symbols' is False.")
        return values


class BatchOrder(_BaseRequest):
    actions: list[CreateLimitOrder | CreateMarketOrder | CancelOrder]


class UpdateLeverage(BaseModel):
    symbol: str
    leverage: int


class UpdateMarginMode(BaseModel):
    symbol: str
    is_isolated: bool


class RequestWithdraw(BaseModel):
    amount: str
