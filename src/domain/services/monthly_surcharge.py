"""Monthly surcharge calculation domain service.

This domain service encapsulates the business logic for calculating
monthly surcharge fees based on visit frequency.
"""

from decimal import Decimal
from typing import Optional
from domain.entities.visit import Visit
from domain.repositories.visit_repository import VisitRepository
from domain.repositories.visitor_repository import VisitorRepository
from domain.types import PersonId, Year, Month
from domain.values.price import Price, Currency


class MonthlySurchargeService:
    """Domain service for calculating monthly surcharge fees.

    Business Rules:
    - Individual visitors with 3 or more visits in a month incur a 5% surcharge
    - Business visitors are exempt from the monthly surcharge
    - Surcharge applies to all visits in that month
    - Surcharge is calculated on the total price of each visit
    """

    SURCHARGE_THRESHOLD = 3
    SURCHARGE_RATE = Decimal("0.05")  # 5%

    def __init__(
        self, visit_repository: VisitRepository, visitor_repository: VisitorRepository
    ):
        """Initialize with visit and visitor repository dependencies.

        Args:
            visit_repository: Repository for accessing visit data
            visitor_repository: Repository for accessing visitor data
        """
        self._visit_repository = visit_repository
        self._visitor_repository = visitor_repository

    def calculate_surcharge_for_visit(
        self,
        visit: Visit,
        visitor_city: Optional[str] = None,
        customer_type: Optional[str] = None,
    ) -> Price:
        """Calculate surcharge amount for a specific visit.

        Args:
            visit: The visit to calculate surcharge for
            visitor_city: Optional city for city-specific pricing
            customer_type: Optional customer type for customer-specific pricing

        Returns:
            Surcharge amount (0.00 if no surcharge applies)
        """
        if not self._should_apply_surcharge(visit):
            return Price(0.0, Currency.EUR)

        base_price = visit.calculate_base_price(visitor_city, customer_type)
        surcharge_amount = float(Decimal(str(base_price.amount)) * self.SURCHARGE_RATE)
        return Price(surcharge_amount, base_price.currency)

    def _calculate_surcharge_for_base_price(
        self, visit: Visit, base_price: Price
    ) -> Price:
        """Calculate surcharge amount for a given base price.

        Args:
            visit: The visit to check surcharge eligibility
            base_price: Pre-calculated base price

        Returns:
            Surcharge amount (0.00 if no surcharge applies)
        """
        if not self._should_apply_surcharge(visit):
            return Price(0.0, Currency.EUR)

        surcharge_amount = float(Decimal(str(base_price.amount)) * self.SURCHARGE_RATE)
        return Price(surcharge_amount, base_price.currency)

    def calculate_total_price_with_surcharge(
        self,
        visit: Visit,
        visitor_city: Optional[str] = None,
        customer_type: Optional[str] = None,
    ) -> Price:
        """Calculate total price including surcharge for a visit.

        Args:
            visit: The visit to calculate total price for
            visitor_city: Optional city for city-specific pricing
            customer_type: Optional customer type for customer-specific pricing

        Returns:
            Total price including any applicable surcharge
        """
        # Calculate base price only once
        base_price = visit.calculate_base_price(visitor_city, customer_type)

        # Calculate surcharge using the already computed base price
        surcharge = self._calculate_surcharge_for_base_price(visit, base_price)

        return base_price.add(surcharge)

    def is_surcharge_applicable(self, visit: Visit) -> bool:
        """Check if surcharge applies to a given visit.

        Args:
            visit: The visit to check

        Returns:
            True if surcharge applies, False otherwise
        """
        return self._should_apply_surcharge(visit)

    def get_monthly_visit_summary(
        self, visitor_id: PersonId, year: Year, month: Month
    ) -> dict:
        """Get summary of visits and surcharges for a month.

        Args:
            visitor_id: ID of the visitor
            year: Year to check
            month: Month to check

        Returns:
            Dictionary with visit count, total base price, total surcharge, and final total
        """
        visits = self._visit_repository.find_visits_for_person_in_month(
            visitor_id, year, month
        )

        if not visits:
            zero_price = Price(0.0, Currency.EUR)
            return {
                "visit_count": 0,
                "total_base_price": zero_price,
                "total_surcharge": zero_price,
                "final_total": zero_price,
                "surcharge_applied": False,
            }

        total_base_price = visits[
            0
        ].calculate_base_price()  # Start with first visit price
        total_surcharge = self.calculate_surcharge_for_visit(visits[0])

        # Add remaining visits
        for visit in visits[1:]:
            base_price = visit.calculate_base_price()
            surcharge = self.calculate_surcharge_for_visit(visit)

            total_base_price = total_base_price.add(base_price)
            total_surcharge = total_surcharge.add(surcharge)

        final_total = total_base_price.add(total_surcharge)

        # Check if surcharge was actually applied (based on visitor type and visit count)
        surcharge_applied = len(visits) > 0 and self._should_apply_surcharge(visits[0])

        return {
            "visit_count": len(visits),
            "total_base_price": total_base_price,
            "total_surcharge": total_surcharge,
            "final_total": final_total,
            "surcharge_applied": surcharge_applied,
        }

    def _should_apply_surcharge(self, visit: Visit) -> bool:
        """Determine if surcharge should apply to a visit.

        Args:
            visit: The visit to check

        Returns:
            True if surcharge should apply (individual visitors only)
        """
        # Check if visitor is individual (private) - business customers are exempt
        visitor = self._visitor_repository.find_by_id(visit.visitor_id)
        if visitor is None:
            # If visitor not found, default to no surcharge for safety
            return False

        # Only individual visitors get the monthly surcharge
        if visitor.type != "individual":
            return False

        year = Year(visit.date.year)
        month = Month(visit.date.month)

        monthly_visit_count = self._visit_repository.count_visits_for_person_in_month(
            visit.visitor_id, year, month
        )

        return monthly_visit_count >= self.SURCHARGE_THRESHOLD
