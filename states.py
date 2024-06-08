from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    wait_send_seconds = State()
    wait_link = State()
    wait_index = State()
    wait_sleep = State()
    wait_up = State()
    wait_json = State()
    wait_media = State()
    wait_start = State()