import asyncpg
from typing import Optional, List


class PairRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_pair(self, first_user_id: int, second_user_id: int) -> int:
        query = """
            INSERT INTO pairs (first_user_id, second_user_id)
            VALUES ($1, $2)
            RETURNING id;
        """
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                pair_id = await conn.fetchval(query, first_user_id, second_user_id)
                return pair_id

    async def get_pair_by_user_id(self, tg_id: int) -> Optional[dict]:
        query = """
            SELECT id, first_user_id, second_user_id 
            FROM pairs 
            WHERE first_user_id = $1 OR second_user_id = $1;
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, tg_id)
            if not row:
                return None

            pair_data = dict(row)
            partner_id = pair_data['second_user_id'] if pair_data['first_user_id'] == tg_id else pair_data[
                'first_user_id']
            pair_data['partner_id'] = partner_id
            return pair_data

    async def get_all_pairs(self) -> List[dict]:
        query = "SELECT id, first_user_id, second_user_id FROM pairs;"
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]