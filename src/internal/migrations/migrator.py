import asyncpg
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


async def apply_migrations(config, direction: str):
    db_url = config.url or f"postgresql://{config.user}:{config.password}@{config.host}:{config.port}/{config.name}"

    current_dir = os.path.dirname(os.path.abspath(__file__))

    if direction == "up":
        filepath = os.path.join(current_dir, "001_init_up.sql")
    elif direction == "down":
        filepath = os.path.join(current_dir, "001_init_down.sql")
    else:
        print("Error defining direction")
        return

    try:
        conn = await asyncpg.connect(db_url)

        with open(filepath, 'r', encoding='utf-8') as file:
            sql_script = file.read()


        await conn.execute(sql_script)

    except FileNotFoundError:
        print(f"Migration file not found: {filepath}")
    except Exception as e:
        print(f"DB error:: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()