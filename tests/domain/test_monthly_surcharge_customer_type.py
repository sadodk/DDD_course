"""Tests for customer type specific monthly surcharge rules."""

from datetime import datetime
from domain.services.monthly_surcharge import MonthlySurchargeService
from domain.entities.visit import Visit
from domain.entities.visitor import Visitor
from domain.repositories.visit_repository import VisitRepository
from domain.repositories.visitor_repository import VisitorRepository
from domain.types import VisitId, PersonId, Year, Month, CardId, EmailAddress
from domain.values.dropped_fraction import DroppedFraction, FractionType
from domain.values.weight import Weight
from domain.values.price import Currency


class MockVisitRepository(VisitRepository):
    """Mock implementation of VisitRepository for testing."""

    def __init__(self):
        self._visits = []
        self._visit_counts = {}

    def set_visits_for_month(
        self, visitor_id: PersonId, year: Year, month: Month, visits: list[Visit]
    ):
        """Test helper to set up mock data."""
        # Store visits per visitor instead of overwriting
        key = (visitor_id, year, month)
        self._visit_counts[key] = len(visits)

        # Remove existing visits for this visitor/month and add new ones
        self._visits = [
            v
            for v in self._visits
            if not (
                v.visitor_id == visitor_id
                and v.date.year == year
                and v.date.month == month
            )
        ]
        self._visits.extend(visits)

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


class MockVisitorRepository(VisitorRepository):
    """Mock implementation of VisitorRepository for testing."""

    def __init__(self):
        self._visitors = {}

    def add_visitor(self, visitor: Visitor) -> None:
        """Test helper to add visitors."""
        self._visitors[visitor.id] = visitor

    def find_by_id(self, visitor_id: PersonId) -> Visitor | None:
        return self._visitors.get(visitor_id)

    # Other abstract methods (not needed for testing)
    def save(self, visitor: Visitor) -> None:
        pass

    def delete(self, visitor_id: PersonId) -> bool:
        return False

    def find_by_city(self, city: str) -> list[Visitor]:
        return []

    def find_by_card_id(self, card_id: str) -> Visitor | None:
        return None

    def exists(self, visitor_id: PersonId) -> bool:
        return visitor_id in self._visitors

    def find_all(self) -> list[Visitor]:
        return list(self._visitors.values())

    def count(self) -> int:
        return len(self._visitors)

    def clear(self) -> None:
        pass


