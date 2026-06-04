from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class CreateTestRequest(BaseModel):
    url: str

class TestResponse(BaseModel):
    id: int
    url: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    overall_score: Optional[float] = None
    issue_count: int = 0

    class Config:
        from_attributes = True

class IssueResponse(BaseModel):
    id: int
    persona_name: str
    type: str
    description: str
    severity: str
    element: Optional[str] = None
    url: Optional[str] = None
    suggestion: Optional[str] = None

    class Config:
        from_attributes = True

class PersonaResultResponse(BaseModel):
    id: int
    persona_name: str
    status: str
    screenshot_paths: list
    video_path: Optional[str] = None
    navigation_path: list
    issues_found: list
    load_times: dict
    persona_notes: Optional[str] = None

    class Config:
        from_attributes = True

class UXScoreResponse(BaseModel):
    overall_score: float
    navigation_score: float
    clarity_score: float
    speed_score: float
    mobile_score: float
    content_score: float
    summary: str
    breakdown: dict

    class Config:
        from_attributes = True

class TestDetailResponse(BaseModel):
    id: int
    url: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    persona_results: list[PersonaResultResponse] = []
    issues: list[IssueResponse] = []
    ux_score: Optional[UXScoreResponse] = None

    class Config:
        from_attributes = True
