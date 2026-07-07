from typing import Optional
from ..repository.user import UserRepository

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, tg_id: int, name: str) -> dict:
        return await self.user_repo.get_or_create_user(tg_id, name)

    async def get_profile(self, tg_id: int) -> Optional[dict]:
        return await self.user_repo.get_user(tg_id)