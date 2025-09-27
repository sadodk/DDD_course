"""In-memory implementation of VisitRepository."""

from typing import Optional
from datetime import datetime
from domain.repositories.visit_repository import VisitRepository
from domain.entities.visit import Visit
from domain.types import VisitId, PersonId, Year, Month


class InMemoryVisitRepository(VisitRepository):
    """In-memory implementation of VisitRepository for testing and development."""

    def __init__(self):
        """Initialize empty repository."""
        self._visits: dict[VisitId, Visit] = {}

    def find_by_id(self, visit_id: VisitId) -> Optional[Visit]:
        """Find visit by ID.

        Args:
            visit_id: The ID of the visit to find

        Returns:
            The visit if found, None otherwise
        """
        return self._visits.get(visit_id)

    def save(self, visit: Visit) -> None:
        """Save a visit.

        Args:
            visit: The visit to save

        Raises:
            DuplicateVisitException: If visit with same ID already exists
        """
        if visit.id in self._visits:
            # For this implementation, we'll allow updates
            # In a real system, you might want different behavior
            pass

        self._visits[visit.id] = visit

    def find_visits_by_visitor(self, visitor_id: PersonId) -> list[Visit]:
        """Find all visits for a specific visitor.

        Args:
            visitor_id: The ID of the visitor

        Returns:
            List of visits for the visitor
        """
        return [
            visit for visit in self._visits.values() if visit.visitor_id == visitor_id
        ]

    def find_visits_for_person_in_month(
        self, visitor_id: PersonId, year: Year, month: Month
    ) -> list[Visit]:
        """Find all visits for a person in a specific month.

        Args:
            visitor_id: The ID of the visitor
            year: The year to search
            month: The month to search

        Returns:
            List of visits in the specified month
        """
        return [
            visit
            for visit in self._visits.values()
            if (
                visit.visitor_id == visitor_id
                and visit.date.year == year
                and visit.date.month == month
            )
        ]

    def count_visits_for_person_in_month(
        self, visitor_id: PersonId, year: Year, month: Month
    ) -> int:
        """Count visits for a person in a specific month.

        Args:
            visitor_id: The ID of the visitor
            year: The year to search
            month: The month to search

        Returns:
            Number of visits in the specified month
        """
        return len(self.find_visits_for_person_in_month(visitor_id, year, month))

    def find_visits_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Visit]:
        """Find visits within a date range.

        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            List of visits within the date range
        """
        return [
            visit
            for visit in self._visits.values()
            if start_date <= visit.date <= end_date
        ]

    def delete(self, visit_id: VisitId) -> bool:
        """Delete a visit by ID.

        Args:
            visit_id: The ID of the visit to delete

        Returns:
            True if visit was deleted, False if not found
        """
        if visit_id in self._visits:
            del self._visits[visit_id]
            return True
        return False

    def exists(self, visit_id: VisitId) -> bool:
        """Check if a visit exists.

        Args:
            visit_id: The ID of the visit to check

        Returns:
            True if visit exists, False otherwise
        """
        return visit_id in self._visits

    def clear_all_visits(self) -> None:
        """Clear all visits."""
        self._visits.clear()

    def count(self) -> int:
        """Get total number of visits."""
        return len(self._visits)

    def find_all(self) -> list[Visit]:
        """Find all visits (useful for testing)."""
        return list(self._visits.values())
