from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from internal.service.user import UserService
from internal.service.pair import PairService
from internal.states.states import ConnectState
from internal.keyboards.reply import get_main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, user_service: UserService):
    await user_service.register(message.from_user.id, message.from_user.first_name)
    await message.answer(
        f"Welcome, {message.from_user.first_name}! Your connection ID is: {message.from_user.id}",
        reply_markup=get_main_menu()
    )


@router.message(F.text == "Connect Partner")
async def btn_connect(message: Message, state: FSMContext, pair_service: PairService):
    partner = await pair_service.get_partner(message.from_user.id)
    if partner:
        await message.answer(f"You are already paired with {partner['name']}.")
        return

    await message.answer("Send me the ID of your partner:")
    await state.set_state(ConnectState.waiting_for_partner_id)


@router.message(ConnectState.waiting_for_partner_id)
async def process_partner_id(message: Message, state: FSMContext, pair_service: PairService):
    try:
        partner_id = int(message.text)
    except ValueError:
        await message.answer("Invalid ID format. Please send a valid number.")
        return

    success = await pair_service.create_connection(message.from_user.id, partner_id)
    if success:
        await message.answer("Successfully paired!")
    else:
        await message.answer("Could not create pair. Check the ID and try again.")

    await state.clear()