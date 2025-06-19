from typing import Literal, Union

from pydantic import UUID4, BaseModel, Field

from pacifica_sdk.enums import Side, TradeCause, TradeEvent, TradeSide, WSChannel


# Prices Stream
class WSPricesItem(BaseModel):
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


class WSPricesStream(BaseModel):
    channel: Literal[WSChannel.PRICES]
    data: list[WSPricesItem]


# OrderBook Stream
class OrderBookLevel(BaseModel):
    total_amount: str = Field(..., alias="a")
    order_count: int = Field(..., alias="n")
    price: str = Field(..., alias="p")


class WSOrderBookData(BaseModel):
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    symbol: str = Field(..., alias="s")
    timestamp: int = Field(..., alias="t")


class WSOrderBookStream(BaseModel):
    channel: Literal[WSChannel.BOOK]
    data: WSOrderBookData


# Trades Stream
class WSTrade(BaseModel):
    symbol: str = Field(..., alias="s")
    side: TradeSide = Field(..., alias="d")
    amount: str = Field(..., alias="a")
    price: str = Field(..., alias="p")
    account: str = Field(..., alias="u")
    event_type: TradeEvent = Field(..., alias="e")
    cause: TradeCause = Field(..., alias="tc")
    counter_party: str = Field(..., alias="c")
    timestamp: int = Field(..., alias="t")


class WSTradesStream(BaseModel):
    channel: Literal[WSChannel.TRADES]
    data: list[WSTrade]


# Candle Stream
class WSCandleData(BaseModel):
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


class WSCandleStream(BaseModel):
    channel: Literal[WSChannel.CANDLE]
    data: WSCandleData


# Order Updates Stream
class WSOrderUpdate(BaseModel):
    order_id: int = Field(..., alias="i")
    client_order_id: UUID4 | None = Field(None, alias="I")
    account: str = Field(..., alias="u")
    symbol: str = Field(..., alias="s")
    side: Side = Field(..., alias="d")
    average_price: str = Field(..., alias="p")
    original_amount: str = Field(..., alias="o")
    filled_amount: str = Field(..., alias="f")
    cancelled_amount: str = Field(..., alias="c")
    # TODO Enums for order_event, order_type, order_status
    order_event: str = Field(..., alias="oe")
    order_type: str = Field(..., alias="ot")
    order_status: str = Field(..., alias="os")
    stop_price: str | None = Field(None, alias="sp")
    stop_parent_id: str | None = Field(None, alias="si")
    reduce_only: bool = Field(..., alias="r")
    timestamp: int = Field(..., alias="t")


class WSOrderUpdatesStream(BaseModel):
    channel: Literal[WSChannel.ORDER_UPDATES]
    data: list[WSOrderUpdate]


# Account Balance Stream
class WSAccountBalanceData(BaseModel):
    # TODO uncomment when add
    # account: str = Field(..., alias="u")
    total_balance: str = Field(..., alias="total")
    available_balance: str = Field(..., alias="available")
    locked_balance: str = Field(..., alias="locked")
    timestamp: int = Field(..., alias="t")


class WSAccountBalanceStream(BaseModel):
    channel: Literal[WSChannel.ACCOUNT_BALANCE]
    data: WSAccountBalanceData


# Account Margin Stream
class WSAccountMarginData(BaseModel):
    account: str = Field(..., alias="u")
    symbol: str = Field(..., alias="s")
    is_isolated: bool = Field(..., alias="i")
    timestamp: int = Field(..., alias="t")


class WSAccountMarginStream(BaseModel):
    channel: Literal[WSChannel.ACCOUNT_MARGIN]
    data: WSAccountMarginData


# Account Leverage Stream
class WSAccountLeverageData(BaseModel):
    account: str = Field(..., alias="u")
    symbol: str = Field(..., alias="s")
    leverage: str = Field(..., alias="l")
    timestamp: int = Field(..., alias="t")


class WSAccountLeverageStream(BaseModel):
    channel: Literal[WSChannel.ACCOUNT_LEVERAGE]
    data: WSAccountLeverageData


# Account Positions Stream
class WSAccountPosition(BaseModel):
    # TODO uncomment when add
    # account: str = Field(..., alias="u")
    symbol: str = Field(..., alias="s")
    amount: str = Field(..., alias="a")
    entry_price: str = Field(..., alias="p")
    timestamp: int = Field(..., alias="t")
    side: Side = Field(..., alias="d")
    margin: str = Field(..., alias="m")
    funding_rate: str = Field(..., alias="f")
    isolated: bool = Field(..., alias="i")


