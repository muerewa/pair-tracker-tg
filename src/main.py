import asyncio
import logging
import asyncpg
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from internal.config.config import load
from internal.migrations.migrator import apply_migrations

from internal.repository.user import UserRepository
from internal.repository.pair import PairRepository
from internal.repository.habit import HabitRepository

from internal.service.user import UserService
from internal.service.pair import PairService
from internal.service.habit import HabitService

from internal.handlers.user import router as user_router
from internal.handlers.habit import router as habit_router
from internal.scheduler.tasks import evening_reminder, weekly_stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting application")
    config = load()

    try:
        await apply_migrations(config,"up")
    except Exception as e:
        logger.critical("Failed to apply migrations. Error: %s", e)
        return

    db_url = config.url or f"postgresql://{config.user}:{config.password}@{config.host}:{config.port}/{config.name}"

    pool = await asyncpg.create_pool(db_url, min_size=5, max_size=20)

    user_repo = UserRepository(pool)
    pair_repo = PairRepository(pool)
    habit_repo = HabitRepository(pool)

    user_service = UserService(user_repo)
    pair_service = PairService(pair_repo, user_repo)
    habit_service = HabitService(habit_repo, pair_repo)

    bot_token = config.bot_token
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp["user_service"] = user_service
    dp["pair_service"] = pair_service
    dp["habit_service"] = habit_service

    dp.include_router(user_router)
    dp.include_router(habit_router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(evening_reminder, 'cron', hour=21, minute=0, args=[bot, habit_service, pair_service])
    scheduler.add_job(weekly_stats, 'cron', day_of_week='sun', hour=10, minute=0,
                      args=[bot, habit_service, pair_service])
    scheduler.start()

    logger.info("Bot and scheduler are ready and starting polling")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())