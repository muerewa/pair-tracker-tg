from datetime import date
from typing import List, Tuple, Dict, Any
from internal.repository.habit import HabitRepository
from internal.repository.pair import PairRepository


class HabitService:
    def __init__(self, habit_repo: HabitRepository, pair_repo: PairRepository):
        self.habit_repo = habit_repo
        self.pair_repo = pair_repo

    async def create_habit(self, user_id: int, title: str) -> bool:
        pair_data = await self.pair_repo.get_pair_by_user_id(user_id)
        if not pair_data:
            return False

        await self.habit_repo.add_habit_to_pair(pair_data['id'], title)
        return True

    async def get_pair_daily_habits(self, user_id: int, target_date: date) -> Tuple[
        List[Dict[str, Any]], List[Dict[str, Any]]]:
        pair_data = await self.pair_repo.get_pair_by_user_id(user_id)
        if not pair_data:
            return [], []

        pair_id = pair_data['id']
        partner_id = pair_data['partner_id']

        user_habits = await self.habit_repo.get_today_habits_with_logs(pair_id, user_id, target_date)
        partner_habits = await self.habit_repo.get_today_habits_with_logs(pair_id, partner_id, target_date)

        return user_habits, partner_habits

    async def toggle_habit(self, user_id: int, habit_id: int, target_date: date) -> Tuple[bool, str]:
        status = await self.habit_repo.toggle_habit_status(user_id, habit_id, target_date)
        title = await self.habit_repo.get_habit_title(habit_id)
        return status, title

    async def get_weekly_completed_count(self, pair_id: int, user_id: int) -> int:
        return await self.habit_repo.get_weekly_stats(pair_id, user_id)

    async def delete_habit(self, habit_id: int) -> str:
        return await self.habit_repo.delete_habit(habit_id)