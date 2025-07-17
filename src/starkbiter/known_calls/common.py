
class Call:
    to: str
    selector: str
    calldata: list[int]

    def __init__(self, to: str, selector: str, calldata: list[int]):
        self.to = to
        self.selector = selector
        self.calldata = calldata
