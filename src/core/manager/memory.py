from typing import AsyncGenerator, overload
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncEngine

from ..entites.schemas import (
    SleepMemoryCreateModel,
    SleepMemoryModel,
    SleepMemoryUpdateModel,
    BaseResponseModel,
)
from ..entites.models import SleepMemory


class MemoryManager:
    """Менеджер для работы с воспоминаниями"""

    def __init__(self, engine: AsyncEngine):
        """Инцилизация менеджера

        Args:
            engine (AsyncEngine): асинхроннный движок
        """
        self._engine = engine
        self.Session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine, expire_on_commit=False
        )

    async def add_memory(
        self, memory: SleepMemoryCreateModel
    ) -> BaseResponseModel[SleepMemoryModel]:
        """Создать воспоминание

        Args:
            memory (SleepMemoryCreateModel): воспоминание

        Returns:
            BaseResponseModel[SleepMemoryModel]: ответ с результатом операции
        """
        async with self.session() as session:
            try:
                save_memory = self.build_memory(memory)
                session.add(save_memory)
                await session.flush()

                return BaseResponseModel(
                    success=True,
                    message="Воспоминание успешно сохранено",
                    content=self.build_memory(save_memory),
                )
            except Exception as e:
                return BaseResponseModel(
                    success=False,
                    message=f"Ошибка при сохранении воспоминания: {str(e)}",
                    content=None,
                )

    async def get_memory(self, memory_id: int) -> BaseResponseModel[SleepMemoryModel]:
        """Получить воспоминание.

        Args:
            memory_id (int): идентификатор воспоминания

        Returns:
            BaseResponseModel[SleepMemoryModel]: ответ с результатом операции
        """
        async with self.session() as session:
            try:
                result = await session.get(SleepMemory, memory_id)
                if result is None:
                    return BaseResponseModel(
                        success=False, message="Воспоминание не найдено", content=None
                    )
                return BaseResponseModel(
                    success=True,
                    message="Воспоминание успешно получено",
                    content=self.build_memory(result),
                )
            except Exception as e:
                return BaseResponseModel(
                    success=False,
                    message=f"Ошибка при получении воспоминания: {str(e)}",
                    content=None,
                )

    async def delete_memory(self, memory_id: int) -> BaseResponseModel[None]:
        """Удалить воспоминание.

        Args:
            memory_id (int): идентификатор воспоминания

        Returns:
            BaseResponseModel[None]: ответ с результатом операции
        """
        async with self.session() as session:
            try:
                result = await session.get(SleepMemory, memory_id)
                if result is None:
                    return BaseResponseModel(
                        success=False, message="Воспоминание не найдено", content=None
                    )
                await session.delete(result)
                return BaseResponseModel(
                    success=True, message="Воспоминание успешно удалено", content=None
                )
            except Exception as e:
                return BaseResponseModel(
                    success=False,
                    message=f"Ошибка при удалении воспоминания: {str(e)}",
                    content=None,
                )

    async def update_memory(
        self, memory_id: int, memory: SleepMemoryUpdateModel
    ) -> BaseResponseModel[SleepMemoryModel]:
        """Обновить воспоминание.

        Args:
            memory_id (int): идентификатор воспоминания
            memory (SleepMemoryUpdateModel): обновленное воспоминание

        Returns:
            BaseResponseModel[SleepMemoryModel]: ответ с результатом операции
        """
        async with self.session() as session:
            try:
                result = await session.get(SleepMemory, memory_id)
                if result is None:
                    return BaseResponseModel(
                        success=False, message="Воспоминание не найдено", content=None
                    )
                result.title = (
                    memory.title if memory.title is not None else result.title
                )
                result.content = (
                    memory.content if memory.content is not None else result.content
                )
                result.ai_thoughts = (
                    memory.ai_thoughts
                    if memory.ai_thoughts is not None
                    else result.ai_thoughts
                )
                result.telegraph_url = (
                    memory.telegraph_url
                    if memory.telegraph_url is not None
                    else result.telegraph_url
                )
                await session.flush()

                return BaseResponseModel(
                    success=True,
                    message="Воспоминание успешно обновлено",
                    content=self.build_memory(result),
                )
            except Exception as e:
                return BaseResponseModel(
                    success=False,
                    message=f"Ошибка при обновлении воспоминания: {str(e)}",
                    content=None,
                )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Асинхронный контекстный менеджер для работы с сессией базы данных"""
        async with self.Session() as session:
            async with session.begin():
                yield session

    @overload
    def build_memory(self, memory: SleepMemoryCreateModel) -> SleepMemory:
        """Построить модель воспоминания для сохранения в базе данных

        Args:
            memory (SleepMemoryCreateModel): данные воспоминания для сохранения

        Returns:
            SleepMemory: модель воспоминания для сохранения в базе данных
        """

    @overload
    def build_memory(self, memory: SleepMemory) -> SleepMemoryModel:
        """Построить модель воспоминания для возврата пользователю

        Args:
            memory (SleepMemory): данные воспоминания из базы данных

        Returns:
            SleepMemoryModel: модель воспоминания для возврата пользователю
        """

    def build_memory(
        self, memory: SleepMemoryCreateModel | SleepMemory
    ) -> SleepMemory | SleepMemoryModel:
        """Построить модель в зависимости от типа входящих воспоминаний

        Args:
            memory (SleepMemoryCreateModel  | SleepMemory): данные воспоминания для сохранения или данные воспоминания из базы данных

        Returns:
            SleepMemory | SleepMemoryModel: модель воспоминания для сохранения или модели воспоминания для возврата пользователю
        """
        if isinstance(memory, SleepMemory):
            return SleepMemoryModel.model_validate(memory.to_dict())

        elif isinstance(memory, SleepMemoryCreateModel):
            return SleepMemory(
                title=memory.title,
                content=memory.content,
                ai_thoughts=memory.ai_thoughts,
                created_at=memory.created_at,
                telegraph_url=memory.telegraph_url,
            )
        else:
            raise TypeError("Неподдерживаемый тип воспоминания для построения модели")

    @property
    def engine(self) -> AsyncEngine:
        """Получить движок базы данных"""
        return self._engine
