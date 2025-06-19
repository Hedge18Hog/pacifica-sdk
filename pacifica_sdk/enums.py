from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class OperationType(StrEnum):
    CREATE_ORDER = "create_order"
    CREATE_STOP_ORDER = "create_stop_order"
    CANCEL_ORDER = "cancel_order"
    CANCEL_ALL_ORDERS = "cancel_all_orders"
    CANCEL_STOP_ORDER = "cancel_stop_order"
    UPDATE_LEVERAGE = "update_leverage"
    UPDATE_MARGIN_MODE = "update_margin_mode"
    SET_POSITION_TPSL = "set_position_tpsl"
    WITHDRAW = "withdraw"
    SUBACCOUNT_INITIATE = "subaccount_initiate"
    SUBACCOUNT_CONFIRM = "subaccount_confirm"
    BATCH_ORDER = "batch_order"


class OrderType(StrEnum):
    LIMIT = "limit"
    MARKET = "market"
    STOP_LIMIT = "stop_limit"
    STOP_MARKET = "stop_market"
    TAKE_PROFIT_LIMIT = "take_profit_limit"
    STOP_LOSS_LIMIT = "stop_loss_limit"
    TAKE_PROFIT_MARKET = "take_profit_market"
    STOP_LOSS_MARKET = "stop_loss_market"


class OrderStatus(StrEnum):
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderEvent(StrEnum):
    # TODO
    pass


class ActionType(StrEnum):
    CREATE = "Create"
    CANCEL = "Cancel"


class TIF(StrEnum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    PO = "PO"


class Side(StrEnum):
    BID = "bid"
    ASK = "ask"


class TradeSide(StrEnum):
    OPEN_LONG = "open_long"
    OPEN_SHORT = "open_short"
    CLOSE_LONG = "close_long"
    CLOSE_SHORT = "close_short"


class TradeEvent(StrEnum):
    FULFILL_TAKER = "fulfill_taker"
    FULFILL_MAKER = "fulfill_maker"


class TradeCause(StrEnum):
    NORMAL = "normal"
    MARKET_LIQUIDATION = "market_liquidation"
    BACKSTOP_LIQUIDATION = "backstop_liquidation"
    SETTLEMENT = "settlement"


class WSChannel(StrEnum):
    # Market data
    PRICES = "prices"
    BOOK = "book"
    TRADES = "trades"
    CANDLE = "candle"

    # Order-related
    ORDER_UPDATES = "order_updates"

    # Account-related
    ACCOUNT_BALANCE = "account_balance"
    ACCOUNT_MARGIN = "account_margin"
    ACCOUNT_LEVERAGE = "account_leverage"
    ACCOUNT_POSITIONS = "account_positions"
    ACCOUNT_ORDERS = "account_orders"
    ACCOUNT_ORDER_UPDATES = "account_order_updates"
    ACCOUNT_TRADES = "account_trades"


class CandleInterval(StrEnum):
    MIN_1 = "1m"
    MIN_3 = "3m"
    MIN_5 = "5m"
    MIN_15 = "15m"
    MIN_30 = "30m"
    HOUR_1 = "1h"
    HOUR_2 = "2h"
    HOUR_4 = "4h"
    HOUR_8 = "8h"
    HOUR_12 = "12h"
    DAY_1 = "1d"
