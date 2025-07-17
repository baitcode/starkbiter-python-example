import starkbiter_bindings

from .classes import BlockId, LatestBlockTag, Tokens
from .known_calls import Call


class Account:

    def __init__(self, environment_id: str, middleware_id: str, address: str):
        self.environment_id = environment_id
        self.middleware_id = middleware_id
        self.address = address

    async def execute(self, calls: list[Call]) -> str:
        return await starkbiter_bindings.account_execute(
            self.address,
            [
                starkbiter_bindings.Call(call.to, call.selector, call.calldata)
                for call in calls
            ]
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
        return await starkbiter_bindings.call(self.middleware_id, call, block_id)

    async def top_up_balance(self, amount: int, token: Tokens) -> None:
        await starkbiter_bindings.top_up_balance(
            self.middleware_id, self.address, amount, token.value
        )

    async def get_balance(self, token: Tokens) -> int:
        return await starkbiter_bindings.get_balance(
            self.middleware_id, self.address, token.value
        )


class MockAccount:

    def __init__(self, environment_id: str, middleware_id: str, address: str):
        self.environment_id = environment_id
        self.middleware_id = middleware_id
        self.address = address

    async def execute(self, calls: list[Call]) -> str:
        return starkbiter_bindings.account_execute(
            self.address,
            [
                starkbiter_bindings.Call(call.to, call.selector, call.calldata)
                for call in calls
            ]
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
        return await starkbiter_bindings.call(self.middleware_id, call, block_id)

    async def top_up_balance(self, amount: int, token: Tokens) -> None:
        await starkbiter_bindings.top_up_balance(
            self.middleware_id, self.address, amount, token.value
        )

    async def get_balance(self, token: Tokens) -> int:
        return await starkbiter_bindings.get_balance(
            self.middleware_id, self.address, token.value
        )


class EventSubscription:
    def __init__(self, environment_id: str, middleware_id: str):
        self.environment_id = environment_id
        self.middleware_id = middleware_id
        self.id = starkbiter_bindings.create_subscription(
            self.middleware_id
        )

    def poll(self):
        return starkbiter_bindings.poll_subscription(self.id)
