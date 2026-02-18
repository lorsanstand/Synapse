from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.types import Message
from log_config import set_logging
from fastapi import FastAPI

from app.core.config import settings
from app.handlers.base import router as base_router, set_commands
from app.handlers.schedule import router as schedule_router
from app.handlers.admin import router as admin_router
from app.services.user import UserService
from app.services.schedule import ScheduleService
from app.core.taskiq_app import broker
from app.core.redis import init_redis

set_logging(settings.LOG_LEVEL)
log = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
dp.include_router(base_router)
dp.include_router(schedule_router)
dp.include_router(admin_router)

scheduler = AsyncIOScheduler()
scheduler.add_job(ScheduleService.update_message, "cron", hour=0, minute=1, args=[bot])

app = FastAPI()

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


@app.get("/groups")
async def get_groups() -> List[Optional[int]]:
    return await UserService.get_all_groups()


async def main():
    settings.BOT_USERNAME = (await bot.get_me()).username

    scheduler.start()
    log.info("Scheduler started")
    await broker.startup()
    log.info("Taskiq started")
    await init_redis()
    log.info("Redis started")
    await set_commands(bot)
    dp.message.outer_middleware.register(UserUpdateMiddleware())

    config = uvicorn.Config(app, host="0.0.0.0", port=8080)
    server = uvicorn.Server(config)

    await asyncio.gather(
        dp.start_polling(bot),
        server.serve()
    )


if __name__ == "__main__":
    asyncio.run(main())