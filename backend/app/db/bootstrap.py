from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.schema import metadata


async def create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
