from typing import Dict, Any
import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.types import Message
from log_config import set_logging

from app.core.config import settings
from app.handlers.base import router as base_router, set_commands
from app.handlers.schedule import router as schedule_router
from app.handlers.admin import router as admin_router
from app.services.user import UserService
from app.core.taskiq_app import broker

set_logging(settings.LOG_LEVEL)
log = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
dp.include_router(base_router)
dp.include_router(schedule_router)
dp.include_router(admin_router)

last_updates = {}


class UserUpdateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:
        user_id = event.from_user.id
        now = datetime.now()
        last_time = last_updates.get(user_id)

        if not last_time or (now - last_time) > timedelta(minutes=10):
            await UserService.create_and_update_user(event)
            last_updates[user_id] = now


        data["user"] = await UserService.get_user(event.from_user.id)

        return await handler(event, data)


async def main():
    await set_commands(bot)
    dp.message.outer_middleware.register(UserUpdateMiddleware())
    await dp.start_polling(bot)
    await broker.startup()


if __name__ == "__main__":
    try:
        log.info("Starting bot")
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("Stoping bot")