from application.main import app
import json

app.testing = True
client = app.test_client()


def test_index():
    response = client.get("/")
    assert b'{"status":"OK"}' in response.data


def test_start_scenario():
    response = client.post("/startScenario")
    assert response.data == b"{}\n"


def test_calculate_price_with_empty_dropped_fractions():
    response = client.post(
        "/calculatePrice",
        json={
            "date": "2023-07-23",
            "dropped_fractions": [],
            "person_id": "Bald Eagle",
            "visit_id": "1",
        },
    )

    actual = json.loads(response.data)
    # Empty dropped fractions should return an error in the new business logic
    assert "error" in actual
    assert "at least one dropped fraction" in actual["error"]


def test_calculate_price():
    # First reset the scenario to clear any existing data
    client.post("/startScenario")

    response = client.post(
        "/calculatePrice",
        json={
            "date": "2023-07-23",
            "dropped_fractions": [
                {"amount_dropped": 83, "fraction_type": "Green waste"},
                {"amount_dropped": 18, "fraction_type": "Construction waste"},
            ],
            "person_id": "Squirrel Gus",
            "visit_id": "1",
        },
    )

    actual = json.loads(response.data)
    # For the first visit, there should be no surcharge
    # Green waste: 83 * 0.10 = 8.30
    # Construction waste: 18 * 0.19 = 3.42
    # Total: 11.72 (no surcharge on first visit)
    expected = {
        "price_amount": 11.72,
        "person_id": "Squirrel Gus",
        "visit_id": "1",
        "price_currency": "EUR",
    }

    assert actual == expected
