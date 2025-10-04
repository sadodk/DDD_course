"""Tests for Oak City business construction waste exemption rule."""

import unittest
from datetime import datetime
from typing import List, Optional
from domain.business_rules.concrete_pricing_rules import (
    OakCityBusinessConstructionExemptionRule,
)
from domain.business_rules.interface_pricing_rules import PricingContext
from domain.values.dropped_fraction import DroppedFraction, FractionType
from domain.values.weight import Weight
from domain.values.price import Price, Currency
from domain.entities.business import Business
from domain.entities.visitor import Visitor
from domain.repositories.business_repository import BusinessRepository
from domain.types import PersonId, BusinessId, CardId, EmailAddress
from infrastructure.repositories.in_memory_exemption_repository import (
    InMemoryExemptionRepository,
)


class MockBusinessRepository(BusinessRepository):
    """Mock business repository for testing."""

    def __init__(self):
        """Initialize with test data."""
        self.businesses = {}
        self.visitor_map = {}

    def find_by_id(self, business_id: BusinessId) -> Optional[Business]:
        """Find business by ID."""
        return self.businesses.get(business_id)

    def find_by_visitor_id(self, visitor_id: PersonId) -> Optional[Business]:
        """Find business by visitor ID."""
        business_id = self.visitor_map.get(visitor_id)
        return self.businesses.get(business_id)

    def save(self, business: Business) -> None:
        """Save business entity."""
        self.businesses[business.business_id] = business
        for employee in business.employees:
            self.visitor_map[employee.id] = business.business_id

    def get_all(self) -> List[Business]:
        """Get all businesses."""
        return list(self.businesses.values())

    def clear_all_businesses(self) -> None:
        """Clear all businesses."""
        self.businesses.clear()
        self.visitor_map.clear()

    # Implement required abstract methods
    def get_or_create_business_for_visitor(self, visitor: Visitor) -> Business:
        """Get or create business for visitor."""
        if visitor.id in self.visitor_map:
            return self.businesses[self.visitor_map[visitor.id]]

        business_id = Business.create_business_id(visitor.city, visitor.address)
        business = Business(
            business_id=business_id,
            name=f"Business at {visitor.address}, {visitor.city}",
            address=visitor.address,
            city=visitor.city,
        )
        business.add_employee(visitor)
        self.save(business)
        return business

    def clear(self) -> None:
        """Clear all businesses."""
        self.businesses.clear()
        self.visitor_map.clear()

    def add_test_business(
        self, business_id: BusinessId, visitor_id: PersonId
    ) -> Business:
        """Helper to add a test business with a visitor."""
        visitor = Visitor(
            id=visitor_id,
            type="business",
            address="123 Test St",
            city="Oak City",
            card_id=CardId("card123"),
            email=EmailAddress("test@example.com"),
        )
        business = Business(
            business_id=business_id,
            name="Test Business",
            address="123 Test St",
            city="Oak City",
        )
        business.add_employee(visitor)
        self.save(business)
        return business


