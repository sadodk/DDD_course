"""Visitor repository interface - Abstract contract for visitor persistence."""

from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.visitor import Visitor
from domain.types import PersonId


class VisitorRepository(ABC):
    """
    Repository interface for Visitor entities.

    This is a pure domain interface (port) that defines what operations
    the domain needs for visitor persistence. The actual implementation
    (adapter) will be provided by the infrastructure layer.

    Follows the Dependency Inversion Principle:
    - Domain defines the interface it needs
    - Infrastructure implements the interface
    - Domain depends on abstraction, not concrete implementation
    """

    @abstractmethod
    def find_by_id(self, visitor_id: PersonId) -> Optional[Visitor]:
        """
        Find a visitor by their unique ID.

        Args:
            visitor_id: The unique identifier of the visitor

        Returns:
            The visitor if found, None otherwise
        """
        pass

    @abstractmethod
    def save(self, visitor: Visitor) -> None:
        """
        Save a visitor (insert or update).

        Args:
            visitor: The visitor entity to save

        Raises:
            RepositoryException: If the save operation fails
        """
        pass

    @abstractmethod
    def delete(self, visitor_id: PersonId) -> bool:
        """
        Delete a visitor by ID.

        Args:
            visitor_id: The unique identifier of the visitor to delete

        Returns:
            True if the visitor was deleted, False if not found
        """
        pass

    @abstractmethod
    def find_by_city(self, city: str) -> List[Visitor]:
        """
        Find all visitors from a specific city.

        Args:
            city: The city name to search for

        Returns:
            List of visitors from the specified city
        """
        pass

    @abstractmethod
    def find_by_card_id(self, card_id: str) -> Optional[Visitor]:
        """
        Find a visitor by their card ID.

        Args:
            card_id: The card ID to search for

        Returns:
            The visitor if found, None otherwise
        """
        pass

    @abstractmethod
    def exists(self, visitor_id: PersonId) -> bool:
        """
        Check if a visitor exists.

        Args:
            visitor_id: The unique identifier to check

        Returns:
            True if the visitor exists, False otherwise
        """
        pass

    @abstractmethod
    def find_all(self) -> List[Visitor]:
        """
        Retrieve all visitors.

        Returns:
            List of all visitors in the repository

        Note:
            This method should be used carefully in production
            as it may return a large dataset.
        """
        pass
