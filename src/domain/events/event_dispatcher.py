"""Event dispatcher for domain events."""

from abc import ABC, abstractmethod
from typing import Callable, List
from domain.events.domain_event import DomainEvent

# Type alias for event subscribers
EventSubscriber = Callable[[DomainEvent], None]


class EventDispatcher(ABC):
    """
    Interface for dispatching domain events to subscribers.

    The event dispatcher implements the Observer pattern, allowing
    decoupled communication between different parts of the system.
    """

    @abstractmethod
    def subscribe(self, subscriber: EventSubscriber) -> None:
        """
        Subscribe to all dispatched events.

        Args:
            subscriber: Callable that will be invoked when events are dispatched
        """
        pass

    @abstractmethod
    def dispatch(self, event: DomainEvent) -> None:
        """
        Dispatch an event to all subscribers.

        Args:
            event: The domain event to dispatch
        """
        pass


class InMemoryEventDispatcher(EventDispatcher):
    """
    In-memory implementation of EventDispatcher.

    Synchronously notifies all subscribers when an event is dispatched.
    Useful for simple applications and testing.
    """

    def __init__(self):
        """Initialize with empty subscriber list."""
        self._subscribers: List[EventSubscriber] = []

    def subscribe(self, subscriber: EventSubscriber) -> None:
        """Subscribe to all dispatched events."""
        self._subscribers.append(subscriber)

    def dispatch(self, event: DomainEvent) -> None:
        """Dispatch event to all subscribers synchronously."""
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception as e:
                # Log error but continue notifying other subscribers
                print(f"Error in event subscriber: {e}")
                # In production, use proper logging
