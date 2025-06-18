from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class Speaker(str, Enum):
    USER = "user"
    BOT = "bot"

class DialogueTurn(BaseModel):
    speaker: Speaker
    text: str
    timestamp: Optional[str] = None

class CallTranscript(BaseModel):
    call_id: str
    dialog: List[DialogueTurn]
    metadata: Optional[Dict[str, Any]] = None

class AnalysisResult(BaseModel):
    intent: str
    bot_response_summary: str
    issue_detected: bool
    issue_reason: str
    suggested_fix: str
    confidence_score: float = Field(ge=0.0, le=1.0)

class CallAnalysisResponse(BaseModel):
    call_id: str
    status: str  # "analyzed", "skipped", "error"
    reason: Optional[str] = None
    analysis: Optional[AnalysisResult] = None
    error: Optional[str] = None

class BatchAnalysisRequest(BaseModel):
    transcripts: List[CallTranscript]

class BatchAnalysisResponse(BaseModel):
    results: List[CallAnalysisResponse]
    summary: Dict[str, int]  # counts of analyzed, skipped, errors 