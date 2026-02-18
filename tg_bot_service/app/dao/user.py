from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserModel
from app.models.last_message import LastMessageModel
from app.schemas.user import UserCreateDB, UserUpdateDB
from app.core.dao import BaseDAO

class UserDAO(BaseDAO[UserModel, UserCreateDB, UserUpdateDB]):
    model = UserModel


    @classmethod
    async def select_all_group(cls, session: AsyncSession):
        stmt = (
            select(UserModel.group)
            .where(UserModel.group != None)
            .distinct(UserModel.group)
        )
        result = await session.execute(stmt)

        return result.scalars().all()


    @classmethod
    async def select_users_last_messages_id(cls, session: AsyncSession):
        stmt = (
            select(UserModel.tg_id, LastMessageModel.message_id)
            .join(LastMessageModel)
        )
        result = await session.execute(stmt)

        return result.mappings().all()

