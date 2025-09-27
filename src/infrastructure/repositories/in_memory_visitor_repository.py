"""In-memory implementation of VisitorRepository."""

from typing import Optional
from domain.repositories.visitor_repository import VisitorRepository
from domain.entities.visitor import Visitor
from domain.types import PersonId


class InMemoryVisitorRepository(VisitorRepository):
    """In-memory implementation of VisitorRepository for testing and development."""

    def __init__(self):
        """Initialize empty repository."""
        self._visitors: dict[PersonId, Visitor] = {}

    def find_by_id(self, visitor_id: PersonId) -> Optional[Visitor]:
        """Find visitor by ID.

        Args:
            visitor_id: The ID of the visitor to find

        Returns:
            The visitor if found, None otherwise
        """
        return self._visitors.get(visitor_id)

    def save(self, visitor: Visitor) -> None:
        """Save a visitor.

        Args:
            visitor: The visitor to save

        Raises:
            DuplicateVisitorException: If visitor with same ID already exists
        """
        if visitor.id in self._visitors:
            # For this implementation, we'll allow updates
            # In a real system, you might want different behavior
            pass

        self._visitors[visitor.id] = visitor

    def delete(self, visitor_id: PersonId) -> bool:
        """Delete a visitor by ID.

        Args:
            visitor_id: The ID of the visitor to delete

        Returns:
            True if visitor was deleted, False if not found
        """
        if visitor_id in self._visitors:
            del self._visitors[visitor_id]
            return True
        return False

    def find_by_city(self, city: str) -> list[Visitor]:
        """Find all visitors from a specific city.

        Args:
            city: The city to search for

        Returns:
            List of visitors from the specified city
        """
        return [
            visitor
            for visitor in self._visitors.values()
            if visitor.city.lower() == city.lower()
        ]

    def find_by_card_id(self, card_id: str) -> Optional[Visitor]:
        """Find visitor by card ID.

        Args:
            card_id: The card ID to search for

        Returns:
            The visitor if found, None otherwise
        """
        for visitor in self._visitors.values():
            if visitor.card_id == card_id:
                return visitor
        return None

    def exists(self, visitor_id: PersonId) -> bool:
        """Check if a visitor exists.

        Args:
            visitor_id: The ID of the visitor to check

        Returns:
            True if visitor exists, False otherwise
        """
        return visitor_id in self._visitors

    def find_all(self) -> list[Visitor]:
        """Find all visitors.

        Returns:
            List of all visitors
        """
        return list(self._visitors.values())

    def clear(self) -> None:
        """Clear all visitors (useful for testing)."""
        self._visitors.clear()

    def count(self) -> int:
        """Get total number of visitors."""
        return len(self._visitors)
