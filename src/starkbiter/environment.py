import starkbiter_bindings

from .classes import Chains, ForkParams
from .middleware import Middleware


class Environment:

    def __init__(self, label: str, environment_id: str, chain: Chains):
        self.label = label
        self.id = environment_id
        self.chain = chain

    async def create_middleware(self) -> Middleware:
        middleware_id = await starkbiter_bindings.create_middleware(self.id)
        return Middleware(self.id, middleware_id)


async def create_environment(label: str, chain: Chains, fork: ForkParams | None) -> Environment:
    params = starkbiter_bindings.ForkParams(
        fork.url, fork.block_number, fork.block_hash) if fork else None

    environment_id = await starkbiter_bindings.create_environment(
        label, chain.value, params
    )

    starkbiter_bindings.set_tracing(
        "trace,starknet_devnet_core::starknet::defaulter=info,hyper_util::client::legacy::pool=info,microlp=info,starknet_providers::jsonrpc::transports::http=debug")

    return Environment(label, environment_id, chain)
