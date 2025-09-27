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
        # Default rates for private customers
        default_private_rates = {"green_waste": 0.10, "construction_waste": 0.19}

        # City-specific rates for private customers (existing behavior)
        city_private_rates = {
            "Pineville": {"green_waste": 0.10, "construction_waste": 0.15},
            "Oak City": {"green_waste": 0.08, "construction_waste": 0.19},
        }

        # Business customer rates by city
        city_business_rates = {
            "Pineville": {"green_waste": 0.12, "construction_waste": 0.13},
            "Oak City": {"green_waste": 0.08, "construction_waste": 0.21},
        }

        # Default business rates (same as private for now, but explicit)
        default_business_rates = {"green_waste": 0.10, "construction_waste": 0.19}

        # Determine which rate table to use
        if customer_type == "business":
            rates = (
                city_business_rates.get(city, default_business_rates)
                if city
                else default_business_rates
            )
        else:
            # Default to private customer rates for 'individual' or None
            rates = (
                city_private_rates.get(city, default_private_rates)
                if city
                else default_private_rates
            )

        if self.fraction_type == FractionType.GREEN_WASTE:
            rate = rates["green_waste"]
        elif self.fraction_type == FractionType.CONSTRUCTION_WASTE:
            rate = rates["construction_waste"]
        else:
            rate = 0

        return Price(rate, Currency.EUR).times(self.weight.weight)

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