class WSAccountPositionsStream(BaseModel):
    channel: Literal[WSChannel.ACCOUNT_POSITIONS]
    data: list[WSAccountPosition]


# Account Orders Stream
class WSAccountOrder(BaseModel):
    client_order_id: UUID4 | None = Field(None, alias="I")
    initial_amount: str = Field(..., alias="a")
    cancelled_amount: str = Field(..., alias="c")
    side: Side = Field(..., alias="d")
    filled_amount: str = Field(..., alias="f")
    order_id: int = Field(..., alias="i")
    price: str = Field(..., alias="p")
    # TODO Enums for order_type
    order_type: str = Field(..., alias="ot")
    reduce_only: bool = Field(..., alias="ro")
    symbol: str = Field(..., alias="s")
    stop_price: str | None = Field(None, alias="sp")
    stop_parent_id: str | None = Field(None, alias="st")
    timestamp: int = Field(..., alias="t")


class WSAccountOrdersStream(BaseModel):
    channel: Literal[WSChannel.ACCOUNT_ORDERS]
    data: list[WSAccountOrder]


# Account Order Updates Stream
class WSAccountOrderUpdate(BaseModel):
    client_order_id: UUID4 | None = Field(None, alias="I")
    original_amount: str = Field(..., alias="a")
    created_at: int = Field(..., alias="ct")
    side: Side = Field(..., alias="d")
    filled_amount: str = Field(..., alias="f")
    order_id: int = Field(..., alias="i")
    initial_price: str = Field(..., alias="ip")
    # TODO Enums for order_event, order_type, order_status
    order_event: str = Field(..., alias="oe")
    order_status: str = Field(..., alias="os")
    order_type: str = Field(..., alias="ot")
    average_price: str = Field(..., alias="p")
    reduce_only: bool = Field(..., alias="r")
    symbol: str = Field(..., alias="s")
    stop_parent_id: str | None = Field(None, alias="si")
    stop_price: str | None = Field(None, alias="sp")
    account: str = Field(..., alias="u")
    updated_at: int = Field(..., alias="ut")


class WSAccountOrderUpdatesStream(BaseModel):
    channel: Literal[WSChannel.ACCOUNT_ORDER_UPDATES]
    data: list[WSAccountOrderUpdate]


# Account Trades Stream
class WSAccountTrade(BaseModel):
    symbol: str = Field(..., alias="s")
    side: TradeSide = Field(..., alias="ts")
    amount: str = Field(..., alias="a")
    price: str = Field(..., alias="p")
    entry_price: str = Field(..., alias="o")
    fee: str = Field(..., alias="f")
    pnl: str = Field(..., alias="n")
    account: str = Field(..., alias="u")
    order_id: int = Field(..., alias="i")
    client_order_id: UUID4 | None = Field(None, alias="I")
    event_type: TradeEvent = Field(..., alias="te")
    cause: TradeCause = Field(..., alias="tc")
    counter_party: str = Field(..., alias="c")
    timestamp: int = Field(..., alias="t")


class WSAccountTradesStream(BaseModel):
    channel: Literal[WSChannel.ACCOUNT_TRADES]
    data: list[WSAccountTrade]


WSStream = Union[
    WSCandleStream,
    WSPricesStream,
    WSTradesStream,
    WSOrderBookStream,
    WSOrderUpdatesStream,
    WSAccountMarginStream,
    WSAccountOrdersStream,
    WSAccountTradesStream,
    WSAccountBalanceStream,
    WSAccountLeverageStream,
    WSAccountPositionsStream,
    WSAccountOrderUpdatesStream,
]

CHANNEL_MODEL_MAP: dict[WSChannel, type[BaseModel]] = {
    WSChannel.PRICES: WSPricesStream,
    WSChannel.BOOK: WSOrderBookStream,
    WSChannel.TRADES: WSTradesStream,
    WSChannel.CANDLE: WSCandleStream,
    WSChannel.ORDER_UPDATES: WSOrderUpdatesStream,
    WSChannel.ACCOUNT_BALANCE: WSAccountBalanceStream,
    WSChannel.ACCOUNT_MARGIN: WSAccountMarginStream,
    WSChannel.ACCOUNT_LEVERAGE: WSAccountLeverageStream,
    WSChannel.ACCOUNT_POSITIONS: WSAccountPositionsStream,
    WSChannel.ACCOUNT_ORDERS: WSAccountOrdersStream,
    WSChannel.ACCOUNT_ORDER_UPDATES: WSAccountOrderUpdatesStream,
    WSChannel.ACCOUNT_TRADES: WSAccountTradesStream,
}
