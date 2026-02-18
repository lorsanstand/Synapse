import asyncio

from app.services.schedule import ScheduleService
from app.main import bot

asyncio.run(ScheduleService.update_message(bot))