from datetime import date, timedelta
import logging
from typing import Optional, Union

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ParseMode

from app.models.user import UserModel
from app.dao.user import UserDAO
from app.core.database import async_session_maker
from app.utils.schedule import load_schedule
from app.utils.formatter import ScheduleFormatterMessage

log = logging.getLogger(__name__)

class ScheduleAction(CallbackData, prefix="sch"):
    action: str
    date_str: str


class ScheduleService:
    @classmethod
    async def get_schedule(cls, message: Union[Message, CallbackQuery], day: date = None, user: UserModel = None):
        if day is None:
            day = date.today()

        if user is None:
            async with async_session_maker() as session:
                user = await UserDAO.find_one_or_none(session, UserModel.tg_id == message.from_user.id)

        if user.group is None:
            if isinstance(message, Message):
                await message.answer("Пожалуйста укажите номер группы через /group")
            else:
                await message.message.answer("Пожалуйста укажите номер группы через /group")
            return

        keyboard = cls._get_schedule_keyboard(day)

        data = await load_schedule(int(user.group), begin=day, end=day)

        if data is None:
            if isinstance(message, Message):
                await message.answer("Что то сломалось")
            else:
                await message.message.answer("Что то сломалось")
            return

        text = ScheduleFormatterMessage.format_schedule(data[day.strftime("%d.%m.%Y")], day.strftime("%d.%m.%Y"))

        if isinstance(message, Message):
            await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        else:
            try:
                await message.message.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            except Exception as e:
                log.warning("Failed to edit message error: %s", e)


    @classmethod
    def _get_schedule_keyboard(cls, current_date: date):
        prev_date = current_date - timedelta(days=1)
        next_date = current_date + timedelta(days=1)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Пред. день",
                        callback_data=ScheduleAction(action="show", date_str=prev_date.isoformat()).pack()
                    ),
                    InlineKeyboardButton(
                        text="След. день ➡️",
                        callback_data=ScheduleAction(action="show", date_str=next_date.isoformat()).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📅 Сегодня",
                        callback_data=ScheduleAction(action="show", date_str=date.today().isoformat()).pack()
                    )
                ]
            ]
        )
        return keyboard


    @classmethod
    async def set_group(cls, group: str, message: Message):
        async with async_session_maker() as session:
            try:
                group = int(group)
            except ValueError:
                await message.answer("Это не номер группы")
                log.info("User typing not validate group")
                return


            await UserDAO.update(
                session,
                UserModel.tg_id == message.from_user.id,
                obj_in={"group": group}
            )

            await session.commit()

        log.info("Update group from user %s", message.from_user.id)
        await message.answer("Группа успешно добавлена")