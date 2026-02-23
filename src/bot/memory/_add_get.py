import asyncio

from loguru import logger
from aiogram import F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .state import MemoryStates
from .._bot import MEMORY_TEXT
from .._bot import MemoryBotRouter
from ...core.entites.schemas import (
    SleepMemoryBaseModel,
    SleepMemoryCreateModel,
    BaseResponseModel,
    SleepMemoryModel,
)


class MemoryGetSendRouter(MemoryBotRouter):
    def register_handler(self):
        self.router.message.register(self.create_memory, Command("create"))
        self.router.message.register(self.get_memory, Command("memory"))

        self.router.message.register(
            self.process_title, MemoryStates.waiting_for_title, F.text
        )

        self.router.message.register(
            self.process_content, MemoryStates.waiting_for_content, F.text
        )

    async def get_memory(self, message: Message):
        logger.debug(
            f"Получение воспоминания (user_id={message.from_user.id}, chat_id={message.chat.id})"
        )
        try:
            _, id = message.text.split(maxsplit=1)
        except ValueError:
            await message.answer("Пожалуйста, введите ID воспоминания после команды.")
            return

        await self.answer_memory(message, id)

    async def create_memory(self, message: Message, state: FSMContext):
        logger.debug(
            f"Новое воспоминание (user_id={message.from_user.id}, chat_id={message.chat.id})"
        )
        await message.answer("Введите название воспоминания:")
        await state.set_state(MemoryStates.waiting_for_title)

    async def process_title(self, message: Message, state: FSMContext):
        if not message.text.strip():
            await message.answer(
                "Название не может быть пустым. Пожалуйста, введите название воспоминания:"
            )
            return

        logger.debug(f"Добавлено название (title={message.text.strip()})")
        await state.update_data(title=message.text.strip())
        await message.answer("Введите содержание воспоминания:")
        await state.set_state(MemoryStates.waiting_for_content)

    async def process_content(self, message: Message, state: FSMContext):
        if not message.text.strip():
            await message.answer(
                "Содержание не может быть пустым. Пожалуйста, введите содержание воспоминания:"
            )
            return

        logger.debug(f"Добавлено содержание (content={message.text.strip()})")
        data = await state.get_data()
        title: str = data.get("title")
        content: str = message.text.strip()

        response = await self.think(message=message, title=title, content=content)

        try:
            if not response.success:
                await message.answer(response.message)
                return

            await message.answer(
                MEMORY_TEXT.format(
                    id=response.content.id,
                    title=response.content.title,
                    content=response.content.content,
                    thoughts=response.content.ai_thoughts,
                ),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Telegraph", url=response.content.telegraph_url
                            )
                        ]
                    ]
                )
                if response.content.telegraph_url
                else None,
            )
        except Exception as e:
            logger.error(f"Ошибка при обработке воспоминания: {e}")
            await message.answer(
                "Произошла ошибка при обработке воспоминания. Пожалуйста, попробуйте еще раз."
            )

        finally:
            await state.clear()

    async def think(
        self, message: Message, title: str, content: str
    ) -> (
        BaseResponseModel[SleepMemoryCreateModel] | BaseResponseModel[SleepMemoryModel]
    ):
        message = await message.answer("Раздумываю над ответом")
        await self.memory_bot.bot.send_chat_action(
            chat_id=message.chat.id, action="typing"
        )
        try:
            task = asyncio.create_task(self._animation(message))
            response = await self.memory_bot.manager.create_memory(
                SleepMemoryBaseModel(title=title, content=content)
            )

            return response
        finally:
            task.cancel()
            await message.delete()
            await self.memory_bot.bot.send_chat_action(
                chat_id=message.chat.id, action="cancel"
            )

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
                await message.edit_text("Раздумываю над ответом" + text)
        except Exception:
            pass
