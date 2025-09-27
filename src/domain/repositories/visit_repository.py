"""Visit repository interface - Abstract contract for visit persistence."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from domain.entities.visit import Visit
from domain.types import VisitId, PersonId, Year, Month


class VisitRepository(ABC):
    """
    Repository interface for Visit entities.

    This is a pure domain interface (port) that defines what operations
    the domain needs for visit persistence. The actual implementation
    (adapter) will be provided by the infrastructure layer.

    Key domain operations:
    - Finding visits by visitor and time period (for monthly surcharge logic)
    - Saving visits
    - Querying visit history for business rules
    """

    @abstractmethod
    def find_by_id(self, visit_id: VisitId) -> Optional[Visit]:
        """
        Find a visit by its unique ID.

        Args:
            visit_id: The unique identifier of the visit

        Returns:
            The visit if found, None otherwise
        """
        pass

    @abstractmethod
    def save(self, visit: Visit) -> None:
        """
        Save a visit (insert or update).

        Args:
            visit: The visit entity to save

        Raises:
            RepositoryException: If the save operation fails
        """
        pass

    @abstractmethod
    def find_visits_by_visitor(self, visitor_id: PersonId) -> List[Visit]:
        """
        Find all visits made by a specific visitor.

        Args:
            visitor_id: The visitor's unique identifier

        Returns:
            List of all visits made by the visitor, ordered by date
        """
        pass

    @abstractmethod
    def find_visits_for_person_in_month(
        self, visitor_id: PersonId, year: Year, month: Month
    ) -> List[Visit]:
        """
        Find all visits made by a visitor in a specific month.

        This is a key method for the monthly surcharge business rule.

        Args:
            visitor_id: The visitor's unique identifier
            year: The year to search in
            month: The month to search in (1-12)

        Returns:
            List of visits made by the visitor in the specified month
        """
        pass

    @abstractmethod
    def count_visits_for_person_in_month(
        self, visitor_id: PersonId, year: Year, month: Month
    ) -> int:
        """
        Count visits made by a visitor in a specific month.

        Optimized version of find_visits_for_person_in_month when
        only the count is needed (for surcharge calculation).

        Args:
            visitor_id: The visitor's unique identifier
            year: The year to search in
            month: The month to search in (1-12)

        Returns:
            Number of visits made by the visitor in the specified month
        """
        pass

    @abstractmethod
    def find_visits_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Visit]:
        """
        Find all visits within a date range.

        Args:
            start_date: Start of the date range (inclusive)
            end_date: End of the date range (inclusive)

        Returns:
            List of visits within the specified date range
        """
        pass

    @abstractmethod
    def delete(self, visit_id: VisitId) -> bool:
        """
        Delete a visit by ID.

        Args:
            visit_id: The unique identifier of the visit to delete

        Returns:
            True if the visit was deleted, False if not found
        """
        pass

    @abstractmethod
    def exists(self, visit_id: VisitId) -> bool:
        """
        Check if a visit exists.

        Args:
            visit_id: The unique identifier to check

        Returns:
            True if the visit exists, False otherwise
        """
        pass

    @abstractmethod
    def clear_all_visits(self) -> None:
        """
        Clear all visits from the repository.

        This method supports the scenario reset functionality
        where all state needs to be cleared between test scenarios.

        Warning:
            This is a destructive operation that removes all visits.
            Should be used carefully, typically only in test scenarios.
        """
        pass
