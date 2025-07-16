import os
import asyncio
from starkbiter import *


ALCHEMY_API_KEY = os.getenv("ALCHEMY_KEY")
ARGENT_ACCOUNT_CLASS_HASH = "0x36078334509b514626504edc9fb252328d1a240e4e948bef8d0c08dff45927f"


class TraderAgent:

    def __init__(self, account: Account):
        self.account = account
        self.token1 = "ETH"
        self.token2 = "STRK"

    async def act(self):
        pass


class ArbitragerAgent:
    def __init__(self, account: Account):
        self.account = account
        self.token1 = "ETH"
        self.token2 = "STRK"

    async def act(self):
        pass


async def create_agent(env: Environment, agent_class):
    # It's important that each egent had their own middleware
    middleware = await env.create_middleware()
    account = await middleware.create_account(ARGENT_ACCOUNT_CLASS_HASH)
    return agent_class(account)

fork_block = 1593123

fork = ForkParams(
    url=f"https://starknet-mainnet.g.alchemy.com/starknet/version/rpc/v0_8/{ALCHEMY_API_KEY}/",
    block_number=fork_block,
    block_hash="0x3d241b79d08109b8199ef697d3f97592e8a70cb9dd15c9b6075730cc68f5023"
)


EKUBO_CORE_ADDRESS = "0x00000005dd3d2f4429af886cd1a3b08289dbcea99a294197e9eb43b0e0325b4b"  # MAINNET


async def simulation(starting_block_number):
    async with get_environment(chain=Chains.MAINNET, fork=fork) as env:

        middleware = await env.create_middleware()
        await middleware.set_gas_price(ALL_PRICES_1)

        # trader = await create_agent(env, TraderAgent)
        # arbitrager = await create_agent(env, ArbitragerAgent)

        iteration = 0
        events = []
        while True:
            print("Events:", events)

            # await trader.act()
            # await arbitrager.act()

            starting_block_number += 1

            filter_ekubo_swaps = EventFilter(
                from_address=EKUBO_CORE_ADDRESS,
                event_name=b"Swapped",
            )

            # Will only apply transactions that emit ekubo Swapped events from core contract on the mainnet. Will not create a block.
            await middleware.replay_block_with_txs(
                BlockNumber(starting_block_number),
                filters=[filter_ekubo_swaps]
            )

            block_hash = await middleware.create_block()

            print("Block hash:", block_hash)

            events = await middleware.get_block_events(
                from_block=BlockHash(block_hash),
                keys=filter_ekubo_swaps.keys,
                from_address=filter_ekubo_swaps.from_address
            )

            iteration += 1

            if iteration > 5:
                print("Simulation completed after 5 iterations.")
                break


asyncio.run(simulation(fork_block))
