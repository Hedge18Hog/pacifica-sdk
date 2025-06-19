import time

from solders.keypair import Keypair

from pacifica_sdk.enums import OperationType
from pacifica_sdk.utils.signing import sign_message


def get_timestamp_ms() -> int:
    """
    Get the current timestamp in milliseconds.
    """
    return int(time.time() * 1000)


def round_price(price: str | float) -> str:
    if isinstance(price, str):
        price = float(price)
    return str(price)


def build_signer_request(
    keypair: Keypair,
    operation_type: OperationType,
    params: dict,
    expiry_window: int,
    public_key: str | None = None,
    agent_wallet: str | None = None,
    timestamp: int | None = None,
) -> dict:
    """
    TODO

    Returns:
        dict: Complete signed payload ready for sending via HTTP or WebSocket.

    References:
        https://docs.pacifica.fi/api-documentation/api/signing/implementation
    """

    ts = timestamp or get_timestamp_ms()
    pk = public_key or str(keypair.pubkey())
    signature = sign_message(
        keypair=keypair,
        timestamp=ts,
        operation_type=operation_type,
        operation_data=params,
        expiry_window=expiry_window,
    )
    headers = {
        "account": pk,
        "signature": signature,
        "timestamp": ts,
        "expiry_window": expiry_window,
    }
    if agent_wallet:
        headers["agent_wallet"] = agent_wallet
    return {**headers, **params}
