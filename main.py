import asyncio

import uvicorn

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.entites.models import Base
from src.core.manager import GeminiManager, MemoryManager
from src.bot import MemoryBot

from src.frontend import start_frontend

async def main():
    database = create_async_engine("sqlite+aiosqlite:///test.db")
    async with database.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    
    try:
        async with AsyncClient() as client:
            api = GeminiManager(client)
            manager = MemoryManager(database)
            
            #bot = MemoryBot(
            #    memory_manager = manager,
            #    ai_manager = api
            #)
            #
            #await bot.run()
            
            await start_frontend(api, manager)

    finally:
        await database.dispose()

  
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ...