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


class Event:
    from_address: str
    keys: list[str]
    data: list[str]
    transaction_hash: str
    block_hash: t.Optional[str]
    block_number: t.Optional[int]

    def __init__(self, from_address: str, keys: list[str], data: list[str],
                 transaction_hash: str,
                 block_number: t.Optional[int] = None,
                 block_hash: t.Optional[str] = None):
        self.from_address = from_address
        self.keys = keys
        self.data = data
        self.transaction_hash = transaction_hash
        self.block_number = block_number
        self.block_hash = block_hash


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

# fn new(
#     from_address: &str,
#     keys: Vec<Vec<&str>>,

#     // TODO(baitcode): for some reason pyo3 does
#     // not support using python objects
#     // in python objects
#     from_block_number: Option<u64>,
#     from_block_tag: Option<String>,
#     from_block_hash: Option<String>,

#     to_block_number: Option<u64>,
#     to_block_tag: Option<String>,
#     to_block_hash: Option<String>,
# ) -> Self {


class EventFilter:

    def __init__(self,
                 from_address: str,
                 event_name: bytes,
                 keys: list[list[int]] = None,
                 from_block: t.Optional[BlockId] = None,
                 to_block: t.Optional[BlockId] = None):

        self.selector = f"0x{starknet_keccak(event_name).hex()}"
        # TODO(baitcode): Feels like I'm doing something wrong here. Communicate to Damien this bit.
        keys = [
            [self.selector] + [hex(k) for k in keys]
            for keys in keys or [[]]
        ]

        self.from_address = from_address
        self.event_name = event_name
        self.keys = keys
        self.from_block = from_block
        self.to_block = to_block

    def to_filter(self) -> starkbiter_bindings.EventFilter:

        from_block_number = self.from_block.number if isinstance(
            self.from_block, BlockNumber) else None
        from_block_tag = self.from_block.tag if isinstance(
            self.from_block, BlockTag) else None
        from_block_hash = self.from_block.hash if isinstance(
            self.from_block, BlockHash) else None

        to_block_number = self.to_block.number if isinstance(
            self.to_block, BlockNumber) else None
        to_block_tag = self.to_block.tag if isinstance(
            self.to_block, BlockTag) else None
        to_block_hash = self.to_block.hash if isinstance(
            self.to_block, BlockHash) else None

        return starkbiter_bindings.EventFilter(
            self.from_address, self.keys,
            from_block_number, from_block_tag, from_block_hash,
            to_block_number, to_block_tag, to_block_hash,
        )
