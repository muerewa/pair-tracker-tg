import asyncio
import logging

from internal.config.config import load
from internal.migrations.migrator import apply_migrations

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    config = load()
    try:
        await apply_migrations(config, "up")
    except Exception as e:
        logger.critical(f"Couldn't run migrations: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main())