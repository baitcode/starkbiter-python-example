import typing as t
from enum import StrEnum

from nethermind.starknet_abi.utils import starknet_keccak

import starkbiter_bindings


class Chains(StrEnum):
    MAINNET = f"0x{b"SN_MAIN".hex()}"
    SEPOLIA = f"0x{b"SN_SEPOLIA".hex()}"
    SEPOLIA_INTEGRATION = f"0x{b"SN_INTEGRATION_SEPOLIA".hex()}"


class Tokens(StrEnum):
    STRK = "strk"
    ETH = "eth"
    USDC = "usdc"
    USDT = "usdt"
    DAI = "dai"
    EKUBO = "ekubo"


class GasPrice:

    gas_price_wei: int
    gas_price_fri: int
    data_gas_price_wei: int
    data_gas_price_fri: int
    l2_gas_price_wei: int
    l2_gas_price_fri: int
    generate_block: bool

    def __init__(self, gas_price_wei: int, gas_price_fri: int, data_gas_price_wei: int,
                 data_gas_price_fri: int, l2_gas_price_wei: int, l2_gas_price_fri: int,
                 generate_block: bool = False):
        self.gas_price_wei = gas_price_wei
        self.gas_price_fri = gas_price_fri
        self.data_gas_price_wei = data_gas_price_wei
        self.data_gas_price_fri = data_gas_price_fri
        self.l2_gas_price_wei = l2_gas_price_wei
        self.l2_gas_price_fri = l2_gas_price_fri
        self.generate_block = generate_block


ALL_PRICES_1 = GasPrice(
    gas_price_wei=1,
    gas_price_fri=1,
    data_gas_price_wei=1,
    data_gas_price_fri=1,
    l2_gas_price_wei=1,
    l2_gas_price_fri=1,
    generate_block=True
)


class Call:
    to: str
    selector: str
    calldata: list[int]

    def __init__(self, to: str, selector: str, calldata: list[int]):
        self.to = to
        self.selector = selector
        self.calldata = calldata


class ForkParams:
    url: str
    block_number: int
    block_hash: str

    def __init__(self, url: str, block_number: int, block_hash: str):
        self.url = url
        self.block_number = block_number
        self.block_hash = block_hash


class BlockTag:
    def __init__(self, tag: str):
        self.tag = tag

    def to_block_id(self) -> starkbiter_bindings.BlockId:
        return starkbiter_bindings.BlockId.from_tag(self.tag)


class BlockNumber:
    def __init__(self, number: int):
        self.number = number

    def to_block_id(self) -> starkbiter_bindings.BlockId:
        return starkbiter_bindings.BlockId.from_number(self.number)


class BlockHash:
    def __init__(self, hash: str):
        self.hash = hash

    def to_block_id(self) -> starkbiter_bindings.BlockId:
        return starkbiter_bindings.BlockId.from_hash(self.hash)


LatestBlockTag = BlockTag("latest")
BlockId = t.Union[BlockTag, BlockNumber, BlockHash]


class EventFilter:
    def __init__(self, from_address: str, event_name: str, keys: list[int] = None):
        self.from_address = from_address
        self.event_name = event_name
        self.keys = keys or []

    def to_filter(self) -> starkbiter_bindings.EventFilter:
        selector = starknet_keccak(self.event_name).hex()
        keys = [selector] + self.keys
        return starkbiter_bindings.EventFilter(self.from_address, keys)
