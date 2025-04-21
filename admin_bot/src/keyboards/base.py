from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Дефолтная клавиатура
def get_default_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/update_profile"),
                KeyboardButton(text="/add_project"),
            ]
        ],
        resize_keyboard=True,
    )
