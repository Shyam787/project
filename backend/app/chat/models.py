from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None
    filters: dict = Field(default_factory=dict)
    stream: bool = False


class ChatFeedbackRequest(BaseModel):
    message_id: str = Field(min_length=1)
    rating: str = Field(pattern="^(thumbs_up|thumbs_down)$")
    comment: str | None = Field(default=None, max_length=1000)
