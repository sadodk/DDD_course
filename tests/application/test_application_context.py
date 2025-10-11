"""Tests for ApplicationContext."""

from application.dependency_injection import ApplicationContext
from application.services.price_calculation_service import PriceCalculator
from infrastructure.repositories.in_memory_visit_repository import (
    InMemoryVisitRepository,
)


class TestApplicationContext:
    """Test cases for ApplicationContext."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context = ApplicationContext()

    def test_dependencies_are_properly_wired(self):
        """Test that all dependencies are properly configured."""
        # Check that main components exist
        assert hasattr(self.context, "price_calculator")
        assert hasattr(self.context, "visitor_service")
        assert hasattr(self.context, "visit_repository")
        assert hasattr(self.context, "pricing_service")

        # Check types
        assert isinstance(self.context.price_calculator, PriceCalculator)
        assert isinstance(self.context.visit_repository, InMemoryVisitRepository)

    def test_reset_for_new_scenario(self):
        """Test scenario reset functionality."""
        # Add some test data
        from domain.entities.visit import Visit
        from domain.types import VisitId, PersonId
        from domain.values.dropped_fraction import DroppedFraction, FractionType
        from domain.values.weight import Weight
        from datetime import datetime

        visit = Visit(
            id=VisitId("test"),
            visitor_id=PersonId("test"),
            date=datetime.now(),
            dropped_fractions=[DroppedFraction(FractionType.GREEN_WASTE, Weight(10))],
        )

        self.context.visit_repository.save(visit)

        # Verify data exists
        assert len(self.context.visit_repository.find_all()) == 1

        # Reset scenario
        self.context.reset_for_new_scenario()

        # Verify data is cleared
        assert len(self.context.visit_repository.find_all()) == 0
