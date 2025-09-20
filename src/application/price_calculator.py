from dataclasses import dataclass
from typing import Any

from domain.dropped_fraction import DroppedFraction, FractionType
from domain.weight import Weight
from routes import Visit


@dataclass(frozen=True)
class Response:
    price_amount: float
    price_currency: str
    person_id: str
    visit_id: str


class PriceCalculator:
    def calculate(self, visit: Visit) -> Response:
        dropped_fractions = map(self.__parse_dropped_fraction, visit.dropped_fractions)
        # Calculates total price using domain logic
        price = DroppedFraction.sum(dropped_fractions)

        return Response(
            price.amount,
            str(price.currency),
            visit.person_id,
            visit.visit_id,
        )

    def __parse_dropped_fraction(self, dropped_fraction: Any) -> DroppedFraction:
        return DroppedFraction(
            FractionType.from_string(dropped_fraction["fraction_type"]),
            Weight(dropped_fraction["amount_dropped"]),
        )
