from __future__ import annotations
from enum import Enum
from dataclasses import dataclass


class Currency(Enum):
    EUR = "EUR"

    def __str__(self):
        return str(self.value)


@dataclass(frozen=True)
class Price:  # value object
    amount: float
    currency: Currency

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("amount must be positive")

        if not isinstance(self.currency, Currency):
            raise ValueError("currency is invalid")

    def add(self, other: Price) -> Price:
        return Price(self.amount + other.amount, self.currency)

    def times(self, factor: int) -> Price:
        return Price(self.amount * factor, self.currency)
