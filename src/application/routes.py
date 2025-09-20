from dataclasses import asdict
from flask import request, Blueprint
from pydantic import BaseModel
from typing import List, Any
from application.price_calculator import PriceCalculator
from logging import Logger

logger = Logger("routes")

bp = Blueprint("routes", __name__)


class Visit(BaseModel):
    date: str
    dropped_fractions: List[dict[str, Any]]
    person_id: str
    visit_id: str


@bp.route("/")
def hello_world():
    return {"status": "OK"}


# This is run every time a scenario starts, in case you need to reset certain
# things at the beginning of a scenario
@bp.post("/startScenario")
def start_scenario():
    logger.info("starting scenario")
    return {}


@bp.post("/calculatePrice")
def calculate_price():
    visit_data = Visit(**request.get_json())

    response = PriceCalculator().calculate(visit_data)

    return asdict(response)
