import logging

from solders.keypair import Keypair

from pacifica_sdk.async_.api import AsyncHttpClient
from pacifica_sdk.async_.info import Info
from pacifica_sdk.constants import MAINNET_API_URL
from pacifica_sdk.enums import ActionType, OperationType, Side
from pacifica_sdk.models.requests import (
    BatchOrder,
    CancelAllOrders,
    CancelOrder,
    CreateLimitOrder,
    CreateMarketOrder,
    CreateStopOrder,
    CreateTPSLOrder,
    RequestWithdraw,
    UpdateLeverage,
    UpdateMarginMode,
)
from pacifica_sdk.models.responses import (
    ApiResponse,
    BatchOrderResponse,
    CancelAllResponse,
    CreateOrderResponse,
)
from pacifica_sdk.utils.signing import sign_message
from pacifica_sdk.utils.tools import get_timestamp_ms, round_price

logger = logging.getLogger("pacifica_sdk.exchange")


class Exchange(AsyncHttpClient):
    def __init__(
        self,
        private_key: str,
        public_key: str | None = None,
        agent_wallet: str | None = None,
        base_url: str = MAINNET_API_URL,
        expiry_window: int = 30_000,
    ):
        super().__init__(private_key, public_key, agent_wallet, base_url, expiry_window)
        self.info = Info(public_key, base_url, skip_ws=True)

    def _slippage_price(self, price: str, side: Side, slippage: float):
        price = float(price)
        return round_price(price * (1 + slippage) if side == Side.BID else price * (1 - slippage))

    async def create_order(self, order: CreateLimitOrder | CreateMarketOrder) -> ApiResponse[CreateOrderResponse]:
        if isinstance(order, CreateLimitOrder):
            payload = order.model_dump(exclude_none=True)
        elif isinstance(order, CreateMarketOrder):
            order.price = self._slippage_price(order.price, order.side, order.slippage)
        return await self._send_request(
            method="POST",
            endpoint="/orders/create",
            operation_type=OperationType.CREATE_ORDER,
            params=payload,
            response_model=ApiResponse[CreateOrderResponse],
        )

    async def create_stop_order(self, order: CreateStopOrder) -> ApiResponse[CreateOrderResponse]:
        payload = order.model_dump(exclude_none=True)
        return await self._send_request(
            method="POST",
            endpoint="/orders/stop/create",
            operation_type=OperationType.CREATE_STOP_ORDER,
            params=payload,
            response_model=ApiResponse[CreateOrderResponse],
        )

    async def create_position_tp_sl(self, position: CreateTPSLOrder) -> ApiResponse[None]:
        payload = position.model_dump(exclude_none=True)
        return await self._send_request(
            method="POST",
            endpoint="/orders/positions/tpsl",
            operation_type=OperationType.SET_POSITION_TPSL,
            params=payload,
            response_model=ApiResponse[None],
        )

    async def cancel_order(self, cancel: CancelOrder) -> ApiResponse[None]:
        payload = cancel.model_dump(exclude_none=True)
        return await self._send_request(
            method="POST",
            endpoint="/orders/cancel",
            operation_type=OperationType.CANCEL_ORDER,
            params=payload,
            response_model=ApiResponse[None],
        )

    async def cancel_all_orders(self, cancel: CancelAllOrders) -> ApiResponse[CancelAllResponse]:
        payload = cancel.model_dump(exclude_none=True)
        return await self._send_request(
            method="POST",
            endpoint="/orders/cancel_all",
            operation_type=OperationType.CANCEL_ALL_ORDERS,
            params=payload,
            response_model=ApiResponse[CancelAllResponse],
        )

    async def cancel_stop_order(self, cancel: CancelOrder):
        payload = cancel.model_dump(exclude_none=True)
        return await self._send_request(
            method="POST",
            endpoint="/orders/stop/cancel",
            operation_type=OperationType.CANCEL_STOP_ORDER,
            params=payload,
            response_model=ApiResponse[None],
        )

    async def batch_order(self, batch: BatchOrder) -> ApiResponse[BatchOrderResponse]:
        payload = {"actions": []}
        for action in batch.actions:
            if isinstance(action, CancelOrder):
                type = ActionType.CANCEL
                operation_type = OperationType.CANCEL_ORDER
            else:
                type = ActionType.CREATE
                operation_type = OperationType.CREATE_ORDER
                if isinstance(action, CreateMarketOrder):
                    action.price = self._slippage_price(action.price, action.side, action.slippage)
            payload["actions"].append(
                {
                    "operation_type": operation_type,
                    "type": type,
                    "data": action.model_dump(exclude_none=True),
                }
            )
        return await self._send_request(
            method="POST",
            endpoint="/orders/batch",
            operation_type=OperationType.BATCH_ORDER,
            params=payload,
            response_model=ApiResponse[BatchOrderResponse],
        )

    async def update_leverage(self, update: UpdateLeverage) -> ApiResponse[None]:
        payload = update.model_dump(exclude_none=True)
        return await self._send_request(
            method="POST",
            endpoint="/account/leverage",
            operation_type=OperationType.UPDATE_LEVERAGE,
            params=payload,
            response_model=ApiResponse[None],
        )

    async def update_margin_mode(self, update: UpdateMarginMode) -> ApiResponse[None]:
        payload = update.model_dump(exclude_none=True)
        return await self._send_request(
            method="POST",
            endpoint="/account/margin",
            operation_type=OperationType.UPDATE_MARGIN_MODE,
            params=payload,
            response_model=ApiResponse[None],
        )

    async def request_withdrawal(self, request: RequestWithdraw) -> ApiResponse[None]:
        payload = request.model_dump(exclude_none=True)
        return await self._send_request(
            method="POST",
            endpoint="/account/withdraw",
            operation_type=OperationType.WITHDRAW,
            params=payload,
            response_model=ApiResponse[None],
        )

    async def create_subaccount(self, sub_private_key: str) -> ApiResponse[None]:
        timestamp = get_timestamp_ms()

        main_keypair = self.keypair
        sub_keypair = Keypair.from_base58_string(sub_private_key)

        main_public_key = self.public_key
        sub_public_key = str(sub_keypair.pubkey())

        sub_signature = sign_message(
            keypair=sub_keypair,
            timestamp=timestamp,
            operation_type=OperationType.SUBACCOUNT_INITIATE,
            operation_data={"account": main_public_key},
            expiry_window=self.expiry_window,
        )

        main_signature = sign_message(
            keypair=main_keypair,
            timestamp=timestamp,
            operation_type=OperationType.SUBACCOUNT_CONFIRM,
            operation_data={"signature": sub_signature},
            expiry_window=self.expiry_window,
        )

        body = {
            "main_account": main_public_key,
            "subaccount": sub_public_key,
            "main_signature": main_signature,
            "sub_signature": sub_signature,
            "timestamp": timestamp,
            "expiry_window": self.expiry_window,
        }

        return await self._send_request(
            method="POST",
            endpoint="/account/subaccount/create",
            params=body,
            response_model=ApiResponse[None],
        )

    async def subaccount_fund_transfer(self):
        # TODO
        pass

    async def close(self):
        await self.info.close()
        await self.session.close()
