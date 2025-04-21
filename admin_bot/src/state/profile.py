from aiogram.fsm.state import StatesGroup, State


class ProfileStates(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_bio = State()
    waiting_for_location = State()
    waiting_for_experience_summary = State()
    waiting_for_job_status = State()
    waiting_for_resume_link = State()
    waiting_for_social_links = State()
    waiting_for_skills = State()
