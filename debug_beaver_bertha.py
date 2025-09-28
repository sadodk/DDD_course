#!/usr/bin/env python3
"""Debug script to understand the Beaver Bertha pricing calculation issue."""

from datetime import datetime
from unittest.mock import patch

# Import our application components
from application.application_context import ApplicationContext
from application.external_visitor_service import VisitorInfo
from domain.business_rules.interface_pricing_rules import PricingContext
from domain.business_rules.pricing_rule_engine import PricingRuleEngine
from domain.dropped_fraction import DroppedFraction, FractionType
from domain.weight import Weight


def debug_beaver_bertha_pricing():
    """Debug the Beaver Bertha pricing calculation."""
    print("🦫 BEAVER BERTHA PRICING DEBUG")
    print("=" * 50)

    # Test data from the failing scenario
    visit_data = {
        "date": "2023-07-23",
        "dropped_fractions": [
            {"amount_dropped": 1803, "fraction_type": "Construction waste"}
        ],
        "person_id": "Beaver Bertha",
        "visit_id": "2",
    }

    print(f"Input data: {visit_data}")
    print()

    # Create application context
    app = ApplicationContext()

    # Test different customer scenarios
    scenarios = [
        (
            "Default customer",
            VisitorInfo(
                "Beaver Bertha",
                "individual",
                "123 Street",
                "",
                "CARD1",
                "test@example.com",
            ),
        ),
        (
            "Individual from unknown city",
            VisitorInfo(
                "Beaver Bertha",
                "individual",
                "123 Street",
                "Unknown City",
                "CARD1",
                "test@example.com",
            ),
        ),
        (
            "Business from unknown city",
            VisitorInfo(
                "Beaver Bertha",
                "business",
                "123 Street",
                "Unknown City",
                "CARD1",
                "test@example.com",
            ),
        ),
        (
            "Individual from Oak City",
            VisitorInfo(
                "Beaver Bertha",
                "individual",
                "123 Street",
                "Oak City",
                "CARD1",
                "test@example.com",
            ),
        ),
        (
            "Business from Oak City",
            VisitorInfo(
                "Beaver Bertha",
                "business",
                "123 Street",
                "Oak City",
                "CARD1",
                "test@example.com",
            ),
        ),
    ]

    for scenario_name, mock_visitor in scenarios:
        print(f"🧪 SCENARIO: {scenario_name}")
        print(f"   Type: {mock_visitor.type}, City: {mock_visitor.city}")

        # Mock the external visitor service
        with patch.object(
            app.visitor_service, "get_visitor_by_id", return_value=mock_visitor
        ):
            try:
                # Reset for clean state
                app.reset_for_new_scenario()

                result = app.price_calculator.calculate_price(visit_data)
                print(f"   💰 Price: {result.price_amount} EUR")

                if result.price_amount == 490.63:
                    print("   ✅ MATCHES EXPECTED!")
                elif result.price_amount == 378.63:
                    print("   ⚠️  Matches actual (but wrong)")

                # Also test with direct pricing engine to understand the rules
                context = PricingContext(
                    customer_type=mock_visitor.type,
                    city=mock_visitor.city,
                    visitor_id=mock_visitor.id,
                    visit_date=datetime(2023, 7, 23),
                )

                engine = PricingRuleEngine()
                fraction = DroppedFraction(
                    FractionType.CONSTRUCTION_WASTE, Weight(1803)
                )
                direct_price = engine.calculate_price(fraction, context)
                print(f"   💡 Direct pricing engine: {direct_price.amount} EUR")

            except Exception as e:
                print(f"   ❌ Error: {e}")

        print()

    # Manual calculation check
    print("📊 MANUAL CALCULATIONS:")
    print("-" * 30)
    print("Default rate (0.19): 1803 * 0.19 =", 1803 * 0.19)
    print("Business rate (0.19): 1803 * 0.19 =", 1803 * 0.19)
    print("Oak City individual (0.19): 1803 * 0.19 =", 1803 * 0.19)
    print("Oak City business (0.21): 1803 * 0.21 =", 1803 * 0.21)
    print("Oak City business WITH exemption:")
    print("  First 1000kg: 1000 * 0.21 =", 1000 * 0.21)
    print("  Remaining 803kg: 803 * 0.29 =", 803 * 0.29)
    print("  Total:", (1000 * 0.21) + (803 * 0.29))
    print("Oak City business WITH exemption + 5% surcharge:")
    base_with_exemption = (1000 * 0.21) + (803 * 0.29)
    print("  With surcharge:", base_with_exemption * 1.05)
    print()
    print("Expected: 490.63 EUR")
    print("Actual: 378.63 EUR")
    print("Difference:", 490.63 - 378.63, "EUR")


if __name__ == "__main__":
    debug_beaver_bertha_pricing()
