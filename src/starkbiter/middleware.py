import starkbiter_bindings
import typing as t

from .classes import Call, EventFilter, LatestBlockTag, Tokens, BlockId, GasPrice
from .accounts import Account, MockAccount


class Subscription:
    def __init__(self, subscription_id: str):
        self.id = subscription_id

    async def get_event(self) -> starkbiter_bindings.Event | None:
        return await starkbiter_bindings.poll_subscription(self.id)


class Middleware:

    def __init__(self, environment_id: str, middleware_id: str):
        self.environment_id = environment_id
        self.id = middleware_id

    async def create_account(self, class_hash: str) -> Account:
        address = await starkbiter_bindings.create_account(self.id, class_hash)
        return Account(self.environment_id, self.id, address)

    async def create_mock_account(self, address: str) -> MockAccount:
        address = await starkbiter_bindings.create_mock_account(self.id, address)
        return MockAccount(self.environment_id, self.id, address)

    async def top_up_balance(self, address: str, amount: int, token: Tokens) -> None:
        await starkbiter_bindings.top_up_balance(
            self.id, address, amount, token.value
        )

    async def get_balance(self, address: str, token: Tokens) -> int:
        return await starkbiter_bindings.get_balance(
            self.id, address, token.value
        )

    async def set_storage(self, address: str, key: str, value: str) -> None:
        await starkbiter_bindings.set_storage(
            self.id, address, key, value
        )

    async def get_storage(self, address: str, key: str) -> str:
        await starkbiter_bindings.get_storage(
            self.id, address, key
        )

    async def set_gas_price(self, gas_price: GasPrice):
        await starkbiter_bindings.set_gas_price(
            self.id,
            gas_price_wei=gas_price.gas_price_wei,
            gas_price_fri=gas_price.gas_price_fri,
            data_gas_price_wei=gas_price.data_gas_price_wei,
            data_gas_price_fri=gas_price.data_gas_price_fri,
            l2_gas_price_wei=gas_price.l2_gas_price_wei,
            l2_gas_price_fri=gas_price.l2_gas_price_fri,
            generate_block=gas_price.generate_block,
        )

    async def call(
        self,
        call: Call,
        block_id: BlockId = LatestBlockTag,
    ) -> list[str]:

        block_id = block_id.to_block_id()

        call = starkbiter_bindings.Call(
            call.to, call.selector, call.calldata
        )
        return await starkbiter_bindings.call(self.id, call, block_id)

    async def replay_block_with_txs(self,
                                    block_id: BlockId,
                                    filters: t.Optional[list[EventFilter]] = None):
        await starkbiter_bindings.replay_block_with_txs(
            self.id,
            block_id.to_block_id(),
            filters.map(lambda f: f.to_filter()) if filters else None
        )

    async def impersonate(self, address: str) -> MockAccount:
        await starkbiter_bindings.impersonate(self.id, address)
        return MockAccount(self.environment_id, self.id, address)

    async def stop_impersonate(self, address: str):
        await starkbiter_bindings.stop_impersonate(self.id, address)

    async def subscribe_to_events(self) -> Subscription:
        middleware_id = await starkbiter_bindings.create_middleware(self.id)
        subscription_id = await starkbiter_bindings.create_subscription(middleware_id)
        return Subscription(subscription_id)
