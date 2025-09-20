from enum import Enum
from dataclasses import dataclass
from typing import Any
from .price import Price, Currency


GREEN_WASTE_COST = 0.1  # euro/kg
CONSTRUCTION_WASTE_COST = 0.15  # euro/kg


@dataclass(frozen=True)
class Invoice:
    price_amount: float
    person_id: str
    visit_id: str
    price_currency: str


@dataclass(frozen=True)
class Visit:
    date: str
    dropped_fractions: list[dict[str, Any]]
    person_id: str
    visit_id: str

    def calculate_price(self) -> Price:
        """Calculate the total price for this visit based on dropped fractions."""
        price = Price.zero(Currency.EUR)

        for fraction in self.dropped_fractions:
            fraction_price = self._calculate_fraction_price(fraction)
            price = price.add(fraction_price)

        return price

    def create_invoice(self) -> Invoice:
        """Create an invoice for this visit."""
        price = self.calculate_price()
        return Invoice(
            price_amount=price.amount,
            person_id=self.person_id,
            visit_id=self.visit_id,
            price_currency=price.currency.value,
        )

    def _calculate_fraction_price(self, fraction: dict[str, Any]) -> Price:
        """Calculate the price for a single fraction."""
        amount_dropped = float(fraction["amount_dropped"])

        if fraction["fraction_type"] == "Green waste":
            cost_per_kg = GREEN_WASTE_COST
        elif fraction["fraction_type"] == "Construction waste":
            cost_per_kg = CONSTRUCTION_WASTE_COST
        else:
            # Unknown waste types return zero price
            return Price.zero(Currency.EUR)

        total_amount = amount_dropped * cost_per_kg
        return Price(amount=total_amount, currency=Currency.EUR)
