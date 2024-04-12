from dataclasses import dataclass


@dataclass(frozen=True)
class Response:
    price_amount: float
    price_currency: str
    person_id: str
    visit_id: str


class PriceCalculator:
    def calculate(self, visit: dict[str, str]) -> Response:
        return Response(0, "EUR", visit["person_id"], visit["visit_id"])
