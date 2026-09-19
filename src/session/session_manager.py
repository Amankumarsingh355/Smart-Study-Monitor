import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from src.behavior.study_state import StudyState
from src.behavior.session_metrics import SessionMetrics
from src.database.models import SessionRecord, EventRecord, BehaviorSampleRecord
from src.database.repository import SessionRepository


class SessionManager:
    """
    Orchestrates the lifecycle of a study session.
    
    Coordinates live perception signals with persistent storage:
    - Generates unique session IDs
    - Manages session lifecycle (START -> MONITORING -> END)
    - Aggregates behavioral events over time (prevents per-frame duplicate database insertions)
    - Records periodic behavior timeline samples
    - Computes and persists final session analytics upon exit
    """

    DISTRACTION_EVENT_MAP = {
        StudyState.PHONE_USAGE: "PHONE_DETECTED",
        StudyState.DROWSY: "DROWSINESS",
        StudyState.LOOKING_AWAY: "LOOKING_AWAY",
        StudyState.POOR_POSTURE: "POOR_POSTURE",
        StudyState.AWAY_FROM_DESK: "AWAY_FROM_DESK",
        StudyState.DISTRACTED: "DISTRACTED"
    }

    def __init__(
        self,
        repository: SessionRepository,
        sample_interval_seconds: float = 2.0
    ):
        self.repository = repository
        self.sample_interval_seconds = sample_interval_seconds

        self.session_metrics = SessionMetrics()
        self._current_session: Optional[SessionRecord] = None

        # Event aggregation state: event_type -> dict(start_time, start_ts, confidences, metadata)
        self._active_events: Dict[str, Dict[str, Any]] = {}
        self._last_state: Optional[StudyState] = None

        # Sample rate limiting
        self._last_sample_time: float = 0.0

    @property
    def is_active(self) -> bool:
        return self._current_session is not None and self._current_session.status == "ACTIVE"

    @property
    def session_id(self) -> Optional[str]:
        return self._current_session.id if self._current_session else None

    @property
    def current_session(self) -> Optional[SessionRecord]:
        return self._current_session

    def start_session(self, session_id: Optional[str] = None) -> SessionRecord:
        """
        Begin a new study session.
        Generates a unique session ID and writes the initial record to the database.
        """
        if self.is_active:
            self.end_session()

        now = datetime.now()
        if session_id is None:
            date_str = now.strftime("%Y%m%d")
            short_id = uuid.uuid4().hex[:8]
            sid = f"SSM-{date_str}-{short_id}"
        else:
            sid = session_id

        self.session_metrics.reset()
        self._active_events.clear()
        self._last_state = None
        self._last_sample_time = 0.0

        session = SessionRecord(
            id=sid,
            start_time=now.isoformat(),
            created_at=now.isoformat(),
            status="ACTIVE"
        )
        self._current_session = self.repository.create_session(session)

        # Publish to EventBus
        from src.events.event_bus import event_bus
        event_bus.publish("SESSION_STARTED", {
            "type": "SESSION_STARTED",
            "session_id": sid,
            "start_time": now.isoformat()
        })

        return self._current_session

    def update(
        self,
        current_state: Union[StudyState, str],
        confidence: float = 1.0,
        dt: float = 0.0,
        current_time: Optional[float] = None
    ) -> None:
        """
        Feed live state into the session engine per frame.
        Handles time accumulation, event lifecycle, and periodic behavior sampling.
        """
        if not self.is_active:
            return

        # Normalize state
        state = current_state
        if isinstance(state, str):
            try:
                state = StudyState(state)
            except ValueError:
                for s in StudyState:
                    if s.name.lower() == state.lower() or s.value.lower() == state.lower():
                        state = s
                        break

        # 1. Accumulate session time and streaks
        self.session_metrics.update(state, dt)

        now_dt = datetime.now()
        now_ts = current_time if current_time is not None else now_dt.timestamp()

        # 2. Event lifecycle aggregation (Deduplication!)
        current_event_type = self.DISTRACTION_EVENT_MAP.get(state)

        # Check for events that have ended
        ended_types = [
            etype for etype in list(self._active_events.keys())
            if etype != current_event_type
        ]
        for etype in ended_types:
            self._finalize_active_event(etype, end_time_dt=now_dt, end_ts=now_ts)

        # Check for new event that has started
        if current_event_type and current_event_type not in self._active_events:
            self._active_events[current_event_type] = {
                "start_time_iso": now_dt.isoformat(),
                "start_ts": now_ts,
                "confidences": [confidence],
                "metadata": {"state": state.value}
            }
        elif current_event_type and current_event_type in self._active_events:
            self._active_events[current_event_type]["confidences"].append(confidence)

        # 3. Periodic Behavior Sampling
        # Sample if state changed OR if sample_interval_seconds elapsed
        time_since_sample = now_ts - self._last_sample_time
        state_changed = (self._last_state != state)

        if state_changed or time_since_sample >= self.sample_interval_seconds:
            sample = BehaviorSampleRecord(
                session_id=self._current_session.id,
                timestamp=now_dt.isoformat(),
                state=state.value if isinstance(state, StudyState) else str(state),
                confidence=confidence
            )
            self.repository.save_behavior_sample(sample)

            from src.events.event_bus import event_bus
            if state_changed and self._last_state is not None:
                event_bus.publish("BEHAVIOR_CHANGE", {
                    "type": "BEHAVIOR_CHANGE",
                    "session_id": self._current_session.id,
                    "previous": self._last_state.value if isinstance(self._last_state, StudyState) else str(self._last_state),
                    "current": state.value if isinstance(state, StudyState) else str(state),
                    "confidence": round(confidence, 2),
                    "focus_score": self.session_metrics.focus_percentage
                })

            if time_since_sample >= self.sample_interval_seconds:
                event_bus.publish("MONITOR_UPDATE", {
                    "type": "MONITOR_UPDATE",
                    "timestamp": now_dt.isoformat(),
                    "session_id": self._current_session.id,
                    "state": state.value if isinstance(state, StudyState) else str(state),
                    "confidence": round(confidence, 2),
                    "focus_score": self.session_metrics.focus_percentage,
                    "focused_time": round(self.session_metrics.focused_time, 1),
                    "distracted_time": round(self.session_metrics.distracted_time, 1),
                    "phone_time": round(self.session_metrics.phone_time, 1),
                    "reading_time": round(self.session_metrics.reading_time, 1),
                    "current_streak": round(self.session_metrics.current_focus_streak, 1),
                    "longest_streak": round(self.session_metrics.longest_focus_streak, 1),
                    "distraction_count": self.session_metrics.distraction_count
                })

            self._last_sample_time = now_ts
            self._last_state = state

    def _finalize_active_event(
        self,
        event_type: str,
        end_time_dt: datetime,
        end_ts: float
    ) -> Optional[EventRecord]:
        """Complete an ongoing event episode and commit to database."""
        event_info = self._active_events.pop(event_type, None)
        if not event_info or not self._current_session:
            return None

        duration = max(0.1, end_ts - event_info["start_ts"])
        confs = event_info["confidences"]
        avg_conf = sum(confs) / len(confs) if confs else 1.0
        meta_str = json.dumps(event_info.get("metadata", {}))

        record = EventRecord(
            session_id=self._current_session.id,
            event_type=event_type,
            start_time=event_info["start_time_iso"],
            end_time=end_time_dt.isoformat(),
            duration=round(duration, 2),
            confidence=round(avg_conf, 2),
            metadata=meta_str
        )
        self.repository.save_event(record)
        return record

    def record_event(
        self,
        event_type: str,
        start_time: str,
        end_time: Optional[str] = None,
        duration: float = 0.0,
        confidence: float = 1.0,
        metadata: Optional[Union[Dict[str, Any], str]] = None
    ) -> Optional[EventRecord]:
        """Directly insert an externally produced event into the database."""
        if not self._current_session:
            return None

        meta_str = json.dumps(metadata) if isinstance(metadata, dict) else metadata
        record = EventRecord(
            session_id=self._current_session.id,
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            duration=round(duration, 2),
            confidence=round(confidence, 2),
            metadata=meta_str
        )
        self.repository.save_event(record)
        return record

    def end_session(self, end_time: Optional[datetime] = None) -> Optional[SessionRecord]:
        """
        Finalize the current study session.
        Closes active events, calculates final scores, and persists to the database.
        """
        if not self._current_session:
            return None

        now_dt = end_time if end_time is not None else datetime.now()
        now_ts = now_dt.timestamp()

        # Finalize all remaining active events
        for etype in list(self._active_events.keys()):
            self._finalize_active_event(etype, end_time_dt=now_dt, end_ts=now_ts)

        # Calculate final analytics
        summary = self.session_metrics.summary()
        duration = summary["total_time"]
        focus_score = summary["focus_percentage"]

        self.repository.end_session(
            session_id=self._current_session.id,
            end_time=now_dt.isoformat(),
            duration=duration,
            focus_score=focus_score,
            metrics=summary
        )

        # Refresh local record
        self._current_session = self.repository.get_session(self._current_session.id)

        from src.events.event_bus import event_bus
        event_bus.publish("SESSION_ENDED", {
            "type": "SESSION_ENDED",
            "session_id": self._current_session.id,
            "duration": round(duration, 1),
            "focus_score": round(focus_score, 1),
            "end_time": now_dt.isoformat()
        })

        return self._current_session

    def summary(self) -> Dict[str, Any]:
        """Return analytics summary for current active session."""
        base = self.session_metrics.summary()
        base["session_id"] = self.session_id
        base["is_active"] = self.is_active
        return base
