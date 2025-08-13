import starkbiter_bindings

from .classes import Chains, ForkParams
from .middleware import Middleware


class BridgedToken:
    id: str
    name: str
    symbol: str
    decimals: str
    l1_token_address: str
    l1_bridge_address: str
    l2_token_address: str
    l2_bridge_address: str

    def __init__(self, id: str, name: str, symbol: str, decimals: str,
                 l1_token_address: str, l1_bridge_address: str,
                 l2_token_address: str, l2_bridge_address: str):
        self.id = id
        self.name = name
        self.symbol = symbol
        self.decimals = decimals
        self.l1_token_address = l1_token_address
        self.l1_bridge_address = l1_bridge_address
        self.l2_token_address = l2_token_address
        self.l2_bridge_address = l2_bridge_address


class Environment:

    def __init__(self, label: str, environment_id: str, chain: Chains):
        self.label = label
        self.id = environment_id
        self.chain = chain

    async def create_middleware(self) -> Middleware:
        middleware_id = await starkbiter_bindings.create_middleware(self.id)
        return Middleware(self.id, middleware_id)

    async def get_token_data(self, token: str) -> BridgedToken:
        token_data = await starkbiter_bindings.get_token(self.id, token.lower())

        return BridgedToken(
            id=token_data.id,
            name=token_data.name,
            symbol=token_data.symbol,
            decimals=token_data.decimals,
            l1_token_address=token_data.l1_token_address,
            l1_bridge_address=token_data.l1_bridge_address,
            l2_token_address=token_data.l2_token_address,
            l2_bridge_address=token_data.l2_bridge_address,
        )


async def create_environment(label: str, chain: Chains, fork: ForkParams | None) -> Environment:
    params = starkbiter_bindings.ForkParams(
        fork.url, fork.block_number, fork.block_hash) if fork else None

    environment_id = await starkbiter_bindings.create_environment(
        label, chain.value, params
    )

    starkbiter_bindings.set_tracing(
        "trace,starknet_devnet_core::starknet::defaulter=debug,hyper_util::client::legacy::pool=info,microlp=info,starknet_providers::jsonrpc::transports::http=debug")

    return Environment(label, environment_id, chain)
