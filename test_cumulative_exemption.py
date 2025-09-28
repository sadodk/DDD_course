#!/usr/bin/env python3
"""Test cumulative exemption tracking across multiple visits."""

from datetime import datetime
from unittest.mock import patch

# Import our application components
from application.application_context import ApplicationContext
from application.external_visitor_service import VisitorInfo


def test_cumulative_exemption():
    """Test that exemption tracking works across multiple visits."""
    print("🧪 CUMULATIVE EXEMPTION TRACKING TEST")
    print("=" * 50)
    
    # Create Beaver Bertha as Oak City business customer
    beaver_bertha = VisitorInfo(
        id="Beaver Bertha", 
        type="business", 
        address="123 Street", 
        city="Oak City", 
        card_id="CARD1", 
        email="test@example.com"
    )
    
    app = ApplicationContext()
    
    with patch.object(app.visitor_service, 'get_visitor_by_id', return_value=beaver_bertha):
        # Reset for clean state
        app.reset_for_new_scenario()
        
        # Visit 1: 597kg construction waste
        print("🚛 VISIT 1: 597kg construction waste")
        visit1_data = {
            "date": "2023-07-23",
            "dropped_fractions": [
                {
                    "amount_dropped": 597,
                    "fraction_type": "Construction waste"
                }
            ],
            "person_id": "Beaver Bertha",
            "visit_id": "1"
        }
        
        result1 = app.price_calculator.calculate_price(visit1_data)
        print(f"   💰 Price: {result1.price_amount} EUR")
        print(f"   📊 Expected: 125.37 EUR")
        print(f"   ✅ Match: {result1.price_amount == 125.37}")
        print(f"   📈 Calculation: 597 * 0.21 = {597 * 0.21}")
        print(f"   🏷️  Exemption used: 597kg, remaining: {1000 - 597}kg")
        print()
        
        # Visit 2: 1803kg construction waste
        print("🚛 VISIT 2: 1803kg construction waste (same customer)")
        visit2_data = {
            "date": "2023-07-23",
            "dropped_fractions": [
                {
                    "amount_dropped": 1803,
                    "fraction_type": "Construction waste"
                }
            ],
            "person_id": "Beaver Bertha",
            "visit_id": "2"
        }
        
        result2 = app.price_calculator.calculate_price(visit2_data)
        print(f"   💰 Price: {result2.price_amount} EUR")
        print(f"   📊 Expected: 490.63 EUR")
        print(f"   ✅ Match: {result2.price_amount == 490.63}")
        print(f"   📈 Expected calculation:")
        print(f"      - First 403kg (remaining exemption): 403 * 0.21 = {403 * 0.21}")
        print(f"      - Remaining 1400kg: 1400 * 0.29 = {1400 * 0.29}")
        print(f"      - Total: {403 * 0.21} + {1400 * 0.29} = {(403 * 0.21) + (1400 * 0.29)}")
        print()
        
        # Check what actually happened
        if result2.price_amount != 490.63:
            print("❌ ISSUE DETECTED:")
            if result2.price_amount == 442.87:
                print("   The system calculated as if this was the first visit (full exemption)")
                print("   This suggests exemption state is not being maintained between visits")
            else:
                print(f"   Unexpected calculation result: {result2.price_amount}")
            
        # Test one more customer to ensure they get their own exemption
        print("👤 Testing different customer (Peppa Python)")
        peppa = VisitorInfo(
            id="Peppa Python", 
            type="business", 
            address="456 Street", 
            city="Oak City", 
            card_id="CARD2", 
            email="peppa@example.com"
        )
        
        with patch.object(app.visitor_service, 'get_visitor_by_id', return_value=peppa):
            visit3_data = {
                "date": "2023-07-23",
                "dropped_fractions": [
                    {
                        "amount_dropped": 1228,
                        "fraction_type": "Construction waste"
                    }
                ],
                "person_id": "Peppa Python",
                "visit_id": "3"
            }
            
            result3 = app.price_calculator.calculate_price(visit3_data)
            print(f"   💰 Price: {result3.price_amount} EUR")
            print(f"   📊 Expected: 276.12 EUR")  
            print(f"   ✅ Match: {result3.price_amount == 276.12}")
            print(f"   📈 Expected calculation:")
            print(f"      - First 1000kg: 1000 * 0.21 = {1000 * 0.21}")
            print(f"      - Remaining 228kg: 228 * 0.29 = {228 * 0.29}")
            print(f"      - Total: {1000 * 0.21} + {228 * 0.29} = {(1000 * 0.21) + (228 * 0.29)}")


if __name__ == "__main__":
    test_cumulative_exemption()