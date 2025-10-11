"""Base domain event class."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent:
    """
    Base class for all domain events.

    Domain events represent something significant that happened in the domain.
    They are immutable (frozen=True) and capture the state at the time of the event.
    """

    occurred_at: datetime

    def __post_init__(self):
        """Ensure occurred_at is set if not provided."""
        if not self.occurred_at:
            object.__setattr__(self, "occurred_at", datetime.now())
