from unittest.mock import Mock
from application.price_calculator import PriceCalculator
from domain.monthly_visit_tracker import MonthlyVisitTracker
from application.external_visitor_repository import ExternalVisitorService
from dataclasses import dataclass
from typing import List, Any


@dataclass
class MockVisit:
    """Mock visit data for testing."""

    date: str
    dropped_fractions: List[dict[str, Any]]
    person_id: str
    visit_id: str


class TestPriceCalculatorWithMonthlySurcharge:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock the external visitor service
        self.mock_visitor_service = Mock(spec=ExternalVisitorService)

        # Create a real monthly visit tracker
        self.visit_tracker = MonthlyVisitTracker()

        # Create the price calculator with both dependencies
        self.calculator = PriceCalculator(self.mock_visitor_service, self.visit_tracker)

        # Mock visitor data (with city for pricing)
        mock_visitor = Mock()
        mock_visitor.city = "Oak City"
        self.mock_visitor_service.get_visitor_by_id.return_value = mock_visitor

    def test_first_visit_no_surcharge(self):
        """Test that the first visit in a month has no surcharge applied."""
        visit = MockVisit(
            date="2025-09-15T10:00:00Z",
            dropped_fractions=[
                {
                    "fraction_type": "Green waste",
                    "amount_dropped": 10,
                }  # 10kg * 0.08 = 0.80 EUR
            ],
            person_id="user1",
            visit_id="visit1",
        )

        response = self.calculator.calculate(visit)

        # Expected: 10kg * 0.08 (Oak City green waste rate) = 0.80 EUR (no surcharge)
        assert response.price_amount == 0.80
        assert response.person_id == "user1"
        assert response.visit_id == "visit1"

    def test_second_visit_no_surcharge(self):
        """Test that the second visit in a month has no surcharge applied."""
        # First visit
        visit1 = MockVisit(
            date="2025-09-15T10:00:00Z",
            dropped_fractions=[{"fraction_type": "Green waste", "amount_dropped": 10}],
            person_id="user1",
            visit_id="visit1",
        )
        self.calculator.calculate(visit1)

        # Second visit
        visit2 = MockVisit(
            date="2025-09-20T10:00:00Z",
            dropped_fractions=[{"fraction_type": "Green waste", "amount_dropped": 10}],
            person_id="user1",
            visit_id="visit2",
        )

        response = self.calculator.calculate(visit2)

        # Expected: 10kg * 0.08 = 0.80 EUR (no surcharge for 2nd visit)
        assert response.price_amount == 0.80

    def test_third_visit_applies_surcharge(self):
        """Test that the third visit in a month applies 5% surcharge."""
        # First two visits
        visit1 = MockVisit(
            date="2025-09-15T10:00:00Z",
            dropped_fractions=[{"fraction_type": "Green waste", "amount_dropped": 10}],
            person_id="user1",
            visit_id="visit1",
        )
        visit2 = MockVisit(
            date="2025-09-20T10:00:00Z",
            dropped_fractions=[{"fraction_type": "Green waste", "amount_dropped": 10}],
            person_id="user1",
            visit_id="visit2",
        )
        self.calculator.calculate(visit1)
        self.calculator.calculate(visit2)

        # Third visit (should have surcharge)
        visit3 = MockVisit(
            date="2025-09-25T10:00:00Z",
            dropped_fractions=[{"fraction_type": "Green waste", "amount_dropped": 10}],
            person_id="user1",
            visit_id="visit3",
        )

        response = self.calculator.calculate(visit3)

        # Expected: (10kg * 0.08) + 5% surcharge = 0.80 + 0.04 = 0.84 EUR
        assert round(response.price_amount, 2) == 0.84

    def test_fourth_visit_also_applies_surcharge(self):
        """Test that the fourth visit also applies 5% surcharge."""
        # First three visits
        for i in range(3):
            visit = MockVisit(
                date=f"2025-09-{15 + i*5}T10:00:00Z",
                dropped_fractions=[
                    {"fraction_type": "Green waste", "amount_dropped": 10}
                ],
                person_id="user1",
                visit_id=f"visit{i+1}",
            )
            self.calculator.calculate(visit)

        # Fourth visit (should have surcharge)
        visit4 = MockVisit(
            date="2025-09-30T10:00:00Z",
            dropped_fractions=[{"fraction_type": "Green waste", "amount_dropped": 10}],
            person_id="user1",
            visit_id="visit4",
        )

        response = self.calculator.calculate(visit4)

        # Expected: (10kg * 0.08) + 5% surcharge = 0.80 + 0.04 = 0.84 EUR
        assert round(response.price_amount, 2) == 0.84

    def test_month_boundary_resets_counter(self):
        """Test that crossing month boundary resets the visit counter."""
        # Three visits in September (to trigger surcharge)
        for i in range(3):
            visit = MockVisit(
                date=f"2025-09-{15 + i*5}T10:00:00Z",
                dropped_fractions=[
                    {"fraction_type": "Green waste", "amount_dropped": 10}
                ],
                person_id="user1",
                visit_id=f"sept_visit{i+1}",
            )
            response = self.calculator.calculate(visit)

            if i == 2:  # Third visit should have surcharge
                assert round(response.price_amount, 2) == 0.84  # 0.80 + 5%

        # First visit in October (should not have surcharge - counter reset)
        oct_visit = MockVisit(
            date="2025-10-05T10:00:00Z",
            dropped_fractions=[{"fraction_type": "Green waste", "amount_dropped": 10}],
            person_id="user1",
            visit_id="oct_visit1",
        )

        response = self.calculator.calculate(oct_visit)

        # Expected: No surcharge for first visit in new month
        assert response.price_amount == 0.80

    def test_different_users_separate_counters(self):
        """Test that different users have separate visit counters."""
        # Two visits for user1
        for i in range(2):
            visit = MockVisit(
                date=f"2025-09-{15 + i*5}T10:00:00Z",
                dropped_fractions=[
                    {"fraction_type": "Green waste", "amount_dropped": 10}
                ],
                person_id="user1",
                visit_id=f"user1_visit{i+1}",
            )
            self.calculator.calculate(visit)

        # One visit for user2 (should not have surcharge even though user1 has 2 visits)
        user2_visit = MockVisit(
            date="2025-09-25T10:00:00Z",
            dropped_fractions=[{"fraction_type": "Green waste", "amount_dropped": 10}],
            person_id="user2",
            visit_id="user2_visit1",
        )

        response = self.calculator.calculate(user2_visit)

        # Expected: No surcharge for user2's first visit
        assert response.price_amount == 0.80
        assert response.person_id == "user2"

    def test_complex_scenario_with_mixed_waste_types(self):
        """Test surcharge calculation with mixed waste types and higher prices."""
        # Setup visits to trigger surcharge
        for i in range(2):
            visit = MockVisit(
                date=f"2025-09-{10 + i*5}T10:00:00Z",
                dropped_fractions=[
                    {"fraction_type": "Green waste", "amount_dropped": 5}
                ],
                person_id="user1",
                visit_id=f"setup_visit{i+1}",
            )
            self.calculator.calculate(visit)

        # Third visit with mixed waste types (should have surcharge)
        visit3 = MockVisit(
            date="2025-09-20T10:00:00Z",
            dropped_fractions=[
                {
                    "fraction_type": "Green waste",
                    "amount_dropped": 50,
                },  # 50 * 0.08 = 4.00
                {
                    "fraction_type": "Construction waste",
                    "amount_dropped": 20,
                },  # 20 * 0.19 = 3.80
            ],
            person_id="user1",
            visit_id="visit3",
        )

        response = self.calculator.calculate(visit3)

        # Expected: (4.00 + 3.80) + 5% surcharge = 7.80 + 0.39 = 8.19 EUR
        assert response.price_amount == 8.19
