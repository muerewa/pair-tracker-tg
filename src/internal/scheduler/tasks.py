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

        u1_done = [h for h in user1_habits if h['is_completed']]
        u2_done = [h for h in user2_habits if h['is_completed']]

        u1_all_done = len(u1_done) == len(user1_habits)
        u2_all_done = len(u2_done) == len(user2_habits)

        if u1_all_done and u2_all_done:
            msg = "🌟 Вы супер! Сегодня закрыты все привычки, так держать!"
            await bot.send_message(user1_id, msg)
            await bot.send_message(user2_id, msg)
            continue

        if not u1_all_done:
            missing = [h['title'] for h in user1_habits if not h['is_completed']]
            msg = f"🌙 День подходит к концу! Остались незакрытые привычки:\n" + "\n".join(
                missing) + "\nУдели им несколько минут"
            if u2_all_done:
                msg += "\n\n⭐️ Твой партнёр сегодня всё выполнил! Не отставай."
            else:
                msg += "\n\nУ партнёра тоже есть незакрытые задачи."
            await bot.send_message(user1_id, msg)

        if not u2_all_done:
            missing = [h['title'] for h in user2_habits if not h['is_completed']]
            msg = f"🌙 День подходит к концу! Остались незакрытые привычки:\n" + "\n".join(
                missing) + "\nУдели им несколько минут"
            if u1_all_done:
                msg += "\n\n⭐️ Твой партнёр сегодня всё выполнил! Не отставай."
            else:
                msg += "\n\nУ партнёра тоже есть незакрытые задачи."
            await bot.send_message(user2_id, msg)


async def weekly_stats(bot: Bot, habit_service: HabitService, pair_service: PairService):
    logger.info("Running weekly stats job")
    pairs = await pair_service.pair_repo.get_all_pairs()

    for pair in pairs:
        pair_id = pair['id']
        user1_id = pair['first_user_id']
        user2_id = pair['second_user_id']

        u1 = await pair_service.user_repo.get_user(user1_id)
        u2 = await pair_service.user_repo.get_user(user2_id)

        u1_stats = await habit_service.get_weekly_completed_count(pair_id, user1_id)
        u2_stats = await habit_service.get_weekly_completed_count(pair_id, user2_id)

        total = len(await habit_service.habit_repo.get_today_habits_with_logs(pair_id, user1_id, date.today())) * 7

        def build_report(current_user, partner, c_stats, p_stats):
            report = "<b>📊 Статистика за неделю</b>\n\n"
            report += f"<u>{current_user['name']}</u>\n✅ Выполнено: {c_stats}/{total} привычек\n🔥 Текущий стрик: {current_user['streak']} дн.\n\n"
            report += f"<u>{partner['name']}</u>\n✅ Выполнено: {p_stats}/{total} привычек\n🔥 Текущий стрик: {partner['streak']} дн.\n\n"

            if c_stats > p_stats:
                leader = current_user['name']
            elif p_stats > c_stats:
                leader = partner['name']
            else:
                leader = "Ничья! Оба круты."

            report += f"🏆 Самый активный за неделю: {leader}"
            return report

        await bot.send_message(user1_id, build_report(u1, u2, u1_stats, u2_stats), parse_mode="HTML")
        await bot.send_message(user2_id, build_report(u2, u1, u2_stats, u1_stats), parse_mode="HTML")