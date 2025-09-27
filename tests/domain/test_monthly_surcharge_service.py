"""Tests for MonthlySurchargeService domain service."""

from datetime import datetime
from domain.services.monthly_surcharge_service import MonthlySurchargeService
from domain.entities.visit import Visit
from domain.repositories.visit_repository import VisitRepository
from domain.types import VisitId, PersonId, Year, Month
from domain.dropped_fraction import DroppedFraction, FractionType
from domain.weight import Weight
from domain.price import Currency


class MockVisitRepository(VisitRepository):
    """Mock implementation of VisitRepository for testing."""

    def __init__(self):
        self._visits = []
        self._visit_counts = {}

    def set_visits_for_month(
        self, visitor_id: PersonId, year: Year, month: Month, visits: list[Visit]
    ):
        """Test helper to set up mock data."""
        self._visits = visits
        self._visit_counts[(visitor_id, year, month)] = len(visits)

    def find_visits_for_person_in_month(
        self, visitor_id: PersonId, year: Year, month: Month
    ) -> list[Visit]:
        """Return mock visits for the given month."""
        return [
            v
            for v in self._visits
            if v.visitor_id == visitor_id
            and v.date.year == year
            and v.date.month == month
        ]

    def count_visits_for_person_in_month(
        self, visitor_id: PersonId, year: Year, month: Month
    ) -> int:
        """Return mock visit count for the given month."""
        return self._visit_counts.get((visitor_id, year, month), 0)

    # Other abstract methods (not needed for testing)
    def find_by_id(self, visit_id: VisitId):
        return None

    def save(self, visit: Visit) -> None:
        pass

    def find_visits_by_visitor(self, visitor_id: PersonId):
        return []

    def find_visits_by_date_range(self, start_date: datetime, end_date: datetime):
        return []

    def delete(self, visit_id: VisitId) -> bool:
        return False

    def exists(self, visit_id: VisitId) -> bool:
        return False

    def clear_all_visits(self) -> None:
        pass


