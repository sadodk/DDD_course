"""Construction waste exemption tracking service for Oak City business customers.

This service tracks the cumulative construction waste dropped by business customers
in Oak City throughout a calendar year. It maintains exemption state that resets
annually and supports the tiered pricing structure where the first 1000kg is
charged at a lower rate.
"""

from typing import Dict, Tuple
from datetime import datetime


class ConstructionWasteExemptionService:
    """Domain service for tracking construction waste exemptions.

    Tracks cumulative construction waste per business customer per calendar year.
    Exemptions reset automatically at the start of each calendar year.
    """

    def __init__(self):
        """Initialize the exemption service with empty tracking."""
        # Key: (visitor_id, year) -> cumulative_weight_kg
        self._exemption_usage: Dict[Tuple[str, int], float] = {}

    def get_used_exemption(self, visitor_id: str, year: int) -> float:
        """Get the amount of exemption already used by a visitor in a given year.

        Args:
            visitor_id: The unique identifier for the visitor
            year: The calendar year to check

        Returns:
            The weight in kg of exemption already used (0 if none used)
        """
        return self._exemption_usage.get((visitor_id, year), 0.0)

    def record_construction_waste(
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
        year = visit_date.year
        key = (visitor_id, year)
        current_usage = self._exemption_usage.get(key, 0.0)
        self._exemption_usage[key] = current_usage + weight_kg

    def calculate_tiered_pricing(
        self, visitor_id: str, weight_kg: float, visit_date: datetime
    ) -> Tuple[float, float]:
        """Calculate tiered pricing amounts for construction waste.

        Returns the weight amounts for low-rate (≤1000kg) and high-rate (>1000kg)
        pricing tiers, taking into account previous exemption usage.

        Args:
            visitor_id: The unique identifier for the visitor
            weight_kg: The weight of construction waste for this visit
            visit_date: The date of the visit

        Returns:
            Tuple of (low_rate_weight_kg, high_rate_weight_kg)
        """
        year = visit_date.year
        already_used = self.get_used_exemption(visitor_id, year)

        # Constants
        EXEMPTION_LIMIT_KG = 1000.0

        # Calculate how much exemption is still available
        remaining_exemption = max(0.0, EXEMPTION_LIMIT_KG - already_used)

        # Apply exemption to current visit
        low_rate_weight = min(weight_kg, remaining_exemption)
        high_rate_weight = max(0.0, weight_kg - remaining_exemption)

        return low_rate_weight, high_rate_weight

    def clear_all_exemptions(self) -> None:
        """Clear all exemption tracking data.

        This is primarily useful for testing scenarios.
        """
        self._exemption_usage.clear()

    def get_total_exemption_usage_for_year(self, visitor_id: str, year: int) -> float:
        """Get total exemption usage for a visitor in a specific year.

        Args:
            visitor_id: The unique identifier for the visitor
            year: The calendar year to check

        Returns:
            Total exemption used in kg for that year
        """
        return self.get_used_exemption(visitor_id, year)
