from .price_calculator import PriceCalculator
from dataclasses import asdict
from flask import request, Blueprint
from pydantic import BaseModel
from typing import List, Any
from .price_calculator import Visit
from logging import Logger

logger = Logger("routes")

bp = Blueprint("routes", __name__)


class PriceRequest(BaseModel):
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
    price_request = PriceRequest(**request.get_json())

    visit = Visit(
        date=price_request.date,
        dropped_fractions=price_request.dropped_fractions,
        person_id=price_request.person_id,
        visit_id=price_request.visit_id,
    )

    invoice = PriceCalculator().calculate(visit)

    return asdict(invoice)
