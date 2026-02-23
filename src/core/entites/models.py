from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime


__all__ = ["SleepMemory", "Base"]


class Base(DeclarativeBase): ...


class SleepMemory(Base):
    """Модель данных для хранения воспоминаний о сне."""

    __tablename__ = "sleep_memory"
    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    ai_thoughts: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    def __repr__(self):
        content_preview = (
            self.content[:20] + "..." if len(self.content) > 20 else self.content
        )
        ai_preview = None
        if self.ai_thoughts:
            ai_preview = (
                self.ai_thoughts[:20] + "..."
                if len(self.ai_thoughts) > 20
                else self.ai_thoughts
            )

        return (
            f"<SleepMemory(id={self.id}, title='{self.title}', "
            f"created_at='{self.created_at}', content='{content_preview}', "
            f"ai_thoughts='{ai_preview}')>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "ai_thoughts": self.ai_thoughts,
            "created_at": self.created_at,
        }
