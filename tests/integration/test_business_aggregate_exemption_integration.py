"""Integration test for business aggregates with exemptions."""

import pytest
import json
from application.main import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client


def test_business_aggregate_shared_exemptions(client):
    """Test that multiple employees from same business share exemption limits."""
    # Start with a fresh scenario
    response = client.post(
        "/startScenario",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json() == {}

    # First employee (Beaver Bertha) drops construction waste (597kg)
    # Since this is within the exemption limit (1000kg), it should be charged at the lower rate
    response = client.post(
        "/calculatePrice",
        data=json.dumps(
            {
                "date": "2023-07-23",
                "dropped_fractions": [
                    {"amount_dropped": 597, "fraction_type": "Construction waste"}
                ],
                "person_id": "Beaver Bertha",
                "visit_id": "1",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    result = response.get_json()
    assert round(result["price_amount"], 2) == 125.37  # 597kg * 0.21 EUR/kg = 125.37
    assert result["person_id"] == "Beaver Bertha"
    assert result["price_currency"] == "EUR"

    # Second employee (Beaver Bruce) from the same business drops more construction waste (1803kg)
    # Since the business already used 597kg of its exemption, it has 403kg left at the lower rate
    # The remaining 1400kg should be charged at the higher rate
    # Expected calculation:
    # 403kg * 0.21 EUR/kg (lower rate) + 1400kg * 0.29 EUR/kg (higher rate) = 490.63 EUR
    response = client.post(
        "/calculatePrice",
        data=json.dumps(
            {
                "date": "2023-07-23",
                "dropped_fractions": [
                    {"amount_dropped": 1803, "fraction_type": "Construction waste"}
                ],
                "person_id": "Beaver Bruce",
                "visit_id": "2",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 200
    result = response.get_json()
    assert round(result["price_amount"], 2) == 490.63
    assert result["person_id"] == "Beaver Bruce"
    assert result["price_currency"] == "EUR"

    # Verify calculation:
    # Bertha used 597kg of the exemption, leaving 403kg for Bruce
    # Bruce's waste is 1803kg:
    #  - First 403kg at 0.21 EUR/kg = 84.63 EUR
    #  - Remaining 1400kg at 0.29 EUR/kg = 406.00 EUR
    #  - Total: 84.63 + 406.00 = 490.63 EUR
