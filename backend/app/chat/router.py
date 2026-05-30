from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import require_permission
from app.auth.models import IdentityContext
from app.chat.models import ChatQueryRequest
from app.chat.service import answer_query
from app.db.dependencies import SessionDep, VectorStoreDep
from app.rbac.policies import Permission

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/query")
async def chat_query(
    request: Request,
    body: ChatQueryRequest,
    session: SessionDep,
    vector_store: VectorStoreDep,
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
    )
    return {
        "success": True,
        "payload": payload,
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }
