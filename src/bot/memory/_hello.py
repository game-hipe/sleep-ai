from aiogram.filters import Command
from aiogram.types import Message
from .._bot import MemoryBotRouter


class BaseRouter(MemoryBotRouter):
    def register_handler(self):
        self.router.message.register(self.hello, Command("start"))

        self.router.message.register(self.help, Command("help"))

    async def hello(self, message: Message):
        await message.answer(
            "Привет! Я бот для создания и хранения воспоминаний.\n"
            "Используйте /create для создания нового воспоминания и /memory для просмотра существующих."
        )

    async def help(self, message: Message):
        await message.answer(
            "Список доступных команд:\n"
            "/create - Создать новое воспоминание\n"
            "/memory - Посмотреть существующие воспоминания\n"
            "/help - Показать это сообщение"
        )
