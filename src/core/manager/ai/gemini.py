from loguru import logger
from google import genai
from httpx import AsyncClient

from ...entites.schemas import (
    SleepMemoryBaseModel,
    SleepMemoryCreateModel,
    BaseResponseModel,
)
from ...abstract.ai import AIInterface
from ..._config import config


class GeminiManager(AIInterface):
    """Класс для взаимодействия с моделью Gemini от Google для анализа снов и воспоминаний."""

    def __init__(
        self,
        httpx_client: AsyncClient,
        api_key: str | None = None,
        model: str | None = None,
    ):
        """Класс для взаимодействия с моделью Gemini от Google для анализа снов и воспоминаний.

        Args:
            httpx_client (AsyncClient): Асинхронный HTTP-клиент для выполнения запросов к API Gemini.
            api_key (str | None, optional): API-ключ для доступа к модели Gemini. Если не предоставлен, будет использован ключ из конфигурации. Обычное состояние None
            model (str | None, optional): Название модели Gemini для генерации контента. Если не предоставлено, будет использовано значение из конфигурации. Обычное состояние None
        """
        self.api_key = api_key or config.gemini_api_key
        self.model = model or config.gemini_model
        self._client = genai.Client(
            api_key=api_key, http_options={"httpx_async_client": httpx_client}
        )

    async def generate_response(
        self, memory: SleepMemoryBaseModel
    ) -> BaseResponseModel[SleepMemoryCreateModel]:
        """Сгенерировать ответ от AI.
        Промпт будт использоваться из переменной PROMPT_TEMPLATE.

        Args:
            memory (SleepMemoryBaseModel): Данные сна или воспоминания, которые нужно проанализировать. Ожидается, что это будет экземпляр модели Pydantic, содержащий все необходимые поля для анализа.

        Returns:
            SleepMemoryCreateModel: Модель с результатами анализа, включая оригинальные данные и сгенерированный текст.
        """
        logger.info(f"Генерация ответа для воспоминания: '{memory.title}'")
        memory_data = memory.model_dump_json()
        prompt = self.PROMPT_TEMPLATE.format(memory_data=memory_data)

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model, contents=prompt
            )

            if response.text is None:
                logger.warning("Ответ от модели Gemini не содержит текста.")
            else:
                logger.debug(
                    f"Ответ от модели Gemini успешно получен. (len={len(response.text)})"
                )

            output_memory = SleepMemoryCreateModel(
                **memory.model_dump(),
                ai_thoughts=response.text,
            )
            logger.success(
                f"Ответ от модели Gemini успешно обработан (title='{output_memory.title}', created_at={output_memory.created_at})"
            )
            return BaseResponseModel(
                success=True,
                message="Успешно удалось сгенерировать мнение Ai",
                content=output_memory,
            )
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа от модели Gemini: {str(e)}")
            return BaseResponseModel(
                success=False,
                message=f"Ошибка при обработке ответа от модели Gemini: {str(e)}",
                content=SleepMemoryCreateModel(**memory.model_dump()),
            )

    @property
    def client(self) -> genai.Client:
        """Геттер для доступа к экземпляру клиента Gemini."""
        return self._client
