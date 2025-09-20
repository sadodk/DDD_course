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

    def add(self, other: "Price") -> "Price":
        """Add two prices together, returning a new Price object.
        Both prices must have the same currency."""
        if self.currency != other.currency:
            raise ValueError("Cannot add prices with different currencies")

        return Price(amount=self.amount + other.amount, currency=self.currency)

    @classmethod
    def zero(cls, currency: Currency) -> "Price":
        """Create a zero price for the given currency."""
        return cls(amount=0.0, currency=currency)
