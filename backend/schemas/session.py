from typing import Optional
from pydantic import BaseModel, ConfigDict


class StartSessionRequest(BaseModel):
    session_id: Optional[str] = None


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    created_at: str


class CurrentSessionResponse(BaseModel):
    session_id: str
    status: str
    state: str
    focus_score: float = 100.0
    duration: float = 0.0
    focused_time: float = 0.0
    distracted_time: float = 0.0
    phone_time: float = 0.0
    drowsy_time: float = 0.0
    reading_time: float = 0.0
    current_streak: float = 0.0
    longest_streak: float = 0.0
    distraction_count: int = 0
    average_recovery_time: float = 0.0
