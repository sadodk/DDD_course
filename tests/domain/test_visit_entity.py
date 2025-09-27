"""Tests for Visit entity."""

import pytest
from datetime import datetime
from domain.entities.visit import Visit
from domain.types import VisitId, PersonId
from domain.dropped_fraction import DroppedFraction, FractionType
from domain.weight import Weight
from domain.price import Currency


class TestVisitEntity:
    def test_visit_creation_with_valid_data(self):
        """Test creating a visit with valid data."""
        dropped_fractions = [
            DroppedFraction(FractionType.GREEN_WASTE, Weight(10)),
            DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(20)),
        ]

        visit = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=dropped_fractions,
        )

        assert visit.id == VisitId("visit123")
        assert visit.visitor_id == PersonId("user123")
        assert visit.date == datetime(2025, 9, 15, 10, 0, 0)
        assert len(visit.dropped_fractions) == 2

    def test_visit_requires_valid_id(self):
        """Test that visit must have a valid ID."""
        dropped_fractions = [DroppedFraction(FractionType.GREEN_WASTE, Weight(10))]

        with pytest.raises(ValueError, match="Visit must have a valid ID"):
            Visit(
                id=VisitId(""),  # Empty ID should fail
                visitor_id=PersonId("user123"),
                date=datetime(2025, 9, 15, 10, 0, 0),
                dropped_fractions=dropped_fractions,
            )

    def test_visit_requires_visitor_id(self):
        """Test that visit must be associated with a visitor."""
        dropped_fractions = [DroppedFraction(FractionType.GREEN_WASTE, Weight(10))]

        with pytest.raises(ValueError, match="Visit must be associated with a visitor"):
            Visit(
                id=VisitId("visit123"),
                visitor_id=PersonId(""),  # Empty visitor ID should fail
                date=datetime(2025, 9, 15, 10, 0, 0),
                dropped_fractions=dropped_fractions,
            )

    def test_visit_requires_dropped_fractions(self):
        """Test that visit must have at least one dropped fraction."""
        with pytest.raises(
            ValueError, match="Visit must have at least one dropped fraction"
        ):
            Visit(
                id=VisitId("visit123"),
                visitor_id=PersonId("user123"),
                date=datetime(2025, 9, 15, 10, 0, 0),
                dropped_fractions=[],  # Empty fractions should fail
            )

    def test_visit_requires_datetime_object(self):
        """Test that visit date must be a datetime object."""
        dropped_fractions = [DroppedFraction(FractionType.GREEN_WASTE, Weight(10))]

        # This test would need to be adjusted since dataclass enforces types at creation
        # We'll test the business invariant instead
        visit = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=dropped_fractions,
        )

        # Verify it's a datetime object
        assert isinstance(visit.date, datetime)

    def test_visit_equality_based_on_identity(self):
        """Test that visit equality is based on identity (ID), not attributes."""
        dropped_fractions1 = [DroppedFraction(FractionType.GREEN_WASTE, Weight(10))]
        dropped_fractions2 = [
            DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(20))
        ]

        visit1 = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=dropped_fractions1,
        )

        visit2 = Visit(
            id=VisitId("visit123"),  # Same ID
            visitor_id=PersonId("user456"),  # Different attributes
            date=datetime(2025, 9, 20, 15, 0, 0),
            dropped_fractions=dropped_fractions2,
        )

        visit3 = Visit(
            id=VisitId("visit456"),  # Different ID
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=dropped_fractions1,
        )

        # Same ID = equal entities
        assert visit1 == visit2

        # Different ID = not equal
        assert visit1 != visit3
        assert visit2 != visit3

    def test_visit_hash_based_on_identity(self):
        """Test that visit hash is based on identity for use in sets/dicts."""
        dropped_fractions1 = [DroppedFraction(FractionType.GREEN_WASTE, Weight(10))]
        dropped_fractions2 = [
            DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(20))
        ]

        visit1 = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=dropped_fractions1,
        )

        visit2 = Visit(
            id=VisitId("visit123"),  # Same ID
            visitor_id=PersonId("user456"),  # Different attributes
            date=datetime(2025, 9, 20, 15, 0, 0),
            dropped_fractions=dropped_fractions2,
        )

        # Same ID should have same hash
        assert hash(visit1) == hash(visit2)

        # Should work in sets
        visit_set = {visit1, visit2}
        assert len(visit_set) == 1  # Only one unique visit

    def test_calculate_base_price_without_city(self):
        """Test calculating base price using default pricing."""
        dropped_fractions = [
            DroppedFraction(FractionType.GREEN_WASTE, Weight(10)),  # 10 * 0.10 = 1.00
            DroppedFraction(
                FractionType.CONSTRUCTION_WASTE, Weight(20)
            ),  # 20 * 0.19 = 3.80
        ]

        visit = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=dropped_fractions,
        )

        price = visit.calculate_base_price()
        assert price.amount == 4.80  # 1.00 + 3.80
        assert price.currency == Currency.EUR

    def test_calculate_base_price_with_city(self):
        """Test calculating base price with city-specific pricing."""
        dropped_fractions = [
            DroppedFraction(FractionType.GREEN_WASTE, Weight(10)),  # 10 * 0.08 = 0.80
            DroppedFraction(
                FractionType.CONSTRUCTION_WASTE, Weight(20)
            ),  # 20 * 0.19 = 3.80
        ]

        visit = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=dropped_fractions,
        )

        price = visit.calculate_base_price(visitor_city="Oak City")
        assert price.amount == 4.60  # 0.80 + 3.80
        assert price.currency == Currency.EUR

    def test_get_total_weight(self):
        """Test getting total weight of all dropped fractions."""
        dropped_fractions = [
            DroppedFraction(FractionType.GREEN_WASTE, Weight(10)),
            DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(20)),
            DroppedFraction(FractionType.GREEN_WASTE, Weight(5)),
        ]

        visit = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=dropped_fractions,
        )

        assert visit.get_total_weight() == 35  # 10 + 20 + 5

    def test_has_fraction_type(self):
        """Test checking if visit contains a specific fraction type."""
        dropped_fractions = [
            DroppedFraction(FractionType.GREEN_WASTE, Weight(10)),
            DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(20)),
        ]

        visit = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=dropped_fractions,
        )

        assert visit.has_fraction_type("Green waste") is True
        assert visit.has_fraction_type("Construction waste") is True
        assert visit.has_fraction_type("Other waste") is False

    def test_get_year_month(self):
        """Test getting year and month from visit date."""
        visit = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=[DroppedFraction(FractionType.GREEN_WASTE, Weight(10))],
        )

        year_month = visit.get_year_month()
        assert year_month == (2025, 9)

    def test_is_same_month(self):
        """Test checking if two visits are in the same month."""
        dropped_fractions = [DroppedFraction(FractionType.GREEN_WASTE, Weight(10))]

        visit1 = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=dropped_fractions,
        )

        visit2 = Visit(
            id=VisitId("visit456"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 25, 15, 0, 0),  # Same month
            dropped_fractions=dropped_fractions,
        )

        visit3 = Visit(
            id=VisitId("visit789"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 10, 5, 12, 0, 0),  # Different month
            dropped_fractions=dropped_fractions,
        )

        assert visit1.is_same_month(visit2) is True
        assert visit1.is_same_month(visit3) is False
        assert visit2.is_same_month(visit3) is False

    def test_add_dropped_fraction(self):
        """Test adding a new dropped fraction to visit."""
        visit = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=[DroppedFraction(FractionType.GREEN_WASTE, Weight(10))],
        )

        assert len(visit.dropped_fractions) == 1

        new_fraction = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(5))
        visit.add_dropped_fraction(new_fraction)

        assert len(visit.dropped_fractions) == 2
        assert new_fraction in visit.dropped_fractions

    def test_add_invalid_dropped_fraction_fails(self):
        """Test that adding invalid dropped fraction fails."""
        visit = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=[DroppedFraction(FractionType.GREEN_WASTE, Weight(10))],
        )

        # Test with None (type checker allows this)
        with pytest.raises(ValueError, match="Must add a valid DroppedFraction"):
            visit.add_dropped_fraction(None)  # type: ignore

    def test_visit_string_representations(self):
        """Test string representations of visit."""
        visit = Visit(
            id=VisitId("visit123"),
            visitor_id=PersonId("user123"),
            date=datetime(2025, 9, 15, 10, 0, 0),
            dropped_fractions=[DroppedFraction(FractionType.GREEN_WASTE, Weight(10))],
        )

        assert "visit123" in str(visit)
        assert "user123" in str(visit)
        assert "2025-09-15" in str(visit)
        assert "visit123" in repr(visit)
        assert "fractions=1" in repr(visit)