class TestMonthlySurchargeService:
    """Test cases for MonthlySurchargeService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_repo = MockVisitRepository()
        self.service = MonthlySurchargeService(self.mock_repo)

        # Common test data
        self.visitor_id = PersonId("visitor123")
        self.year = Year(2025)
        self.month = Month(9)

    def _create_visit(self, visit_id: str, date: datetime, weight: int = 10) -> Visit:
        """Helper to create a visit with test data."""
        return Visit(
            id=VisitId(visit_id),
            visitor_id=self.visitor_id,
            date=date,
            dropped_fractions=[
                DroppedFraction(FractionType.GREEN_WASTE, Weight(weight))
            ],
        )

    def test_no_surcharge_with_fewer_than_three_visits(self):
        """Test that no surcharge applies with fewer than 3 visits."""
        # Setup: 2 visits in September 2025
        visits = [
            self._create_visit("visit1", datetime(2025, 9, 5)),
            self._create_visit("visit2", datetime(2025, 9, 15)),
        ]
        self.mock_repo.set_visits_for_month(
            self.visitor_id, self.year, self.month, visits
        )

        # Test each visit
        for visit in visits:
            surcharge = self.service.calculate_surcharge_for_visit(visit)
            assert surcharge.amount == 0.0
            assert surcharge.currency == Currency.EUR

            assert not self.service.is_surcharge_applicable(visit)

            # Total price should equal base price
            base_price = visit.calculate_base_price()
            total_price = self.service.calculate_total_price_with_surcharge(visit)
            assert total_price.amount == base_price.amount

    def test_surcharge_applies_with_three_or_more_visits(self):
        """Test that 5% surcharge applies with 3+ visits."""
        # Setup: 3 visits in September 2025
        visits = [
            self._create_visit("visit1", datetime(2025, 9, 5)),
            self._create_visit("visit2", datetime(2025, 9, 15)),
            self._create_visit("visit3", datetime(2025, 9, 25)),
        ]
        self.mock_repo.set_visits_for_month(
            self.visitor_id, self.year, self.month, visits
        )

        # Test each visit
        for visit in visits:
            base_price = visit.calculate_base_price()
            surcharge = self.service.calculate_surcharge_for_visit(visit)

            # Should have 5% surcharge
            expected_surcharge = base_price.amount * 0.05
            assert abs(surcharge.amount - expected_surcharge) < 0.01
            assert surcharge.currency == Currency.EUR

            assert self.service.is_surcharge_applicable(visit)

            # Total price should be base + surcharge
            total_price = self.service.calculate_total_price_with_surcharge(visit)
            expected_total = base_price.amount + expected_surcharge
            assert abs(total_price.amount - expected_total) < 0.01

    def test_surcharge_applies_with_four_visits(self):
        """Test surcharge with more than 3 visits."""
        # Setup: 4 visits in September 2025
        visits = [
            self._create_visit("visit1", datetime(2025, 9, 5)),
            self._create_visit("visit2", datetime(2025, 9, 15)),
            self._create_visit("visit3", datetime(2025, 9, 20)),
            self._create_visit("visit4", datetime(2025, 9, 25)),
        ]
        self.mock_repo.set_visits_for_month(
            self.visitor_id, self.year, self.month, visits
        )

        # All visits should have surcharge
        for visit in visits:
            assert self.service.is_surcharge_applicable(visit)
            surcharge = self.service.calculate_surcharge_for_visit(visit)
            assert surcharge.amount > 0

    def test_monthly_visit_summary_no_surcharge(self):
        """Test monthly summary with no surcharge."""
        # Setup: 2 visits
        visits = [
            self._create_visit("visit1", datetime(2025, 9, 5)),
            self._create_visit("visit2", datetime(2025, 9, 15)),
        ]
        self.mock_repo.set_visits_for_month(
            self.visitor_id, self.year, self.month, visits
        )

        summary = self.service.get_monthly_visit_summary(
            self.visitor_id, self.year, self.month
        )

        assert summary["visit_count"] == 2
        assert not summary["surcharge_applied"]
        assert summary["total_surcharge"].amount == 0.0

        # Total should equal base prices
        expected_base = (
            visits[0].calculate_base_price().add(visits[1].calculate_base_price())
        )
        assert abs(summary["total_base_price"].amount - expected_base.amount) < 0.01
        assert abs(summary["final_total"].amount - expected_base.amount) < 0.01

    def test_monthly_visit_summary_with_surcharge(self):
        """Test monthly summary with surcharge applied."""
        # Setup: 3 visits
        visits = [
            self._create_visit("visit1", datetime(2025, 9, 5)),
            self._create_visit("visit2", datetime(2025, 9, 15)),
            self._create_visit("visit3", datetime(2025, 9, 25)),
        ]
        self.mock_repo.set_visits_for_month(
            self.visitor_id, self.year, self.month, visits
        )

        summary = self.service.get_monthly_visit_summary(
            self.visitor_id, self.year, self.month
        )

        assert summary["visit_count"] == 3
        assert summary["surcharge_applied"]
        assert summary["total_surcharge"].amount > 0

        # Verify calculations
        total_base = visits[0].calculate_base_price()
        for visit in visits[1:]:
            total_base = total_base.add(visit.calculate_base_price())

        expected_surcharge_amount = total_base.amount * 0.05
        assert abs(summary["total_surcharge"].amount - expected_surcharge_amount) < 0.01

        expected_final = total_base.amount + expected_surcharge_amount
        assert abs(summary["final_total"].amount - expected_final) < 0.01

    def test_monthly_visit_summary_no_visits(self):
        """Test monthly summary with no visits."""
        # Setup: No visits
        self.mock_repo.set_visits_for_month(self.visitor_id, self.year, self.month, [])

        summary = self.service.get_monthly_visit_summary(
            self.visitor_id, self.year, self.month
        )

        assert summary["visit_count"] == 0
        assert not summary["surcharge_applied"]
        assert summary["total_base_price"].amount == 0.0
        assert summary["total_surcharge"].amount == 0.0
        assert summary["final_total"].amount == 0.0

    def test_surcharge_threshold_constant(self):
        """Test that surcharge threshold is correctly set."""
        assert MonthlySurchargeService.SURCHARGE_THRESHOLD == 3

    def test_surcharge_rate_constant(self):
        """Test that surcharge rate is correctly set to 5%."""
        from decimal import Decimal

        assert MonthlySurchargeService.SURCHARGE_RATE == Decimal("0.05")

    def test_different_months_tracked_separately(self):
        """Test that surcharge is calculated per month independently."""
        # Setup: 2 visits in September, 2 in October
        sept_visits = [
            self._create_visit("visit1", datetime(2025, 9, 5)),
            self._create_visit("visit2", datetime(2025, 9, 15)),
        ]
        oct_visits = [
            self._create_visit("visit3", datetime(2025, 10, 5)),
            self._create_visit("visit4", datetime(2025, 10, 15)),
        ]

        # Mock setup for September (2 visits)
        self.mock_repo.set_visits_for_month(
            self.visitor_id, self.year, Month(9), sept_visits
        )

        # Test September visits (no surcharge)
        for visit in sept_visits:
            assert not self.service.is_surcharge_applicable(visit)

        # Mock setup for October (2 visits)
        self.mock_repo.set_visits_for_month(
            self.visitor_id, self.year, Month(10), oct_visits
        )

        # Test October visits (no surcharge)
        for visit in oct_visits:
            assert not self.service.is_surcharge_applicable(visit)