class TestOakCityBusinessConstructionExemptionRule(unittest.TestCase):
    """Test the Oak City business construction waste exemption rule."""

    def setUp(self):
        """Set up test fixtures."""
        # Create fresh repositories for each test
        self.exemption_repository = InMemoryExemptionRepository()
        self.business_repository = MockBusinessRepository()

        # Create business IDs for testing
        self.business1_id = BusinessId("business1")
        self.business2_id = BusinessId("business2")

        # Create visitor IDs and map them to businesses
        self.visitor1_id = PersonId("visitor1")
        self.visitor2_id = PersonId("visitor2")

        # Create test businesses with visitors
        self.business1 = self.business_repository.add_test_business(
            self.business1_id, self.visitor1_id
        )
        self.business2 = self.business_repository.add_test_business(
            self.business2_id, self.visitor2_id
        )

        # Create rule with repositories
        self.rule = OakCityBusinessConstructionExemptionRule(
            self.exemption_repository, self.business_repository
        )

    def tearDown(self):
        """Clean up after each test."""
        # Clear repository after each test
        self.exemption_repository.clear_all_exemptions()
        self.business_repository.clear()

    def test_can_apply_oak_city_business_with_required_fields(self):
        """Rule should apply to Oak City business customers with visitor_id and visit_date."""
        context = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=str(self.visitor1_id),
            visit_date=datetime(2025, 9, 28),
        )
        self.assertTrue(self.rule.can_apply(context))

    def test_cannot_apply_individual_customer(self):
        """Rule should not apply to individual customers."""
        context = PricingContext(
            customer_type="individual",
            city="Oak City",
            visitor_id=str(self.visitor1_id),
            visit_date=datetime(2025, 9, 28),
        )
        self.assertFalse(self.rule.can_apply(context))

    def test_cannot_apply_different_city(self):
        """Rule should not apply to customers from other cities."""
        context = PricingContext(
            customer_type="business",
            city="Pineville",
            visitor_id=str(self.visitor1_id),
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
            visitor_id=str(self.visitor1_id),
            visit_date=None,
        )
        self.assertFalse(self.rule.can_apply(context))

    def test_construction_waste_within_exemption_limit(self):
        """Test pricing for construction waste fully within exemption limit."""
        fraction = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(600))
        context = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=str(self.visitor1_id),
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
            visitor_id=str(self.visitor1_id),
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
        visit_date = datetime(2025, 9, 28)
        context = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=str(self.visitor1_id),
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
            visitor_id=str(self.visitor1_id),
            visit_date=datetime(2025, 9, 28),
        )

        price = self.rule.calculate_price(fraction, context)
        expected_price = Price(
            500 * 0.08, Currency.EUR
        )  # Standard Oak City business green waste rate
        self.assertEqual(price.amount, expected_price.amount)

    def test_exemption_resets_different_calendar_years(self):
        """Test that exemptions reset between calendar years."""
        # First year: use full exemption
        context_2025 = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=str(self.visitor1_id),
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
            visitor_id=str(self.visitor1_id),
            visit_date=datetime(2026, 1, 1),
        )
        fraction2 = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(800))
        price2 = self.rule.calculate_price(fraction2, context_2026)
        expected_price2 = Price(800 * 0.21, Currency.EUR)  # All at low rate again
        self.assertEqual(price2.amount, expected_price2.amount)

    def test_different_business_separate_exemptions(self):
        """Test that different businesses have separate exemption limits."""
        visit_date = datetime(2025, 9, 28)

        # First business uses exemption
        context1 = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=str(self.visitor1_id),
            visit_date=visit_date,
        )
        fraction1 = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(1000))
        price1 = self.rule.calculate_price(fraction1, context1)
        expected_price1 = Price(1000 * 0.21, Currency.EUR)
        self.assertEqual(price1.amount, expected_price1.amount)

        # Second business should have full exemption available
        context2 = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=str(self.visitor2_id),
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

    def test_business_employees_share_exemption(self):
        """Test that employees from the same business share exemption limits."""
        visit_date = datetime(2025, 9, 28)

        # Create another visitor for the first business
        visitor3_id = PersonId("visitor3")
        self.business_repository.add_test_business(self.business1_id, visitor3_id)

        # First employee uses 800kg of exemption
        context1 = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=str(self.visitor1_id),
            visit_date=visit_date,
        )
        fraction1 = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(800))
        price1 = self.rule.calculate_price(fraction1, context1)
        expected_price1 = Price(800 * 0.21, Currency.EUR)
        self.assertEqual(price1.amount, expected_price1.amount)

        # Second employee from same business has only 200kg exemption remaining
        context2 = PricingContext(
            customer_type="business",
            city="Oak City",
            visitor_id=str(visitor3_id),
            visit_date=visit_date,
        )
        fraction2 = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(400))
        price2 = self.rule.calculate_price(fraction2, context2)
        expected_amount2 = (200 * 0.21) + (
            200 * 0.29
        )  # Split between low and high rate
        expected_price2 = Price(expected_amount2, Currency.EUR)
        self.assertEqual(price2.amount, expected_price2.amount)


