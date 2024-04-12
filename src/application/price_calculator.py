from dataclasses import dataclass
from functools import reduce


@dataclass(frozen=True)
class Response:
    price_amount: float
    price_currency: str
    person_id: str
    visit_id: str


class PriceCalculator:
    def calculate(self, visit: dict[str, str]) -> Response:
        price_amount = reduce(
            lambda price, dropped_fraction: price
            + dropped_fraction["amount_dropped"]
            * (0.1 if dropped_fraction["fraction_type"] == "Green waste" else 0.15),
            visit["dropped_fractions"],
            0,
        )
        return Response(price_amount, "EUR", visit["person_id"], visit["visit_id"])
