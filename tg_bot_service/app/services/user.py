import json
from typing import Optional, List
import logging

from aiogram.types import Message

from app.schemas.user import UserCreate, UserCreateDB, UserUpdateDB, User
from app.models.user import UserModel
from app.dao.user import UserDAO
from app.core.database import async_session_maker
from app.core.redis import get_redis

log = logging.getLogger(__name__)


class UserService:
    @classmethod
    async def create_user(cls, new_user: UserCreate) -> UserModel:
        async with async_session_maker() as session:
            user = await UserDAO.add(
                session,
                UserCreateDB(
                    **new_user.model_dump(),
                    is_verified=False,
                    is_admin=False
                )
            )

            await session.commit()
            log.info("Create new user %s", user.id)

        return user

    @classmethod
    async def get_user(cls, tg_id: int) -> Optional[UserModel]:
        redis_client = await get_redis()
        user = await redis_client.get(f"user:{tg_id}")

        if user:
            log.debug("User founded in redis")
            user = json.loads(user)
            return user

        async with async_session_maker() as session:
            user = await UserDAO.find_one_or_none(session, UserModel.tg_id == tg_id)
            user_schemas = User.model_validate(user)
            await redis_client.setex(f"user:{tg_id}", 30, user_schemas.model_dump_json())
            log.info("User founded in db")

        return user


    @classmethod
    async def create_and_update_user(cls, message: Message):
        log.debug("Started updating user: %s in DB", message.from_user.id)
        async with async_session_maker() as session:
            user_exist = await UserDAO.find_one_or_none(session, UserModel.tg_id == message.from_user.id)

            if user_exist is None:
                await UserDAO.add(
                    session,
                    UserCreateDB(
                        tg_id=message.from_user.id,
                        first_name=message.from_user.first_name,
                        last_name=message.from_user.last_name,
                        username=message.from_user.username,
                        is_verified=False,
                        is_admin=False,
                        group=None
                    )
                )
                log.info("New user: %s", message.from_user.id)
            else:
                await UserDAO.update(
                    session,
                    UserModel.id == user_exist.id,
                    obj_in=UserUpdateDB(
                        tg_id=message.from_user.id,
                        first_name=message.from_user.first_name,
                        last_name=message.from_user.last_name,
                        username=message.from_user.username,
                    )
                )
                log.info("Update user %s in DB", message.from_user.id)

            await session.commit()


    @classmethod
    async def get_all_groups(cls) -> List[int]:
        async with async_session_maker() as session:
            groups = await UserDAO.select_all_group(session)

            return groups