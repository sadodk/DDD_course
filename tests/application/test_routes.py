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


def test_calculate_price_with_dropped_fractions():
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
    expected = {
        "price_amount": 0,
        "person_id": "Bald Eagle",
        "visit_id": "1",
        "price_currency": "EUR",
    }

    assert actual == expected


def test_calculate_price():
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
    expected = {
        "price_amount": 10.06,
        "person_id": "Squirrel Gus",
        "visit_id": "1",
        "price_currency": "EUR",
    }

    assert actual == expected
