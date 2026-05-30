from collections.abc import AsyncIterator
from typing import Protocol

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class GenerationRequest(BaseModel):
    messages: list[ChatMessage]
    model: str
    temperature: float = 0.0
    stream: bool = True


class GenerationToken(BaseModel):
    content: str


class LLMProvider(Protocol):
    async def stream_chat(
        self, request: GenerationRequest
    ) -> AsyncIterator[GenerationToken]:
        """Stream grounded generation tokens."""


class PromptBundle(BaseModel):
    messages: list[ChatMessage]
    citation_ids: list[str] = Field(default_factory=list)
