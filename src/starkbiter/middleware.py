import starkbiter_bindings
import typing as t

from .classes import EventFilter, LatestBlockTag, Tokens, BlockId, GasPrice, Event
from .accounts import Account, MockAccount
from .known_calls import Call


class Middleware:

    def __init__(self, environment_id: str, middleware_id: str):
        self.environment_id = environment_id
        self.id = middleware_id

    async def declare_contract(self, contract_class: str) -> str:
        return await starkbiter_bindings.declare_contract(self.id, contract_class)

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

    async def get_deployed_contract_address(self, tx_hash: str) -> str:
        return await starkbiter_bindings.get_deployed_contract_address(self.id, tx_hash)

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
        filters = [
            f.to_filter()
            for f in filters
        ] if filters else None

        await starkbiter_bindings.replay_block_with_txs(
            self.id,
            block_id.to_block_id(),
            filters,
            True
        )

    async def impersonate(self, address: str) -> MockAccount:
        await starkbiter_bindings.impersonate(self.id, address)
        return MockAccount(self.environment_id, self.id, address)

    async def stop_impersonate(self, address: str):
        await starkbiter_bindings.stop_impersonate(self.id, address)

    async def create_block(self):
        return await starkbiter_bindings.create_block(self.id)

    async def get_block_events(
        self,
        from_block: t.Optional[BlockId] = None,
        to_block: t.Optional[BlockId] = None,
        from_address: t.Optional[str] = None,
        keys: t.Optional[list[list[str]]] = None,
    ) -> list[Event]:
        events = await starkbiter_bindings.get_block_events(
            self.id,
            from_block=from_block.to_block_id() if from_block else None,
            to_block=to_block.to_block_id() if to_block else None,
            from_address=from_address,
            keys=keys
        )

        return [
            Event(
                event.from_address,
                event.keys,
                event.data,
                event.transaction_hash,
                event.block_number,
                event.block_hash
            )
            for event in events
        ]
