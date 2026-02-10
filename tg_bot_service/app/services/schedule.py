from datetime import date, timedelta
import json
import time
import logging
from typing import Optional, Union

import httpx
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ParseMode

from app.core.config import settings
from app.models.user import UserModel
from app.dao.user import UserDAO
from app.core.database import async_session_maker

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

        keyboard = cls.get_keyboard(day)

        data = await cls._get_schedule(int(user.group), begin=day, end=day)

        if data is None:
            if isinstance(message, Message):
                await message.answer("Что то сломалось")
            else:
                await message.message.answer("Что то сломалось")
            return

        text = cls.format_schedule(data[day.strftime("%d.%m.%Y")], day.strftime("%d.%m.%Y"))

        if isinstance(message, Message):
            await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        else:
            try:
                await message.message.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            except Exception as e:
                log.warning("Failed to edit message error: %s", e)


    @classmethod
    def get_keyboard(cls, current_date: date):
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
    async def _get_schedule(cls, group: int, begin: date, end: date) -> Optional[dict]:
        start_time = time.perf_counter()
        async with httpx.AsyncClient() as client:
            data = dict(
                group=group,
                begin=begin,
                end=end
            )

            try:
                response = await client.get(settings.SCHEDULE_URL, params=data)
            except httpx.ConnectError as e:
                log.error("Schedule getting error %s", e)
                return None

            if response.status_code != 200:
                log.error("Schedule getting error status code: %s", response.status_code)
                return None

        process_time = time.perf_counter() - start_time
        log.debug("Schedule completed successfully time: %.3fs", process_time)

        return json.loads(response.content)


    @classmethod
    def format_schedule(cls, data: dict, date_: str):
        if not data:
            return "🏖 Занятий нет, отдыхай!"

        text = f"🗓 <b>{data['day_week']} {date}</b>\n"
        text += "─" * 15 + "\n"

        sorted_pairs = sorted(data['pairs'].items(), key=lambda x: int(x[0]))

        for num, lessons in sorted_pairs:
            for lesson in lessons:

                sub = f" [Гр.{lesson['subgroup']}]" if lesson['subgroup'] else ""
                text += f"<b>{num}️⃣ {lesson['time']}</b>\n"
                text += f"🎓 <b>{lesson['lesson_name']}</b> ({lesson['type']}){sub}\n"
                text += f"👤 {lesson['teacher']}\n"

                audience = lesson['audience'].replace("Учебный корпус", "корп.")
                if "он-лайн" in audience.lower():
                    audience = "🌐 Онлайн"

                text += f"📍 <i>{audience}</i>\n\n"

        return text


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