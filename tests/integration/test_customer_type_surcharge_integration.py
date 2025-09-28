"""Integration test specifically for customer type surcharge rules."""

from unittest.mock import patch

from application.application_context import ApplicationContext
from application.external_visitor_service import VisitorInfo


class TestCustomerTypeSurchargeIntegration:
    """Integration test for customer type specific monthly surcharge rules."""

    def setup_method(self):
        """Set up test environment."""
        self.app = ApplicationContext()

        # Mock visitors - individual and business
        self.individual_visitor = VisitorInfo(
            id="individual123",
            type="individual",
            address="123 Individual Street",
            city="TestCity",
            card_id="CARD001",
            email="individual@example.com",
        )

        self.business_visitor = VisitorInfo(
            id="business456",
            type="business",
            address="456 Business Avenue",
            city="TestCity",
            card_id="CARD002",
            email="business@example.com",
        )

    def test_individual_gets_surcharge_business_does_not(self):
        """Test that individual visitors get surcharge but business visitors don't."""
        # Test individual visitor with 3 visits (should get surcharge)
        with patch.object(
            self.app.visitor_service,
            "get_visitor_by_id",
            return_value=self.individual_visitor,
        ):
            individual_visits = []
            for i in range(3):
                visit_data = {
                    "person_id": "individual123",
                    "visit_id": f"visit{i+1}",
                    "date": f"2025-09-{5 + i * 5:02d}T10:00:00",
                    "dropped_fractions": [
                        {"fraction_type": "Green waste", "amount_dropped": 10}
                    ],
                }
                result = self.app.price_calculator.calculate_price(visit_data)
                individual_visits.append(result)

        # Reset for business visitor test
        self.app.reset_for_new_scenario()

        # Test business visitor with 4 visits (should NOT get surcharge)
        with patch.object(
            self.app.visitor_service,
            "get_visitor_by_id",
            return_value=self.business_visitor,
        ):
            business_visits = []
            for i in range(4):
                visit_data = {
                    "person_id": "business456",
                    "visit_id": f"visit{i+1}",
                    "date": f"2025-09-{5 + i * 3:02d}T10:00:00",
                    "dropped_fractions": [
                        {"fraction_type": "Green waste", "amount_dropped": 10}
                    ],
                }
                result = self.app.price_calculator.calculate_price(visit_data)
                business_visits.append(result)

        # Verify individual visitor gets surcharge correctly
        assert len(individual_visits) == 3
        # First 2 visits should have no surcharge (1.00)
        assert (
            individual_visits[0].price_amount == 1.00
        ), f"Visit 1 should be 1.00, got {individual_visits[0].price_amount}"
        assert (
            individual_visits[1].price_amount == 1.00
        ), f"Visit 2 should be 1.00, got {individual_visits[1].price_amount}"
        # 3rd visit should have surcharge (1.05)
        assert (
            individual_visits[2].price_amount == 1.05
        ), f"Visit 3 should be 1.05, got {individual_visits[2].price_amount}"

        # Verify business visitor never gets surcharge (always 1.00)
        assert len(business_visits) == 4
        for result in business_visits:
            assert (
                result.price_amount == 1.00
            ), f"Business should not get surcharge, got {result.price_amount}"

    def test_business_customer_with_many_visits_no_surcharge(self):
        """Test that business customers never get surcharge, even with many visits."""
        with patch.object(
            self.app.visitor_service,
            "get_visitor_by_id",
            return_value=self.business_visitor,
        ):
            # Make 10 visits (way more than threshold)
            results = []
            for i in range(10):
                visit_data = {
                    "person_id": "business456",
                    "visit_id": f"visit{i+1}",
                    "date": f"2025-09-{(i % 30) + 1:02d}T10:00:00",
                    "dropped_fractions": [
                        {"fraction_type": "Green waste", "amount_dropped": 10}
                    ],
                }
                result = self.app.price_calculator.calculate_price(visit_data)
                results.append(result)

        # All visits should be base price only (no surcharge)
        assert len(results) == 10
        for i, result in enumerate(results):
            assert (
                result.price_amount == 1.00
            ), f"Business visit {i+1} should not have surcharge, got {result.price_amount}"

    def test_individual_business_mixed_in_same_month(self):
        """Test individual and business customers independently in the same month."""
        # Start with individual customer - 3 visits
        with patch.object(
            self.app.visitor_service,
            "get_visitor_by_id",
            return_value=self.individual_visitor,
        ):
            individual_results = []
            for i in range(3):
                visit_data = {
                    "person_id": "individual123",
                    "visit_id": f"ind_visit{i+1}",
                    "date": f"2025-09-{3 + i * 2:02d}T10:00:00",
                    "dropped_fractions": [
                        {"fraction_type": "Green waste", "amount_dropped": 10}
                    ],
                }
                individual_result = self.app.price_calculator.calculate_price(
                    visit_data
                )
                individual_results.append(individual_result)

            # Verify individual customer surcharge: first 2 visits = 1.00, 3rd visit = 1.05
            assert individual_results[0].price_amount == 1.00  # Visit 1: no surcharge
            assert individual_results[1].price_amount == 1.00  # Visit 2: no surcharge
            assert individual_results[2].price_amount == 1.05  # Visit 3: has surcharge

        # Now business customer - 4 visits in same month
        with patch.object(
            self.app.visitor_service,
            "get_visitor_by_id",
            return_value=self.business_visitor,
        ):
            for i in range(4):
                visit_data = {
                    "person_id": "business456",
                    "visit_id": f"bus_visit{i+1}",
                    "date": f"2025-09-{10 + i * 3:02d}T10:00:00",
                    "dropped_fractions": [
                        {"fraction_type": "Green waste", "amount_dropped": 10}
                    ],
                }
                business_result = self.app.price_calculator.calculate_price(visit_data)
                assert business_result.price_amount == 1.00  # No surcharge

        print("✅ Successfully verified:")
        print("- Individual customers get 5% surcharge on 3rd+ visit")
        print("- Business customers never get monthly surcharge")
        print("- Different customer types are tracked independently")
