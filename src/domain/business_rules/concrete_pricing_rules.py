"""Concrete pricing rules for specific business scenarios."""

from typing import Optional
from domain.business_rules.interface_pricing_rules import PricingRule, PricingContext
from domain.values.dropped_fraction import DroppedFraction, FractionType
from domain.values.price import Price, Currency
from domain.services.construction_waste_exemption import (
    ConstructionWasteExemptionService,
)


class OakCityBusinessConstructionExemptionRule(PricingRule):
    """Pricing rule for Oak City business customers with construction waste exemptions.

    Business customers in Oak City get exemptions on construction waste:
    - First 1000kg per calendar year: 0.21 euro/kg
    - Over 1000kg: 0.29 euro/kg

    Exemptions reset every calendar year.
    """

    LOW_RATE = 0.21  # euro/kg for first 1000kg
    HIGH_RATE = 0.29  # euro/kg over 1000kg

    def __init__(
        self, exemption_service: Optional[ConstructionWasteExemptionService] = None
    ):
        """Initialize with an exemption tracking service.

        Args:
            exemption_service: Service for tracking exemptions. If None, creates new instance.
        """
        self._exemption_service = (
            exemption_service or ConstructionWasteExemptionService()
        )

    def can_apply(self, context: PricingContext) -> bool:
        """Applies to Oak City business customers dropping construction waste."""
        return (
            context.city == "Oak City"
            and context.is_business_customer()
            and context.visitor_id is not None
            and context.visit_date is not None
        )

    def calculate_price(
        self, fraction: DroppedFraction, context: PricingContext
    ) -> Price:
        """Calculate price using Oak City business construction waste exemption rules."""
        # Type guards for required fields
        if context.visitor_id is None or context.visit_date is None:
            raise ValueError(
                "visitor_id and visit_date are required for exemption tracking"
            )

        # Only apply to construction waste
        if fraction.fraction_type != FractionType.CONSTRUCTION_WASTE:
            # Fall back to regular Oak City business rate for other fraction types
            rate = 0.08 if fraction.fraction_type == FractionType.GREEN_WASTE else 0.21
            return Price(rate * fraction.weight.weight, Currency.EUR)

        # Apply tiered pricing for construction waste
        weight_kg = fraction.weight.weight
        low_rate_weight, high_rate_weight = (
            self._exemption_service.calculate_tiered_pricing(
                context.visitor_id, weight_kg, context.visit_date
            )
        )

        # Calculate total price
        low_rate_amount = self.LOW_RATE * low_rate_weight
        high_rate_amount = self.HIGH_RATE * high_rate_weight
        total_price = Price(low_rate_amount + high_rate_amount, Currency.EUR)

        # Record the construction waste for future exemption tracking
        self._exemption_service.record_construction_waste(
            context.visitor_id, weight_kg, context.visit_date
        )

        return total_price

    def get_priority(self) -> int:
        """Very high priority - should override regular Oak City rule for business customers."""
        return 5


class PinevillePricingRule(PricingRule):
    """Pricing rule for Pineville city."""

    INDIVIDUAL_RATES = {"Green waste": 0.10, "Construction waste": 0.15}

    BUSINESS_RATES = {"Green waste": 0.12, "Construction waste": 0.13}

    def can_apply(self, context: PricingContext) -> bool:
        """Applies to visitors from Pineville."""
        return context.city == "Pineville"

    def calculate_price(
        self, fraction: DroppedFraction, context: PricingContext
    ) -> Price:
        """Calculate price using Pineville rates."""
        fraction_name = str(fraction.fraction_type)

        if context.is_business_customer():
            rate = self.BUSINESS_RATES.get(fraction_name, 0.0)
        else:
            rate = self.INDIVIDUAL_RATES.get(fraction_name, 0.0)

        return Price(rate, Currency.EUR).times(fraction.weight.weight)

    def get_priority(self) -> int:
        """High priority for city-specific rules."""
        return 10


class OakCityPricingRule(PricingRule):
    """Pricing rule for Oak City."""

    INDIVIDUAL_RATES = {"Green waste": 0.08, "Construction waste": 0.19}

    BUSINESS_RATES = {"Green waste": 0.08, "Construction waste": 0.21}

    def can_apply(self, context: PricingContext) -> bool:
        """Applies to visitors from Oak City."""
        return context.city == "Oak City"

    def calculate_price(
        self, fraction: DroppedFraction, context: PricingContext
    ) -> Price:
        """Calculate price using Oak City rates."""
        fraction_name = str(fraction.fraction_type)

        if context.is_business_customer():
            rate = self.BUSINESS_RATES.get(fraction_name, 0.0)
        else:
            rate = self.INDIVIDUAL_RATES.get(fraction_name, 0.0)

        return Price(rate, Currency.EUR).times(fraction.weight.weight)

    def get_priority(self) -> int:
        """High priority for city-specific rules."""
        return 10


class BusinessCustomerDiscountRule(PricingRule):
    """General discount rule for business customers from unknown cities."""

    DISCOUNT_RATES = {"Green waste": 0.10, "Construction waste": 0.19}

    def can_apply(self, context: PricingContext) -> bool:
        """Applies to business customers from cities without specific rules."""
        return context.is_business_customer() and context.city not in [
            "Pineville",
            "Oak City",
        ]

    def calculate_price(
        self, fraction: DroppedFraction, context: PricingContext
    ) -> Price:
        """Calculate discounted price for business customers."""
        fraction_name = str(fraction.fraction_type)
        rate = self.DISCOUNT_RATES.get(fraction_name, 0.0)

        return Price(rate, Currency.EUR).times(fraction.weight.weight)

    def get_priority(self) -> int:
        """Medium priority for customer type rules."""
        return 50


class DefaultPricingRule(PricingRule):
    """Default pricing rule that serves as fallback when no other rules apply."""

    DEFAULT_RATES = {"Green waste": 0.10, "Construction waste": 0.19}

    def can_apply(self, context: PricingContext) -> bool:
        """Default rule always applies as fallback."""
        return True

    def calculate_price(
        self, fraction: DroppedFraction, context: PricingContext
    ) -> Price:
        """Calculate price using default rates."""
        fraction_name = str(fraction.fraction_type)
        rate = self.DEFAULT_RATES.get(fraction_name, 0.0)

        from domain.values.price import Currency

        return Price(rate, Currency.EUR).times(fraction.weight.weight)

    def get_priority(self) -> int:
        """Lowest priority - used as fallback."""
        return 1000
