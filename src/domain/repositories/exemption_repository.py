"""Interface definition for the exemption repository.

This repository is responsible for tracking construction waste exemptions
for entities (businesses and households), specifically for Oak City's tiered pricing system.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple, Optional, Union
from domain.types import BusinessId, PersonId, HouseholdId

# Define a type for entity IDs that can receive exemptions
EntityId = Union[BusinessId, HouseholdId]


class ExemptionRepository(ABC):
    """Repository interface for tracking construction waste exemptions.

    This repository tracks the cumulative construction waste dropped by entities
    (businesses and households) throughout a calendar year and supports the
    tiered pricing structure where certain amounts are charged at different rates.
    """

    @abstractmethod
    def get_used_exemption(self, entity_id: EntityId, year: int) -> float:
        """Get the amount of exemption already used by an entity in a given year.

        Args:
            entity_id: The unique identifier for the business or household
            year: The calendar year to check

        Returns:
            The weight in kg of exemption already used (0 if none used)
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def clear_all_exemptions(self) -> None:
        """Clear all exemption tracking data.

        This is primarily useful for testing scenarios.
        """
        pass

    @abstractmethod
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
        pass
