from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None
    filters: dict = Field(default_factory=dict)
    stream: bool = False
