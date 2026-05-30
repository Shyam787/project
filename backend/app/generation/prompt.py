from app.generation.models import ChatMessage, PromptBundle
from app.retrieval.context import RetrievalContext

SYSTEM_PROMPT = (
    "You are an enterprise RAG assistant. Answer only from the supplied "
    "authorized context. Cite supporting context using citation ids such as "
    "[c1]. If the context is insufficient, say that the answer is not "
    "grounded in the available documents."
)


def build_grounded_prompt(*, query: str, context: RetrievalContext) -> PromptBundle:
    context_lines: list[str] = []
    for citation, chunk in zip(context.citations, context.chunks, strict=True):
        context_lines.append(
            "\n".join(
                [
                    f"Citation: [{citation.citation_id}]",
                    f"Tenant: {citation.tenant_id}",
                    f"Document: {citation.document_id}",
                    f"Chunk: {citation.chunk_id}",
                    f"Evidence: {chunk.text}",
                ]
            )
        )
    user_content = "\n\n".join(
        [
            "Authorized context:",
            "\n\n---\n\n".join(context_lines),
            f"Question: {query}",
        ]
    )
    return PromptBundle(
        messages=[
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(role="user", content=user_content),
        ],
        citation_ids=[citation.citation_id for citation in context.citations],
    )