class TestMonthlySurchargeCustomerType:
    """Test cases for customer type specific surcharge rules."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_visit_repo = MockVisitRepository()
        self.mock_visitor_repo = MockVisitorRepository()
        self.service = MonthlySurchargeService(
            self.mock_visit_repo, self.mock_visitor_repo
        )

        # Test data
        self.individual_visitor_id = PersonId("individual_visitor")
        self.business_visitor_id = PersonId("business_visitor")
        self.year = Year(2025)
        self.month = Month(9)

        # Create visitors with different types
        self.individual_visitor = Visitor(
            id=self.individual_visitor_id,
            type="individual",
            address="123 Main St",
            city="TestCity",
            card_id=CardId("CARD001"),
            email=EmailAddress("individual@example.com"),
        )

        self.business_visitor = Visitor(
            id=self.business_visitor_id,
            type="business",
            address="456 Business Ave",
            city="TestCity",
            card_id=CardId("CARD002"),
            email=EmailAddress("business@example.com"),
        )

        # Add visitors to mock repository
        self.mock_visitor_repo.add_visitor(self.individual_visitor)
        self.mock_visitor_repo.add_visitor(self.business_visitor)

    def _create_visit(
        self, visit_id: str, visitor_id: PersonId, date: datetime, weight: int = 10
    ) -> Visit:
        """Helper to create a visit with test data."""
        return Visit(
            id=VisitId(visit_id),
            visitor_id=visitor_id,
            date=date,
            dropped_fractions=[
                DroppedFraction(FractionType.GREEN_WASTE, Weight(weight))
            ],
        )

    def test_individual_visitor_gets_surcharge_on_third_visit(self):
        """Test that individual visitors get surcharge starting from the 3rd visit."""
        # Setup: 3 visits for individual visitor
        visits = [
            self._create_visit(
                "visit1", self.individual_visitor_id, datetime(2025, 9, 5)
            ),
            self._create_visit(
                "visit2", self.individual_visitor_id, datetime(2025, 9, 15)
            ),
            self._create_visit(
                "visit3", self.individual_visitor_id, datetime(2025, 9, 25)
            ),
        ]
        self.mock_visit_repo.set_visits_for_month(
            self.individual_visitor_id, self.year, self.month, visits
        )

        # All visits should have surcharge for individual visitor
        for visit in visits:
            assert self.service.is_surcharge_applicable(visit)
            surcharge = self.service.calculate_surcharge_for_visit(visit)
            assert (
                surcharge.amount > 0
            ), f"Individual visitor should get surcharge on visit {visit.id}"

    def test_business_visitor_never_gets_surcharge(self):
        """Test that business visitors never get the monthly surcharge, even with 3+ visits."""
        # Setup: 4 visits for business visitor (more than threshold)
        visits = [
            self._create_visit(
                "visit1", self.business_visitor_id, datetime(2025, 9, 5)
            ),
            self._create_visit(
                "visit2", self.business_visitor_id, datetime(2025, 9, 10)
            ),
            self._create_visit(
                "visit3", self.business_visitor_id, datetime(2025, 9, 15)
            ),
            self._create_visit(
                "visit4", self.business_visitor_id, datetime(2025, 9, 20)
            ),
        ]
        self.mock_visit_repo.set_visits_for_month(
            self.business_visitor_id, self.year, self.month, visits
        )

        # No visits should have surcharge for business visitor
        for visit in visits:
            assert not self.service.is_surcharge_applicable(
                visit
            ), f"Business visitor should not get surcharge on visit {visit.id}"
            surcharge = self.service.calculate_surcharge_for_visit(visit)
            assert (
                surcharge.amount == 0.0
            ), f"Business visitor surcharge should be 0.00, got {surcharge.amount}"

    def test_mixed_customer_types_independent_surcharges(self):
        """Test that individual and business visitors are treated independently."""
        # Setup visits for both types
        individual_visits = [
            self._create_visit(
                "ind1", self.individual_visitor_id, datetime(2025, 9, 5)
            ),
            self._create_visit(
                "ind2", self.individual_visitor_id, datetime(2025, 9, 15)
            ),
            self._create_visit(
                "ind3", self.individual_visitor_id, datetime(2025, 9, 25)
            ),
        ]

        business_visits = [
            self._create_visit("bus1", self.business_visitor_id, datetime(2025, 9, 6)),
            self._create_visit("bus2", self.business_visitor_id, datetime(2025, 9, 16)),
            self._create_visit("bus3", self.business_visitor_id, datetime(2025, 9, 26)),
            self._create_visit("bus4", self.business_visitor_id, datetime(2025, 9, 28)),
        ]

        # Set up visit counts
        self.mock_visit_repo.set_visits_for_month(
            self.individual_visitor_id, self.year, self.month, individual_visits
        )

        # Test individual visitor (should get surcharge)
        for visit in individual_visits:
            assert self.service.is_surcharge_applicable(visit)
            surcharge = self.service.calculate_surcharge_for_visit(visit)
            assert surcharge.amount > 0

        # Set up business visits separately
        self.mock_visit_repo.set_visits_for_month(
            self.business_visitor_id, self.year, self.month, business_visits
        )

        # Test business visitor (should not get surcharge)
        for visit in business_visits:
            assert not self.service.is_surcharge_applicable(visit)
            surcharge = self.service.calculate_surcharge_for_visit(visit)
            assert surcharge.amount == 0.0

    def test_visitor_not_found_defaults_to_no_surcharge(self):
        """Test that if visitor is not found, no surcharge is applied for safety."""
        unknown_visitor_id = PersonId("unknown_visitor")
        visit = self._create_visit("visit1", unknown_visitor_id, datetime(2025, 9, 5))

        # Set up high visit count that would normally trigger surcharge
        self.mock_visit_repo.set_visits_for_month(
            unknown_visitor_id, self.year, self.month, [visit, visit, visit, visit]
        )

        # Should not apply surcharge when visitor is not found
        assert not self.service.is_surcharge_applicable(visit)
        surcharge = self.service.calculate_surcharge_for_visit(visit)
        assert surcharge.amount == 0.0

    def test_total_price_calculation_with_customer_type_rules(self):
        """Test total price calculation respects customer type rules."""
        # Individual visitor with 3 visits
        individual_visit = self._create_visit(
            "ind1", self.individual_visitor_id, datetime(2025, 9, 5)
        )
        self.mock_visit_repo.set_visits_for_month(
            self.individual_visitor_id, self.year, self.month, [individual_visit] * 3
        )

        # Business visitor with 3 visits
        business_visit = self._create_visit(
            "bus1", self.business_visitor_id, datetime(2025, 9, 5)
        )
        self.mock_visit_repo.set_visits_for_month(
            self.business_visitor_id, self.year, self.month, [business_visit] * 3
        )

        # Individual visitor should have base price + surcharge
        individual_base_price = individual_visit.calculate_base_price()
        individual_total = self.service.calculate_total_price_with_surcharge(
            individual_visit
        )
        expected_individual_surcharge = individual_base_price.amount * 0.05
        expected_individual_total = (
            individual_base_price.amount + expected_individual_surcharge
        )
        assert abs(individual_total.amount - expected_individual_total) < 0.01

        # Business visitor should have only base price (no surcharge)
        business_base_price = business_visit.calculate_base_price()
        business_total = self.service.calculate_total_price_with_surcharge(
            business_visit
        )
        assert business_total.amount == business_base_price.amount  # No surcharge added

    def test_monthly_summary_respects_customer_type(self):
        """Test that monthly summary calculations respect customer type rules."""
        # Individual visitor with 3 visits
        individual_visits = [
            self._create_visit(
                "ind1", self.individual_visitor_id, datetime(2025, 9, 5)
            ),
            self._create_visit(
                "ind2", self.individual_visitor_id, datetime(2025, 9, 15)
            ),
            self._create_visit(
                "ind3", self.individual_visitor_id, datetime(2025, 9, 25)
            ),
        ]
        self.mock_visit_repo.set_visits_for_month(
            self.individual_visitor_id, self.year, self.month, individual_visits
        )

        # Business visitor with 4 visits
        business_visits = [
            self._create_visit("bus1", self.business_visitor_id, datetime(2025, 9, 5)),
            self._create_visit("bus2", self.business_visitor_id, datetime(2025, 9, 10)),
            self._create_visit("bus3", self.business_visitor_id, datetime(2025, 9, 15)),
            self._create_visit("bus4", self.business_visitor_id, datetime(2025, 9, 20)),
        ]
        self.mock_visit_repo.set_visits_for_month(
            self.business_visitor_id, self.year, self.month, business_visits
        )

        # Individual summary should show surcharge applied
        individual_summary = self.service.get_monthly_visit_summary(
            self.individual_visitor_id, self.year, self.month
        )
        assert individual_summary["visit_count"] == 3
        assert individual_summary["surcharge_applied"] is True
        assert individual_summary["total_surcharge"].amount > 0

        # Business summary should show no surcharge
        business_summary = self.service.get_monthly_visit_summary(
            self.business_visitor_id, self.year, self.month
        )
        assert business_summary["visit_count"] == 4
        assert business_summary["surcharge_applied"] is False
        assert business_summary["total_surcharge"].amount == 0.0
