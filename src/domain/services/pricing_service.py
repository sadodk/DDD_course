"""Pricing domain service for calculating prices of dropped fractions."""

from typing import List, Optional
from datetime import datetime
from domain.values.dropped_fraction import DroppedFraction
from domain.values.price import Price, Currency
from domain.business_rules.pricing_rule_engine import PricingRuleEngine
from domain.business_rules.interface_pricing_rules import PricingContext


class PricingService:
    """Domain service responsible for pricing calculations.

    This service orchestrates the pricing of individual or collections of
    DroppedFraction objects using the business rules engine.
    """

    def __init__(self, pricing_engine: Optional[PricingRuleEngine] = None):
        """Initialize the pricing service.

        Args:
            pricing_engine: Optional pricing rule engine. If None, creates default.
        """
        self._pricing_engine = pricing_engine or PricingRuleEngine()

    def calculate_price(
        self,
        fraction: DroppedFraction,
        city: Optional[str] = None,
        customer_type: Optional[str] = None,
        visitor_id: Optional[str] = None,
        visit_date: Optional[datetime] = None,
    ) -> Price:
        """Calculate price for a single dropped fraction.

        Args:
            fraction: The dropped fraction to price
            city: The city for city-specific pricing
            customer_type: The customer type ('individual' for private, 'business' for business)
            visitor_id: The unique identifier for the visitor (needed for exemption tracking)
            visit_date: The date of the visit (needed for calendar year exemptions)

        Returns:
            Price for the dropped fraction
        """
        context = PricingContext(
            customer_type=customer_type,
            city=city,
            visitor_id=visitor_id,
            visit_date=visit_date,
        )

        return self._pricing_engine.calculate_price(fraction, context)

    def calculate_total_price(
        self,
        fractions: List[DroppedFraction],
        city: Optional[str] = None,
        customer_type: Optional[str] = None,
        visitor_id: Optional[str] = None,
        visit_date: Optional[datetime] = None,
    ) -> Price:
        """Calculate total price for multiple dropped fractions.

        Args:
            fractions: List of dropped fractions to price
            city: The city for city-specific pricing
            customer_type: The customer type ('individual' for private, 'business' for business)
            visitor_id: The unique identifier for the visitor (needed for exemption tracking)
            visit_date: The date of the visit (needed for calendar year exemptions)

        Returns:
            Total price for all dropped fractions
        """
        total_price = Price(0, Currency.EUR)

        for fraction in fractions:
            fraction_price = self.calculate_price(
                fraction, city, customer_type, visitor_id, visit_date
            )
            total_price = total_price.add(fraction_price)

        return total_price
