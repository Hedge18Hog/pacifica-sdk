import copy
import json
import time
from typing import Type, TypeVar

import aiohttp
from pydantic import BaseModel
from solders.keypair import Keypair

from pacifica_sdk.constants import MAINNET_API_URL
from pacifica_sdk.enums import OperationType
from pacifica_sdk.utils.error import ApiError, ServerError
from pacifica_sdk.utils.tools import build_signer_request

T = TypeVar("T", bound=BaseModel)


class AsyncHttpClient:
    def __init__(
        self,
        private_key: str | None = None,
        public_key: str | None = None,
        agent_wallet: str | None = None,
        base_url: str = MAINNET_API_URL,
        expiry_window: int = 30_000,
    ):
        self.base_url = base_url
        self.expiry_window = expiry_window

        if private_key:
            self.keypair: Keypair = Keypair.from_base58_string(private_key)
            self.public_key = public_key if public_key else str(self.keypair.pubkey())
            self.agent_wallet = agent_wallet

        self.session = aiohttp.ClientSession()
        self.headers = {"Content-Type": "application/json"}

    def _prepare_headers(self, signature: str, timestamp: int):
        headers = {
            "account": self.public_key,
            "signature": signature,
            "timestamp": timestamp,
            "expiry_window": self.expiry_window,
        }
        if self.agent_wallet:
            headers["agent_wallet"] = self.agent_wallet
        return headers

    async def _send_request(
        self,
        method: str,
        endpoint: str,
        *,
        operation_type: OperationType | None = None,
        params: dict | None = None,
        response_model: Type[T] | None = None,
    ) -> T | dict:
        url = f"{self.base_url}{endpoint}"
        full_request = params

        if operation_type == OperationType.BATCH_ORDER:
            temp_params = copy.deepcopy(params)
            for action in temp_params["actions"]:
                action["data"] = build_signer_request(
                    self.keypair,
                    action["operation_type"],
                    action["data"],
                    self.expiry_window,
                    self.public_key,
                    self.agent_wallet,
                )
            full_request = temp_params
        elif isinstance(operation_type, OperationType):
            full_request = build_signer_request(
                self.keypair,
                operation_type,
                params,
                self.expiry_window,
                self.public_key,
                self.agent_wallet,
            )

        async with self.session.request(
            method,
            url,
            headers=self.headers,
            params=params if method.upper() == "GET" else None,
            json=full_request,
        ) as response:
            raw = await self._handle_response(response)
            if response_model:
                try:
                    return response_model.model_validate(raw)
                except Exception as e:
                    raise ValueError(f"Failed to parse response into model {response_model}: {e} data: {raw}")
            return raw

    async def _handle_response(self, response: aiohttp.ClientResponse) -> dict:
        response_text = await response.text()
        status_code = response.status

        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to decode JSON response: {response_text}")
        if 200 <= status_code < 300:
            return response_data
        elif 400 <= status_code < 500:
            raise ApiError(
                status_code=status_code,
                code=response_data.get("code"),
                error_message=response_data.get("error"),
                data=response_data.get("data"),
                raw_body=response_text,
            )
        raise ServerError(status_code=status_code, message=response_text)

    async def close(self):
        await self.session.close()
