from dataclasses import dataclass


@dataclass(frozen=True)
class Invoice:
    price_amount: float
    person_id: str
    visit_id: str
    price_currency: str


class PriceCalculator:
    def calculate(self, visit: dict[str, str]) -> Invoice:
        return Invoice(
            price_amount=0 if not visit["dropped_fractions"] else 1,
            person_id=visit["person_id"],
            visit_id=visit["visit_id"],
            price_currency="EUR",
        )