class TestExemptionRepository(unittest.TestCase):
    """Test the exemption repository."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a fresh repository for each test
        self.exemption_repository = InMemoryExemptionRepository()

        # Create business IDs for testing
        self.business1_id = BusinessId("business1")
        self.business2_id = BusinessId("business2")

    def tearDown(self):
        """Clean up after each test."""
        # Clear repository after each test
        self.exemption_repository.clear_all_exemptions()

    def test_get_used_exemption_no_prior_usage(self):
        """Test getting exemption usage with no prior usage."""
        usage = self.exemption_repository.get_used_exemption(self.business1_id, 2025)
        self.assertEqual(usage, 0)

    def test_record_and_get_construction_waste(self):
        """Test recording and retrieving construction waste usage."""
        visit_date = datetime(2025, 9, 28)
        self.exemption_repository.record_waste(self.business1_id, 600, visit_date)

        usage = self.exemption_repository.get_used_exemption(self.business1_id, 2025)
        self.assertEqual(usage, 600.0)

    def test_cumulative_construction_waste_same_year(self):
        """Test that construction waste accumulates within the same year."""
        visit_date1 = datetime(2025, 3, 15)
        visit_date2 = datetime(2025, 9, 28)

        self.exemption_repository.record_waste(self.business1_id, 400, visit_date1)
        self.exemption_repository.record_waste(self.business1_id, 300, visit_date2)

        usage = self.exemption_repository.get_used_exemption(self.business1_id, 2025)
        self.assertEqual(usage, 700.0)

    def test_calculate_tiered_pricing_within_limit(self):
        """Test tiered pricing calculation when fully within exemption limit."""
        visit_date = datetime(2025, 9, 28)
        low_rate, high_rate = self.exemption_repository.calculate_tiered_weights(
            self.business1_id, 600, visit_date, 1000
        )

        self.assertEqual(low_rate, 600.0)
        self.assertEqual(high_rate, 0.0)

    def test_calculate_tiered_pricing_exceeding_limit(self):
        """Test tiered pricing calculation when exceeding exemption limit."""
        visit_date = datetime(2025, 9, 28)
        low_rate, high_rate = self.exemption_repository.calculate_tiered_weights(
            self.business1_id, 1500, visit_date, 1000
        )

        self.assertEqual(low_rate, 1000.0)  # Exemption limit
        self.assertEqual(high_rate, 500.0)  # Excess

    def test_calculate_tiered_pricing_with_prior_usage(self):
        """Test tiered pricing with prior exemption usage."""
        visit_date1 = datetime(2025, 3, 15)
        visit_date2 = datetime(2025, 9, 28)

        # First visit uses 600kg of exemption
        self.exemption_repository.record_waste(self.business1_id, 600, visit_date1)

        # Second visit: 900kg (400kg exemption remaining, 500kg at high rate)
        low_rate, high_rate = self.exemption_repository.calculate_tiered_weights(
            self.business1_id, 900, visit_date2, 1000
        )

        self.assertEqual(low_rate, 400)  # Remaining exemption
        self.assertEqual(high_rate, 500)  # Excess

    def test_separate_years_separate_exemptions(self):
        """Test that different years have separate exemption limits."""
        visit_date_2025 = datetime(2025, 12, 31)
        visit_date_2026 = datetime(2026, 1, 1)

        # Use exemption in 2025
        self.exemption_repository.record_waste(self.business1_id, 1000, visit_date_2025)

        # 2026 should have fresh exemption
        low_rate, high_rate = self.exemption_repository.calculate_tiered_weights(
            self.business1_id, 800, visit_date_2026, 1000
        )

        self.assertEqual(low_rate, 800)  # Full exemption available
        self.assertEqual(high_rate, 0)

    def test_different_businesses_separate_tracking(self):
        """Test that different businesses are tracked separately."""
        visit_date = datetime(2025, 9, 28)

        # Business 1 uses exemption
        self.exemption_repository.record_waste(self.business1_id, 1000, visit_date)

        # Business 2 should have full exemption
        low_rate, high_rate = self.exemption_repository.calculate_tiered_weights(
            self.business2_id, 800, visit_date, 1000
        )

        self.assertEqual(low_rate, 800)
        self.assertEqual(high_rate, 0)

    def test_clear_all_exemptions(self):
        """Test clearing all exemption data."""
        visit_date = datetime(2025, 9, 28)
        self.exemption_repository.record_waste(self.business1_id, 600, visit_date)

        # Verify data exists
        self.assertEqual(
            self.exemption_repository.get_used_exemption(self.business1_id, 2025), 600.0
        )

        # Clear and verify
        self.exemption_repository.clear_all_exemptions()
        self.assertEqual(
            self.exemption_repository.get_used_exemption(self.business1_id, 2025), 0.0
        )


if __name__ == "__main__":
    unittest.main()
