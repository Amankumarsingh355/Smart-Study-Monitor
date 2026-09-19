from typing import Dict
from pydantic import BaseModel


class SessionAnalyticsResponse(BaseModel):
    session_id: str
    duration: float
    focus_score: float
    focused_time: float
    reading_time: float
    distracted_time: float
    phone_time: float
    drowsy_time: float
    no_face_time: float
    posture_issue_time: float
    distraction_count: int
    longest_streak: float
    events_count: int
    events_breakdown: Dict[str, int]


class AggregatedAnalyticsResponse(BaseModel):
    total_sessions: int
    total_study_time: float
    average_focus_score: float
    total_distractions: int
    total_phone_time: float
    total_reading_time: float
    longest_focus_streak: float
