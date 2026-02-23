import asyncio


from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.entites.models import Base
from src.core.manager import GeminiManager, MemoryManager

from src.frontend import start_frontend
from src.bot import start_bot


async def main():
    database = create_async_engine("sqlite+aiosqlite:///test.db")
    async with database.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        async with AsyncClient() as client:
            ai_manager = GeminiManager(client)
            memory_manager = MemoryManager(database)

            await asyncio.gather(
                start_frontend(ai_manager, memory_manager),
                start_bot(ai_manager, memory_manager),
            )

    finally:
        await database.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ...
