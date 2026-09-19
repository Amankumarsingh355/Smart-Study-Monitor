from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class BehaviorSample:
    """
    Represents a timestamped observation of student behavior.
    """
    timestamp: datetime
    state: str
    confidence: float = 1.0
    duration: float = 0.0


class BehaviorHistory:
    """
    Maintains a bounded historical record of behavioral states over time.
    Uses collections.deque to maintain fixed memory and predictable performance.
    """

    def __init__(self, max_samples: int = 600):
        self.max_samples = max_samples
        self.samples: deque[BehaviorSample] = deque(maxlen=max_samples)

    def add(
        self,
        state: str,
        confidence: float = 1.0,
        duration: float = 0.0,
        timestamp: Optional[datetime] = None
    ) -> BehaviorSample:
        """
        Record a new behavior observation.
        """
        ts = timestamp if timestamp is not None else datetime.now()
        sample = BehaviorSample(
            timestamp=ts,
            state=str(state),
            confidence=float(confidence),
            duration=float(duration)
        )
        self.samples.append(sample)
        return sample

    def get_recent(self) -> List[BehaviorSample]:
        """Return all samples currently in the deque as a list."""
        return list(self.samples)

    def get_last_sample(self) -> Optional[BehaviorSample]:
        """Return the most recent sample recorded, or None if empty."""
        return self.samples[-1] if self.samples else None

    def get_window(
        self,
        seconds: float,
        reference_time: Optional[datetime] = None
    ) -> List[BehaviorSample]:
        """
        Return samples that fall within `seconds` before `reference_time`.
        If reference_time is omitted, the latest sample's timestamp is used.
        """
        if not self.samples:
            return []

        ref = reference_time if reference_time is not None else self.samples[-1].timestamp
        cutoff = ref - timedelta(seconds=seconds)
        return [s for s in self.samples if s.timestamp >= cutoff]

    def get_dominant_state(
        self,
        seconds: float,
        reference_time: Optional[datetime] = None
    ) -> Optional[str]:
        """
        Determine the state that appears most frequently within the time window.
        """
        window = self.get_window(seconds, reference_time)
        if not window:
            return None

        counts: Dict[str, int] = {}
        for s in window:
            counts[s.state] = counts.get(s.state, 0) + 1

        return max(counts, key=counts.get)

    def get_state_distribution(
        self,
        seconds: float,
        reference_time: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Calculate relative proportion (0.0 to 1.0) of each state in the window.
        """
        window = self.get_window(seconds, reference_time)
        if not window:
            return {}

        total = len(window)
        counts: Dict[str, int] = {}
        for s in window:
            counts[s.state] = counts.get(s.state, 0) + 1

        return {state: count / total for state, count in counts.items()}

    def clear(self):
        """Clear the sample history."""
        self.samples.clear()

    def __len__(self) -> int:
        return len(self.samples)
