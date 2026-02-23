from abc import ABC, abstractmethod
from urllib.parse import urlparse

from loguru import logger
from aiohttp import BasicAuth
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, Router

from ..core.manager.memory import MemoryManager
from ..core.abstract.ai import AIInterface
from ..core import config


class MemoryBotRouter(ABC):
    def __init__(self, memory_bot: "BaseMemoryBot"):
        self.memory_bot = memory_bot
        self._router = Router()

        self.register_handler()

    @abstractmethod
    def register_handler(self): ...

    @property
    def router(self):
        return self._router


class BaseMemoryBot:
    """Базовый класс Бота Aiogram, который использует MemoryManager для управления памятью и AIInterface для взаимодействия с ИИ."""

    def __init__(
        self,
        ai_manager: AIInterface,
        memory_manager: MemoryManager,
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

    async def run(self):
        """Запустить бота"""
        try:
            logger.success(f"Бот [{await self.bot.get_my_name()}] - Запущен!")
            await self.dispatcher.start_polling(self.bot)
        finally:
            await self.bot.session.close()

    def register_router(self, router: MemoryBotRouter):
        """Регистрирует новый Handler

        Args:
            router (MemoryBotRouter): Экземпляр класса MemoryBotRouter
        """
        self.dispatcher.include_router(router.router)

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
            session=AiohttpSession(proxy=self.proxy),
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
    def proxy(self) -> str | tuple[str, BasicAuth] | None:
        """Получить прокси сервера"""
        logger.debug(self._proxy)
        if not self._proxy:
            logger.debug("Нету прокси")
            return None

        parsed = urlparse(self._proxy)
        if not parsed.username and parsed.password:
            logger.debug("Прокси есть но без логина и пароля")
            return self._proxy

        logger.debug("Пароль и логин есть")
        return self._proxy, BasicAuth(login=parsed.username, password=parsed.password)

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
