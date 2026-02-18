from datetime import datetime

from aiogram.types import Message, Chat
from aiogram.enums import ParseMode
from aiogram import Bot


class MessageUtils:
    @classmethod
    async def send_message(cls, bot: Bot, chat_id: int, text: str, parse_mode: ParseMode) -> Message:
        msg = await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
        return msg


    @classmethod
    async def edit_message(cls, bot: Bot, chat_id: int, message_id: int, text: str, parse_mode: ParseMode) -> Message:
        msg = await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode=parse_mode)
        return msg

    @classmethod
    def get_message(cls, bot: Bot, chat_id: int, message_id: int) -> Message:
        return Message(
                    message_id=message_id,
                    chat=Chat(id=chat_id, type="private"),
                    date=datetime.today(),
                    bot=bot
                )