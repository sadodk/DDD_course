"""Tests for VisitRepository interface contract."""

import pytest
from abc import ABC
from datetime import datetime
from domain.repositories.visit_repository import VisitRepository
from domain.entities.visit import Visit
from domain.types import VisitId, PersonId, Year, Month
from domain.dropped_fraction import DroppedFraction, FractionType
from domain.weight import Weight


class TestVisitRepositoryInterface:
    """Tests to ensure VisitRepository follows the abstract contract."""

    def test_visit_repository_is_abstract(self):
        """Test that VisitRepository is an abstract class."""
        assert issubclass(VisitRepository, ABC)

        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            VisitRepository()  # type: ignore

    def test_visit_repository_has_required_methods(self):
        """Test that VisitRepository defines all required abstract methods."""
        expected_methods = {
            "find_by_id",
            "save",
            "find_visits_by_visitor",
            "find_visits_for_person_in_month",
            "count_visits_for_person_in_month",
            "find_visits_by_date_range",
            "delete",
            "exists",
            "clear_all_visits",
        }

        actual_methods = set(VisitRepository.__abstractmethods__)
        assert actual_methods == expected_methods

    def test_concrete_implementation_must_implement_all_methods(self):
        """Test that concrete implementations must implement all abstract methods."""

        # Incomplete implementation should fail
        class IncompleteRepository(VisitRepository):
            def find_by_id(self, visit_id: VisitId):
                pass

            # Missing other required methods

        with pytest.raises(TypeError):
            IncompleteRepository()  # type: ignore

    def test_complete_implementation_can_be_instantiated(self):
        """Test that complete implementations can be instantiated."""

        class CompleteRepository(VisitRepository):
            def find_by_id(self, visit_id: VisitId):
                return None

            def save(self, visit: Visit) -> None:
                pass

            def find_visits_by_visitor(self, visitor_id: PersonId):
                return []

            def find_visits_for_person_in_month(
                self, visitor_id: PersonId, year: Year, month: Month
            ):
                return []

            def count_visits_for_person_in_month(
                self, visitor_id: PersonId, year: Year, month: Month
            ) -> int:
                return 0

            def find_visits_by_date_range(
                self, start_date: datetime, end_date: datetime
            ):
                return []

            def delete(self, visit_id: VisitId) -> bool:
                return False

            def exists(self, visit_id: VisitId) -> bool:
                return False

            def clear_all_visits(self) -> None:
                pass

        # Should be able to instantiate
        repo = CompleteRepository()
        assert isinstance(repo, VisitRepository)

    def test_repository_method_signatures(self):
        """Test that repository methods have correct signatures."""

        class TestRepository(VisitRepository):
            def find_by_id(self, visit_id: VisitId):
                return None

            def save(self, visit: Visit) -> None:
                pass

            def find_visits_by_visitor(self, visitor_id: PersonId):
                return []

            def find_visits_for_person_in_month(
                self, visitor_id: PersonId, year: Year, month: Month
            ):
                return []

            def count_visits_for_person_in_month(
                self, visitor_id: PersonId, year: Year, month: Month
            ) -> int:
                return 0

            def find_visits_by_date_range(
                self, start_date: datetime, end_date: datetime
            ):
                return []

            def delete(self, visit_id: VisitId) -> bool:
                return False

            def exists(self, visit_id: VisitId) -> bool:
                return False

            def clear_all_visits(self) -> None:
                pass

        repo = TestRepository()

        # Test method signatures work with expected types
        visit_id = VisitId("visit123")
        visitor_id = PersonId("user123")
        visit = Visit(
            id=visit_id,
            visitor_id=visitor_id,
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=[DroppedFraction(FractionType.GREEN_WASTE, Weight(10))],
        )

        # These should not raise type errors
        repo.find_by_id(visit_id)
        repo.save(visit)
        repo.find_visits_by_visitor(visitor_id)
        repo.find_visits_for_person_in_month(visitor_id, Year(2025), Month(9))
        repo.count_visits_for_person_in_month(visitor_id, Year(2025), Month(9))
        repo.find_visits_by_date_range(datetime(2025, 9, 1), datetime(2025, 9, 30))
        repo.delete(visit_id)
        repo.exists(visit_id)
        repo.clear_all_visits()
