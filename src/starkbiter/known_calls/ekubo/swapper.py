import json

import starkbiter_bindings

from nethermind.starknet_abi.utils import starknet_keccak
from nethermind.starknet_abi import StarknetAbi

from .common import PoolKey
from ..common import Call

SWAPPER_CONTRACT_SIERRA = starkbiter_bindings.contracts.SWAPPER_CONTRACT_SIERRA

_compiled_contract = json.loads(SWAPPER_CONTRACT_SIERRA)
_abi = StarknetAbi.from_json(_compiled_contract["abi"])


def swap(swapper_address: str, key: PoolKey, amount: int, sqrt_ratio_limit: int, token: str) -> None:
    function = _abi.functions["swap"]

    args = function.encode(
        inputs={
            "swap_data": {
                "pool_key": {
                    "token0": key.token0,
                    "token1": key.token1,
                    "fee": key.fee,
                    "tick_spacing": key.tick_spacing,
                    "extension": key.extension
                },
                "amount": {
                    "mag": amount,
                    "sign": True if amount < 0 else False
                },
                "sqrt_ratio_limit": sqrt_ratio_limit,
                "token": token
            }

        }
    )

    return Call(
        to=swapper_address,
        selector=starknet_keccak(b"swap").hex(),
        calldata=args
    )
