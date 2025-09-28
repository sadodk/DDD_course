from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Iterable
from domain.price import Price, Currency
from domain.weight import Weight


class FractionType(Enum):
    GREEN_WASTE = "Green waste"
    CONSTRUCTION_WASTE = "Construction waste"

    @staticmethod
    def from_string(label: str) -> FractionType:
        if label == "Green waste":
            return FractionType.GREEN_WASTE
        if label == "Construction waste":
            return FractionType.CONSTRUCTION_WASTE

        raise ValueError("incorrect fraction type")

    def __str__(self):
        return str(self.value)


@dataclass(frozen=True)
class DroppedFraction:
    fraction_type: FractionType
    weight: Weight

    def __post_init__(self):
        if not isinstance(self.fraction_type, FractionType):
            raise ValueError("fraction_type is invalid")

        if not isinstance(self.weight, Weight):
            raise ValueError("weight is invalid")

    def price(self, city: str | None = None, customer_type: str | None = None) -> Price:
        """Calculate price for this dropped fraction based on city and customer type.

        Args:
            city: The city for city-specific pricing
            customer_type: The customer type ('individual' for private, 'business' for business)

        Returns:
            Price for this dropped fraction
        """
        # Import here to avoid circular dependencies
        from domain.business_rules.pricing_rule_engine import PricingRuleEngine
        from domain.business_rules.interface_pricing_rules import PricingContext

        # Create pricing context from parameters
        context = PricingContext(customer_type=customer_type, city=city)

        # Use pricing rule engine to calculate price
        engine = PricingRuleEngine()
        return engine.calculate_price(self, context)

    @staticmethod
    def sum(
        dropped_fractions: Iterable[DroppedFraction],
        city: str | None = None,
        customer_type: str | None = None,
    ) -> Price:
        total_price = Price(0, Currency.EUR)
        for fraction in dropped_fractions:
            total_price = total_price.add(fraction.price(city, customer_type))
        return total_price
