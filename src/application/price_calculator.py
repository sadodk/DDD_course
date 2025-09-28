"""Clean price calculator using DDD entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from domain.entities.visit import Visit
from domain.entities.visitor import Visitor
from domain.services.monthly_surcharge_service import MonthlySurchargeService
from domain.repositories.visit_repository import VisitRepository
from domain.repositories.visitor_repository import VisitorRepository
from domain.types import PersonId, VisitId, CardId, EmailAddress
from domain.dropped_fraction import DroppedFraction, FractionType
from domain.weight import Weight
from application.external_visitor_service import ExternalVisitorService


@dataclass(frozen=True)
class PriceResponse:
    """Response for price calculations."""

    price_amount: float
    price_currency: str
    person_id: str
    visit_id: str


class PriceCalculator:
    """Clean price calculator using domain entities.

    This service coordinates between external services, repositories, and domain services
    to calculate the price of a visit.
    """

    def __init__(
        self,
        visitor_service: ExternalVisitorService,
        surcharge_service: MonthlySurchargeService,
        visit_repository: VisitRepository,
        visitor_repository: VisitorRepository,
    ):
        self._visitor_service = visitor_service
        self._surcharge_service = surcharge_service
        self._visit_repository = visit_repository
        self._visitor_repository = visitor_repository

    def calculate_price(self, visit_data: Dict[str, Any]) -> PriceResponse:
        """Calculate price for a visit.

        Args:
            visit_data: Dictionary with visit information

        Returns:
            PriceResponse with calculated price
        """
        # Create domain entities from request data
        visit = self._create_visit_entity(visit_data)

        # Fetch visitor information to get city and customer type for pricing
        visitor_info = self._visitor_service.get_visitor_by_id(visit_data["person_id"])
        visitor_city = visitor_info.city if visitor_info else None
        customer_type = visitor_info.type if visitor_info else None

        # Save visitor information to repository if found and not already exists
        if visitor_info and not self._visitor_repository.exists(
            PersonId(visitor_info.id)
        ):
            visitor_entity = Visitor(
                id=PersonId(visitor_info.id),
                type=visitor_info.type,
                address=visitor_info.address,
                city=visitor_info.city,
                card_id=CardId(visitor_info.card_id),
                email=EmailAddress(visitor_info.email),
            )
            self._visitor_repository.save(visitor_entity)

        # Save the visit so the surcharge service can see it
        self._visit_repository.save(visit)

        # Calculate total price using domain service, passing visitor city and type
        total_price = self._surcharge_service.calculate_total_price_with_surcharge(
            visit, visitor_city, customer_type
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
