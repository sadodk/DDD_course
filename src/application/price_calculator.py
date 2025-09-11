from dataclasses import dataclass
from typing import Any
from domain.price import Price, Currency


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


GREEN_WASTE_COST = 0.1  # euro/kg
CONSTRUCTION_WASTE_COST = 0.15  # euro/kg


class PriceCalculator:
    def calculate(self, visit: Visit) -> Invoice:
        total_amount = 0
        for fraction in visit.dropped_fractions:
            if fraction["fraction_type"] == "Green waste":
                total_amount += float(fraction["amount_dropped"]) * GREEN_WASTE_COST
            elif fraction["fraction_type"] == "Construction waste":
                total_amount += (
                    float(fraction["amount_dropped"]) * CONSTRUCTION_WASTE_COST
                )
            else:
                total_amount = 0
        price = Price(amount=total_amount, currency=Currency.EUR)
        return Invoice(
            price_amount=price.amount,
            person_id=visit.person_id,
            visit_id=visit.visit_id,
            price_currency=price.currency.value,
        )
