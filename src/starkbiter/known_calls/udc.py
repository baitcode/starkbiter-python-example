import starkbiter_bindings

from nethermind.starknet_abi.utils import starknet_keccak

from .common import Call

UDC_CONTRACT_ADDRESS = starkbiter_bindings.contracts.UDC_CONTRACT_ADDRESS


def deploy(
    class_hash: str,
    salt: str = "0x0",
    udc_address: str = UDC_CONTRACT_ADDRESS,
    is_unique: bool = False,
    constructor_calldata: list[int] = None,
) -> Call:
    constructor_calldata = constructor_calldata or []

    return Call(
        to=udc_address,
        selector=starknet_keccak(b"deployContract").hex(),
        calldata=[
            int(class_hash, 0),
            int(salt, 0),
            int(is_unique),
            len(constructor_calldata),
            *constructor_calldata,
        ]
    )
