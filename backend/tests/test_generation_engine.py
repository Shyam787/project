import json

import pytest

from app.generation.models import GenerationRequest, GenerationToken
from app.generation.prompt import build_grounded_prompt
from app.generation.streaming import sse_event, stream_grounded_response
from app.retrieval.context import assemble_retrieval_context
from app.retrieval.models import RetrievalCandidate


def _context():
    return assemble_retrieval_context(
        tenant_id="tenant-a",
        candidates=[
            RetrievalCandidate(
                chunk_id="chunk-1",
                document_id="doc-1",
                tenant_id="tenant-a",
                text="The policy requires annual access review.",
                retrieval_source="rrf",
                retrieval_score=0.42,
                rerank_score=0.9,
                rank=1,
            )
        ],
    )


def test_prompt_injects_only_authorized_context_with_citation_ids():
    prompt = build_grounded_prompt(query="What is required?", context=_context())

    assert prompt.citation_ids == ["c1"]
    assert "[c1]" in prompt.messages[1].content
    assert "annual access review" in prompt.messages[1].content


def test_sse_event_uses_documented_shape():
    event = sse_event("token", {"content": "hello"})

    assert event.startswith("event: token\n")
    payload = json.loads(event.split("data: ", 1)[1])
    assert payload == {"content": "hello"}


@pytest.mark.anyio
async def test_stream_grounded_response_orders_tokens_citations_and_end():
    class Provider:
        async def stream_chat(self, request: GenerationRequest):
            yield GenerationToken(content="Access ")
            yield GenerationToken(content="review")

    events = [
        event
        async for event in stream_grounded_response(
            query="What is required?",
            context=_context(),
            provider=Provider(),
            model="test-model",
        )
    ]

    assert events[0].startswith("event: message_start")
    assert events[1].startswith("event: token")
    assert events[2].startswith("event: token")
    assert events[3].startswith("event: citation")
    assert events[4].startswith("event: message_end")
