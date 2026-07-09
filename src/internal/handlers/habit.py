import logging
from datetime import date
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from internal.service.habit import HabitService
from internal.service.pair import PairService
from internal.states.states import HabitState
from internal.keyboards.inline import get_today_keyboard, get_myhabits_keyboard

router = Router()
logger = logging.getLogger(__name__)


async def build_today_message(user_id: int, habit_service: HabitService, pair_service: PairService):
    target_date = date.today()
    user_habits, partner_habits = await habit_service.get_pair_daily_habits(user_id, target_date)
    partner = await pair_service.get_partner(user_id)

    msg = f"📅 <b>Привычки на {target_date.strftime('%d.%m.%Y')}</b>\n\n"

    if not user_habits and not partner_habits:
        msg += "<i>У тебя пока нет привычек. Добавь их через /myhabits</i>"
    else:
        msg += "<u>Твои привычки:</u>\n"
        for h in user_habits:
            icon = "✅" if h["is_completed"] else "❌"
            msg += f"{h['title']} [{icon}]\n"

    if partner and partner_habits:
        msg += f"\n\n<u>Прогресс партнера ({partner['name']}):</u>\n"
        for h in partner_habits:
            icon = "✅" if h["is_completed"] else "❌"
            msg += f"{h['title']} [{icon}]\n"
    elif not partner:
        msg += "\n\nℹ️ <i>Ты пока один — добавь партнёра для совместного трекинга!</i>\nНажми /invite, чтобы получить код приглашения."

    keyboard = get_today_keyboard(user_habits, bool(partner))
    return msg, keyboard


@router.message(Command("today"))
async def cmd_today(message: Message, habit_service: HabitService, pair_service: PairService):
    text, keyboard = await build_today_message(message.from_user.id, habit_service, pair_service)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("check|"))
async def handle_checkin(call: CallbackQuery, habit_service: HabitService, pair_service: PairService, bot: Bot):
    habit_id = int(call.data.split("|")[1])
    target_date = date.today()

    new_status, title = await habit_service.toggle_habit(call.from_user.id, habit_id, target_date)

    if new_status:
        await call.answer(f"Отметили: {title}")
        partner = await pair_service.get_partner(call.from_user.id)
        if partner:
            name = call.from_user.first_name
            try:
                await bot.send_message(partner['id'],
                                       f"🎉 {name} только что выполнил(а): {title}! Отличный повод не отставать!")
            except Exception as e:
                logger.warning("Failed to notify partner: %s", e)
    else:
        await call.answer("Отметка снята.")

    text, keyboard = await build_today_message(call.from_user.id, habit_service, pair_service)
    await call.message.edit_text(text=text, reply_markup=keyboard, parse_mode="HTML")


@router.message(Command("myhabits"))
async def cmd_myhabits(message: Message, habit_service: HabitService):
    user_habits, _ = await habit_service.get_pair_daily_habits(message.from_user.id, date.today())

    text = "📋 <b>Текущие привычки:</b>\n"
    if not user_habits:
        text += "— нет привычек —"
    else:
        for h in user_habits:
            text += f"– {h['title']}\n"

    await message.answer(text, reply_markup=get_myhabits_keyboard(user_habits), parse_mode="HTML")


@router.callback_query(F.data == "addhabit_prompt")
async def prompt_add_habit(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введи название новой привычки (до 50 символов):")
    await state.set_state(HabitState.waiting_for_title)
    await call.answer()


@router.message(HabitState.waiting_for_title)
async def process_new_habit(message: Message, state: FSMContext, habit_service: HabitService, pair_service: PairService,
                            bot: Bot):
    title = message.text.strip()
    if len(title) > 50:
        await message.answer("Название должно быть до 50 символов.")
        return

    success = await habit_service.create_habit(message.from_user.id, title)
    if success:
        await message.answer(f"Привычка «{title}» добавлена.")
        partner = await pair_service.get_partner(message.from_user.id)
        if partner:
            try:
                await bot.send_message(partner['id'],
                                       f"📝 Твой партнёр добавил новую общую привычку: «{title}».\nСписок привычек обновлён (/myhabits).")
            except Exception as e:
                logger.warning("Failed to notify partner: %s", e)
    else:
        await message.answer("Для добавления привычек нужен партнёр.")

    await state.clear()


@router.callback_query(F.data.startswith("delhabit|"))
async def handle_delete_habit(call: CallbackQuery, habit_service: HabitService, pair_service: PairService, bot: Bot):
    habit_id = int(call.data.split("|")[1])

    deleted_title = await habit_service.delete_habit(habit_id)
    if not deleted_title:
        await call.answer("Привычка не найдена.")
        return

    await call.answer(f"«{deleted_title}» удалена.")

    partner = await pair_service.get_partner(call.from_user.id)
    if partner:
        try:
            await bot.send_message(
                partner['id'],
                f"🗑 Твой партнёр удалил общую привычку «{deleted_title}»."
            )
        except Exception as e:
            logger.warning("Failed to notify partner: %s", e)

    user_habits, _ = await habit_service.get_pair_daily_habits(call.from_user.id, date.today())

    text = "📋 <b>Текущие привычки:</b>\n"
    if not user_habits:
        text += "— нет привычек —"
    else:
        for h in user_habits:
            text += f"– {h['title']}\n"

    await call.message.edit_text(text=text, reply_markup=get_myhabits_keyboard(user_habits), parse_mode="HTML")