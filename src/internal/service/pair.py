import logging
from typing import Optional
from ..repository.pair import PairRepository
from ..repository.user import UserRepository

logger = logging.getLogger(__name__)


class PairService:
    def __init__(self, pair_repo: PairRepository, user_repo: UserRepository):
        self.pair_repo = pair_repo
        self.user_repo = user_repo

    async def create_connection(self, first_user_id: int, second_user_id: int) -> bool:
        if first_user_id == second_user_id:
            logger.warning("User attempted to pair with themselves. User ID: %s", first_user_id)
            return False

        first_user_pair = await self.pair_repo.get_pair_by_user_id(first_user_id)
        second_user_pair = await self.pair_repo.get_pair_by_user_id(second_user_id)

        if first_user_pair or second_user_pair:
            logger.info("Connection failed. One of the users is already in a pair.")
            return False

        await self.pair_repo.create_pair(first_user_id, second_user_id)
        logger.info("Pair created successfully between %s and %s", first_user_id, second_user_id)
        return True

    async def get_partner(self, user_id: int) -> Optional[dict]:
        pair_data = await self.pair_repo.get_pair_by_user_id(user_id)
        if not pair_data:
            return None

        partner_id = pair_data['partner_id']
        return await self.user_repo.get_user(partner_id)