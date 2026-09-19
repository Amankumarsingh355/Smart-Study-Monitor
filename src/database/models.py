import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class SessionRecord:
    """
    Persistent record representing a study session.
    """
    id: str
    start_time: str
    end_time: Optional[str] = None
    duration: float = 0.0
    focus_score: float = 100.0
    focused_time: float = 0.0
    distracted_time: float = 0.0
    phone_time: float = 0.0
    drowsy_time: float = 0.0
    reading_time: float = 0.0
    no_face_time: float = 0.0
    posture_issue_time: float = 0.0
    longest_streak: float = 0.0
    distraction_count: int = 0
    status: str = "ACTIVE"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": round(self.duration, 1),
            "focus_score": round(self.focus_score, 1),
            "focused_time": round(self.focused_time, 1),
            "distracted_time": round(self.distracted_time, 1),
            "phone_time": round(self.phone_time, 1),
            "drowsy_time": round(self.drowsy_time, 1),
            "reading_time": round(self.reading_time, 1),
            "no_face_time": round(self.no_face_time, 1),
            "posture_issue_time": round(self.posture_issue_time, 1),
            "longest_streak": round(self.longest_streak, 1),
            "distraction_count": self.distraction_count,
            "status": self.status,
            "created_at": self.created_at
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'SessionRecord':
        return cls(
            id=row["id"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            duration=float(row["duration"] or 0.0),
            focus_score=float(row["focus_score"] or 100.0),
            focused_time=float(row["focused_time"] or 0.0),
            distracted_time=float(row["distracted_time"] or 0.0),
            phone_time=float(row["phone_time"] or 0.0),
            drowsy_time=float(row["drowsy_time"] or 0.0),
            reading_time=float(row["reading_time"] or 0.0),
            no_face_time=float(row["no_face_time"] or 0.0),
            posture_issue_time=float(row["posture_issue_time"] or 0.0),
            longest_streak=float(row["longest_streak"] or 0.0),
            distraction_count=int(row["distraction_count"] or 0),
            status=row["status"],
            created_at=row["created_at"]
        )


@dataclass
class EventRecord:
    """
    Persistent record representing a discrete behavioral episode.
    """
    session_id: str
    event_type: str
    start_time: str
    id: Optional[int] = None
    end_time: Optional[str] = None
    duration: float = 0.0
    confidence: float = 1.0
    metadata: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "event_type": self.event_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": round(self.duration, 1),
            "confidence": round(self.confidence, 2),
            "metadata": self.metadata
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'EventRecord':
        return cls(
            id=row["id"],
            session_id=row["session_id"],
            event_type=row["event_type"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            duration=float(row["duration"] or 0.0),
            confidence=float(row["confidence"] or 1.0),
            metadata=row["metadata"]
        )


@dataclass
class BehaviorSampleRecord:
    """
    Periodic sample representing state at a specific point in time.
    """
    session_id: str
    timestamp: str
    state: str
    id: Optional[int] = None
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "state": self.state,
            "confidence": round(self.confidence, 2)
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'BehaviorSampleRecord':
        return cls(
            id=row["id"],
            session_id=row["session_id"],
            timestamp=row["timestamp"],
            state=row["state"],
            confidence=float(row["confidence"] or 1.0)
        )
