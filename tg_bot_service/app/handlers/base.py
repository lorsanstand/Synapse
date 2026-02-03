import logging

from aiogram import Router, Bot
from aiogram.types import Message, BotCommand, BotCommandScopeDefault
from aiogram.filters import CommandStart, Command

log = logging.getLogger(__name__)
router = Router()

async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="start",
            description="Запустить бота"
        ),
        BotCommand(
            command="help",
            description="Помощь"
        ),
        BotCommand(
            command="schedule",
            description="Расписание"
        ),
        BotCommand(
            command="group",
            description="Поставить группу"
        )
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

@router.message(CommandStart())
async def command_start(message: Message):
    await message.answer("""Хей! Приветствую! 🤖✨

Рад знакомству! Я — твой персональный ассистент. Со мной ты забудешь о рутине и сможешь .

Жми /help, если потеряешься, или просто выбирай нужный раздел в меню! 🚀""")
    log.info("send /start user: %s", message.from_user.id)


@router.message(Command("help"))
async def command_help(message: Message):
    await message.answer("help")
    log.info("send /helo user: %s", message.from_user.id)