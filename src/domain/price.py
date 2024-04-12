from enum import Enum
from dataclasses import dataclass


class Currency(Enum):
    EUR = "EUR"


@dataclass(frozen=True)
class Price:
    amount: float
    currency: Currency

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("amount must be positive")

        if not isinstance(self.currency, Currency):
            raise ValueError("currency is invalid")
