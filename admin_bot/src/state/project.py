from aiogram.fsm.state import StatesGroup, State


class ProjectStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_role = State()
    waiting_for_technologies = State()
    waiting_for_business_goal = State()
    waiting_for_result = State()
    waiting_for_access_note = State()
    waiting_for_is_featured = State()
