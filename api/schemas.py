from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field

class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    docs_path: str = Field(..., min_length=1, max_length=255)
    prompt: str = Field(..., min_length=1)
    agent_type: Literal["specialist","supervisor"]="specialist"
    active: bool = True

class AgentCreate(AgentBase):
    connected_agent_ids: list[int] = Field(default_factory=list)

class AgentUpdate(BaseModel):
    description: Optional[str] = None
    docs_path: Optional[str] = Field(default=None, max_length=255)
    prompt: Optional[str] = None
    agent_type: Optional[Literal["specialist","supervisor"]]=None
    active: Optional[bool] = None
    connected_agent_ids: Optional[list[int]]= None

class AgentResponse(BaseModel):
    id: int
    name: str
    description: str
    docs_path: str
    prompt: str
    agent_type: str
    active: bool
    connected_agent_ids: list[int] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    question: str = Field(...,min_length=1)
    selected_agent: Optional[str] = Field(default=None, min_length=1, max_length=100)

class ChatResponse(BaseModel):
    agent:str
    answer:str
    sources: list[str]