from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="/today")],
        [KeyboardButton(text="/myhabits"), KeyboardButton(text="/invite")],
        [KeyboardButton(text="/week"), KeyboardButton(text="/streak")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)