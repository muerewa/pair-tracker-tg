import logging
from typing import Optional, Tuple
from internal.repository.pair import PairRepository
from internal.repository.user import UserRepository

logger = logging.getLogger(__name__)


class PairService:
    def __init__(self, pair_repo: PairRepository, user_repo: UserRepository):
        self.pair_repo = pair_repo
        self.user_repo = user_repo

    async def connect_by_id(self, current_user_id: int, partner_id: int) -> Tuple[bool, str]:
        if current_user_id == partner_id:
            return False, "Нельзя пригласить самого себя."

        partner = await self.user_repo.get_user(partner_id)
        if not partner:
            return False, "Пользователь с таким ID не найден. Пусть он сначала запустит бота (/start)."

        first_user_pair = await self.pair_repo.get_pair_by_user_id(current_user_id)
        second_user_pair = await self.pair_repo.get_pair_by_user_id(partner_id)

        if first_user_pair or second_user_pair:
            return False, "Один из пользователей уже состоит в паре."

        await self.pair_repo.create_pair(current_user_id, partner_id)
        return True, "Успех"

    async def get_partner(self, user_id: int) -> Optional[dict]:
        pair_data = await self.pair_repo.get_pair_by_user_id(user_id)
        if not pair_data:
            return None
        return await self.user_repo.get_user(pair_data['partner_id'])