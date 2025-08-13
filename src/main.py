from starkbiter import *
import typing as t
import os
import asyncio


ALCHEMY_API_KEY = os.getenv("ALCHEMY_KEY")
ARGENT_ACCOUNT_CLASS_HASH = "0x36078334509b514626504edc9fb252328d1a240e4e948bef8d0c08dff45927f"
EKUBO_CORE_ADDRESS = "0x00000005dd3d2f4429af886cd1a3b08289dbcea99a294197e9eb43b0e0325b4b"  # MAINNET


class TraderAgent:

    def __init__(self, environment: Environment):
        self.token0 = "ETH"
        self.token1 = "USDC"
        self.environment: Environment = environment
        self.middleware: t.Optional[Middleware] = None
        self.account: t.Optional[Account] = None
        self.token0_data: t.Optional[BridgedToken] = None
        self.token1_data: t.Optional[BridgedToken] = None
        self.swapper_address: t.Optional[str] = None

    async def prepare(self):
        self.middleware = await self.environment.create_middleware()
        self.account = await self.middleware.create_account(ARGENT_ACCOUNT_CLASS_HASH)
        await self.middleware.top_up_balance(self.account.address, 1000000000000000000, Tokens.STRK)

        self.token0_data = await self.environment.get_token_data(self.token0)
        self.token1_data = await self.environment.get_token_data(self.token1)

        # TODO(baitcode): validate token0 address < token1 address

        # Deploying swapper contract.
        # 1. Declaring swapper
        swapper_class_hash = await self.middleware.declare_contract(known_calls.ekubo.swapper.SWAPPER_CONTRACT_SIERRA)

        # 2. UDC deploy call using traders account (must be the money)
        res = await self.account.execute(calls=[
            known_calls.udc.deploy(
                class_hash=swapper_class_hash,
                constructor_calldata=[
                    # This is ekubo core address. Swapper will send swaps there.
                    int(EKUBO_CORE_ADDRESS, 16),
                    # This is withdrawal address. All funds are withdrawn as Swap ends.
                    # This might be undesirable, but for now we use it.
                    int(self.account.address, 16),
                ]
            )
        ])

        # Getting the deployed contract address. (By default UDC does not return it)
        self.swapper_address = await self.middleware.get_deployed_contract_address(res)

        # Let's send some moneys to swapper, as swapper uses it's balance to perform swap agains EKUBO
        await self.middleware.top_up_balance(self.swapper_address, 1000000000000000000, Tokens.ETH)
        print("Swapper deployed:", res)

        # Lets calculate sqrt_ratio_limit for swaps.
        # The API looks awful. I was in a rush, I'm open to suggestions.
        get_pool_price_call, parse_res = known_calls.ekubo.core.get_pool_price_call(
            EKUBO_CORE_ADDRESS, known_calls.ekubo.PoolKey(
                token0=self.token0_data.l2_token_address,
                token1=self.token1_data.l2_token_address,
                fee_tick=known_calls.ekubo.FeeAndTickSpacing.FEE_0_01_PRECISION_0_02,
            )
        )
        sqrt_ratio_res = parse_res(await self.account.call(get_pool_price_call))
        print("Sqrt ratio", sqrt_ratio_res)

        # # Let's get liquidity.
        get_pool_liquidity_call, parse_res = known_calls.ekubo.core.get_pool_liquidity_call(
            EKUBO_CORE_ADDRESS, known_calls.ekubo.PoolKey(
                token0=self.token0_data.l2_token_address,
                token1=self.token1_data.l2_token_address,
                fee_tick=known_calls.ekubo.FeeAndTickSpacing.FEE_0_01_PRECISION_0_02,
            )
        )
        liquidity_res = parse_res(await self.account.call(get_pool_liquidity_call))
        print("Liquidity", liquidity_res)
        return

    async def act(self):

        print("Trader agent acting...")

        res = await self.middleware.get_balance(self.swapper_address, Tokens.ETH)
        print("Trader agent ETH balance:", res)

        res = await self.account.execute(calls=[
            known_calls.ekubo.swapper.swap(
                swapper_address=self.swapper_address,
                key=known_calls.ekubo.PoolKey(
                    token0=self.token0_data.l2_token_address,
                    token1=self.token1_data.l2_token_address,
                    fee_tick=known_calls.ekubo.FeeAndTickSpacing.FEE_5_PRECISION_10,
                ),
                amount=1000000000000000,  # 0.001 ETH
                # This is the minimum sqrt ratio limit
                sqrt_ratio_limit=known_calls.ekubo.SQRT_RATE_LIMIT_MIN,
                token=self.token0_data.l2_token_address,
            )
        ])

        print("Swap result:", res)

        await self.middleware.get_balance(self.swapper_address, Tokens.ETH)
        print("Trader agent ETH balance:", res)


fork_block = 1521205  # 1593123
fork_hash = "0x7aabf76192d3d16fe8bda54c0e7d0a9843c21fe20dd23704366bad38d57dc30"
node_url = f"https://starknet-mainnet.g.alchemy.com/starknet/version/rpc/v0_8/{ALCHEMY_API_KEY}/"

fork = ForkParams(
    # IMPORTANT: Do not use blast API, it's API format is incompatible with starknet-rs lib
    # url=node_url,
    url=f"sqlite://{os.getcwd()}/../mainnet-vacuumed.sqlite",

    # This is the block number to fork from
    block_number=fork_block,
    # This is the block hash to fork from. Yes we need both parameters for environment to work.
    # This can be optimised, but I didn't want to spend time on it.
    block_hash=fork_hash
)


async def simulation(starting_block_number):

    # This spins the environment up
    async with get_environment(chain=Chains.MAINNET, fork=fork) as env:

        # This is a separate middleware I use to set environment up.
        middleware = await env.create_middleware()
        await middleware.set_gas_price(ALL_PRICES_1)

        trader = TraderAgent(env)
        await trader.prepare()

        iteration = 0
        events = []
        while True:
            print("Events:", events)

            await trader.act()
            # await arbitrager.act()

            starting_block_number += 1

            filter_ekubo_swaps = EventFilter(
                from_address=EKUBO_CORE_ADDRESS,
                event_name=b"Swapped",
            )

            # Will only apply transactions that emit ekubo Swapped events from core contract on the mainnet. Will not create a block.
            await middleware.replay_block_with_txs(
                node_url,
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
