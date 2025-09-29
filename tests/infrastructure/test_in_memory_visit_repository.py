"""Tests for InMemoryVisitRepository."""

from datetime import datetime
from infrastructure.repositories.in_memory_visit_repository import (
    InMemoryVisitRepository,
)
from domain.entities.visit import Visit
from domain.types import VisitId, PersonId, Year, Month
from domain.values.dropped_fraction import DroppedFraction, FractionType
from domain.values.weight import Weight


class TestInMemoryVisitRepository:
    """Test cases for InMemoryVisitRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = InMemoryVisitRepository()

        # Test data
        self.visitor1_id = PersonId("visitor1")
        self.visitor2_id = PersonId("visitor2")

        self.visit1 = Visit(
            id=VisitId("visit1"),
            visitor_id=self.visitor1_id,
            date=datetime(2025, 9, 5, 10, 0),
            dropped_fractions=[DroppedFraction(FractionType.GREEN_WASTE, Weight(10))],
        )

        self.visit2 = Visit(
            id=VisitId("visit2"),
            visitor_id=self.visitor1_id,  # Same visitor
            date=datetime(2025, 9, 15, 14, 0),
            dropped_fractions=[
                DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(5))
            ],
        )

        self.visit3 = Visit(
            id=VisitId("visit3"),
            visitor_id=self.visitor2_id,  # Different visitor
            date=datetime(2025, 9, 25, 11, 0),
            dropped_fractions=[
                DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(3))
            ],
        )

        self.visit4 = Visit(
            id=VisitId("visit4"),
            visitor_id=self.visitor1_id,  # Same visitor, different month
            date=datetime(2025, 10, 5, 9, 0),
            dropped_fractions=[DroppedFraction(FractionType.GREEN_WASTE, Weight(8))],
        )

    def test_save_and_find_by_id(self):
        """Test saving and finding visits by ID."""
        # Initially empty
        assert self.repo.find_by_id(self.visit1.id) is None

        # Save visit
        self.repo.save(self.visit1)

        # Should be able to find it
        found = self.repo.find_by_id(self.visit1.id)
        assert found is not None
        assert found.id == self.visit1.id
        assert found.visitor_id == self.visit1.visitor_id
        assert found.date == self.visit1.date

    def test_save_allows_updates(self):
        """Test that saving an existing visit updates it."""
        # Save original visit
        self.repo.save(self.visit1)

        # Update visit
        updated_visit = Visit(
            id=self.visit1.id,  # Same ID
            visitor_id=self.visit1.visitor_id,
            date=datetime(2025, 9, 6, 15, 0),  # Different date
            dropped_fractions=[
                DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(15))
            ],  # Different fraction
        )

        # Save updated version
        self.repo.save(updated_visit)

        # Should retrieve updated version
        found = self.repo.find_by_id(self.visit1.id)
        assert found is not None
        assert found.date == datetime(2025, 9, 6, 15, 0)
        assert (
            found.dropped_fractions[0].fraction_type == FractionType.CONSTRUCTION_WASTE
        )

    def test_delete(self):
        """Test deleting visits."""
        # Save visit
        self.repo.save(self.visit1)
        assert self.repo.exists(self.visit1.id)

        # Delete should return True
        result = self.repo.delete(self.visit1.id)
        assert result is True

        # Should no longer exist
        assert not self.repo.exists(self.visit1.id)
        assert self.repo.find_by_id(self.visit1.id) is None

        # Deleting non-existent visit should return False
        result = self.repo.delete(VisitId("nonexistent"))
        assert result is False

    def test_exists(self):
        """Test checking if visits exist."""
        assert not self.repo.exists(self.visit1.id)

        self.repo.save(self.visit1)
        assert self.repo.exists(self.visit1.id)

        self.repo.delete(self.visit1.id)
        assert not self.repo.exists(self.visit1.id)

    def test_find_visits_by_visitor(self):
        """Test finding visits by visitor."""
        # Save test visits
        self.repo.save(self.visit1)  # visitor1
        self.repo.save(self.visit2)  # visitor1
        self.repo.save(self.visit3)  # visitor2
        self.repo.save(self.visit4)  # visitor1

        # Find visits for visitor1
        visitor1_visits = self.repo.find_visits_by_visitor(self.visitor1_id)
        assert len(visitor1_visits) == 3
        visit_ids = {v.id for v in visitor1_visits}
        assert self.visit1.id in visit_ids
        assert self.visit2.id in visit_ids
        assert self.visit4.id in visit_ids

        # Find visits for visitor2
        visitor2_visits = self.repo.find_visits_by_visitor(self.visitor2_id)
        assert len(visitor2_visits) == 1
        assert visitor2_visits[0].id == self.visit3.id

        # Non-existent visitor
        empty_results = self.repo.find_visits_by_visitor(PersonId("nonexistent"))
        assert len(empty_results) == 0

    def test_find_visits_for_person_in_month(self):
        """Test finding visits for a person in a specific month."""
        # Save test visits
        self.repo.save(self.visit1)  # visitor1, September
        self.repo.save(self.visit2)  # visitor1, September
        self.repo.save(self.visit3)  # visitor2, September
        self.repo.save(self.visit4)  # visitor1, October

        # Find visitor1's visits in September
        sept_visits = self.repo.find_visits_for_person_in_month(
            self.visitor1_id, Year(2025), Month(9)
        )
        assert len(sept_visits) == 2
        visit_ids = {v.id for v in sept_visits}
        assert self.visit1.id in visit_ids
        assert self.visit2.id in visit_ids

        # Find visitor1's visits in October
        oct_visits = self.repo.find_visits_for_person_in_month(
            self.visitor1_id, Year(2025), Month(10)
        )
        assert len(oct_visits) == 1
        assert oct_visits[0].id == self.visit4.id

        # Find visitor2's visits in September
        visitor2_sept = self.repo.find_visits_for_person_in_month(
            self.visitor2_id, Year(2025), Month(9)
        )
        assert len(visitor2_sept) == 1
        assert visitor2_sept[0].id == self.visit3.id

        # Non-existent month
        empty_month = self.repo.find_visits_for_person_in_month(
            self.visitor1_id, Year(2025), Month(11)
        )
        assert len(empty_month) == 0

    def test_count_visits_for_person_in_month(self):
        """Test counting visits for a person in a specific month."""
        # Save test visits
        self.repo.save(self.visit1)  # visitor1, September
        self.repo.save(self.visit2)  # visitor1, September
        self.repo.save(self.visit3)  # visitor2, September
        self.repo.save(self.visit4)  # visitor1, October

        # Count visitor1's visits in September
        count = self.repo.count_visits_for_person_in_month(
            self.visitor1_id, Year(2025), Month(9)
        )
        assert count == 2

        # Count visitor1's visits in October
        count = self.repo.count_visits_for_person_in_month(
            self.visitor1_id, Year(2025), Month(10)
        )
        assert count == 1

        # Count visitor2's visits in September
        count = self.repo.count_visits_for_person_in_month(
            self.visitor2_id, Year(2025), Month(9)
        )
        assert count == 1

        # Count for non-existent month
        count = self.repo.count_visits_for_person_in_month(
            self.visitor1_id, Year(2025), Month(11)
        )
        assert count == 0

    def test_find_visits_by_date_range(self):
        """Test finding visits by date range."""
        # Save test visits
        self.repo.save(self.visit1)  # 2025-09-05
        self.repo.save(self.visit2)  # 2025-09-15
        self.repo.save(self.visit3)  # 2025-09-25
        self.repo.save(self.visit4)  # 2025-10-05

        # Find visits in September
        sept_start = datetime(2025, 9, 1)
        sept_end = datetime(2025, 9, 30)
        sept_visits = self.repo.find_visits_by_date_range(sept_start, sept_end)
        assert len(sept_visits) == 3

        # Find visits in first half of September
        mid_sept = datetime(2025, 9, 16)
        early_sept = self.repo.find_visits_by_date_range(sept_start, mid_sept)
        assert len(early_sept) == 2

        # Find visits spanning months
        late_sept = datetime(2025, 9, 20)
        early_oct = datetime(2025, 10, 10)
        cross_month = self.repo.find_visits_by_date_range(late_sept, early_oct)
        assert len(cross_month) == 2  # visit3 and visit4

    def test_count_and_find_all(self):
        """Test counting and finding all visits."""
        assert self.repo.count() == 0
        assert len(self.repo.find_all()) == 0

        # Add visits
        self.repo.save(self.visit1)
        assert self.repo.count() == 1
        assert len(self.repo.find_all()) == 1

        self.repo.save(self.visit2)
        assert self.repo.count() == 2
        assert len(self.repo.find_all()) == 2

        # Delete one
        self.repo.delete(self.visit1.id)
        assert self.repo.count() == 1
        assert len(self.repo.find_all()) == 1

    def test_clear_all_visits(self):
        """Test clearing all visits."""
        # Add some visits
        self.repo.save(self.visit1)
        self.repo.save(self.visit2)
        assert self.repo.count() == 2

        # Clear
        self.repo.clear_all_visits()
        assert self.repo.count() == 0
        assert len(self.repo.find_all()) == 0
        assert not self.repo.exists(self.visit1.id)
