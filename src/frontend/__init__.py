import uvicorn

from ..core.manager.create_memory import CreateMemoryManager
from ._frontend import FrontEnd
from ._api import create_api


def setup_frontend(manager: CreateMemoryManager) -> FrontEnd:
    frontend = FrontEnd(manager)

    create_api(manager, frontend)

    return frontend


async def start_frontend(manager: CreateMemoryManager) -> None:
    frontend = setup_frontend(manager)

    config = uvicorn.Config(app=frontend.app, host="0.0.0.0", port=8000)

    await uvicorn.Server(config).serve()
