from datetime import date
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from internal.service.habit import HabitService
from internal.service.pair import PairService
from internal.states.states import HabitState
from internal.keyboards.inline import get_habits_keyboard

router = Router()


@router.message(F.text == "Add Habit")
async def btn_add_habit(message: Message, state: FSMContext, pair_service: PairService):
    partner = await pair_service.get_partner(message.from_user.id)
    if not partner:
        await message.answer("You need to connect with a partner first.")
        return

    await message.answer("Enter the title of the new habit:")
    await state.set_state(HabitState.waiting_for_title)


@router.message(HabitState.waiting_for_title)
async def process_habit_title(message: Message, state: FSMContext, habit_service: HabitService):
    success = await habit_service.create_habit(message.from_user.id, message.text)
    if success:
        await message.answer(f"Habit '{message.text}' added successfully!")
    else:
        await message.answer("Failed to add habit.")

    await state.clear()


@router.message(F.text == "Today's Habits")
@router.message(F.text == "/today")
async def cmd_today(message: Message, habit_service: HabitService, pair_service: PairService):
    target_date = date.today()
    user_habits, partner_habits = await habit_service.get_pair_daily_habits(message.from_user.id, target_date)
    partner = await pair_service.get_partner(message.from_user.id)

    if not user_habits and not partner_habits:
        await message.answer("No habits found. Add one first!")
        return

    text = "Твои привычки на сегодня:\n"
    for h in user_habits:
        status = "✅" if h["is_completed"] else "❌"
        text += f"{h['title']} [{status}]\n"

    if partner_habits and partner:
        text += f"\nПрогресс партнера ({partner['name']}):\n"
        for h in partner_habits:
            status = "✅" if h["is_completed"] else "❌"
            text += f"{h['title']} [{status}]\n"

    await message.answer(text, reply_markup=get_habits_keyboard(user_habits))


@router.callback_query(F.data.startswith("toggle_"))
async def process_toggle(callback: CallbackQuery, habit_service: HabitService, pair_service: PairService, bot: Bot):
    habit_id = int(callback.data.split("_")[1])
    target_date = date.today()

    new_status, title = await habit_service.toggle_habit(callback.from_user.id, habit_id, target_date)

    user_habits, partner_habits = await habit_service.get_pair_daily_habits(callback.from_user.id, target_date)
    partner = await pair_service.get_partner(callback.from_user.id)

    text = "Твои привычки на сегодня:\n"
    for h in user_habits:
        status = "✅" if h["is_completed"] else "❌"
        text += f"{h['title']} [{status}]\n"

    if partner_habits and partner:
        text += f"\nПрогресс партнера ({partner['name']}):\n"
        for h in partner_habits:
            status = "✅" if h["is_completed"] else "❌"
            text += f"{h['title']} [{status}]\n"

    await callback.message.edit_text(text=text, reply_markup=get_habits_keyboard(user_habits))

    if new_status and partner:
        await bot.send_message(
            partner['id'],
            f"🎉 Твой партнер только что выполнил: {title}! Отличный повод не отставать!"
        )

    await callback.answer()