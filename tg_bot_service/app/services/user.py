from typing import Optional
import logging

from aiogram.types import Message

from app.schemas.user import UserCreate, UserCreateDB, UserUpdateDB
from app.models.user import UserModel
from app.dao.user import UserDAO
from app.core.database import async_session_maker

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
        async with async_session_maker() as session:
            user = await UserDAO.find_one_or_none(session, UserModel.tg_id == tg_id)

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