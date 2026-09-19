import asyncio
import inspect
from typing import Callable, Dict, List, Any


class EventBus:
    """
    Decoupled publish-subscribe event bus.
    
    Enables multi-consumer architecture:
    Perception / Behavior Engine -> Event Bus -> [Database, AlertManager, WebSocket]
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Register a callback handler for a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove a previously registered handler."""
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Publish an event to all registered subscribers.
        Executes sync handlers immediately and schedules async handlers on the active event loop if present.
        """
        handlers = self._subscribers.get(event_type, [])
        # Also notify wildcard subscribers if any
        wildcard_handlers = self._subscribers.get("*", [])
        all_handlers = list(handlers) + list(wildcard_handlers)

        for handler in all_handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(handler(data))
                    except RuntimeError:
                        # No running event loop in this thread; execute synchronously
                        asyncio.run(handler(data))
                else:
                    handler(data)
            except Exception as e:
                # Keep bus resilient; individual subscriber failures don't break publisher
                print(f"[EventBus] Error in subscriber for '{event_type}': {e}")

    def clear(self) -> None:
        """Clear all registered event subscribers."""
        self._subscribers.clear()


# Global event bus singleton
event_bus = EventBus()
