import json
from collections.abc import AsyncIterator

from app.generation.models import GenerationRequest, LLMProvider
from app.generation.prompt import build_grounded_prompt
from app.retrieval.context import RetrievalContext


def sse_event(event: str, data: dict) -> str:
    encoded = json.dumps(data, separators=(",", ":"))
    return f"event: {event}\ndata: {encoded}\n\n"


async def stream_grounded_response(
    *,
    query: str,
    context: RetrievalContext,
    provider: LLMProvider,
    model: str,
) -> AsyncIterator[str]:
    prompt = build_grounded_prompt(query=query, context=context)
    yield sse_event("message_start", {"citation_ids": prompt.citation_ids})
    async for token in provider.stream_chat(
        GenerationRequest(messages=prompt.messages, model=model)
    ):
        yield sse_event("token", {"content": token.content})
    for citation in context.citations:
        yield sse_event("citation", citation.model_dump())
    yield sse_event("message_end", {"status": "complete"})
