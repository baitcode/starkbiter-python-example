from nethermind.starknet_abi.utils import starknet_keccak

from ..accounts import Call


def deploy_contract(
    udc_address: str,
    class_hash: str,
    salt: str,
    is_unique: bool = False,
    constructor_calldata: list[int] = None,
) -> Call:
    constructor_calldata = constructor_calldata or []

    return Call(
        to=udc_address,
        selector=starknet_keccak("deployContract").hex(),
        calldata=[
            int(class_hash, 0),
            int(salt, 0),
            int(is_unique),
            len(constructor_calldata),
            *constructor_calldata,
        ]
    )
