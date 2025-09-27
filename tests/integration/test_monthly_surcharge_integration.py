"""Integration tests for the monthly surcharge feature."""

from unittest.mock import patch

from application.application_context import ApplicationContext
from application.external_visitor_service import VisitorInfo


class TestMonthlySurchargeIntegration:
    """Integration tests for monthly surcharge feature using clean DDD architecture."""

    def setup_method(self):
        """Set up test environment."""
        self.app = ApplicationContext()

        # Mock visitor data
        self.mock_visitor = VisitorInfo(
            id="visitor123",
            type="individual",
            address="123 Test Street",
            city="Amsterdam",
            card_id="CARD001",
            email="test@example.com",
        )

    def test_no_surcharge_with_two_visits(self):
        """Test that no surcharge is applied with only 2 visits in a month."""
        # Mock the external visitor service
        with patch.object(
            self.app.visitor_service,
            "get_visitor_by_id",
            return_value=self.mock_visitor,
        ):
            # First visit
            visit1_data = {
                "person_id": "visitor123",
                "visit_id": "visit1",
                "date": "2025-09-05T10:00:00",
                "dropped_fractions": [
                    {"fraction_type": "Green waste", "amount_dropped": 10}
                ],
            }

            result1 = self.app.price_calculator.calculate_price(visit1_data)

            # Second visit
            visit2_data = {
                "person_id": "visitor123",
                "visit_id": "visit2",
                "date": "2025-09-15T10:00:00",
                "dropped_fractions": [
                    {"fraction_type": "Green waste", "amount_dropped": 10}
                ],
            }

            result2 = self.app.price_calculator.calculate_price(visit2_data)

            # Both visits should have no surcharge (base price = 10 * 0.10 = 1.00 EUR)
            assert result1.price_amount == 1.0
            assert result2.price_amount == 1.0
            assert result1.price_currency == "EUR"
            assert result2.price_currency == "EUR"

    def test_surcharge_applied_with_three_visits(self):
        """Test that 5% surcharge is applied starting from the 3rd visit in a month."""
        # Mock the external visitor service
        with patch.object(
            self.app.visitor_service,
            "get_visitor_by_id",
            return_value=self.mock_visitor,
        ):
            # First two visits (no surcharge expected)
            visit1_data = {
                "person_id": "visitor123",
                "visit_id": "visit1",
                "date": "2025-09-05T10:00:00",
                "dropped_fractions": [
                    {"fraction_type": "Green waste", "amount_dropped": 10}
                ],
            }

            visit2_data = {
                "person_id": "visitor123",
                "visit_id": "visit2",
                "date": "2025-09-15T10:00:00",
                "dropped_fractions": [
                    {"fraction_type": "Green waste", "amount_dropped": 10}
                ],
            }

            # Third visit (surcharge should apply to all visits this month)
            visit3_data = {
                "person_id": "visitor123",
                "visit_id": "visit3",
                "date": "2025-09-25T10:00:00",
                "dropped_fractions": [
                    {"fraction_type": "Green waste", "amount_dropped": 10}
                ],
            }

            result1 = self.app.price_calculator.calculate_price(visit1_data)
            result2 = self.app.price_calculator.calculate_price(visit2_data)
            result3 = self.app.price_calculator.calculate_price(visit3_data)

            # First two visits: base price only (1.00 EUR)
            assert result1.price_amount == 1.0
            assert result2.price_amount == 1.0

            # Third visit triggers surcharge for all visits
            # Base price = 1.00, surcharge = 0.05, total = 1.05 EUR
            assert result3.price_amount == 1.05

    def test_surcharge_applies_to_different_waste_types(self):
        """Test surcharge works with different waste types."""
        with patch.object(
            self.app.visitor_service,
            "get_visitor_by_id",
            return_value=self.mock_visitor,
        ):
            visits_data = [
                {
                    "person_id": "visitor123",
                    "visit_id": "visit1",
                    "date": "2025-09-05T10:00:00",
                    "dropped_fractions": [
                        {"fraction_type": "Green waste", "amount_dropped": 10}
                    ],  # 1.00 EUR
                },
                {
                    "person_id": "visitor123",
                    "visit_id": "visit2",
                    "date": "2025-09-15T10:00:00",
                    "dropped_fractions": [
                        {"fraction_type": "Construction waste", "amount_dropped": 10}
                    ],  # 1.90 EUR
                },
                {
                    "person_id": "visitor123",
                    "visit_id": "visit3",
                    "date": "2025-09-25T10:00:00",
                    "dropped_fractions": [
                        {"fraction_type": "Green waste", "amount_dropped": 5}
                    ],  # 0.50 EUR
                },
            ]

            results = []
            for visit_data in visits_data:
                result = self.app.price_calculator.calculate_price(visit_data)
                results.append(result)

            # First two visits: base price only
            assert results[0].price_amount == 1.0  # Green waste
            assert results[1].price_amount == 1.9  # Construction waste

            # Third visit triggers surcharge
            # Base: 0.50, Surcharge: 0.025, Total: 0.525 ≈ 0.53
            assert abs(results[2].price_amount - 0.53) < 0.01

    def test_monthly_surcharge_resets_each_month(self):
        """Test that surcharge calculation resets for different months."""
        with patch.object(
            self.app.visitor_service,
            "get_visitor_by_id",
            return_value=self.mock_visitor,
        ):
            # Two visits in September
            sept_visits = [
                {
                    "person_id": "visitor123",
                    "visit_id": "visit1",
                    "date": "2025-09-15T10:00:00",
                    "dropped_fractions": [
                        {"fraction_type": "Green waste", "amount_dropped": 10}
                    ],
                },
                {
                    "person_id": "visitor123",
                    "visit_id": "visit2",
                    "date": "2025-09-25T10:00:00",
                    "dropped_fractions": [
                        {"fraction_type": "Green waste", "amount_dropped": 10}
                    ],
                },
            ]

            # One visit in October (should not trigger surcharge)
            oct_visit = {
                "person_id": "visitor123",
                "visit_id": "visit3",
                "date": "2025-10-05T10:00:00",
                "dropped_fractions": [
                    {"fraction_type": "Green waste", "amount_dropped": 10}
                ],
            }

            # Process September visits
            sept_results = []
            for visit_data in sept_visits:
                result = self.app.price_calculator.calculate_price(visit_data)
                sept_results.append(result)

            # Process October visit
            oct_result = self.app.price_calculator.calculate_price(oct_visit)

            # September visits should have no surcharge (only 2 visits)
            assert sept_results[0].price_amount == 1.0
            assert sept_results[1].price_amount == 1.0

            # October visit should have no surcharge (first visit of the month)
            assert oct_result.price_amount == 1.0

    def test_error_handling_invalid_visitor(self):
        """Test error handling when visitor is not found."""
        # Mock visitor service to return None (visitor not found)
        with patch.object(
            self.app.visitor_service, "get_visitor_by_id", return_value=None
        ):
            visit_data = {
                "person_id": "nonexistent",
                "visit_id": "visit1",
                "date": "2025-09-15T10:00:00",
                "dropped_fractions": [
                    {"fraction_type": "Green waste", "amount_dropped": 10}
                ],
            }

            try:
                self.app.price_calculator.calculate_price(visit_data)
                assert False, "Expected an exception for invalid visitor"
            except Exception as e:
                assert "not found" in str(e).lower() or "visitor" in str(e).lower()

    def test_scenario_reset_functionality(self):
        """Test that scenario reset clears visit history."""
        with patch.object(
            self.app.visitor_service,
            "get_visitor_by_id",
            return_value=self.mock_visitor,
        ):
            # Add some visits
            visit_data = {
                "person_id": "visitor123",
                "visit_id": "visit1",
                "date": "2025-09-15T10:00:00",
                "dropped_fractions": [
                    {"fraction_type": "Green waste", "amount_dropped": 10}
                ],
            }

            self.app.price_calculator.calculate_price(visit_data)

            # Verify visit exists
            assert len(self.app.visit_repository.find_all()) == 1

            # Reset scenario
            self.app.reset_for_new_scenario()

            # Verify visits are cleared
            assert len(self.app.visit_repository.find_all()) == 0
