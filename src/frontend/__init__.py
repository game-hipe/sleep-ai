import uvicorn

from ..core.abstract.ai import AIInterface
from ..core.manager import MemoryManager

from ._frontend import FrontEnd
from ._api import create_api


def setup_frontend(ai_manager: AIInterface, memory_manager: MemoryManager) -> FrontEnd:
    frontend = FrontEnd(ai_manager, memory_manager)

    create_api(frontend)

    return frontend


async def start_frontend(
    ai_manager: AIInterface, memory_manager: MemoryManager
) -> None:
    frontend = setup_frontend(ai_manager, memory_manager)

    config = uvicorn.Config(app=frontend.app, host="0.0.0.0", port=8000)

    await uvicorn.Server(config).serve()
