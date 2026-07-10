from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from internal.service.user import UserService
from internal.service.pair import PairService
from internal.keyboards.reply import get_main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, user_service: UserService):
    name = message.from_user.first_name
    await user_service.register(message.from_user.id, name)

    text = (
        f"Привет, <b>{name}</b>! Я бот для трекинга привычек.\n"
        "Используй /today для просмотра дня.\n"
        "Нажимай кнопки под своими привычками, чтобы отметить выполнение.\n\n"
        "⚙️ /myhabits — управление привычками\n"
        "🔥 /streak — текущий стрик\n"
        "📊 /week — статистика за неделю\n\n"
        "🔗 Твой ID:"
        f"<blockquote><code>{message.from_user.id}</code></blockquote>"
        "<i>(нажми на цифры, чтобы скопировать)</i>"
    )
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="HTML")

@router.message(Command("invite"))
async def cmd_invite(message: Message, pair_service: PairService):
    partner = await pair_service.get_partner(message.from_user.id)
    if partner:
        await message.answer("У тебя уже есть партнёр.")
        return

    user_id = message.from_user.id
    text = (
        "🔗 Твой ID для приглашения:"
        f"<blockquote><code>{user_id}</code></blockquote>"
        "Отправь его партнёру. Ему нужно написать боту команду:"
        f"<blockquote><code>/pair {user_id}</code></blockquote>"
        "После этого вы будете в паре! 🤝"
    )
    await message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "invite_button")
async def callback_invite(callback: CallbackQuery, pair_service: PairService):
    user_id = callback.from_user.id
    text = (
        "🔗 Твой ID для приглашения:"
        f"<blockquote><code>{user_id}</code></blockquote>"
        "Отправь его партнёру. Ему нужно написать боту команду:"
        f"<blockquote><code>/pair {user_id}</code></blockquote>"
        "После этого вы будете в паре! 🤝"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@router.message(Command("pair"))
async def cmd_pair(message: Message, pair_service: PairService, user_service: UserService, bot: Bot):
    parts = message.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer(
            "Неверный формат. Нужно написать так:"
            "<blockquote><code>/pair 123456789</code></blockquote>"
            "Попробуй еще раз.",
            parse_mode="HTML"
        )
        return

    partner_id = int(parts[1])
    success, msg = await pair_service.connect_by_id(message.from_user.id, partner_id)

    if not success:
        await message.answer(msg)
        return

    inviter = await user_service.get_profile(partner_id)
    user_name = message.from_user.first_name

    await message.answer(
        f"🎉 Теперь вы в паре с <b>{inviter['name']}</b>!\n"
        "Привычки объединены. Используй /today для просмотра общего прогресса.",
        parse_mode="HTML"
    )
    await bot.send_message(
        partner_id,
        f"🎉 <b>{user_name}</b> присоединился к вам!\nТеперь у вас общие привычки. /today — смотреть день.",
        parse_mode="HTML"
    )

@router.message(Command("week"))
async def cmd_week(message: Message):
    await message.answer("Статистика формируется автоматически в конце недели.")

@router.message(Command("streak"))
async def cmd_streak(message: Message, user_service: UserService, pair_service: PairService):
    user = await user_service.get_profile(message.from_user.id)
    partner = await pair_service.get_partner(message.from_user.id)

    text = f"🔥 Твой текущий стрик: <b>{user['streak']}</b> дн."
    if partner:
        text += f"\n🔥 Стрик {partner['name']}: <b>{partner['streak']}</b> дн."

    await message.answer(text, parse_mode="HTML")