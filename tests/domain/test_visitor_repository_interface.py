"""Tests for VisitorRepository interface contract."""

import pytest
from abc import ABC
from domain.repositories.visitor_repository import VisitorRepository
from domain.entities.visitor import Visitor
from domain.types import PersonId, CardId


class TestVisitorRepositoryInterface:
    """Tests to ensure VisitorRepository follows the abstract contract."""

    def test_visitor_repository_is_abstract(self):
        """Test that VisitorRepository is an abstract class."""
        assert issubclass(VisitorRepository, ABC)

        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            VisitorRepository()  # type: ignore

    def test_visitor_repository_has_required_methods(self):
        """Test that VisitorRepository defines all required abstract methods."""
        expected_methods = {
            "find_by_id",
            "save",
            "delete",
            "find_by_city",
            "find_by_card_id",
            "exists",
            "find_all",
        }

        actual_methods = set(VisitorRepository.__abstractmethods__)
        assert actual_methods == expected_methods

    def test_concrete_implementation_must_implement_all_methods(self):
        """Test that concrete implementations must implement all abstract methods."""

        # Incomplete implementation should fail
        class IncompleteRepository(VisitorRepository):
            def find_by_id(self, visitor_id: PersonId):
                pass

            # Missing other required methods

        with pytest.raises(TypeError):
            IncompleteRepository()  # type: ignore

    def test_complete_implementation_can_be_instantiated(self):
        """Test that complete implementations can be instantiated."""

        class CompleteRepository(VisitorRepository):
            def find_by_id(self, visitor_id: PersonId):
                return None

            def save(self, visitor: Visitor) -> None:
                pass

            def delete(self, visitor_id: PersonId) -> bool:
                return False

            def find_by_city(self, city: str):
                return []

            def find_by_card_id(self, card_id: str):
                return None

            def exists(self, visitor_id: PersonId) -> bool:
                return False

            def find_all(self):
                return []

        # Should be able to instantiate
        repo = CompleteRepository()
        assert isinstance(repo, VisitorRepository)

    def test_repository_method_signatures(self):
        """Test that repository methods have correct signatures."""

        class TestRepository(VisitorRepository):
            def find_by_id(self, visitor_id: PersonId):
                return None

            def save(self, visitor: Visitor) -> None:
                pass

            def delete(self, visitor_id: PersonId) -> bool:
                return False

            def find_by_city(self, city: str):
                return []

            def find_by_card_id(self, card_id: str):
                return None

            def exists(self, visitor_id: PersonId) -> bool:
                return False

            def find_all(self):
                return []

        repo = TestRepository()

        # Test method signatures work with expected types
        visitor_id = PersonId("test123")
        visitor = Visitor(
            id=visitor_id,
            type="individual",
            address="Test Address",
            city="Test City",
            card_id=CardId("CARD001"),
        )

        # These should not raise type errors
        repo.find_by_id(visitor_id)
        repo.save(visitor)
        repo.delete(visitor_id)
        repo.find_by_city("Test City")
        repo.find_by_card_id("CARD001")
        repo.exists(visitor_id)
        repo.find_all()
