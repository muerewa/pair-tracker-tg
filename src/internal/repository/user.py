import asyncpg
from typing import Optional

class UserRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_or_create_user(self, tg_id: int, name: str) -> dict:
        query = """
            INSERT INTO users (id, name, streak)
            VALUES ($1, $2, 0)
            ON CONFLICT (id) DO UPDATE SET name = $2
            RETURNING id, name, streak;
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, tg_id, name)
            return dict(row)

    async def get_user(self, tg_id: int) -> Optional[dict]:
        query = "SELECT id, name, streak FROM users WHERE id = $1;"
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, tg_id)
            return dict(row) if row else None

    async def update_streak(self, tg_id: int, streak: int) -> None:
        query = "UPDATE users SET streak = $1 WHERE id = $2;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, streak, tg_id)