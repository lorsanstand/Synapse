from datetime import timedelta

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters.callback_data import CallbackData

from app.core.redis import get_redis
from app.dao.user import UserDAO
from app.models.user import UserModel
from app.utils.strings import generate_random_string
from app.core.config import settings
from app.core.database import async_session_maker


class LinkTimeAction(CallbackData, prefix="lnktime"):
    action: str
    time: int
    type: str


class LinkTypeAction(CallbackData, prefix="lnktype"):
    action: str
    type: str


class LinkService:
    @classmethod
    async def choose_type_link(cls, message: Message):
        await message.answer("Пожалуйста выберите тип ссылки", reply_markup=cls._get_type_link_keyboard())


    @classmethod
    async def choose_time_link(cls, message: CallbackQuery, type: str):
        await message.message.edit_text(text="Выбери длительность работы ссылки", reply_markup=cls._get_time_link_keyboard(type))


    @classmethod
    async def create_link(cls, message: CallbackQuery, type: str, time: int):
        redis_client = await get_redis()

        key = generate_random_string(7)

        key_exist = await redis_client.get(f"{type}:{key}")

        if key_exist is not None:
            key = generate_random_string(7)

        await redis_client.setex(f"{type}:{key}", time, 1)

        await message.message.edit_text(f"Приглашение: https://t.me/{settings.BOT_USERNAME}?start={key}")


    @classmethod
    async def verify_user(cls, message: Message, key: str, user: UserModel):
        redis_client = await get_redis()

        key_exist = await redis_client.get(f"get_access:{key}")

        if key_exist is None:
            return

        async with async_session_maker() as session:
            await UserDAO.update(
                session,
                UserModel.id == user.id,
                obj_in={"is_verified": True}
            )
            await session.commit()

        await message.answer("Поздравляю вы верифицированы")


    @staticmethod
    def _get_type_link_keyboard():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Дать доступ к боту",
                        callback_data=LinkTypeAction(action="show", type="get_access").pack()
                    )
                ]
            ]
        )
        return keyboard


    @staticmethod
    def _get_time_link_keyboard(type: str):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="1 Час",
                        callback_data=LinkTimeAction(action="show", time=int(timedelta(hours=1).total_seconds()),
                                                     type=type).pack()
                    ),
                    InlineKeyboardButton(
                        text="2 Часа",
                        callback_data=LinkTimeAction(action="show", time=int(timedelta(hours=2).total_seconds()),
                                                     type=type).pack()
                    ),
                    InlineKeyboardButton(
                        text="4 Часа",
                        callback_data=LinkTimeAction(action="show", time=int(timedelta(hours=4).total_seconds()),
                                                     type=type).pack()
                    ),
                    InlineKeyboardButton(
                        text="12 Часов",
                        callback_data=LinkTimeAction(action="show", time=int(timedelta(hours=12).total_seconds()),
                                                     type=type).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="1 день",
                        callback_data=LinkTimeAction(action="show", time=int(timedelta(days=1).total_seconds()),
                                                     type=type).pack()
                    ),
                    InlineKeyboardButton(
                        text="2 дня",
                        callback_data=LinkTimeAction(action="show", time=int(timedelta(days=2).total_seconds()),
                                                     type=type).pack()
                    ),
                    InlineKeyboardButton(
                        text="5 дней",
                        callback_data=LinkTimeAction(action="show", time=int(timedelta(days=5).total_seconds()),
                                                     type=type).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="1 неделя",
                        callback_data=LinkTimeAction(action="show", time=int(timedelta(days=7).total_seconds()),
                                                     type=type).pack()
                    )
                ]
            ]
        )
        return keyboard