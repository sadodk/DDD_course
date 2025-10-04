"""In-memory implementation of the Household repository."""

from typing import Dict, Optional, List
from domain.entities.household import Household
from domain.entities.visitor import Visitor
from domain.repositories.household_repository import HouseholdRepository
from domain.types import HouseholdId, PersonId
from application.external_visitor_adapter import ExternalVisitorAdapter


class InMemoryHouseholdRepository(HouseholdRepository):
    """
    In-memory implementation of the Household repository.

    This repository maintains the consistency boundary of the Household aggregate,
    ensuring that households and their residents are managed correctly.
    """

    def __init__(self, visitor_adapter: ExternalVisitorAdapter):
        """
        Initialize the repository with external visitor adapter.

        Args:
            visitor_adapter: Anti-corruption layer for external visitor service
        """
        self._visitor_adapter = visitor_adapter
        self._households: Dict[HouseholdId, Household] = {}
        self._visitor_to_household_map: Dict[PersonId, HouseholdId] = {}

    def save(self, household: Household) -> None:
        """
        Save or update a household entity and all its residents.

        Args:
            household: Household aggregate root to save
        """
        self._households[household.household_id] = household

        # Update visitor to household map
        for resident in household.residents:
            self._visitor_to_household_map[resident.id] = household.household_id

    def find_by_id(self, household_id: HouseholdId) -> Optional[Household]:
        """
        Find a household by its ID.

        Args:
            household_id: Unique identifier for the household

        Returns:
            Household entity if found, None otherwise
        """
        return self._households.get(household_id)

    def find_by_visitor_id(self, visitor_id: PersonId) -> Optional[Household]:
        """
        Find a household by the ID of one of its residents.

        Args:
            visitor_id: ID of a visitor (resident)

        Returns:
            Household entity if found, None otherwise
        """
        if visitor_id not in self._visitor_to_household_map:
            # Try to find the household through the adapter
            visitor = self._visitor_adapter.get_visitor(visitor_id)
            if not visitor:
                return None

            if visitor.type != "individual":
                return None  # Only individual visitors belong to households

            return self.get_or_create_household_for_visitor(visitor)

        household_id = self._visitor_to_household_map[visitor_id]
        return self._households.get(household_id)

    def get_or_create_household_for_visitor(self, visitor: Visitor) -> Household:
        """
        Get an existing household for a visitor or create a new one if none exists.

        Args:
            visitor: A visitor entity that should be part of a household

        Returns:
            Existing or newly created household entity
        """
        if visitor.type != "individual":
            raise ValueError("Only individual visitors can be part of households")

        # Generate household ID from visitor
        household_id = Household.create_household_id(visitor.city, visitor.address)

        # If we already have this household, add the visitor and return it
        if household_id in self._households:
            household = self._households[household_id]
            if not household.has_resident(visitor.id):
                household.add_resident(visitor)
                self._visitor_to_household_map[visitor.id] = household_id
            return household

        # Otherwise, create a new household
        household = Household(
            household_id=household_id, address=visitor.address, city=visitor.city
        )
        household.add_resident(visitor)

        # Save the new household
        self.save(household)

        return household

    def get_all(self) -> List[Household]:
        """
        Get all households.

        Returns:
            List of all household entities
        """
        return list(self._households.values())

    def clear(self) -> None:
        """Clear all households from the repository."""
        self._households.clear()
        self._visitor_to_household_map.clear()
