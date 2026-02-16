from datetime import date
from typing import Optional
import time
import logging
import json

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)

async def load_schedule(group: int, begin: date, end: date) -> Optional[dict]:
    start_time = time.perf_counter()
    async with httpx.AsyncClient() as client:
        data = dict(
            group=group,
            begin=begin,
            end=end
        )

        try:
            response = await client.get(settings.SCHEDULE_URL, params=data)
        except httpx.ConnectError as e:
            log.error("Schedule getting error %s", e)
            return None

        if response.status_code != 200:
            log.error("Schedule getting error status code: %s", response.status_code)
            return None

    process_time = time.perf_counter() - start_time
    log.debug("Schedule completed successfully time: %.3fs", process_time)

    return json.loads(response.content)