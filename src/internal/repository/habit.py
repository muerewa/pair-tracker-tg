import asyncpg
from datetime import date
from typing import List

class HabitRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def add_habit_to_pair(self, pair_id: int, title: str) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                habit_id = await conn.fetchval(
                    "INSERT INTO habits (title) VALUES ($1) RETURNING id;",
                    title
                )
                await conn.execute(
                    "INSERT INTO pair_habits (pair_id, habit_id) VALUES ($1, $2);",
                    pair_id, habit_id
                )

    async def get_today_habits_with_logs(self, pair_id: int, user_id: int, target_date: date) -> List[dict]:
        query = """
            SELECT 
                h.id AS habit_id,
                h.title,
                COALESCE(hl.status, FALSE) AS is_completed
            FROM pair_habits ph
            JOIN habits h ON ph.habit_id = h.id
            LEFT JOIN habits_log hl ON h.id = hl.habit_id 
                AND hl.user_id = $1 
                AND hl.date = $2
            WHERE ph.pair_id = $3;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, user_id, target_date, pair_id)
            return [dict(row) for row in rows]

    async def toggle_habit_status(self, user_id: int, habit_id: int, target_date: date) -> bool:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                check_query = """
                    SELECT id FROM habits_log 
                    WHERE user_id = $1 AND habit_id = $2 AND date = $3;
                """
                log_id = await conn.fetchval(check_query, user_id, habit_id, target_date)

                if log_id:
                    await conn.execute("DELETE FROM habits_log WHERE id = $1;", log_id)
                    return False
                else:
                    await conn.execute(
                        """
                        INSERT INTO habits_log (user_id, habit_id, status, date) 
                        VALUES ($1, $2, TRUE, $3);
                        """,
                        user_id, habit_id, target_date
                    )
                    return True