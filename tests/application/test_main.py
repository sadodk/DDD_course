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


def test_calculate_price():
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
