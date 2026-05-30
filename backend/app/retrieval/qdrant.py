from app.retrieval.models import AuthorizedRetrievalScope


def tenant_collection_name(tenant_id: str) -> str:
    return f"tenant_{tenant_id}"


def qdrant_document_filter(scope: AuthorizedRetrievalScope) -> dict:
    return {
        "must": [
            {"key": "tenant_id", "match": {"value": scope.tenant_id}},
            {
                "key": "document_id",
                "match": {"any": sorted(scope.allowed_document_ids)},
            },
        ]
    }
