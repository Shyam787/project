from typing import Annotated

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.auth.dependencies import require_identity, require_permission
from app.auth.models import IdentityContext
from app.db.dependencies import SessionDep, VectorStoreDep
from app.core.config import get_settings
from app.documents.service import (
    archive_document,
    get_document_for_identity,
    list_documents_for_identity,
    permanently_delete_document,
    preview_document_for_identity,
    repository_summary,
    restore_document,
    soft_delete_document,
    update_document_metadata,
    upload_text_document,
)
from app.rbac.policies import Permission

router = APIRouter(prefix="/documents", tags=["documents"])


class MetadataUpdateRequest(BaseModel):
    classification: str
    allowed_roles: list[str] | None = None
    description: str = ""
    tags: list[str] = []


@router.post("/upload")
async def upload_document(
    request: Request,
    session: SessionDep,
    vector_store: VectorStoreDep,
    identity: Annotated[
        IdentityContext,
        Depends(require_permission(Permission.DOCUMENT_UPLOAD)),
    ],
    file: UploadFile = File(...),
    allowed_roles: str = Form("viewer,employee,manager,tenant_admin"),
    classification: str = Form("Internal"),
    pii_sensitive: bool = Form(False),
) -> dict:
    role_set = {role.strip() for role in allowed_roles.split(",") if role.strip()}
    try:
        payload = await upload_text_document(
            session=session,
            vector_store=vector_store,
            identity=identity,
            filename=file.filename or "document.txt",
            content_type=file.content_type or "text/plain",
            raw_bytes=await file.read(),
            allowed_roles=role_set,
            pii_sensitive=pii_sensitive,
            classification=classification,
            settings=get_settings(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "success": True,
        "payload": payload,
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }


@router.get("")
async def list_documents(
    request: Request,
    session: SessionDep,
    identity: Annotated[IdentityContext, Depends(require_identity)],
) -> dict:
    return {
        "success": True,
        "payload": {
            "documents": await list_documents_for_identity(
                session=session,
                identity=identity,
            )
        },
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }


@router.get("/summary")
async def documents_summary(
    request: Request,
    session: SessionDep,
    identity: Annotated[IdentityContext, Depends(require_identity)],
) -> dict:
    return {
        "success": True,
        "payload": await repository_summary(session=session, identity=identity),
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    session: SessionDep,
    identity: Annotated[IdentityContext, Depends(require_identity)],
) -> FileResponse:
    doc = await get_document_for_identity(
        session=session, identity=identity, document_id=document_id
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    storage_path = doc.get("storage_path")
    if not storage_path or not Path(storage_path).exists():
        raise HTTPException(status_code=404, detail="Stored file not found.")
    return FileResponse(path=storage_path, filename=doc["title"])


@router.get("/{document_id}/preview")
async def preview_document(
    document_id: str,
    session: SessionDep,
    identity: Annotated[IdentityContext, Depends(require_identity)],
) -> dict:
    doc = await preview_document_for_identity(
        session=session, identity=identity, document_id=document_id
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"success": True, "payload": doc, "metadata": {}, "error": None}


@router.patch("/{document_id}/metadata")
async def edit_metadata(
    request: Request,
    document_id: str,
    body: MetadataUpdateRequest,
    session: SessionDep,
    identity: Annotated[IdentityContext, Depends(require_permission(Permission.DOCUMENT_DELETE))],
) -> dict:
    try:
        payload = await update_document_metadata(
            session=session,
            identity=identity,
            document_id=document_id,
            classification=body.classification,
            allowed_roles=body.allowed_roles,
            description=body.description,
            tags=body.tags,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "success": True,
        "payload": payload,
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }


@router.post("/{document_id}/archive")
async def archive_document_endpoint(
    request: Request,
    document_id: str,
    session: SessionDep,
    identity: Annotated[IdentityContext, Depends(require_permission(Permission.DOCUMENT_DELETE))],
) -> dict:
    try:
        payload = await archive_document(
            session=session, identity=identity, document_id=document_id
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {
        "success": True,
        "payload": payload,
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }


@router.post("/{document_id}/restore")
async def restore_document_endpoint(
    request: Request,
    document_id: str,
    session: SessionDep,
    identity: Annotated[IdentityContext, Depends(require_permission(Permission.DOCUMENT_DELETE))],
) -> dict:
    try:
        payload = await restore_document(
            session=session, identity=identity, document_id=document_id
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {
        "success": True,
        "payload": payload,
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }


@router.delete("/{document_id}")
async def soft_delete_document_endpoint(
    request: Request,
    document_id: str,
    session: SessionDep,
    identity: Annotated[IdentityContext, Depends(require_permission(Permission.DOCUMENT_DELETE))],
) -> dict:
    try:
        payload = await soft_delete_document(
            session=session, identity=identity, document_id=document_id
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {
        "success": True,
        "payload": payload,
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }


@router.delete("/{document_id}/permanent")
async def permanent_delete_document_endpoint(
    request: Request,
    document_id: str,
    session: SessionDep,
    vector_store: VectorStoreDep,
    identity: Annotated[IdentityContext, Depends(require_permission(Permission.DOCUMENT_DELETE))],
) -> dict:
    try:
        payload = await permanently_delete_document(
            session=session,
            vector_store=vector_store,
            identity=identity,
            document_id=document_id,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {
        "success": True,
        "payload": payload,
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }
