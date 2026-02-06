from taskiq_aio_pika import AioPikaBroker

from app.core.config import settings

broker = AioPikaBroker(
    settings.RABBITMQ_URL,
    queue_name="tg_service_queue"
)