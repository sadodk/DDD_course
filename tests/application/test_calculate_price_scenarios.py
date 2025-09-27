"""Integration tests for calculate price scenarios."""

import json
from application.main import app

app.testing = True
client = app.test_client()


class TestCalculatePriceScenarios:
    """Test specific price calculation scenarios."""

    def test_beaver_bertha_scenario(self):
        """Test price calculation for Beaver Bertha scenario."""
        # Reset scenario to ensure clean state
        client.post("/startScenario")

        response = client.post(
            "/calculatePrice",
            json={
                "date": "2023-07-23",
                "dropped_fractions": [
                    {"amount_dropped": 83, "fraction_type": "Green waste"},
                    {"amount_dropped": 18, "fraction_type": "Construction waste"},
                ],
                "person_id": "Beaver Bertha",
                "visit_id": "1",
            },
        )

        assert response.status_code == 200
        actual = json.loads(response.data)

        expected = {
            "price_amount": 10.42,
            "person_id": "Beaver Bertha",
            "visit_id": "1",
            "price_currency": "EUR",
        }

        assert actual == expected

    def test_bear_billy_scenario(self):
        """Test price calculation for Bear Billy scenario."""
        # Reset scenario to ensure clean state
        client.post("/startScenario")

        response = client.post(
            "/calculatePrice",
            json={
                "date": "2023-09-30",
                "dropped_fractions": [
                    {"amount_dropped": 134, "fraction_type": "Green waste"},
                    {"amount_dropped": 201, "fraction_type": "Construction waste"},
                ],
                "person_id": "Bear Billy",
                "visit_id": "2",
            },
        )

        assert response.status_code == 200
        actual = json.loads(response.data)

        expected = {
            "price_amount": 42.21,
            "person_id": "Bear Billy",
            "visit_id": "2",
            "price_currency": "EUR",
        }

        assert actual == expected

    def test_both_scenarios_in_sequence(self):
        """Test both scenarios in sequence to verify they work independently."""
        # Reset scenario to ensure clean state
        client.post("/startScenario")

        # First scenario - Beaver Bertha
        response1 = client.post(
            "/calculatePrice",
            json={
                "date": "2023-07-23",
                "dropped_fractions": [
                    {"amount_dropped": 83, "fraction_type": "Green waste"},
                    {"amount_dropped": 18, "fraction_type": "Construction waste"},
                ],
                "person_id": "Beaver Bertha",
                "visit_id": "1",
            },
        )

        assert response1.status_code == 200
        result1 = json.loads(response1.data)
        assert result1["price_amount"] == 10.42
        assert result1["person_id"] == "Beaver Bertha"

        # Second scenario - Bear Billy
        response2 = client.post(
            "/calculatePrice",
            json={
                "date": "2023-09-30",
                "dropped_fractions": [
                    {"amount_dropped": 134, "fraction_type": "Green waste"},
                    {"amount_dropped": 201, "fraction_type": "Construction waste"},
                ],
                "person_id": "Bear Billy",
                "visit_id": "2",
            },
        )

        assert response2.status_code == 200
        result2 = json.loads(response2.data)
        assert result2["price_amount"] == 42.21
        assert result2["person_id"] == "Bear Billy"
