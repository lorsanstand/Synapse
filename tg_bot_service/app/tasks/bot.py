import logging
from datetime import datetime

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.taskiq_app import broker
from app.core.database import async_session_maker
from app.dao.user import UserDAO
from app.models.user import UserModel
from app.services.schedule import ScheduleAction

log = logging.getLogger(__name__)


class BotTasks:

    @staticmethod
    @broker.task(task_name="send_edit_schedule")
    async def send_message(data: dict, group: int):
        async with async_session_maker() as session:
            users = await UserDAO.find_all(session, None, None, UserModel.group == group)

        bot: Bot = broker.state.bot

        date_obj = datetime.strptime(data["day"], "%d.%m.%Y")

        text = format_change_notification(data)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{data["day"]}",
                        callback_data=ScheduleAction(action="show", date_str=date_obj.date().isoformat()).pack()
                    )
                ]
            ]
        )

        for user in users:
            try:
                await bot.send_message(user.tg_id, text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            except Exception as ex:
                log.warning("Failed send to message %s", ex)
                continue

        log.info("Successfully send messages")



def format_change_notification(data):
    text = f"⚠️ <b>Внимание! Изменение в расписании</b>\n"
    text += f"📅 <b>{data['day']} ({data['day_week']})</b>\n"
    text += "─" * 15 + "\n"

    for i, change in enumerate(data["changes"], 1):
        field_name = change["field"]
        old_val = change["old"] if change["old"] else "—"
        new_val = change["new"] if change["new"] else "❌ Отменено"

        field_map = {
            "lesson_name": "Предмет",
            "teacher": "Преподаватель",
            "audience": "Аудитория",
            "time": "Время",
            "type": "Тип занятия"
        }
        display_field = field_map.get(field_name, field_name)

        text += f"{i}. <b>{display_field}:</b>\n"
        text += f"   <s>{old_val}</s> ➔ <b>{new_val}</b>\n\n"

    text += "🔔 Проверьте обновленное расписание в меню!"
    return text
