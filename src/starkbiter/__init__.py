import contextlib
from .accounts import MockAccount, Account
from .classes import Call, Chains, EventFilter, BlockHash, LatestBlockTag, BlockId, BlockNumber, BlockTag, ForkParams, Tokens, ALL_PRICES_1, GasPrice
from .environment import Environment, create_environment
from .middleware import Middleware


@contextlib.asynccontextmanager
async def get_environment(label="default", chain=Chains.MAINNET, fork: ForkParams = None):
    env = await create_environment(
        label=label,
        chain=chain,
        fork=fork,
    )

    try:
        yield env
    finally:
        # TODO: add stop environment
        pass
