from abc import ABC, abstractmethod

from loguru import logger
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher

from ..core.manager.memory import MemoryManager
from ..core.abstract.ai import AIInterface
from ..core import config


class BaseMemoryBot(ABC):
    """Базовый класс Бота Aiogram, который использует MemoryManager для управления памятью и AIInterface для взаимодействия с ИИ."""

    def __init_subclass__(cls):
        return super().__init_subclass__()

    def __init__(
        self,
        memory_manager: MemoryManager,
        ai_manager: AIInterface,
        token: str | None = None,
        proxy: str | None = None,
    ):
        """Базовый класс Бота Aiogram

        Args:
            memory_manager (MemoryManager): Менеджер памяти.
            ai_manager (AIInterface): Менеджер ИИ.
            token (str | None, optional): Токен бота, если токен бота не указае берётся дефолтное из config. Обычное состояние None.
            proxy (str | None, optional): Прокси сервер. Обычное состояние None.
        """
        self.memory_manager = memory_manager
        self.ai_manager = ai_manager

        self._token = token or config.bot_token
        self._proxy = proxy or config.proxy
        self._bot: Bot | None = None
        self._dp: Dispatcher | None = None

        self.register_handlers()

    async def run(self):
        """Запустить бота"""
        try:
            logger.success(f"Бот [{await self.bot.get_my_name()}] - Запущен!")
            await self.dispatcher.start_polling(self.bot)
        finally:
            await self.bot.session.close()

    @abstractmethod
    def register_handlers(self):
        """Зарегистрировать обработчики бота"""

    def _create_bot(self, token: str | None = None) -> Bot:
        """Создать экземпляр бота

        Args:
            token (str | None, optional): Токен бота, если токен бота не указан, берётся дефолтное из config. Обычное состояние None.

        Returns:
            Bot: Экземпляр бота.
        """
        return Bot(
            token=token or self._token,
            default=DefaultBotProperties(parse_mode="HTML"),
            session=AiohttpSession(proxy=self._proxy),
        )

    def _create_dispatcher(self) -> Dispatcher:
        """Создать экземпляр диспетчера

        Returns:
            Dispatcher: Экземпляр диспетчера.
        """
        return Dispatcher(storage=MemoryStorage())

    @property
    def token(self) -> str:
        """Получить токен бота"""
        return self._token

    @property
    def proxy(self) -> str | None:
        """Получить прокси сервера"""
        return self._proxy

    @property
    def bot(self) -> Bot:
        """Получить экземпляр бота, если он не был создан, создать его."""
        if self._bot is None:
            self._bot = self._create_bot()
        return self._bot

    @property
    def dispatcher(self) -> Dispatcher:
        """Получить экземпляр диспетчера, если он не был создан, создать его."""
        if self._dp is None:
            self._dp = self._create_dispatcher()
        return self._dp
