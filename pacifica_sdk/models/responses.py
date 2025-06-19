from typing import Generic, TypeVar

from pydantic import UUID4, BaseModel, Field

from pacifica_sdk.enums import (
    OrderEvent,
    OrderStatus,
    OrderType,
    Side,
    TradeCause,
    TradeEvent,
    TradeSide,
)

T = TypeVar("T", bound=BaseModel)


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: str | None = None
    code: int | None = None


# Public REST API responses
class MarketInfo(BaseModel):
    symbol: str
    tick_size: str
    min_tick: str
    max_tick: str
    lot_size: str
    max_leverage: int
    isolated_only: bool
    min_order_size: str
    max_order_size: str
    funding_rate: str
    next_funding_rate: str


class PriceInfo(BaseModel):
    # TODO: Check model
    funding: str
    mark: str
    mid: str
    next_funding: str
    open_interest: str
    oracle: str
    symbol: str
    timestamp: int
    volume_24h: str
    yesterday_price: str


# Candle Stream
class CandleInfo(BaseModel):
    start_time: int = Field(..., alias="t")
    end_time: int = Field(..., alias="T")
    symbol: str = Field(..., alias="s")
    interval: str = Field(..., alias="i")
    open_price: str = Field(..., alias="o")
    close_price: str = Field(..., alias="c")
    high_price: str = Field(..., alias="h")
    low_price: str = Field(..., alias="l")
    volume: str = Field(..., alias="v")
    trade_count: int = Field(..., alias="n")


class TradeInfo(BaseModel):
    side: TradeSide
    amount: str
    price: str
    event_type: TradeEvent
    cause: TradeCause
    created_at: int


class AccountInfo(BaseModel):
    balance: str
    fee_level: int
    account_equity: str
    available_to_spend: str
    pending_balance: str
    total_margin_used: str
    positions_count: int
    orders_count: int
    stop_orders_count: int
    updated_at: int


class AccountSettings(BaseModel):
    symbol: str
    isolated: bool
    leverage: int
    created_at: int
    updated_at: int


class PositionInfo(BaseModel):
    symbol: str
    side: Side
    amount: str
    entry_price: str
    margin: str | None = None
    funding: str
    isolated: bool
    created_at: int
    updated_at: int


class AccountTradeHistoryItem(BaseModel):
    symbol: str
    side: TradeSide
    amount: str
    price: str
    entry_price: str
    fee: str
    pnl: str
    history_id: int
    order_id: int
    client_order_id: UUID4 | None = None
    event_type: TradeEvent
    cause: TradeCause
    counter_party: str
    created_at: int


class AccountFundingHistoryItem(BaseModel):
    symbol: str
    side: Side
    amount: str
    payout: str
    rate: str
    history_id: int
    created_at: int


class AccountEquityHistoryItem(BaseModel):
    account_equity: str
    timestamp: int


class OpenOrderInfo(BaseModel):
    order_id: int
    client_order_id: UUID4 | None
    symbol: str
    side: str
    price: str
    initial_amount: str
    filled_amount: str
    cancelled_amount: str
    stop_price: str | None
    order_type: OrderType
    stop_parent_order_id: int | None
    reduce_only: bool
    created_at: int
    updated_at: int


class OrderHistoryItem(BaseModel):
    order_id: int
    client_order_id: UUID4 | None
    symbol: str
    side: str
    initial_price: str
    average_filled_price: str
    amount: str
    filled_amount: str
    order_status: OrderStatus
    order_type: str
    stop_price: str | None
    stop_parent_order_id: int | None
    reduce_only: bool
    reason: str | None
    created_at: int
    updated_at: int


class OrderHistoryByIdItem(BaseModel):
    history_id: int
    order_id: int
    client_order_id: UUID4 | None
    symbol: str
    side: str
    price: str
    initial_amount: str
    filled_amount: str
    cancelled_amount: str
    # TODO replace to OrderEvent
    event_type: str
    order_type: OrderType
    order_status: OrderStatus
    stop_price: str | None
    stop_parent_order_id: int | None
    reduce_only: bool
    created_at: int


class CreateOrderResponse(BaseModel):
    order_id: int


class CancelAllResponse(BaseModel):
    cancelled_count: int


class BatchActionResult(BaseModel):
    success: bool
    order_id: int | None = None
    error: str | None = None


class BatchOrderResponse(BaseModel):
    results: list[BatchActionResult]
