from typing import Optional
from pydantic import BaseModel, ConfigDict


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    session_id: str
    event_type: str
    start_time: str
    end_time: Optional[str] = None
    duration: float = 0.0
    confidence: float = 1.0
    metadata: Optional[str] = None
