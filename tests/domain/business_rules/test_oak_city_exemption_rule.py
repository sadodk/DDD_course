"""Tests for Oak City business construction waste exemption rule."""

import unittest
from datetime import datetime
from domain.business_rules.concrete_pricing_rules import (
    OakCityBusinessConstructionExemptionRule,
)
from domain.business_rules.interface_pricing_rules import PricingContext
from domain.dropped_fraction import DroppedFraction, FractionType
from domain.weight import Weight
from domain.price import Price, Currency
from domain.construction_waste_exemption_service import (
    ConstructionWasteExemptionService,
)


class TestOakCityBusinessConstructionExemptionRule(unittest.TestCase):
    """Test the Oak City business construction waste exemption rule."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset singleton to ensure test isolation
        ConstructionWasteExemptionService.reset_singleton()
        self.exemption_service = ConstructionWasteExemptionService()
        self.rule = OakCityBusinessConstructionExemptionRule(self.exemption_service)

    def tearDown(self):
        """Clean up after each test."""
        # Reset singleton after each test to ensure isolation
        ConstructionWasteExemptionService.reset_singleton()

    def test_can_apply_oak_city_business_with_required_fields(self):
        """Rule should apply to Oak City business customers with visitor_id and visit_date."""
        context = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id="visitor123",
            visit_date=datetime(2025, 9, 28),
        )
        self.assertTrue(self.rule.can_apply(context))

    def test_cannot_apply_individual_customer(self):
        """Rule should not apply to individual customers."""
        context = PricingContext(
            customer_type="individual",
            city="Oak City",
            visitor_id="visitor123",
            visit_date=datetime(2025, 9, 28),
        )
        self.assertFalse(self.rule.can_apply(context))

    def test_cannot_apply_different_city(self):
        """Rule should not apply to customers from other cities."""
        context = PricingContext(
            customer_type="business",
            city="Pineville",
            visitor_id="visitor123",
            visit_date=datetime(2025, 9, 28),
        )
        self.assertFalse(self.rule.can_apply(context))

    def test_cannot_apply_missing_visitor_id(self):
        """Rule should not apply when visitor_id is missing."""
        context = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=None,
            visit_date=datetime(2025, 9, 28),
        )
        self.assertFalse(self.rule.can_apply(context))

    def test_cannot_apply_missing_visit_date(self):
        """Rule should not apply when visit_date is missing."""
        context = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id="visitor123",
            visit_date=None,
        )
        self.assertFalse(self.rule.can_apply(context))

    def test_construction_waste_within_exemption_limit(self):
        """Test pricing for construction waste fully within exemption limit."""
        fraction = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(600))
        context = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id="visitor123",
            visit_date=datetime(2025, 9, 28),
        )

        price = self.rule.calculate_price(fraction, context)
        expected_price = Price(600 * 0.21, Currency.EUR)  # All at low rate
        self.assertEqual(price.amount, expected_price.amount)
        self.assertEqual(price.currency, expected_price.currency)

    def test_construction_waste_exceeding_exemption_limit(self):
        """Test pricing for construction waste exceeding exemption limit."""
        fraction = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(1500))
        context = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id="visitor123",
            visit_date=datetime(2025, 9, 28),
        )

        price = self.rule.calculate_price(fraction, context)
        # 1000kg at 0.21 + 500kg at 0.29
        expected_amount = (1000 * 0.21) + (500 * 0.29)
        expected_price = Price(expected_amount, Currency.EUR)
        self.assertEqual(price.amount, expected_price.amount)
        self.assertEqual(price.currency, expected_price.currency)

    def test_multiple_visits_within_year_scenario(self):
        """Test the specific scenario from requirements: 600kg + 900kg visits."""
        visitor_id = "visitor123"
        visit_date = datetime(2025, 9, 28)
        context = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=visitor_id,
            visit_date=visit_date,
        )

        # First visit: 600kg
        fraction1 = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(600))
        price1 = self.rule.calculate_price(fraction1, context)
        expected_price1 = Price(600 * 0.21, Currency.EUR)  # All at low rate
        self.assertEqual(price1.amount, expected_price1.amount)

        # Second visit: 900kg (400kg at low rate, 500kg at high rate)
        fraction2 = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(900))
        price2 = self.rule.calculate_price(fraction2, context)
        expected_amount2 = (400 * 0.21) + (
            500 * 0.29
        )  # 400kg remaining exemption + 500kg at high rate
        expected_price2 = Price(expected_amount2, Currency.EUR)
        self.assertEqual(price2.amount, expected_price2.amount)

    def test_green_waste_uses_standard_rate(self):
        """Test that green waste uses standard Oak City business rate."""
        fraction = DroppedFraction(FractionType.GREEN_WASTE, Weight(500))
        context = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id="visitor123",
            visit_date=datetime(2025, 9, 28),
        )

        price = self.rule.calculate_price(fraction, context)
        expected_price = Price(
            500 * 0.08, Currency.EUR
        )  # Standard Oak City business green waste rate
        self.assertEqual(price.amount, expected_price.amount)

    def test_exemption_resets_different_calendar_years(self):
        """Test that exemptions reset between calendar years."""
        visitor_id = "visitor123"

        # First year: use full exemption
        context_2025 = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=visitor_id,
            visit_date=datetime(2025, 12, 31),
        )
        fraction = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(1000))
        price1 = self.rule.calculate_price(fraction, context_2025)
        expected_price1 = Price(1000 * 0.21, Currency.EUR)  # All at low rate
        self.assertEqual(price1.amount, expected_price1.amount)

        # Second year: exemption should reset
        context_2026 = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=visitor_id,
            visit_date=datetime(2026, 1, 1),
        )
        fraction2 = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(800))
        price2 = self.rule.calculate_price(fraction2, context_2026)
        expected_price2 = Price(800 * 0.21, Currency.EUR)  # All at low rate again
        self.assertEqual(price2.amount, expected_price2.amount)

    def test_different_visitors_separate_exemptions(self):
        """Test that different visitors have separate exemption limits."""
        visit_date = datetime(2025, 9, 28)

        # First visitor uses exemption
        context1 = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id="visitor1",
            visit_date=visit_date,
        )
        fraction1 = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(1000))
        price1 = self.rule.calculate_price(fraction1, context1)
        expected_price1 = Price(1000 * 0.21, Currency.EUR)
        self.assertEqual(price1.amount, expected_price1.amount)

        # Second visitor should have full exemption available
        context2 = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id="visitor2",
            visit_date=visit_date,
        )
        fraction2 = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(1000))
        price2 = self.rule.calculate_price(fraction2, context2)
        expected_price2 = Price(1000 * 0.21, Currency.EUR)
        self.assertEqual(price2.amount, expected_price2.amount)

    def test_rule_priority(self):
        """Test that the rule has high priority to override regular Oak City rule."""
        self.assertEqual(self.rule.get_priority(), 5)

    def test_calculate_price_missing_required_fields(self):
        """Test that calculate_price raises ValueError when required fields are missing."""
        fraction = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(600))
        context = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=None,  # Missing
            visit_date=datetime(2025, 9, 28),
        )

        with self.assertRaises(ValueError) as cm:
            self.rule.calculate_price(fraction, context)
        self.assertIn("visitor_id and visit_date are required", str(cm.exception))


class TestConstructionWasteExemptionService(unittest.TestCase):
    """Test the construction waste exemption service."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset singleton to ensure test isolation
        ConstructionWasteExemptionService.reset_singleton()
        self.service = ConstructionWasteExemptionService()

    def tearDown(self):
        """Clean up after each test."""
        # Reset singleton after each test to ensure isolation
        ConstructionWasteExemptionService.reset_singleton()

    def test_get_used_exemption_no_prior_usage(self):
        """Test getting exemption usage with no prior usage."""
        usage = self.service.get_used_exemption("visitor1", 2025)
        self.assertEqual(usage, 0.0)

    def test_record_and_get_construction_waste(self):
        """Test recording and retrieving construction waste usage."""
        visit_date = datetime(2025, 9, 28)
        self.service.record_construction_waste("visitor1", 600.0, visit_date)

        usage = self.service.get_used_exemption("visitor1", 2025)
        self.assertEqual(usage, 600.0)

    def test_cumulative_construction_waste_same_year(self):
        """Test that construction waste accumulates within the same year."""
        visit_date1 = datetime(2025, 3, 15)
        visit_date2 = datetime(2025, 9, 28)

        self.service.record_construction_waste("visitor1", 400.0, visit_date1)
        self.service.record_construction_waste("visitor1", 300.0, visit_date2)

        usage = self.service.get_used_exemption("visitor1", 2025)
        self.assertEqual(usage, 700.0)

    def test_calculate_tiered_pricing_within_limit(self):
        """Test tiered pricing calculation when fully within exemption limit."""
        visit_date = datetime(2025, 9, 28)
        low_rate, high_rate = self.service.calculate_tiered_pricing(
            "visitor1", 600.0, visit_date
        )

        self.assertEqual(low_rate, 600.0)
        self.assertEqual(high_rate, 0.0)

    def test_calculate_tiered_pricing_exceeding_limit(self):
        """Test tiered pricing calculation when exceeding exemption limit."""
        visit_date = datetime(2025, 9, 28)
        low_rate, high_rate = self.service.calculate_tiered_pricing(
            "visitor1", 1500.0, visit_date
        )

        self.assertEqual(low_rate, 1000.0)  # Exemption limit
        self.assertEqual(high_rate, 500.0)  # Excess

    def test_calculate_tiered_pricing_with_prior_usage(self):
        """Test tiered pricing with prior exemption usage."""
        visit_date1 = datetime(2025, 3, 15)
        visit_date2 = datetime(2025, 9, 28)

        # First visit uses 600kg of exemption
        self.service.record_construction_waste("visitor1", 600.0, visit_date1)

        # Second visit: 900kg (400kg exemption remaining, 500kg at high rate)
        low_rate, high_rate = self.service.calculate_tiered_pricing(
            "visitor1", 900.0, visit_date2
        )

        self.assertEqual(low_rate, 400.0)  # Remaining exemption
        self.assertEqual(high_rate, 500.0)  # Excess

    def test_separate_years_separate_exemptions(self):
        """Test that different years have separate exemption limits."""
        visit_date_2025 = datetime(2025, 12, 31)
        visit_date_2026 = datetime(2026, 1, 1)

        # Use exemption in 2025
        self.service.record_construction_waste("visitor1", 1000.0, visit_date_2025)

        # 2026 should have fresh exemption
        low_rate, high_rate = self.service.calculate_tiered_pricing(
            "visitor1", 800.0, visit_date_2026
        )

        self.assertEqual(low_rate, 800.0)  # Full exemption available
        self.assertEqual(high_rate, 0.0)

    def test_different_visitors_separate_tracking(self):
        """Test that different visitors are tracked separately."""
        visit_date = datetime(2025, 9, 28)

        # Visitor 1 uses exemption
        self.service.record_construction_waste("visitor1", 1000.0, visit_date)

        # Visitor 2 should have full exemption
        low_rate, high_rate = self.service.calculate_tiered_pricing(
            "visitor2", 800.0, visit_date
        )

        self.assertEqual(low_rate, 800.0)
        self.assertEqual(high_rate, 0.0)

    def test_clear_all_exemptions(self):
        """Test clearing all exemption data."""
        visit_date = datetime(2025, 9, 28)
        self.service.record_construction_waste("visitor1", 600.0, visit_date)

        # Verify data exists
        self.assertEqual(self.service.get_used_exemption("visitor1", 2025), 600.0)

        # Clear and verify
        self.service.clear_all_exemptions()
        self.assertEqual(self.service.get_used_exemption("visitor1", 2025), 0.0)


if __name__ == "__main__":
    unittest.main()
