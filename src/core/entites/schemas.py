from typing import TypeVar, Generic
from datetime import datetime

from pydantic import BaseModel, Field


__all__ = [
    "SleepMemoryBaseModel",
    "SleepMemoryCreateModel",
    "SleepMemoryModel",
    "BaseResponseModel",
]

_T = TypeVar("_T", bound=BaseModel)


class SleepMemoryBaseModel(BaseModel):
    """Базовая модель данных для воспоминаний о сне."""

    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)


class SleepMemoryCreateModel(SleepMemoryBaseModel):
    """Модель данных для создания воспоминаний о сне."""

    ai_thoughts: str | None = Field(default=None)
    telegraph_url: str | None = Field(default=None)


class SleepMemoryModel(SleepMemoryCreateModel):
    """Модель данных для представления воспоминаний о сне с ID."""

    id: int


class BaseResponseModel(BaseModel, Generic[_T]):
    """Базовая модель данных для ответов API."""

    success: bool
    message: str | None = Field(default=None)
    content: _T | None = Field(default=None)


class SleepMemoryUpdateModel(BaseModel):
    """Модель данных для обновления воспоминаний о сне."""

    title: str | None = Field(default=None)
    content: str | None = Field(default=None)
    ai_thoughts: str | None = Field(default=None)
    telegraph_url: str | None = Field(default=None)
