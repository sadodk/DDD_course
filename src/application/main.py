from dataclasses import asdict
from flask import Flask, request
from .price_calculator import PriceCalculator

app = Flask(__name__)


@app.route("/")
def hello_world():
    return {"status": "OK"}


# This is run every time a scenario starts, in case you need to reset certain
# things at the beginning of a scenario
@app.post("/startScenario")
def start_scenario():
    app.logger.info("starting scenario")
    return {}


@app.post("/calculatePrice")
def calculate_price():
    visit_data = request.get_json()
    app.logger.info(f"calculate price request: {visit_data}")

    response = PriceCalculator().calculate(visit_data)

    app.logger.info(f"calculate price response: {response}")
    return asdict(response)
