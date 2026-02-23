from fastapi import FastAPI, APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from ..core.abstract.ai import AIInterface
from ..core.manager import MemoryManager


app = FastAPI()


class FrontEnd:
    def __init__(
        self,
        ai_manager: AIInterface,
        memory_manager: MemoryManager
    ):
        self._app = FastAPI()
        self.ai_manager = ai_manager
        self.memory_manager = memory_manager
        self.register_handlers()

    def register_handlers(self):
        """Регистрирует хэндлеры"""
        self.app.add_api_route(
            "/",
            self.index,
            methods=["GET"],
            response_class=HTMLResponse,
            tags = ["main"]
        )
        
        self.app.add_api_route(
            "/memory/{id}",
            self.memory,
            methods=["GET"],
            response_class=HTMLResponse,
            tags = ["main"]
        )

    async def index(self, request: Request):
        return HTMLResponse(
            content = "sex",
        )

    async def memory(self, id: int, request: Request):
        return HTMLResponse(
            content = f"sex {id}",
        )

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
