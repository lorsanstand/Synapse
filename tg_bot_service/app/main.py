import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.core.config import settings

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def starting(message: Message):
    await message.answer("Hi")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())