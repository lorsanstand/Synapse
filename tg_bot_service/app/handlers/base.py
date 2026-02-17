import logging

from aiogram import Router, Bot
from aiogram.types import Message, BotCommand, BotCommandScopeDefault, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram import F

from app.models.user import UserModel
from app.services.link import LinkService

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
async def command_start(message: Message, command: CommandObject, user: UserModel):
    args = command.args

    await message.answer("""Хей! Приветствую! 🤖✨

Рад знакомству! Я — твой персональный ассистент. Со мной ты забудешь о рутине и сможешь .

Жми /help, если потеряешься, или просто выбирай нужный раздел в меню! 🚀""")
    log.info("send /start user: %s", message.from_user.id)

    if args:
        await LinkService.verify_user(message, args, user)


@router.message(Command("help"))
async def command_help(message: Message):
    await message.answer("""Я помогу тебе всегда держать расписание под рукой. Вот как со мной работать:
🛠 Основные команды

    /group — Установить твою учебную группу. Бот запомнит её, и тебе не придется вводить её каждый раз.

    /schedule — Показать расписание на сегодня для выбранной группы.""")
    log.info("send /helo user: %s", message.from_user.id)


@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()