"""In-memory implementation of the exemption repository."""

from datetime import datetime
from typing import Dict, Tuple

from domain.repositories.exemption_repository import ExemptionRepository, EntityId


class InMemoryExemptionRepository(ExemptionRepository):
    """In-memory implementation of the exemption repository.

    Stores exemption data in a dictionary keyed by (entity_id, year).
    """

    def __init__(self):
        """Initialize with an empty tracking dictionary."""
        # Key: (entity_id, year) -> cumulative_weight_kg
        self._exemption_usage: Dict[Tuple[EntityId, int], float] = {}

    def get_used_exemption(self, entity_id: EntityId, year: int) -> float:
        """Get the amount of exemption already used by an entity in a given year.

        Args:
            entity_id: The unique identifier for the business or household
            year: The calendar year to check

        Returns:
            The weight in kg of exemption already used (0 if none used)
        """
        return self._exemption_usage.get((entity_id, year), 0.0)

    def record_waste(
        self, entity_id: EntityId, weight_kg: float, visit_date: datetime
    ) -> None:
        """Record construction waste dropped by an entity.

        This updates the cumulative exemption usage for the entity
        in the calendar year of the visit.

        Args:
            entity_id: The unique identifier for the business or household
            weight_kg: The weight of construction waste in kg
            visit_date: The date of the visit
        """
        year = visit_date.year
        key = (entity_id, year)
        current_usage = self._exemption_usage.get(key, 0.0)
        self._exemption_usage[key] = current_usage + weight_kg

    def calculate_tiered_weights(
        self,
        entity_id: EntityId,
        weight_kg: float,
        visit_date: datetime,
        tier_limit_kg: float = 1000.0,
    ) -> Tuple[float, float]:
        """Calculate tiered weight amounts for construction waste.

        Returns the weight amounts for low-rate (≤tier_limit_kg) and high-rate (>tier_limit_kg)
        pricing tiers, taking into account previous exemption usage.

        Args:
            entity_id: The unique identifier for the business or household
            weight_kg: The weight of construction waste for this visit
            visit_date: The date of the visit
            tier_limit_kg: The limit for the lower tier pricing (default: 1000.0 kg)

        Returns:
            Tuple of (low_tier_weight_kg, high_tier_weight_kg)
        """
        year = visit_date.year
        already_used = self.get_used_exemption(entity_id, year)

        # Calculate how much exemption is still available
        remaining_exemption = max(0.0, tier_limit_kg - already_used)

        # Apply exemption to current visit
        low_rate_weight = min(weight_kg, remaining_exemption)
        high_rate_weight = max(0.0, weight_kg - remaining_exemption)

        return low_rate_weight, high_rate_weight

    def clear_all_exemptions(self) -> None:
        """Clear all exemption tracking data.

        This is primarily useful for testing scenarios.
        """
        self._exemption_usage.clear()

    def get_total_exemption_usage_for_year(
        self, entity_id: EntityId, year: int
    ) -> float:
        """Get total exemption usage for an entity in a specific year.

        Args:
            entity_id: The unique identifier for the business or household
            year: The calendar year to check

        Returns:
            Total exemption used in kg for that year
        """
        return self.get_used_exemption(entity_id, year)
