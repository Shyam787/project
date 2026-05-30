import re
from dataclasses import dataclass

from app.auth.models import IdentityContext
from app.retrieval.models import AuthorizedRetrievalScope

MAX_QUERY_LENGTH = 2000
WHITESPACE_PATTERN = re.compile(r"\s+")


@dataclass(frozen=True)
class PreparedQuery:
    raw_query: str
    normalized_query: str
    tenant_id: str
    user_id: str
    scope: AuthorizedRetrievalScope


def normalize_query(query: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", query.strip()).lower()


def prepare_query(
    *,
    query: str,
    identity: IdentityContext,
    allowed_document_ids: set[str],
) -> PreparedQuery:
    normalized = normalize_query(query)
    if not normalized:
        raise ValueError("Query must not be empty.")
    if len(normalized) > MAX_QUERY_LENGTH:
        raise ValueError("Query exceeds maximum length.")
    return PreparedQuery(
        raw_query=query,
        normalized_query=normalized,
        tenant_id=identity.tenant.tenant_id,
        user_id=identity.user_id,
        scope=AuthorizedRetrievalScope(
            tenant_id=identity.tenant.tenant_id,
            allowed_document_ids=allowed_document_ids,
        ),
    )
