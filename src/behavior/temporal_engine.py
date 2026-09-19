import time
from typing import Dict, Optional


class TemporalEngine:
    """
    Tracks signal durations over time to prevent noisy, instantaneous decisions.
    
    FRAME -> SIGNAL -> TIME -> BEHAVIOR
    """

    def __init__(self):
        self.active_since: Dict[str, float] = {}

    def update(
        self,
        signal_name: str,
        active: bool,
        current_time: Optional[float] = None
    ):
        """
        Track when a signal becomes active or inactive.
        """
        now = current_time if current_time is not None else time.time()

        if active:
            if signal_name not in self.active_since:
                self.active_since[signal_name] = now
        else:
            self.active_since.pop(signal_name, None)

    def duration(
        self,
        signal_name: str,
        current_time: Optional[float] = None
    ) -> float:
        """
        Return how long a signal has been continuously active in seconds.
        """
        if signal_name not in self.active_since:
            return 0.0

        now = current_time if current_time is not None else time.time()
        return max(0.0, now - self.active_since[signal_name])

    def get_duration(
        self,
        signal_name: str,
        current_time: Optional[float] = None
    ) -> float:
        """Alias for duration() for cross-subsystem consistency."""
        return self.duration(signal_name, current_time)

    def active_for(
        self,
        signal_name: str,
        seconds: float,
        current_time: Optional[float] = None
    ) -> bool:
        """
        Check if a signal has been continuously active for at least `seconds`.
        """
        return self.duration(signal_name, current_time) >= seconds

    @property
    def phone_duration(self) -> float:
        return self.duration("phone")

    @property
    def eyes_closed_duration(self) -> float:
        return self.duration("eyes_closed")

    @property
    def no_face_duration(self) -> float:
        return self.duration("no_face")

    def reset(self):
        """Clear all active signal timers."""
        self.active_since.clear()
