from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(min_length=1)

class Msg(BaseModel):
    role: Literal["user", "bot"]
    message: str

class ChatResponse(BaseModel):
    conversation_id: str
    message: List[Msg]
