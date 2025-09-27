"""Domain repository interfaces - Abstract contracts for data persistence."""

from .visitor_repository import VisitorRepository
from .visit_repository import VisitRepository

__all__ = ["VisitorRepository", "VisitRepository"]
