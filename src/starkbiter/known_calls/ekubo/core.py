import typing as t
import json
import starkbiter_bindings

from nethermind.starknet_abi.utils import starknet_keccak
from nethermind.starknet_abi import StarknetAbi, decode_from_types

from ..common import Call

from .common import PoolKey

EKUBO_CORE_CONTRACT_SIERRA = starkbiter_bindings.contracts.EKUBO_CORE_CONTRACT_SIERRA


_compiled_contract = json.loads(EKUBO_CORE_CONTRACT_SIERRA)
_abi = StarknetAbi.from_json(_compiled_contract["abi"])

# Possible calls:
#     get_primary_interface_id
#     get_protocol_fees_collected
#     get_locker_state
#     get_locker_delta
#     get_pool_price
#     get_pool_liquidity
#     get_pool_fees_per_liquidity
#     get_pool_fees_per_liquidity_inside
#     get_pool_tick_liquidity_delta
#     get_pool_tick_liquidity_net
#     get_pool_tick_fees_outside
#     get_position
#     get_position_with_fees
#     get_saved_balance
#     next_initialized_tick
#     prev_initialized_tick
#     withdraw_all_protocol_fees
#     withdraw_protocol_fees
#     forward
#     withdraw
#     save
#     pay
#     load
#     update_position
#     collect_fees
#     swap
#     accumulate_as_fees


def get_pool_price_call(core_address: str, key: PoolKey) -> t.Tuple[Call, t.Callable[[list[int]], t.Dict]]:
    function = _abi.functions["get_pool_price"]

    args = function.encode(
        inputs={
            "pool_key": {
                "token0": key.token0,
                "token1": key.token1,
                "fee": key.fee,
                "tick_spacing": key.tick_spacing,
                "extension": key.extension
            }
        }
    )

    def parse_res(res):
        return decode_from_types(function.outputs, [
            int(i, 0)
            for i in res
        ])

    return Call(
        to=core_address,
        selector=starknet_keccak(b"get_pool_price").hex(),
        calldata=args
    ), parse_res


def get_pool_liquidity_call(core_address: str, key: PoolKey) -> t.Tuple[Call, t.Callable[[list[int]], t.Dict]]:
    function = _abi.functions["get_pool_liquidity"]

    args = function.encode(
        inputs={
            "pool_key": {
                "token0": key.token0,
                "token1": key.token1,
                "fee": key.fee,
                "tick_spacing": key.tick_spacing,
                "extension": key.extension
            }
        }
    )

    def parse_res(res):
        return decode_from_types(function.outputs, [
            int(i, 0)
            for i in res
        ])

    return Call(
        to=core_address,
        selector=starknet_keccak(b"get_pool_liquidity").hex(),
        calldata=args
    ), parse_res
