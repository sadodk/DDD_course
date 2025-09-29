from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from domain.values.weight import Weight


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

    @staticmethod
    def from_string(fraction_type_str: str, weight_amount: int) -> DroppedFraction:
        """Create a DroppedFraction from string inputs.

        Args:
            fraction_type_str: String representation of fraction type
            weight_amount: Weight amount in kg (integer)

        Returns:
            DroppedFraction instance
        """
        fraction_type = FractionType.from_string(fraction_type_str)
        weight = Weight(weight_amount)
        return DroppedFraction(fraction_type, weight)
