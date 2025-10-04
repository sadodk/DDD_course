"""Household repository interface for the Household aggregate."""

from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.household import Household
from domain.entities.visitor import Visitor
from domain.types import HouseholdId, PersonId


class HouseholdRepository(ABC):
    """
    Repository interface for the Household aggregate.

    This repository handles operations on the Household aggregate, ensuring
    consistency boundaries are maintained for groups of individual visitors
    living at the same address.
    """

    @abstractmethod
    def save(self, household: Household) -> None:
        """
        Save or update a household entity and all its residents.

        Args:
            household: Household aggregate root to save
        """
        pass

    @abstractmethod
    def find_by_id(self, household_id: HouseholdId) -> Optional[Household]:
        """
        Find a household by its ID.

        Args:
            household_id: Unique identifier for the household

        Returns:
            Household entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_visitor_id(self, visitor_id: PersonId) -> Optional[Household]:
        """
        Find a household by the ID of one of its residents.

        Args:
            visitor_id: ID of a visitor (resident)

        Returns:
            Household entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_or_create_household_for_visitor(self, visitor: Visitor) -> Household:
        """
        Get an existing household for a visitor or create a new one if none exists.

        This method identifies households by address and city, grouping individual
        visitors at the same address into a single household.

        Args:
            visitor: A visitor entity that should be part of a household

        Returns:
            Existing or newly created household entity
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Household]:
        """
        Get all households.

        Returns:
            List of all household entities
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all households from the repository."""
        pass
