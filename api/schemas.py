from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    docs_path: str = Field(..., min_length=1, max_length=255)
    prompt: str = Field(..., min_length=1)
    active: bool = True

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    description: Optional[str] = None
    docs_path: Optional[str] = Field(default=None, max_length=255)
    prompt: Optional[str] = None
    active: Optional[bool] = None

class AgentResponse(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    question: str = Field(...,min_length=1)
    selected_agent: Optional[str] = Field(default=None, min_length=1, max_length=100)

class ChatResponse(BaseModel):
    agent:str
    answer:str
    sources: list[str]