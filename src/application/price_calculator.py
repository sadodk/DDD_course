from dataclasses import dataclass
from typing import Any

from domain.dropped_fraction import DroppedFraction, FractionType
from domain.weight import Weight
from application.external_visitor_repository import ExternalVisitorService
from domain.monthly_visit_tracker import MonthlyVisitTracker


@dataclass(frozen=True)
class Response:
    price_amount: float
    price_currency: str
    person_id: str
    visit_id: str


class PriceCalculator:
    def __init__(
        self,
        visitor_service: ExternalVisitorService,
        visit_tracker: MonthlyVisitTracker,
    ):
        self.visitor_service = visitor_service
        self.visit_tracker = visit_tracker

    def calculate(self, visit) -> Response:  # Accept dict or Pydantic model
        # Fetch visitor to get their city
        visitor = self.visitor_service.get_visitor_by_id(visit.person_id)
        visitor_city = visitor.city if visitor else None

        # Parse fractions and calculate base price with city pricing
        dropped_fractions = [
            self.__parse_dropped_fraction(fraction)
            for fraction in visit.dropped_fractions
        ]

        base_price = DroppedFraction.sum(dropped_fractions, visitor_city)

        # Record this visit for monthly tracking
        self.visit_tracker.record_visit(visit.person_id, visit.date, visit.visit_id)

        # Apply monthly surcharge if applicable (3rd+ visit in month)
        final_price = self.visit_tracker.apply_monthly_surcharge(
            base_price, visit.person_id, visit.date
        )

        return Response(
            final_price.amount,
            str(final_price.currency),
            visit.person_id,
            visit.visit_id,
        )

    def __parse_dropped_fraction(self, dropped_fraction: Any) -> DroppedFraction:
        return DroppedFraction(
            FractionType.from_string(dropped_fraction["fraction_type"]),
            Weight(dropped_fraction["amount_dropped"]),
        )
