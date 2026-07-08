from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_habits_keyboard(habits: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for habit in habits:
        status_icon = "✅" if habit["is_completed"] else "❌"
        text = f"{habit['title']} [{status_icon}]"
        callback_data = f"toggle_{habit['habit_id']}"
        builder.row(InlineKeyboardButton(text=text, callback_data=callback_data))
    return builder.as_markup()