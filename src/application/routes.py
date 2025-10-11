"""Flask routes using DDD entities.

- Entry point for HTTP requests
- No direct domain imports - maintains separation of concerns
- Uses application services (price_calculator) which then use domain
- Framework-specific (Flask) - domain is protected from web framework
"""

from dataclasses import asdict
from flask import request, Blueprint
from pydantic import BaseModel
from typing import List, Dict, Any
from logging import Logger

from application.dependency_injection import ApplicationContext

logger = Logger("routes")
bp = Blueprint("routes", __name__)

# Application setup
app = ApplicationContext()


class VisitRequest(BaseModel):
    """Visit request model."""

    date: str
    dropped_fractions: List[Dict[str, Any]]
    person_id: str
    visit_id: str


@bp.route("/")
def health_check():
    """Health check."""
    return {"status": "OK"}


@bp.post("/startScenario")
def start_scenario():
    """Reset for new test scenario."""
    app.reset_for_new_scenario()
    logger.info("New scenario started")
    return {}


@bp.post("/calculatePrice")
def calculate_price():
    """Calculate price using clean DDD approach."""
    try:
        # Parse request
        visit_request = VisitRequest(**request.get_json())
        logger.info(f"Processing visit: {visit_request.visit_id}")

        # Calculate price using domain entities and services
        response = app.price_calculator.calculate_price(visit_request.model_dump())

        return asdict(response)

    except Exception as e:
        logger.error(f"Price calculation error: {e}")
        return {"error": str(e)}, 400
