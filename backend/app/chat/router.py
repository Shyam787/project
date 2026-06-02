from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.dialects.postgresql import insert
from uuid import uuid4

from app.auth.dependencies import require_permission
from app.auth.models import IdentityContext
from app.audit.service import record_audit_event
from app.chat.models import ChatFeedbackRequest, ChatQueryRequest
from app.chat.service import answer_query
from app.db.dependencies import RedisDep, SessionDep, VectorStoreDep
from app.db.schema import feedback, messages
from app.rbac.policies import Permission

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/query")
async def chat_query(
    request: Request,
    body: ChatQueryRequest,
    session: SessionDep,
    vector_store: VectorStoreDep,
    cache_client: RedisDep,
    identity: Annotated[
        IdentityContext,
        Depends(require_permission(Permission.DOCUMENT_READ)),
    ],
) -> dict:
    payload = await answer_query(
        session=session,
        vector_store=vector_store,
        identity=identity,
        query=body.query,
        settings=request.app.state.settings,
        cache_client=cache_client,
    )
    return {
        "success": True,
        "payload": payload,
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }


@router.post("/feedback")
async def chat_feedback(
    request: Request,
    body: ChatFeedbackRequest,
    session: SessionDep,
    identity: Annotated[
        IdentityContext,
        Depends(require_permission(Permission.FEEDBACK_ACCESS)),
    ],
) -> dict:
    message_row = (
        await session.execute(
            messages.select().where(
                messages.c.id == body.message_id,
                messages.c.tenant_id == identity.tenant.tenant_id,
                messages.c.role == "assistant",
            )
        )
    ).mappings().first()
    if message_row is None:
        raise HTTPException(
            status_code=404,
            detail="Feedback target message was not found for this organization.",
        )
    await session.execute(
        insert(feedback).values(
            id=str(uuid4()),
            tenant_id=identity.tenant.tenant_id,
            message_id=body.message_id,
            user_id=identity.user_id,
            rating=body.rating,
            comment=body.comment,
            retrieval_trace=(message_row["citation_payload"] or {}).get("retrieval", {}),
        )
    )
    await record_audit_event(
        session=session,
        tenant_id=identity.tenant.tenant_id,
        user_id=identity.user_id,
        event_type="Feedback Submitted",
        resource_type="message",
        resource_id=body.message_id,
        metadata={"rating": body.rating},
    )
    return {
        "success": True,
        "payload": {"message_id": body.message_id, "rating": body.rating},
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }
