import asyncio


from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.entites.models import Base
from src.core.service import Telegraph
from src.core.manager import GeminiManager, MemoryManager
from src.core.manager.create_memory import CreateMemoryManager
from src.frontend import start_frontend
from src.bot import start_bot
from src.core import config


async def main():
    engine = create_async_engine(config.database_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncClient(proxy=config.proxy) as client:
        telegraph = Telegraph(client)
        gemini = GeminiManager(client)
        api = MemoryManager(engine)

        manager = CreateMemoryManager(gemini, telegraph, api)

        await asyncio.gather(start_frontend(manager), start_bot(manager))

    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ...
