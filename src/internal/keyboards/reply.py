from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Today's Habits")],
        [KeyboardButton(text="Add Habit"), KeyboardButton(text="Connect Partner")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)