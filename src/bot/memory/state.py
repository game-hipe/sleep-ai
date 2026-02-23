from aiogram.fsm.state import State, StatesGroup


class MemoryStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()
