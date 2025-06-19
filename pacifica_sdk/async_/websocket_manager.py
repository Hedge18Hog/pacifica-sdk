import asyncio
import json
import logging
from collections import defaultdict

import aiohttp

from pacifica_sdk.constants import MAINNET_WS_URL
from pacifica_sdk.enums import WSChannel
from pacifica_sdk.models.ws_stream import (
    CHANNEL_MODEL_MAP,
    WSOrderBookData,
    WSOrderBookStream,
    WSStream,
)
from pacifica_sdk.models.ws_subscribe import (
    SubscribeParams,
    WSSubscribeRequest,
    WSUnsubscribeRequest,
)

logger = logging.getLogger("pacifica_sdk.websocket_manager")


class WebsocketManager:
    def __init__(
        self,
        ws_url: str = MAINNET_WS_URL,
        disconnect_callback: callable = None,
        no_message_timeout: float = None,
        return_raw_msgs: bool = False,
    ):
        self.ws_url = ws_url

        self.session = self._create_session()
        self.ws = None
        self.active_subscriptions: dict[str, set[tuple[callable, dict]]] = defaultdict(set)

        self._disconnect_callback: callable = disconnect_callback
        self._no_message_timeout: float = no_message_timeout
        self._return_raw_msgs: bool = return_raw_msgs

        self._ws_worker_task = asyncio.create_task(self._ws_worker())
        self._ping_worker_task = asyncio.create_task(self._ping_worker())

    def _create_session(self):
        return aiohttp.ClientSession()

    def _subscription_to_identifier(self, params: SubscribeParams) -> str:
        """
        Builds a dot-separated identifier string from a subscription model.

        Example:
            CandleSubscribeParams(symbol="BTC", interval="1m")
            → "candle.BTC.1m"

            PricesSubscribeParams()
            → "prices"
        """
        if params.source == WSChannel.BOOK:
            return f"book.{params.symbol}"
        field_order = list(params.__class__.model_fields.keys())
        data = params.model_dump(exclude_none=True)
        parts = [str(data[field]) for field in field_order if field in data]
        identifier = ".".join(parts)
        logger.debug(f"Generated subscription identifier: {identifier}")
        return identifier

    def _stream_to_identifier(self, channel: str, msg: dict) -> str:
        def safe_get_first_field(data: list[dict], field: str):
            if data:
                return data[0].get(field, "unknown")

        data = msg.get("data", {})
        match channel:
            case WSChannel.PRICES:
                return "prices"
            case WSChannel.BOOK:
                return f"book.{data['s']}"
            case WSChannel.TRADES:
                return f"trades.{safe_get_first_field(data, 's')}"
            case WSChannel.CANDLE:
                return f"candle.{data['s']}.{data['i']}"
            case WSChannel.ORDER_UPDATES:
                return f"order_updates.{data['i']}"
            case WSChannel.ACCOUNT_BALANCE | WSChannel.ACCOUNT_MARGIN | WSChannel.ACCOUNT_LEVERAGE:
                return f"{channel}.{data['u']}"
            case (
                WSChannel.ACCOUNT_POSITIONS
                | WSChannel.ACCOUNT_ORDERS
                | WSChannel.ACCOUNT_ORDER_UPDATES
                | WSChannel.ACCOUNT_TRADES
            ):
                return f"{channel}.{safe_get_first_field(data, 'u')}"
            case _:
                return "unknown"

    def _data_to_stream(self, channel: str, msg: dict) -> WSStream:
        data = msg.get("data", {})
        if channel == WSChannel.BOOK:
            levels = data.get("l", [[], []])
            model_ready_data = {
                "bids": levels[0],
                "asks": levels[1],
                "s": data["s"],
                "t": data["t"],
            }
            book_data = WSOrderBookData.model_validate(model_ready_data)
            return WSOrderBookStream(channel=channel, data=book_data)
        else:
            model_cls = CHANNEL_MODEL_MAP.get(channel)
            return model_cls.model_validate(msg)

    def _prepare_subscription_message(self, params: SubscribeParams) -> WSSubscribeRequest:
        logger.debug(f"Preparing subscription message for params: {params}")
        return WSSubscribeRequest(params=params).model_dump(exclude_none=True)

    def _prepare_unsubscription_message(self, params: SubscribeParams) -> WSUnsubscribeRequest:
        logger.debug(f"Preparing unsubscription message for params: {params}")
        return WSUnsubscribeRequest(params=params).model_dump(exclude_none=True)

    async def subscribe(self, params: SubscribeParams, callback: callable):
        if self.ws:
            identifier = self._subscription_to_identifier(params)
            sub_msg = json.dumps(self._prepare_subscription_message(params))
            await self.ws.send_str(sub_msg)
            logger.info(f"Subscribed to {identifier}")
            self.active_subscriptions[identifier].add((callback, sub_msg))
        else:
            logger.error("WebSocket connection is not established")
            raise RuntimeError("WebSocket connection is not established")

    async def unsubscribe(self, params: SubscribeParams):
        identifier = self._subscription_to_identifier(params)
        if identifier in self.active_subscriptions:
            del self.active_subscriptions[identifier]
            await self.ws.send_json(self._prepare_unsubscription_message(params))
            logger.info(f"Unsubscribed from {identifier}")

    async def resubscribe(self):
        if not self.active_subscriptions:
            return
        logger.info("Resubscribing to active subscriptions...")
        set_of_subs_msgs = set([sub_msg for subs in self.active_subscriptions.values() for _, sub_msg in subs])
        for sub_msg in set_of_subs_msgs:
            try:
                await self.ws.send_str(sub_msg)
                logger.info(f"Resubscribed to {sub_msg}")
            except Exception:
                logger.exception(f"Failed to resubscribe with message {sub_msg}")

    async def _ping_worker(self):
        while True:
            try:
                if self.ws and not self.ws.closed:
                    await self.ws.send_json({"method": "ping"})
                    logger.debug("Sent ping to WebSocket")
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                logger.info("Ping worker cancelled")
                raise
            except Exception as e:
                logger.error(f"Error in ping worker: {e}")

    async def _ws_worker(self):
        min_delay = 0.1
        max_delay = 60
        current_delay = min_delay
        try:
            while True:
                try:
                    if self.session.closed:
                        logger.warning("Session was closed — recreating ClientSession")
                        self.session = self._create_session()

                    async with self.session.ws_connect(self.ws_url) as ws:
                        self.ws = ws
                        logger.info("WebSocket connected")
                        current_delay = min_delay

                        await self.resubscribe()
                        await self._listener()
                except asyncio.CancelledError:
                    logger.info("WebSocket worker task cancelled")
                    raise
                except Exception as e:
                    logger.warning(f"WebSocket connection error: {e}")
                if self._disconnect_callback:
                    try:
                        asyncio.create_task(self._disconnect_callback())
                    except Exception:
                        logger.exception("Error calling disconnec callback")
                logger.info(f"Reconnecting in {current_delay} seconds...")
                await asyncio.sleep(current_delay)
                current_delay = min(current_delay * 2, max_delay)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Unhandled exception in WebSocket worker")
            raise

    async def _listener(self):
        while True:
            try:
                msg = await asyncio.wait_for(self.ws.receive(), timeout=self._no_message_timeout)
                logger.debug(f"Received websocket message: {msg}")
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        msg_json = json.loads(msg.data)
                        channel = msg_json.get("channel")
                        if channel in ["pong", "subscribe", "unsubscribe"]:
                            logger.debug(f"Received {channel} message")
                            continue
                        elif channel in WSChannel._value2member_map_:
                            logger.debug(f"Received message for known channel: {channel}")
                            if self._return_raw_msgs:
                                return_data = msg_json
                            else:
                                return_data = self._data_to_stream(channel, msg_json)
                            identifier = self._stream_to_identifier(channel, msg_json)
                            logger.debug(f"Identifier for channel {channel}: {identifier}")
                            if identifier in self.active_subscriptions:
                                for callback, _ in self.active_subscriptions[identifier]:
                                    logger.debug(f"Calling callback for channel {channel} with identifier {identifier}")
                                    asyncio.create_task(callback(return_data))
                        else:
                            logger.debug(f"Unknown channel: {channel}")
                            continue

                    except json.JSONDecodeError:
                        logger.error(f"JSON decoding error: {msg.data}")
                        return
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    logger.warning("Server closed the connection. Reconnecting...")
                    return
            except asyncio.TimeoutError:
                logger.error("No messages received in the 30 seconds! Connection might be stalled.")
                return
            except asyncio.CancelledError:
                logger.info("Listen task cancelled")
                raise
            except Exception as e:
                logger.error(f"Error while listening to WebSocket: {e}")
                return

    async def close(self):
        logger.info("Shutting down WebsocketManager")
        if self._ping_worker_task:
            self._ping_worker_task.cancel()
            try:
                await self._ping_worker_task
            except asyncio.CancelledError:
                logger.debug("Ping worker task cancelled")
        if self._ws_worker_task:
            self._ws_worker_task.cancel()
            try:
                await self._ws_worker_task
            except asyncio.CancelledError:
                logger.debug("Websocket worker task cancelled")
        if self.ws and not self.ws.closed:
            await self.ws.close()
            logger.debug("WebSocket connection closed")
        if not self.session.closed:
            await self.session.close()
            logger.debug("HTTP session closed")
        logger.info("WebsocketManager shutdown complete")
