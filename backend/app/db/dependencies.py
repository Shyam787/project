from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.retrieval.qdrant_store import QdrantVectorStore


async def get_session(request: Request) -> AsyncSession:
    factory: async_sessionmaker = request.app.state.session_factory
    async with factory() as session:
        async with session.begin():
            yield session


def get_vector_store(request: Request) -> QdrantVectorStore:
    return request.app.state.vector_store


SessionDep = Annotated[AsyncSession, Depends(get_session)]
VectorStoreDep = Annotated[QdrantVectorStore, Depends(get_vector_store)]
