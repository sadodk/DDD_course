"""Tests for PriceCalculator."""

from unittest.mock import Mock

from application.price_calculator import PriceCalculator, PriceResponse
from application.external_visitor_service import VisitorInfo
from domain.values.price import Price, Currency
from infrastructure.repositories.in_memory_visit_repository import (
    InMemoryVisitRepository,
)
from infrastructure.repositories.in_memory_visitor_repository import (
    InMemoryVisitorRepository,
)


class TestPriceCalculator:
    """Test cases for PriceCalculator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.visitor_service = Mock()
        self.surcharge_service = Mock()
        self.visit_repository = InMemoryVisitRepository()
        self.visitor_repository = InMemoryVisitorRepository()

        self.calculator = PriceCalculator(
            self.visitor_service,
            self.surcharge_service,
            self.visit_repository,
            self.visitor_repository,
        )

        # Mock visitor data
        self.mock_visitor = VisitorInfo(
            id="visitor123",
            type="individual",
            address="123 Test St",
            city="Amsterdam",
            card_id="CARD001",
            email="test@example.com",
        )

    def test_calculate_price_success(self):
        """Test successful price calculation."""
        # Mock external visitor service
        self.visitor_service.get_visitor_by_id.return_value = self.mock_visitor

        # Mock surcharge service
        expected_price = Price(12.50, Currency.EUR)
        self.surcharge_service.calculate_total_price_with_surcharge.return_value = (
            expected_price
        )

        # Test data
        visit_data = {
            "person_id": "visitor123",
            "visit_id": "visit123",
            "date": "2025-09-15T10:00:00",
            "dropped_fractions": [
                {"fraction_type": "Green waste", "amount_dropped": 10}
            ],
        }

        # Calculate price
        result = self.calculator.calculate_price(visit_data)

        # Verify result
        assert isinstance(result, PriceResponse)
        assert result.price_amount == 12.50
        assert result.price_currency == "EUR"
        assert result.person_id == "visitor123"
        assert result.visit_id == "visit123"

        # Verify visit was saved
        assert len(self.visit_repository.find_all()) == 1

    def test_parse_date_formats(self):
        """Test different date format parsing."""
        # ISO format
        date1 = self.calculator._parse_date("2025-09-15T10:30:00")
        assert date1.year == 2025
        assert date1.month == 9
        assert date1.day == 15

        # ISO format with timezone
        date2 = self.calculator._parse_date("2025-09-15T10:30:00Z")
        assert date2.year == 2025
        assert date2.month == 9
        assert date2.day == 15

    def test_create_visit_entity(self):
        """Test visit entity creation from request data."""
        visit_data = {
            "person_id": "visitor123",
            "visit_id": "visit456",
            "date": "2025-09-15T10:00:00",
            "dropped_fractions": [
                {"fraction_type": "Green waste", "amount_dropped": 10},
                {"fraction_type": "Construction waste", "amount_dropped": 5},
            ],
        }

        visit = self.calculator._create_visit_entity(visit_data)

        assert str(visit.visitor_id) == "visitor123"
        assert str(visit.id) == "visit456"
        assert len(visit.dropped_fractions) == 2
        assert visit.dropped_fractions[0].weight.weight == 10
        assert visit.dropped_fractions[1].weight.weight == 5
