import asyncio

from loguru import logger
from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .state import MemoryStates
from ._text import MEMORY_TEXT
from .._bot import BaseMemoryBot
from ...core.entites.schemas import SleepMemoryBaseModel, SleepMemoryCreateModel, BaseResponseModel

class MemoryBot(BaseMemoryBot):
    def register_handlers(self):
        self.dispatcher.message.register(
            self.create_memory,
            Command("create")
        )
        
        self.dispatcher.message.register(
            self.process_title,
            MemoryStates.waiting_for_title,
            F.text
        )
        
        self.dispatcher.message.register(
            self.process_content,
            MemoryStates.waiting_for_content,
            F.text
        )
    
    async def create_memory(self, message: Message, state: FSMContext):
        logger.debug(f"Новое воспоминание (user_id={message.from_user.id}, chat_id={message.chat.id})")
        await message.answer("Введите название воспоминания:")
        await state.set_state(MemoryStates.waiting_for_title)
        
    async def process_title(self, message: Message, state: FSMContext):
        if not message.text.strip():
            await message.answer("Название не может быть пустым. Пожалуйста, введите название воспоминания:")
            return
        
        logger.debug(f"Добавлено название (title={message.text.strip()})")
        await state.update_data(title=message.text.strip())
        await message.answer("Введите содержание воспоминания:")
        await state.set_state(MemoryStates.waiting_for_content)
        
    async def process_content(self, message: Message, state: FSMContext):
        if not message.text.strip():
            await message.answer("Содержание не может быть пустым. Пожалуйста, введите содержание воспоминания:")
            return

        logger.debug(f"Добавлено содержание (content={message.text.strip()})")
        data = await state.get_data()
        title: str = data.get("title")
        content: str = message.text.strip()

        response = await self.think(
            message=message,
            title=title,
            content=content
        )

        try:
            if not response.success:
                await message.answer(f"Произошла ошибка при генерации мыслей ИИ: {response.message}")
                return

            memory_response = await self.memory_manager.add_memory(
                response.content
            )

            if not memory_response.success:
                await message.answer(f"Произошла ошибка при добавлении воспоминания: {memory_response.message}")
                return

            await message.answer(
                MEMORY_TEXT.format(
                    id = memory_response.content.id,
                    title = memory_response.content.title,
                    content = memory_response.content.content,
                    thoughts = memory_response.content.ai_thoughts
                )
            )
        except Exception as e:
            logger.error(f"Ошибка при обработке воспоминания: {e}")
            await message.answer("Произошла ошибка при обработке воспоминания. Пожалуйста, попробуйте еще раз.")

        finally:
            await state.clear()

    async def think(self, message: Message, title: str, content: str) -> BaseResponseModel[SleepMemoryCreateModel]:
        await self.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        message = await message.answer(
            "Раздумываю над ответом"
        )
        try:
            task = asyncio.create_task(self._animation(message))
            response = await self.ai_manager.generate_response(
                SleepMemoryBaseModel(
                    title = title,
                    content = content
                )
            )
            
            return response
        finally:
            task.cancel()
            await self.bot.send_chat_action(chat_id=message.chat.id, action="cancel")
            await message.delete()
            
    async def _animation(self, message: Message):
        """Анимация для бота."""
        text = ""
        try:
            while True:
                if text == "....":
                    text = ""
                else:
                    text += "."
     
                await asyncio.sleep(1)
                await message.edit_text(
                    "Раздумываю над ответом" + text
                )
        except Exception:
            pass