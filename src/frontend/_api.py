from fastapi import APIRouter, HTTPException

from ._frontend import FrontEnd
from ..core.entites.schemas import (
    SleepMemoryBaseModel,
    BaseResponseModel,
    SleepMemoryUpdateModel,
    SleepMemoryModel,
)


def create_api(front_end: FrontEnd):

    router = APIRouter(prefix="/api", tags=["api"])

    @router.post("/add")
    async def create_memory(
        memory: SleepMemoryBaseModel,
    ) -> BaseResponseModel[SleepMemoryModel]:
        """Создаёт воспоминание,

        Args:
            memory (SleepMemoryBaseModel): Модель воспоминание.

        Raises:
            HTTPException: Если при генерации ответа произошла ошибка.
            HTTPException: Если при добавлении памяти произошла ошибка.

        Returns:
            BaseResponseModel[SleepMemoryModel]: Модель ответа с воспоминанием.
        """
        response = await front_end.ai_manager.generate_response(memory)
        if not response.success:
            raise HTTPException(status_code=500, detail=response.message)

        response = await front_end.memory_manager.add_memory(response.content)

        if not response.success:
            raise HTTPException(status_code=500, detail=response.message)

        return response

    @router.delete("/delete/{id}")
    async def delete_memory(id: int) -> BaseResponseModel[None]:
        """Удаляет воспоминание по ID

        Args:
            id (int): Уникальный идентификатор воспоминания.

        Returns:
            BaseResponseModel[None]: Ничего не возращает кроме сообшение и статуса
        """
        return await front_end.memory_manager.delete_memory(id)

    @router.get("/memory/{id}")
    async def get_memory(id: int) -> BaseResponseModel[SleepMemoryModel]:
        """Получить память по ID

        Args:
            id (int): Уникальный идентификатор воспоминания.

        Returns:
            BaseResponseModel[SleepMemoryModel]: Модель ответа с воспоминанием.
        """
        return await front_end.memory_manager.get_memory(id)

    @router.patch("/memory/{id}")
    async def update_memory(
        id: int, memory: SleepMemoryUpdateModel
    ) -> BaseResponseModel[SleepMemoryModel]:
        """Обновить память.

        Args:
            id (int): Уникальный идентификатор воспоминания.
            memory (SleepMemoryUpdateModel): Обновленное воспоминание.

        Returns:
            BaseResponseModel[SleepMemoryModel]: Ответ с результатом операции.
        """
        return await front_end.memory_manager.update_memory(memory_id=id, memory=memory)

    front_end.add_router(router)
