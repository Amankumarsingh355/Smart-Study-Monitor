import time
from typing import Optional


class EventManager:
    """
    Manages temporal persistence and event generation.

    Decouples raw sensor detections from business logic:
    Raw detection -> Persistence Filter -> Structured Event.
    """

    def __init__(self, phone_persistence_seconds: float = 1.0):
        self.phone_persistence_seconds = phone_persistence_seconds

        # Internal state tracking
        self._phone_first_seen_time: Optional[float] = None
        self._phone_event_active: bool = False
        self._last_update_time: float = time.time()

    def update_phone_detection(
        self,
        is_visible: bool,
        current_time: Optional[float] = None
    ) -> Optional[str]:
        """
        Update the phone detection state and evaluate persistence.

        Args:
            is_visible: True if phone was detected in current frame.
            current_time: Timestamp in seconds (defaults to time.time()).

        Returns:
            "PHONE_DETECTED" if phone has been stably visible >= persistence threshold.
            None otherwise.
        """
        now = current_time if current_time is not None else time.time()
        self._last_update_time = now

        if is_visible:
            # First time seeing phone in this sequence
            if self._phone_first_seen_time is None:
                self._phone_first_seen_time = now

            duration = now - self._phone_first_seen_time

            # Has it been visible long enough to cross threshold?
            if duration >= self.phone_persistence_seconds:
                self._phone_event_active = True
                return "PHONE_DETECTED"
            else:
                return None
        else:
            # Phone is no longer visible -> reset persistence tracking
            self._phone_first_seen_time = None
            self._phone_event_active = False
            return None

    @property
    def is_phone_event_active(self) -> bool:
        """Returns True if phone is currently confirmed active and persistent."""
        return self._phone_event_active

    def get_phone_persistence_duration(self, current_time: Optional[float] = None) -> float:
        """Return how long the phone has been continuously visible in seconds."""
        if self._phone_first_seen_time is None:
            return 0.0
        now = current_time if current_time is not None else time.time()
        return max(0.0, now - self._phone_first_seen_time)

    def reset(self):
        """Reset all event tracking states."""
        self._phone_first_seen_time = None
        self._phone_event_active = False
