from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class Part(BaseModel):
    text: str

class Content(BaseModel):
    role: Optional[str] = None
    parts: List[Part]

class QueryRequest(BaseModel):
    contents: str
    parameters: Optional[Dict[str, Any]] = None
    loggingData: Optional[Dict[str, Any]] = None

class Conversation(BaseModel):
    user_id: str
    conversation_history: List[Content] = []