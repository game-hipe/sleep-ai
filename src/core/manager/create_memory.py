from loguru import logger

from ..entites.schemas import SleepMemoryBaseModel, SleepMemoryUpdateModel
from ..abstract.ai import AIInterface
from ..service import Telegraph
from .memory import MemoryManager


MEMORY_TEXT = (
    "ID сна: <code>{id}</code>\n"
    "Название сна: <b>{title}</b>\n"
    "Содержание сна: <i>{content}</i>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "{thoughts}"
)


class CreateMemoryManager:
    def __init__(self, ai: AIInterface, telegraph: Telegraph, memory: MemoryManager):
        self.ai = ai
        self.memory = memory
        self.telegraph = telegraph

    async def create_memory(self, memory: SleepMemoryBaseModel):
        response = await self.ai.generate_response(memory)
        if not response.success:
            return response

        response = await self.memory.add_memory(response.content)
        if not response.success:
            return response

        try:
            page = await self.telegraph.create_page(
                title=response.content.title,
                content=MEMORY_TEXT.format(
                    id=response.content.id,
                    title=response.content.title,
                    content=response.content.content,
                    thoughts=response.content.ai_thoughts,
                ),
            )
            if not page.ok:
                logger.warning(
                    f"Не удалось создать ссылку на Telegraph (id={response.content.id})"
                )
                return response

            else:
                return await self.memory.update_memory(
                    response.content.id,
                    SleepMemoryUpdateModel(telegraph_url=str(page.result.url)),
                )

        except Exception as e:
            logger.error(e)
            return response
