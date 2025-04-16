import json
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from src.keyboards.base import get_default_keyboard
from src.producer import Producer
from src.schemas.resume import (
    FullNameSchema,
    BioSchema,
    LocationSchema,
    ExperienceSummarySchema,
    JobStatus,
    JobStatusSchema,
    ResumeLinkSchema,
    SocialLink,
    SocialLinksSchema,
    SkillsSchema,
    ProfileSchema,
    ProjectSchema,
    IsFeaturedSchema,
    AccessNoteSchema,
    ResultSchema,
    BusinessGoalSchema,
    TechnologiesSchema,
    RoleSchema,
    DescriptionSchema,
    TitleSchema,
)
from src.state.profile import ProfileStates
from src.state.project import ProjectStates
from src.utils import entities_to_html

router = Router(name="resume")


# Хелпер для создания одноразовой клавиатуры
def make_keyboard(options: list[str]) -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=option)] for option in options] + [
        [KeyboardButton(text="/cancel")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=buttons, one_time_keyboard=True, resize_keyboard=True
    )


async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Operation cancelled.", reply_markup=get_default_keyboard())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await cancel(message, state)


@router.callback_query(F.data == "cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await cancel(callback.message, state)


# region Profile


@router.message(Command("update_profile"))
async def cmd_update_profile(message: Message, state: FSMContext) -> None:
    await start_update_profile(message, state)


@router.callback_query(F.data == "update_profile")
async def cb_update_profile(callback: CallbackQuery, state: FSMContext) -> None:
    await start_update_profile(callback.message, state)


async def start_update_profile(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Enter your full name (max 50 chars):",
        reply_markup=make_keyboard(["Старобогатов Алексей Игоревич"]),
    )
    await state.set_state(ProfileStates.waiting_for_full_name)


@router.message(ProfileStates.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext) -> None:
    try:
        text = entities_to_html(message.text, entities=message.entities)
        print(text)
        FullNameSchema(full_name=text)
        await state.update_data(full_name=text)
        await message.answer(
            "Enter your bio (max 1500 chars):", reply_markup=make_keyboard([])
        )
        await state.set_state(ProfileStates.waiting_for_bio)
    except ValueError as e:
        await message.answer(f"Invalid name: {e}. Try again:")


@router.message(ProfileStates.waiting_for_bio)
async def process_bio(message: Message, state: FSMContext) -> None:
    try:
        text = entities_to_html(message.text, entities=message.entities)
        BioSchema(bio=text)
        await state.update_data(bio=text)
        await message.answer(
            "Enter your location (max 50 chars):",
            reply_markup=make_keyboard(["Санкт-Петербург"]),
        )
        await state.set_state(ProfileStates.waiting_for_location)
    except ValueError as e:
        await message.answer(f"Invalid bio: {e}. Try again:")


@router.message(ProfileStates.waiting_for_location)
async def process_location(message: Message, state: FSMContext) -> None:
    try:
        text = entities_to_html(message.text, entities=message.entities)
        LocationSchema(location=text)
        await state.update_data(location=text)
        await message.answer(
            "Enter experience summary (max 150 chars):", reply_markup=make_keyboard([])
        )
        await state.set_state(ProfileStates.waiting_for_experience_summary)
    except ValueError as e:
        await message.answer(f"Invalid location: {e}. Try again:")


@router.message(ProfileStates.waiting_for_experience_summary)
async def process_experience_summary(message: Message, state: FSMContext) -> None:
    try:
        text = entities_to_html(message.text, entities=message.entities)
        ExperienceSummarySchema(experience_summary=text)
        await state.update_data(experience_summary=text)
        await message.answer(
            "Enter job status:",
            reply_markup=make_keyboard(JobStatus._member_names_.copy()),
        )
        await state.set_state(ProfileStates.waiting_for_job_status)
    except ValueError as e:
        await message.answer(f"Invalid summary: {e}. Try again:")


@router.message(ProfileStates.waiting_for_job_status)
async def process_job_status(message: Message, state: FSMContext) -> None:
    try:
        JobStatusSchema(job_status=JobStatus(message.text))
        await state.update_data(job_status=message.text)
        await message.answer(
            "Enter resume link (max 255 chars):", reply_markup=make_keyboard([])
        )
        await state.set_state(ProfileStates.waiting_for_resume_link)
    except (ValueError, Exception) as e:
        await message.answer(f"Invalid job status: {e}. Try again:")


example_socials = {
    SocialLink.VK.value: "https://vk.com/username",
    SocialLink.TELEGRAM.value: "https://t.me/username",
    SocialLink.GITHUB.value: "https://github.com/username",
}


@router.message(ProfileStates.waiting_for_resume_link)
async def process_resume_link(message: Message, state: FSMContext) -> None:
    try:
        ResumeLinkSchema(resume_link=message.text)
        await state.update_data(resume_link=message.text)
        await message.answer(
            f"Enter social links as JSON <code>\n{json.dumps(example_socials, ensure_ascii=False, indent=2)}\n </code>",
            reply_markup=make_keyboard([]),
        )
        await state.set_state(ProfileStates.waiting_for_social_links)
    except ValueError as e:
        await message.answer(f"Invalid resume link: {e}. Try again:")


@router.message(ProfileStates.waiting_for_social_links)
async def process_social_links(message: Message, state: FSMContext) -> None:
    try:
        social_links = json.loads(message.text)
        SocialLinksSchema(social_links=social_links)
        await state.update_data(social_links=social_links)
        await message.answer(
            "Enter skills (comma-separated, e.g., Python, FastAPI):",
            reply_markup=make_keyboard([]),
        )
        await state.set_state(ProfileStates.waiting_for_skills)
    except (ValueError, json.JSONDecodeError) as e:
        await message.answer(f"Invalid social links: {e}. Try again:")


@router.message(ProfileStates.waiting_for_skills)
async def process_skills(message: Message, state: FSMContext) -> None:
    try:
        skills = [s.strip() for s in message.text.split(", ")]
        SkillsSchema(skills=skills)
        data = await state.get_data()
        data["skills"] = skills

        # Собираем полную схему
        profile = ProfileSchema(**data)

        # Вызываем use case
        producer = Producer()
        await producer.update_profile(profile)

        await message.answer(
            "Profile updated successfully!", reply_markup=get_default_keyboard()
        )
        await state.clear()
    except Exception as e:
        await message.answer(f"Invalid skills: {e}. Try again:")


# endregion

# region Project


@router.message(Command("add_project"))
async def cmd_add_project(message: Message, state: FSMContext) -> None:
    await start_add_project(message, state)


@router.callback_query(F.data == "add_project")
async def cb_add_project(callback: CallbackQuery, state: FSMContext) -> None:
    await start_add_project(callback.message, state)


async def start_add_project(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Enter project title (max 50 chars):", reply_markup=make_keyboard([])
    )
    await state.set_state(ProjectStates.waiting_for_title)


@router.message(ProjectStates.waiting_for_title)
async def process_title(message: Message, state: FSMContext) -> None:
    try:
        text = entities_to_html(message.text, entities=message.entities)
        TitleSchema(title=text)
        await state.update_data(title=text)
        await message.answer(
            "Enter project description (max 1500 chars):",
            reply_markup=make_keyboard([]),
        )
        await state.set_state(ProjectStates.waiting_for_description)
    except ValueError as e:
        await message.answer(f"Invalid title: {e}. Try again:")


@router.message(ProjectStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext) -> None:
    try:
        text = entities_to_html(message.text, entities=message.entities)
        DescriptionSchema(description=text)
        await state.update_data(description=text)
        await message.answer(
            "Enter your role (max 20 chars):", reply_markup=make_keyboard([])
        )
        await state.set_state(ProjectStates.waiting_for_role)
    except ValueError as e:
        await message.answer(f"Invalid description: {e}. Try again:")


@router.message(ProjectStates.waiting_for_role)
async def process_role(message: Message, state: FSMContext) -> None:
    try:
        text = entities_to_html(message.text, entities=message.entities)
        RoleSchema(role=text)
        await state.update_data(role=text)
        await message.answer(
            "Enter technologies (comma-separated, e.g., Python, FastAPI):",
            reply_markup=make_keyboard([]),
        )
        await state.set_state(ProjectStates.waiting_for_technologies)
    except ValueError as e:
        await message.answer(f"Invalid role: {e}. Try again:")


@router.message(ProjectStates.waiting_for_technologies)
async def process_technologies(message: Message, state: FSMContext) -> None:
    try:
        technologies = [t.strip() for t in message.text.split(", ")]
        TechnologiesSchema(technologies=technologies)
        await state.update_data(technologies=technologies)
        await message.answer(
            "Enter business goal (max 150 chars):", reply_markup=make_keyboard([])
        )
        await state.set_state(ProjectStates.waiting_for_business_goal)
    except ValueError as e:
        await message.answer(f"Invalid technologies: {e}. Try again:")


@router.message(ProjectStates.waiting_for_business_goal)
async def process_business_goal(message: Message, state: FSMContext) -> None:
    try:
        text = entities_to_html(message.text, entities=message.entities)
        BusinessGoalSchema(business_goal=text)
        await state.update_data(business_goal=text)
        await message.answer(
            "Enter result (max 150 chars):", reply_markup=make_keyboard([])
        )
        await state.set_state(ProjectStates.waiting_for_result)
    except ValueError as e:
        await message.answer(f"Invalid business goal: {e}. Try again:")


@router.message(ProjectStates.waiting_for_result)
async def process_result(message: Message, state: FSMContext) -> None:
    try:
        text = entities_to_html(message.text, entities=message.entities)
        ResultSchema(result=text)
        await state.update_data(result=text)
        await message.answer(
            "Enter access note (max 150 chars, e.g., 'Internal project, NDA'):",
            reply_markup=make_keyboard(["Внутренний проект, NDA"]),
        )
        await state.set_state(ProjectStates.waiting_for_access_note)
    except ValueError as e:
        await message.answer(f"Invalid result: {e}. Try again:")


@router.message(ProjectStates.waiting_for_access_note)
async def process_access_note(message: Message, state: FSMContext) -> None:
    try:
        AccessNoteSchema(access_note=message.text)
        await state.update_data(access_note=message.text)
        await message.answer(
            "Is this a featured project? (yes/no):",
            reply_markup=make_keyboard(["Yes", "No"]),
        )
        await state.set_state(ProjectStates.waiting_for_is_featured)
    except ValueError as e:
        await message.answer(f"Invalid access note: {e}. Try again:")


@router.message(ProjectStates.waiting_for_is_featured)
async def process_is_featured(message: Message, state: FSMContext) -> None:
    try:
        is_featured = message.text.lower() in ("yes", "y", "true")
        IsFeaturedSchema(is_featured=is_featured)
        data = await state.get_data()
        data["is_featured"] = is_featured

        # Собираем полную схему
        project = ProjectSchema(
            **data,
            created_at=datetime.now(),  # Добавляем автоматически
        )

        producer = Producer()
        await producer.create_project(project)

        await message.answer(
            "Project added successfully!", reply_markup=get_default_keyboard()
        )
        await state.clear()
    except (ValueError, Exception) as e:
        await message.answer(f"Invalid input: {e}. Enter yes/no for is_featured:")


# endregion
