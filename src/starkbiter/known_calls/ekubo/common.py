from enum import Enum


class FeeAndTickSpacing(Enum):
    FEE_0_01_PRECISION_0_02 = (34028236692093847977029636859101184, 200)
    FEE_0_05_PRECISION_0_1 = (170141183460469235273462165868118016, 1000)
    FEE_0_3_PRECISION_0_6 = (1020847100762815411640772995208708096, 5982)
    FEE_1_PRECISION_2 = (3402823669209384634633746074317682114, 19802)
    FEE_5_PRECISION_10 = (17014118346046923173168730371588410572, 95310)


class PoolKey:
    def __init__(self, token0: str, token1: str, fee_tick: FeeAndTickSpacing, extension: str = None):
        # token0 and token1 validation?
        self.token0 = int(token0, 0)
        self.token1 = int(token1, 0)
        self.fee = fee_tick.value[0]
        self.tick_spacing = fee_tick.value[1]
        self.extension = int(extension, 0) if extension else 0


SQRT_RATE_LIMIT_MIN = 18446748437148339061
SQRT_RATE_LIMIT_MAX = 6277100250585753475930931601400621808602321654880405518632
