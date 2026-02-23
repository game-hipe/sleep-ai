from pathlib import Path

import aiofiles

from fastapi import FastAPI, APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse, FileResponse

from ..core.manager.create_memory import CreateMemoryManager


app = FastAPI()


class FrontEnd:
    def __init__(self, manager: CreateMemoryManager):
        self._app = FastAPI()
        self.manager = manager
        self.register_handlers()

        self._index_path = Path(__file__).parent / "templates" / "index.html"
        self._memory_path = Path(__file__).parent / "templates" / "memory.html"
        self._static_path = Path(__file__).parent / "static"

    def register_handlers(self):
        """Регистрирует хэндлеры"""
        self.app.add_api_route(
            "/", self.index, methods=["GET"], response_class=HTMLResponse, tags=["main"]
        )

        self.app.add_api_route(
            "/memory/{id}",
            self.memory,
            methods=["GET"],
            response_class=HTMLResponse,
            tags=["main"],
        )

        self.app.add_api_route(
            "/static/{path:path}",
            self._get_feature,
            methods=["GET"],
            response_class=FileResponse,
            tags=["static"],
        )

    async def index(self, request: Request):
        if self._index_path.exists():
            async with aiofiles.open(self._index_path, "rb") as f:
                return HTMLResponse(await f.read(), status_code=200)
        else:
            return HTMLResponse(
                content="Не удалось получить index.html", status_code=500
            )

    async def memory(self, id: int, request: Request):
        if self._static_path.exists():
            async with aiofiles.open(self._memory_path, "rb") as f:
                return HTMLResponse(await f.read(), status_code=200)
        else:
            return HTMLResponse(
                content=f"Не удалось получить восопмиание под ID {id}", status_code=500
            )

    async def _get_feature(self, path: str):
        if (self._static_path / path).is_file():
            return FileResponse(self._static_path / path)
        else:
            return HTMLResponse(content="Не удалось получить файл", status_code=500)

    def add_router(self, router: APIRouter):
        """Добавить роутер

        Args:
            router (APIRouter): Роутер
        """
        self.app.include_router(router)

    @property
    def app(self) -> FastAPI:
        """Возращает приложение.

        Returns:
            FastAPI: обьект FastAPI
        """
        return self._app
