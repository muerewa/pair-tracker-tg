from aiogram.fsm.state import State, StatesGroup

class ConnectState(StatesGroup):
    waiting_for_partner_id = State()

class HabitState(StatesGroup):
    waiting_for_title = State()