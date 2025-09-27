"""Clean price calculator using DDD entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from domain.entities.visit import Visit
from domain.services.monthly_surcharge_service import MonthlySurchargeService
from domain.repositories.visit_repository import VisitRepository
from domain.types import PersonId, VisitId
from domain.dropped_fraction import DroppedFraction, FractionType
from domain.weight import Weight
from application.external_visitor_repository import ExternalVisitorService


@dataclass(frozen=True)
class PriceResponse:
    """Response for price calculations."""

    price_amount: float
    price_currency: str
    person_id: str
    visit_id: str


class PriceCalculator:
    """Clean price calculator using domain entities.

    This service focuses on the core business logic with minimal complexity.
    """

    def __init__(
        self,
        visitor_service: ExternalVisitorService,
        surcharge_service: MonthlySurchargeService,
        visit_repository: VisitRepository,
    ):
        self._visitor_service = visitor_service
        self._surcharge_service = surcharge_service
        self._visit_repository = visit_repository

    def calculate_price(self, visit_data: Dict[str, Any]) -> PriceResponse:
        """Calculate price for a visit.

        Args:
            visit_data: Dictionary with visit information

        Returns:
            PriceResponse with calculated price
        """
        # Create domain entities from request data
        visit = self._create_visit_entity(visit_data)

        # Save the visit so the surcharge service can see it
        self._visit_repository.save(visit)

        # Calculate total price using domain service
        total_price = self._surcharge_service.calculate_total_price_with_surcharge(
            visit
        )

        return PriceResponse(
            price_amount=total_price.amount,
            price_currency=str(total_price.currency),
            person_id=visit_data["person_id"],
            visit_id=visit_data["visit_id"],
        )

    def _create_visit_entity(self, visit_data: Dict[str, Any]) -> Visit:
        """Create a Visit entity from request data."""
        # Parse basic visit information
        person_id = PersonId(visit_data["person_id"])
        visit_id = VisitId(visit_data["visit_id"])
        visit_date = self._parse_date(visit_data["date"])

        # Parse dropped fractions
        dropped_fractions = []
        for fraction_data in visit_data["dropped_fractions"]:
            fraction_type = FractionType.from_string(fraction_data["fraction_type"])
            weight = Weight(fraction_data["amount_dropped"])
            dropped_fractions.append(DroppedFraction(fraction_type, weight))

        return Visit(
            id=visit_id,
            visitor_id=person_id,
            date=visit_date,
            dropped_fractions=dropped_fractions,
        )

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime."""
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return datetime.fromisoformat(date_str)
