from aiogram import Bot, Router, Dispatcher
from aiogram.types import BotCommand, Message

from ..core.manager.create_memory import CreateMemoryManager
from ._bot import BaseMemoryBot

from .memory import MemoryGetSendRouter, BaseRouter


__all__ = ["setup_bot", "start_bot"]


def help_func(dp: Dispatcher):
    router = Router()

    @router.message()
    async def unknown_command(message: Message):
        await message.answer(
            "Неизвестная команда. Используйте /help для получения списка доступных команд."
        )

    dp.include_router(router)


async def init_command(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="create", description="Создать воспоминание"),
            BotCommand(command="memory", description="Увидеть воспоминание"),
            BotCommand(command="help", description="Помощь"),
        ]
    )


async def setup_bot(
    manager: CreateMemoryManager,
    token: str | None = None,
    proxy: str | None = None,
) -> BaseMemoryBot:
    bot = BaseMemoryBot(manager, token=token, proxy=proxy)

    routers = [MemoryGetSendRouter(bot), BaseRouter(bot)]

    for router in routers:
        bot.register_router(router)

    help_func(bot.dispatcher)

    await init_command(bot.bot)
    return bot


async def start_bot(
    manager: CreateMemoryManager,
    token: str | None = None,
    proxy: str | None = None,
) -> None:
    bot = await setup_bot(manager, token=token, proxy=proxy)

    await bot.run()
