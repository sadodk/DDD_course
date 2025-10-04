"""Business repository interface for the Business aggregate."""

from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.business import Business
from domain.entities.visitor import Visitor
from domain.types import BusinessId, PersonId


class BusinessRepository(ABC):
    """
    Repository interface for the Business aggregate.

    This repository handles operations on the Business aggregate, ensuring
    consistency boundaries are maintained.
    """

    @abstractmethod
    def save(self, business: Business) -> None:
        """
        Save or update a business entity and all its employees.

        Args:
            business: Business aggregate root to save
        """
        pass

    @abstractmethod
    def find_by_id(self, business_id: BusinessId) -> Optional[Business]:
        """
        Find a business by its ID.

        Args:
            business_id: Unique identifier for the business

        Returns:
            Business entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_visitor_id(self, visitor_id: PersonId) -> Optional[Business]:
        """
        Find a business by the ID of one of its employees.

        Args:
            visitor_id: ID of a visitor (employee)

        Returns:
            Business entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_or_create_business_for_visitor(self, visitor: Visitor) -> Business:
        """
        Get an existing business for a visitor or create a new one if none exists.

        This is a key method for the anti-corruption layer as it handles
        the translation between the legacy visitor model and our business aggregate.

        Args:
            visitor: A visitor entity that should be part of a business

        Returns:
            Existing or newly created business entity
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Business]:
        """
        Get all businesses.

        Returns:
            List of all business entities
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all businesses from the repository."""
        pass
