"""Demonstration of the new Oak City business construction waste exemption rule."""

from datetime import datetime
from domain.business_rules.concrete_pricing_rules import (
    OakCityBusinessConstructionExemptionRule,
)
from domain.business_rules.interface_pricing_rules import PricingContext
from domain.dropped_fraction import DroppedFraction, FractionType
from domain.weight import Weight
from domain.construction_waste_exemption_service import (
    ConstructionWasteExemptionService,
)


def demonstrate_exemption_rule():
    """Demonstrate the Oak City business construction waste exemption rule."""
    print("🏗️ Oak City Business Construction Waste Exemption Rule Demo")
    print("=" * 60)

    # Create the exemption service and rule
    exemption_service = ConstructionWasteExemptionService()
    rule = OakCityBusinessConstructionExemptionRule(exemption_service)

    # Business customer from Oak City
    visitor_id = "business_customer_123"
    visit_date = datetime(2025, 9, 28)
    context = PricingContext(
        customer_type="business",
        city="Oak City",
        visitor_id=visitor_id,
        visit_date=visit_date,
    )

    print(f"Customer: {visitor_id}")
    print(f"City: {context.city}")
    print(f"Customer Type: {context.customer_type}")
    print(f"Visit Date: {visit_date.strftime('%Y-%m-%d')}")
    print()

    # Scenario from requirements: 600kg + 900kg visits
    print("📦 SCENARIO: Multiple visits as described in requirements")
    print("-" * 40)

    # Visit 1: 600kg construction waste
    print("🚛 Visit 1: 600kg construction waste")
    fraction1 = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(600))
    price1 = rule.calculate_price(fraction1, context)
    print(f"   Price calculation: 600kg × €0.21/kg = €{price1.amount:.2f}")
    print(f"   Exemption used so far: 600kg (400kg remaining)")
    print()

    # Visit 2: 900kg construction waste
    print("🚛 Visit 2: 900kg construction waste")
    fraction2 = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(900))
    price2 = rule.calculate_price(fraction2, context)
    expected_low = 400 * 0.21  # Remaining exemption
    expected_high = 500 * 0.29  # Excess at high rate
    expected_total = expected_low + expected_high
    print(f"   Price calculation:")
    print(f"   - 400kg (remaining exemption) × €0.21/kg = €{expected_low:.2f}")
    print(f"   - 500kg (over limit) × €0.29/kg = €{expected_high:.2f}")
    print(f"   - Total: €{price2.amount:.2f}")
    print(f"   Exemption fully used for the year")
    print()

    # Visit 3: Additional construction waste (all at high rate)
    print("🚛 Visit 3: 300kg construction waste (no exemption left)")
    fraction3 = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(300))
    price3 = rule.calculate_price(fraction3, context)
    print(f"   Price calculation: 300kg × €0.29/kg = €{price3.amount:.2f}")
    print(f"   All at high rate (exemption exhausted)")
    print()

    # Test green waste (uses standard rate)
    print("🌿 Green waste pricing (standard rate)")
    green_fraction = DroppedFraction(FractionType.GREEN_WASTE, Weight(200))
    green_price = rule.calculate_price(green_fraction, context)
    print(f"   200kg green waste × €0.08/kg = €{green_price.amount:.2f}")
    print()

    # New year reset demonstration
    print("🗓️ NEW YEAR: Exemption resets")
    print("-" * 30)
    new_year_context = PricingContext(
        customer_type="business",
        city="Oak City",
        visitor_id=visitor_id,
        visit_date=datetime(2026, 1, 15),
    )

    new_year_fraction = DroppedFraction(FractionType.CONSTRUCTION_WASTE, Weight(800))
    new_year_price = rule.calculate_price(new_year_fraction, new_year_context)
    print(f"   800kg construction waste × €0.21/kg = €{new_year_price.amount:.2f}")
    print(f"   Full exemption available again in new calendar year")
    print()

    # Summary
    total_2025 = price1.amount + price2.amount + price3.amount + green_price.amount
    print("💰 PRICING SUMMARY")
    print("-" * 20)
    print(f"Visit 1 (600kg construction): €{price1.amount:.2f}")
    print(f"Visit 2 (900kg construction): €{price2.amount:.2f}")
    print(f"Visit 3 (300kg construction): €{price3.amount:.2f}")
    print(f"Green waste (200kg): €{green_price.amount:.2f}")
    print(f"Total 2025: €{total_2025:.2f}")
    print(f"2026 Visit (800kg construction): €{new_year_price.amount:.2f}")
    print()

    print("✅ Rule features demonstrated:")
    print("- Tiered pricing (€0.21/kg first 1000kg, €0.29/kg over)")
    print("- Cross-visit exemption tracking within calendar year")
    print("- Annual exemption reset")
    print("- Standard rates for non-construction waste")
    print("- Separate tracking per visitor")


if __name__ == "__main__":
    demonstrate_exemption_rule()
