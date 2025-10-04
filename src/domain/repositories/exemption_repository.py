"""Interface definition for the exemption repository.

This repository is responsible for tracking construction waste exemptions
for business customers, specifically for Oak City's tiered pricing system.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple


class ExemptionRepository(ABC):
    """Repository interface for tracking construction waste exemptions.

    This repository tracks the cumulative construction waste dropped by business customers
    throughout a calendar year and supports the tiered pricing structure where
    certain amounts are charged at different rates.
    """

    @abstractmethod
    def get_used_exemption(self, visitor_id: str, year: int) -> float:
        """Get the amount of exemption already used by a visitor in a given year.

        Args:
            visitor_id: The unique identifier for the visitor
            year: The calendar year to check

        Returns:
            The weight in kg of exemption already used (0 if none used)
        """
        pass

    @abstractmethod
    def record_waste(
        self, visitor_id: str, weight_kg: float, visit_date: datetime
    ) -> None:
        """Record construction waste dropped by a visitor.

        This updates the cumulative exemption usage for the visitor
        in the calendar year of the visit.

        Args:
            visitor_id: The unique identifier for the visitor
            weight_kg: The weight of construction waste in kg
            visit_date: The date of the visit
        """
        pass

    @abstractmethod
    def calculate_tiered_weights(
        self,
        visitor_id: str,
        weight_kg: float,
        visit_date: datetime,
        tier_limit_kg: float = 1000.0,
    ) -> Tuple[float, float]:
        """Calculate tiered weight amounts for construction waste.

        Returns the weight amounts for low-rate (≤tier_limit_kg) and high-rate (>tier_limit_kg)
        pricing tiers, taking into account previous exemption usage.

        Args:
            visitor_id: The unique identifier for the visitor
            weight_kg: The weight of construction waste for this visit
            visit_date: The date of the visit
            tier_limit_kg: The limit for the lower tier pricing (default: 1000.0 kg)

        Returns:
            Tuple of (low_tier_weight_kg, high_tier_weight_kg)
        """
        pass

    @abstractmethod
    def clear_all_exemptions(self) -> None:
        """Clear all exemption tracking data.

        This is primarily useful for testing scenarios.
        """
        pass

    @abstractmethod
    def get_total_exemption_usage_for_year(self, visitor_id: str, year: int) -> float:
        """Get total exemption usage for a visitor in a specific year.

        Args:
            visitor_id: The unique identifier for the visitor
            year: The calendar year to check

        Returns:
            Total exemption used in kg for that year
        """
        pass
