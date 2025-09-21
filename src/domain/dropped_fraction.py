from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Iterable
from domain.price import Price, Currency
from domain.weight import Weight


CITY_PRICING = {
    "Pineville": {"green_waste": 0.10, "construction_waste": 0.15},
    "Oak City": {"green_waste": 0.08, "construction_waste": 0.19},
}

DEFAULT_PRICING = {"green_waste": 0.10, "construction_waste": 0.19}


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

    def price(self, city: str | None = None) -> Price:
        # Get pricing for city or use default
        pricing = CITY_PRICING.get(city, DEFAULT_PRICING) if city else DEFAULT_PRICING

        if self.fraction_type == FractionType.GREEN_WASTE:
            rate = pricing["green_waste"]
        elif self.fraction_type == FractionType.CONSTRUCTION_WASTE:
            rate = pricing["construction_waste"]
        else:
            rate = 0

        return Price(rate, Currency.EUR).times(self.weight.weight)

    @staticmethod
    def sum(
        dropped_fractions: Iterable[DroppedFraction], city: str | None = None
    ) -> Price:
        total_price = Price(0, Currency.EUR)
        for fraction in dropped_fractions:
            total_price = total_price.add(fraction.price(city))
        return total_price
