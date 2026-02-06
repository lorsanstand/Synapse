from taskiq_aio_pika import AioPikaBroker
from taskiq import TaskiqState, TaskiqEvents
from aiogram import Bot

from app.core.config import settings

broker = AioPikaBroker(
    settings.RABBITMQ_URL,
    queue_name="tg_service_queue"
)

import app.tasks.bot

@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def setup_bot(state: TaskiqState):
    bot = Bot(token=settings.BOT_TOKEN)
    state.bot = bot


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def close_bot(state: TaskiqState):
    await state.bot.session.close()