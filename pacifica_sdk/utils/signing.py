import base58
from solders.keypair import Keypair

from pacifica_sdk.enums import OperationType

try:
    import orjson

    def _dumps_encode(obj: any) -> str:
        return orjson.dumps(obj, option=orjson.OPT_SORT_KEYS)

except ImportError:
    import json

    def _dumps_encode(obj: any) -> str:
        return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sign_message(
    *,
    keypair: Keypair,
    timestamp: int,
    operation_type: OperationType,
    operation_data: dict,
    expiry_window: int,
) -> str:
    data_to_sign = {
        "timestamp": timestamp,
        "expiry_window": expiry_window,
        "type": operation_type,
        "data": operation_data,
    }
    msg_bytes = _dumps_encode(data_to_sign)
    sig = keypair.sign_message(msg_bytes)
    sig_b58 = base58.b58encode(bytes(sig)).decode("ascii")
    return sig_b58
