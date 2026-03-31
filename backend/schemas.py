from pydantic import BaseModel
from typing import Optional

# --- Query & Response Schemas ---

class Query(BaseModel):
    text: str
    session_id: Optional[str] = "default"

class Response(BaseModel):
    question: str
    answer: str
    score: float
    requires_login: bool = False
    original_answer: Optional[str] = None
