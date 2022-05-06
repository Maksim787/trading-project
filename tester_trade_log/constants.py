import datetime
from enum import Enum

EXCHANGE_OPEN = datetime.time(10, 0, 0)
EXCHANGE_CLOSE = datetime.time(18, 40, 0)


class DIRECTION(Enum):
    LONG = 1
    SHORT = -1
