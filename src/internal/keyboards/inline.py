from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_today_keyboard(habits: list, has_partner: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for h in habits:
        icon = "✅" if h["is_completed"] else "❌"
        builder.row(InlineKeyboardButton(text=f"{icon} {h['title']}", callback_data=f"check|{h['habit_id']}"))

    if not has_partner:
        builder.row(InlineKeyboardButton(text="🔗 Пригласить партнёра", callback_data="invite_button"))

    return builder.as_markup()


def get_myhabits_keyboard(habits: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for h in habits:
        builder.row(InlineKeyboardButton(text=f"❌ {h['title']}", callback_data=f"delhabit|{h['habit_id']}"))

    builder.row(InlineKeyboardButton(text="➕ Добавить привычку", callback_data="addhabit_prompt"))
    return builder.as_markup()