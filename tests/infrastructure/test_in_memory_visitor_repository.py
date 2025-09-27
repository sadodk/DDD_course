"""Tests for InMemoryVisitorRepository."""

from infrastructure.repositories.in_memory_visitor_repository import (
    InMemoryVisitorRepository,
)
from domain.entities.visitor import Visitor
from domain.types import PersonId, CardId


class TestInMemoryVisitorRepository:
    """Test cases for InMemoryVisitorRepository."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repo = InMemoryVisitorRepository()

        # Test data
        self.visitor1 = Visitor(
            id=PersonId("visitor1"),
            type="individual",
            address="123 Main St",
            city="Amsterdam",
            card_id=CardId("CARD001"),
        )

        self.visitor2 = Visitor(
            id=PersonId("visitor2"),
            type="business",
            address="456 Business Ave",
            city="Rotterdam",
            card_id=CardId("CARD002"),
        )

        self.visitor3 = Visitor(
            id=PersonId("visitor3"),
            type="individual",
            address="789 Other St",
            city="Amsterdam",  # Same city as visitor1
            card_id=CardId("CARD003"),
        )

    def test_save_and_find_by_id(self):
        """Test saving and finding visitors by ID."""
        # Initially empty
        assert self.repo.find_by_id(self.visitor1.id) is None

        # Save visitor
        self.repo.save(self.visitor1)

        # Should be able to find it
        found = self.repo.find_by_id(self.visitor1.id)
        assert found is not None
        assert found.id == self.visitor1.id
        assert found.city == self.visitor1.city

    def test_save_allows_updates(self):
        """Test that saving an existing visitor updates it."""
        # Save original visitor
        self.repo.save(self.visitor1)

        # Update visitor
        updated_visitor = Visitor(
            id=self.visitor1.id,  # Same ID
            type="business",  # Different type
            address="Updated Address",
            city="Updated City",
            card_id=self.visitor1.card_id,
        )

        # Save updated version
        self.repo.save(updated_visitor)

        # Should retrieve updated version
        found = self.repo.find_by_id(self.visitor1.id)
        assert found is not None
        assert found.type == "business"
        assert found.address == "Updated Address"
        assert found.city == "Updated City"

    def test_delete(self):
        """Test deleting visitors."""
        # Save visitor
        self.repo.save(self.visitor1)
        assert self.repo.exists(self.visitor1.id)

        # Delete should return True
        result = self.repo.delete(self.visitor1.id)
        assert result is True

        # Should no longer exist
        assert not self.repo.exists(self.visitor1.id)
        assert self.repo.find_by_id(self.visitor1.id) is None

        # Deleting non-existent visitor should return False
        result = self.repo.delete(PersonId("nonexistent"))
        assert result is False

    def test_exists(self):
        """Test checking if visitors exist."""
        assert not self.repo.exists(self.visitor1.id)

        self.repo.save(self.visitor1)
        assert self.repo.exists(self.visitor1.id)

        self.repo.delete(self.visitor1.id)
        assert not self.repo.exists(self.visitor1.id)

    def test_find_by_city(self):
        """Test finding visitors by city."""
        # Save test visitors
        self.repo.save(self.visitor1)  # Amsterdam
        self.repo.save(self.visitor2)  # Rotterdam
        self.repo.save(self.visitor3)  # Amsterdam

        # Find by Amsterdam
        amsterdam_visitors = self.repo.find_by_city("Amsterdam")
        assert len(amsterdam_visitors) == 2
        visitor_ids = {v.id for v in amsterdam_visitors}
        assert self.visitor1.id in visitor_ids
        assert self.visitor3.id in visitor_ids

        # Find by Rotterdam
        rotterdam_visitors = self.repo.find_by_city("Rotterdam")
        assert len(rotterdam_visitors) == 1
        assert rotterdam_visitors[0].id == self.visitor2.id

        # Case insensitive search
        case_insensitive = self.repo.find_by_city("amsterdam")
        assert len(case_insensitive) == 2

        # Non-existent city
        empty_results = self.repo.find_by_city("NonExistent")
        assert len(empty_results) == 0

    def test_find_by_card_id(self):
        """Test finding visitors by card ID."""
        # Save test visitors
        self.repo.save(self.visitor1)
        self.repo.save(self.visitor2)

        # Find by card ID
        found = self.repo.find_by_card_id("CARD001")
        assert found is not None
        assert found.id == self.visitor1.id

        # Non-existent card ID
        not_found = self.repo.find_by_card_id("NONEXISTENT")
        assert not_found is None

    def test_find_all(self):
        """Test finding all visitors."""
        # Initially empty
        assert len(self.repo.find_all()) == 0

        # Add visitors
        self.repo.save(self.visitor1)
        self.repo.save(self.visitor2)

        all_visitors = self.repo.find_all()
        assert len(all_visitors) == 2

        visitor_ids = {v.id for v in all_visitors}
        assert self.visitor1.id in visitor_ids
        assert self.visitor2.id in visitor_ids

    def test_count(self):
        """Test counting visitors."""
        assert self.repo.count() == 0

        self.repo.save(self.visitor1)
        assert self.repo.count() == 1

        self.repo.save(self.visitor2)
        assert self.repo.count() == 2

        self.repo.delete(self.visitor1.id)
        assert self.repo.count() == 1

    def test_clear(self):
        """Test clearing all visitors."""
        # Add some visitors
        self.repo.save(self.visitor1)
        self.repo.save(self.visitor2)
        assert self.repo.count() == 2

        # Clear
        self.repo.clear()
        assert self.repo.count() == 0
        assert len(self.repo.find_all()) == 0
        assert not self.repo.exists(self.visitor1.id)
