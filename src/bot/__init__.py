from aiogram import Bot
from aiogram.types import BotCommand

from ..core.manager.create_memory import CreateMemoryManager
from ._bot import BaseMemoryBot

from .memory import MemoryGetSendRouter


__all__ = ["setup_bot", "start_bot"]


async def init_command(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="create", description="Создать воспоминание"),
            BotCommand(command="memory", description="Увидеть воспоминание"),
        ]
    )


async def setup_bot(
    manager: CreateMemoryManager,
    token: str | None = None,
    proxy: str | None = None,
) -> BaseMemoryBot:
    bot = BaseMemoryBot(manager, token=token, proxy=proxy)

    routers = [MemoryGetSendRouter(bot)]

    for router in routers:
        bot.register_router(router)

    await init_command(bot.bot)
    return bot


async def start_bot(
    manager: CreateMemoryManager,
    token: str | None = None,
    proxy: str | None = None,
) -> None:
    bot = await setup_bot(manager, token=token, proxy=proxy)

    await bot.run()
