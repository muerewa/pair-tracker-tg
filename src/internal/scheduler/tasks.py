import logging
from datetime import date
from aiogram import Bot
from internal.service.habit import HabitService
from internal.service.pair import PairService

logger = logging.getLogger(__name__)


async def evening_reminder(bot: Bot, habit_service: HabitService, pair_service: PairService):
    logger.info("Running evening reminder job")
    target_date = date.today()
    pairs = await pair_service.pair_repo.get_all_pairs()

    for pair in pairs:
        user1_id = pair['first_user_id']
        user2_id = pair['second_user_id']

        user1_habits, user2_habits = await habit_service.get_pair_daily_habits(user1_id, target_date)

        if not user1_habits:
            continue

        u1_all_done = all(h['is_completed'] for h in user1_habits)
        u2_all_done = all(h['is_completed'] for h in user2_habits)

        if u1_all_done and u2_all_done:
            msg = "Вы супер! Сегодня закрыты все привычки, так держать!"
            await bot.send_message(user1_id, msg)
            await bot.send_message(user2_id, msg)
        else:
            if not u1_all_done:
                missing = [h['title'] for h in user1_habits if not h['is_completed']]
                await bot.send_message(user1_id,
                                       f"Привет! День подходит к концу, а {', '.join(missing)} еще не сделано. Удели этому 5 минут!")

            if not u2_all_done:
                missing = [h['title'] for h in user2_habits if not h['is_completed']]
                await bot.send_message(user2_id,
                                       f"Привет! День подходит к концу, а {', '.join(missing)} еще не сделано. Удели этому 5 минут!")


async def weekly_stats(bot: Bot, habit_service: HabitService, pair_service: PairService):
    logger.info("Running weekly stats job")
    pairs = await pair_service.pair_repo.get_all_pairs()

    for pair in pairs:
        pair_id = pair['id']
        user1_id = pair['first_user_id']
        user2_id = pair['second_user_id']

        u1_stats = await habit_service.get_weekly_completed_count(pair_id, user1_id)
        u2_stats = await habit_service.get_weekly_completed_count(pair_id, user2_id)

        msg = f"📊 Итоги недели:\n\nТвои выполненные привычки: {u1_stats}\nПривычки партнера: {u2_stats}"
        await bot.send_message(user1_id, msg)

        msg_partner = f"📊 Итоги недели:\n\nТвои выполненные привычки: {u2_stats}\nПривычки партнера: {u1_stats}"
        await bot.send_message(user2_id, msg_partner)