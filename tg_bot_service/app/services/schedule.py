from datetime import date, timedelta
import logging
from typing import Optional, Union

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

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
        builder = InlineKeyboardBuilder()

        prev_week = current_date - timedelta(days=7)
        next_week = current_date + timedelta(days=7)

        monday = current_date - timedelta(days=current_date.weekday())
        sunday = monday + timedelta(days=6)

        week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]

        for index, week_day in enumerate(week):
            day = monday + timedelta(days=index)

            if day == current_date:
                week_day = "🔸" + week_day

            builder.add(InlineKeyboardButton(
                        text=week_day,
                        callback_data=ScheduleAction(action="show", date_str=day.isoformat()).pack()
                    ))

        builder.adjust(7)

        text = f"{monday.strftime('%d.%m.%Y')} - {sunday.strftime('%d.%m.%Y')}"

        builder.row(InlineKeyboardButton(text=text, callback_data="ignore"))

        builder.row(
            InlineKeyboardButton(
                text="Пред. Неделя",
                callback_data=ScheduleAction(action="show", date_str=prev_week.isoformat()).pack()
            ),
            InlineKeyboardButton(
                text="След. Неделя",
                callback_data=ScheduleAction(action="show", date_str=next_week.isoformat()).pack()
            ),
        )

        builder.row(
            InlineKeyboardButton(
                text="📅 Сегодня",
                callback_data=ScheduleAction(action="show", date_str=date.today().isoformat()).pack()
            )
        )

        return builder.as_markup()


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