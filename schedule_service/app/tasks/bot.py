import logging

from app.core.taskiq_app import broker

log = logging.getLogger(__name__)


class BotTasks:
    @staticmethod
    @broker.task(task_name="send_edit_schedule")
    async def send_message(data: dict, group: int):
        log.info("Send bot change")