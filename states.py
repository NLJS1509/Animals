from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    wait_send_seconds = State()
    wait_link = State()
    wait_index = State()
    wait_time = State()