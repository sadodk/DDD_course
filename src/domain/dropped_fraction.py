from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from functools import reduce
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

    def price(self) -> Price:
        if self.fraction_type == FractionType.GREEN_WASTE:
            return Price(0.10, Currency.EUR).times(self.weight.weight)
        if self.fraction_type == FractionType.CONSTRUCTION_WASTE:
            return Price(0.15, Currency.EUR).times(self.weight.weight)

    @staticmethod
    def sum(dropped_fractions: list[DroppedFraction]) -> Price:
        return reduce(
            lambda price, dropped_fraction: price.add(dropped_fraction.price()),
            dropped_fractions,
            Price(0, Currency.EUR),
        )
