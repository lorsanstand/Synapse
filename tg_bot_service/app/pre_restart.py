import asyncio

from app.core.database import async_session_maker
from app.core.config import settings
from app.schemas.user import UserCreateDB
from app.dao.user import UserDAO
from app.models.user import UserModel


async def init() -> None:
    async with async_session_maker() as session:
        super_user = await UserDAO.find_one_or_none(session, UserModel.tg_id==settings.TG_ID_ADMIN)

        if super_user is not None:
            return

        await UserDAO.add(
            session,
            obj_in=UserCreateDB(
                tg_id=settings.TG_ID_ADMIN,
                is_admin=True,
                is_verified=True
            )
        )
        await session.commit()

asyncio.run(init())