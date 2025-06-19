from typing import Literal, Union

from pydantic import BaseModel

from pacifica_sdk.enums import CandleInterval, WSChannel


class WSPricesSubscribe(BaseModel):
    source: Literal[WSChannel.PRICES] = WSChannel.PRICES


class WSBookSubscribe(BaseModel):
    source: Literal[WSChannel.BOOK] = WSChannel.BOOK
    symbol: str
    agg_level: int


class WSTradesSubscribe(BaseModel):
    source: Literal[WSChannel.TRADES] = WSChannel.TRADES
    symbol: str


class WSCandleSubscribe(BaseModel):
    source: Literal[WSChannel.CANDLE] = WSChannel.CANDLE
    symbol: str
    interval: CandleInterval


class WSOrderUpdatesSubscribe(BaseModel):
    source: Literal[WSChannel.ORDER_UPDATES] = WSChannel.ORDER_UPDATES
    order_id: int


class WSAccountFieldSubscribe(BaseModel):
    source: Literal[
        WSChannel.ACCOUNT_BALANCE,
        WSChannel.ACCOUNT_MARGIN,
        WSChannel.ACCOUNT_LEVERAGE,
        WSChannel.ACCOUNT_POSITIONS,
        WSChannel.ACCOUNT_ORDERS,
        WSChannel.ACCOUNT_ORDER_UPDATES,
        WSChannel.ACCOUNT_TRADES,
    ]
    account: str


SubscribeParams = Union[
    WSPricesSubscribe,
    WSBookSubscribe,
    WSTradesSubscribe,
    WSCandleSubscribe,
    WSOrderUpdatesSubscribe,
    WSAccountFieldSubscribe,
]


class WSSubscribeRequest(BaseModel):
    method: Literal["subscribe"] = "subscribe"
    params: SubscribeParams


class WSUnsubscribeRequest(BaseModel):
    method: Literal["unsubscribe"] = "unsubscribe"
    params: SubscribeParams
